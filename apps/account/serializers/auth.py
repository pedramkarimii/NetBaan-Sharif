from rest_framework import serializers
from django.contrib.auth import get_user_model

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
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

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
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data


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
