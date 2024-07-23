from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core import validators

User = get_user_model()


class VerifyCodeSerializer(serializers.Serializer):
    """
    Serializer for verifying a code.
    """
    code = serializers.CharField(max_length=6, min_length=6, required=True, write_only=True)

    def validate_code(self, value):  # noqa
        """
        Validate that the code is numeric and exactly 6 digits long.
        """
        if not value.isdigit():
            raise serializers.ValidationError("The code must be numeric.")
        if len(value) != 6:
            raise serializers.ValidationError("The code must be exactly 6 digits long.")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, validators=[validators.PasswordValidator()])
    password2 = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(validators=[validators.PhoneNumberMobileValidator()])
    email = serializers.EmailField(validators=[validators.EmailValidator()])
    username = serializers.CharField(validators=[validators.UsernameValidator()])

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, data):
        """
        Validate that the two passwords match.
        """
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")

        # Ensure the password meets complexity requirements
        password_validator = validators.PasswordValidator()
        try:
            password_validator(password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": e.detail})

        return data

    def create(self, validated_data):
        """
        Create and return a new user instance, setting the password.
        """
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate the provided email and password.
        """
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")
        data['user'] = user
        return data
