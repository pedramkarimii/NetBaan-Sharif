from decouple import config  # noqa
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from apps.account.models import UserAuth, User
from apps.account.serializers import auth
from rest_framework import status, views
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import redis
import pytz
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login, logout

from apps.account.throttling import CustomRateThrottle
from apps.account.users_auth.services import update_user_auth_uuid
from utility.otp_redis.otp import CodeGenerator

"""
Initializes a Redis client to connect to the Redis server.
- `redis.StrictRedis`: Creates a Redis client instance using the specified host, port, and database index.
- `host=config('REDIS_HOST')`: Specifies the Redis server hostname, retrieved from configuration.
- `port=config('REDIS_PORT')`: Specifies the Redis server port, retrieved from configuration.
- `db=0`: Specifies the Redis database index (default is 0).
"""
redis_client = redis.StrictRedis(host=config('REDIS_HOST'), port=config('REDIS_PORT'), db=0)


class Logout(views.APIView):
    """
    API view to handle user logout.
    This view handles the process of logging out a user. It will log out the user and flush their session data
    if they are authenticated. If the user is not authenticated, it returns an appropriate error message.
    """

    def get(self, request):
        """
        Handles GET requests to log out the authenticated user.

        - Parameters:
            - `request`: The HTTP request object containing user and session information.
        - Returns: A `Response` object indicating the result of the logout attempt.
        """
        if request.user.is_authenticated:
            logout(self.request)
            request.session.flush()
            return Response({"message": _("You have been logged out successfully")}, status=status.HTTP_200_OK)
        else:
            return Response({"error": _("You are not logged in")}, status=status.HTTP_400_BAD_REQUEST)


class Login(views.APIView):
    """
    API view to handle user login operations.
    This view provides endpoints for displaying the login page and for processing login requests.
    It handles the initial request for login by sending a verification code to the user's email.
    """
    throttle_classes = [CustomRateThrottle]
    throttle_scope = 'default'

    def post(self, request):  # noqa
        """
        Handles POST requests for user login.
        This method processes the login request by validating the provided email and sending a verification code to it.
        - Parameters:
            - `request`: The HTTP request object containing the user-provided email.
        - Returns: A `Response` object with a success message if the email is valid, or error details
         if validation fails.
        """
        serializer = auth.LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = serializer.validated_data['user']
            code = CodeGenerator().generate_and_store_code(email)
            send_mail(
                subject='Verification Code',
                message=f'Your verification code is: {code}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            request.session['user_login_info'] = {'email': email}

            return Response({"message": _("Code sent to your email")}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginVerifyCode(views.APIView):
    """
    API view to handle verification of login codes sent to the user via email.
    This view processes the verification code entered by the user, checking its validity
    and ensuring that the user is authenticated. If valid, it logs the user in and updates
    authentication tokens.
    """

    def post(self, request):  # noqa
        """
        Handles POST requests for verifying the login code.
        - Parameters:
            - `request`: The HTTP request object containing the verification code.
        - Returns: A `Response` object with the result of the verification process.
        """
        serializer = auth.VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            user_session = request.session.get('user_login_info')
            if not user_session:
                return Response({"error": _("Session expired")}, status=status.HTTP_400_BAD_REQUEST)
            email_session = user_session['email']
            user = User.objects.filter(email=email_session).first()

            if user:
                code_instance = redis_client.get(email_session)  # noqa
                if not code_instance:
                    return Response({"error": _("Code is expired")}, status=status.HTTP_400_BAD_REQUEST)

                stored_code = code_instance.decode('utf-8')  # noqa
                current_time = datetime.now(tz=pytz.timezone('Asia/Tehran'))
                expiration_time = current_time + timedelta(minutes=2)

                if code == stored_code and expiration_time > current_time:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    user = request.user
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)

                    redis_client.set(f"{email_session}:access_token", access_token, ex=600)
                    redis_client.set(f"{email_session}:refresh_token", refresh_token, ex=3600)
                    redis_client.delete(email_session)
                    return Response({"message": _("Code verified successfully")}, status=status.HTTP_200_OK)
                else:
                    redis_client.delete(email_session)
                    return Response({"error": _("Code is expired or invalid")}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": _("User not found")}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegister(views.APIView):
    """
    API view for user registration. This view handles user registration requests, including sending
    an OTP to the user's email for verification.
    Methods:
       - get: Returns a message prompting the user to enter their information.
       - post: Handles user registration by validating the data and sending an OTP.
    """
    serializer_class = auth.UserRegistrationSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'default'

    def post(self, request):
        """
        Handles POST requests for user registration. Validates the provided data and sends an OTP
        to the user's email if the data is valid.
        Parameters:
            - request: The HTTP request object containing user registration data.
        Returns:
            - Response: A success message if registration is successful, or validation errors if data is invalid.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": _("Code sent to your email")}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """
        Handles the process of creating a user and sending an OTP.
        Parameters:
           - serializer: The validated serializer instance containing user data.
        Actions:
           - Generates and stores an OTP for the user.
           - Stores user registration information in the session.
           - Sends an OTP email to the user.
        """
        user_data = serializer.validated_data
        email = user_data['email']
        otp = CodeGenerator().generate_and_store_code(email)

        self.request.session['user_registration_info'] = {
            'phone_number': user_data['phone_number'],
            'email': email,
            'username': user_data['username'],
            'password': user_data['password'],
        }

        self.send_otp_email(email, otp)

    def send_otp_email(self, email, otp):  # noqa
        """
        Sends an OTP email to the user.
        Parameters:
            - email: The recipient's email address.
            - otp: The OTP to be included in the email.
        Actions:
            - Sends an email to the user containing the OTP and its expiration time.
        """
        subject = _('Your OTP for Verification')
        message = _('Your OTP for login is (Expiry date two minutes): {otp}').format(otp=otp)
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)


class UserRegistrationVerifyCode(views.APIView):
    """
    API view for verifying user registration using an OTP code. This view handles the verification of
    the OTP code sent to the user's email and completes the user registration if the code is valid.
    Methods:
       - get: Returns a message prompting the user to enter their OTP code.
       - post: Handles the verification of the OTP code and completes the user registration.
    """

    def post(self, request):  # noqa
        """
        Handles POST requests for OTP verification and user registration. Validates the OTP code and
        creates a user if the code is valid.
        Parameters:
            - request: The HTTP request object containing the OTP code.
        Returns:
            - Response: A success message if registration is successful, or error messages if the code is
             invalid or expired.
        """
        serializer = auth.VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            user_session = request.session.get('user_registration_info')
            if not user_session:
                return Response({"error": _("Session expired")}, status=status.HTTP_400_BAD_REQUEST)

            email = user_session.get('email')
            code_instance = redis_client.get(email)  # noqa

            if not code_instance:
                return Response({"error": _("Code is expired")}, status=status.HTTP_400_BAD_REQUEST)

            stored_code = code_instance.decode('utf-8')  # noqa
            current_time = datetime.now(tz=pytz.timezone('Asia/Tehran'))
            expiration_time = current_time + timedelta(minutes=2)

            if code == stored_code and expiration_time > current_time:
                User.objects.create_user(
                    phone_number=user_session['phone_number'],
                    email=user_session['email'],
                    username=user_session['username'],
                    password=user_session['password'],
                )
                redis_client.delete(email)
                return Response({"message": _("User created successfully")}, status=status.HTTP_201_CREATED)
            else:
                redis_client.delete(email)
                return Response({"error": _("Code is expired or invalid")}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
