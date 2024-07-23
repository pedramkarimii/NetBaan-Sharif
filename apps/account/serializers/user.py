import re
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.core import validators

User = get_user_model()


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    """
    username = serializers.CharField(
        validators=[validators.UsernameValidator()],
        required=False
    )
    email = serializers.EmailField(
        validators=[validators.EmailValidator()],
        required=False
    )
    phone_number = serializers.CharField(
        validators=[validators.PhoneNumberMobileValidator()],
        required=False
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validators.PasswordValidator()]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False},
            'username': {'required': False},
            'phone_number': {'required': False},
        }

    def validate(self, data):
        """
        Validate the data and return the validated data.
        """
        # Check for uniqueness of the data if necessary
        if 'email' in data and User.objects.filter(email=data['email']).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError({'email': 'This email is already in use.'})
        if 'username' in data and User.objects.filter(username=data['username']).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError({'username': 'This username is already in use.'})
        if 'phone_number' in data and User.objects.filter(phone_number=data['phone_number']).exclude(
                id=self.instance.id).exists():
            raise serializers.ValidationError({'phone_number': 'This phone number is already in use.'})
        return data

    def update(self, instance, validated_data):
        """
        Update the user instance with the validated data.
        """
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for handling password change requests.
    """
    old_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True, validators=[validators.PasswordValidator()])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate that the two new password fields match and the new password is different from the old password.
        """
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({"new_password2": "New passwords don't match"})

        user = self.context['request'].user
        if user.check_password(data['new_password1']):
            raise serializers.ValidationError("The new password must be different from the old password.")

        return data

    def save(self, **kwargs):
        """
        Update the user's password with the new password.
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed representation of the User model.
    """

    class Meta:
        """
        Specifies the model to serialize, which is the User model.
        """
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'is_staff', 'is_active', 'is_superuser']
        read_only_fields = ['id', 'username', 'email', 'phone_number', 'is_staff', 'is_active', 'is_superuser']
        error_messages = {
            'default': 'Bad Request.'
        }
