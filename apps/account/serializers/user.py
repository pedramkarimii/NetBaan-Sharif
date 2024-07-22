import re
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False},
            'username': {'required': False},
            'phone_number': {'required': False},
        }
        validators = [
            serializers.UniqueTogetherValidator(queryset=User.objects.all(),
                                                fields=['username', 'email', 'phone_number'])
        ]
        error_messages = {
            'default': 'Bad Request.'
        }

    def update(self, instance, validated_data):
        """
        Update the user instance with the validated data.
        """
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
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)
    error_messages = {
        'default': 'Bad Request.'
    }

    def validate(self, data):
        """
        Validate that the two new password fields match.
        """
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({"new_password2": "New passwords don't match"})
        return data

    def validate_new_password1(self, value):
        """
       Validate the new password to ensure it meets complexity requirements and is different from the old password.
       """
        user = self.context['request'].user
        if user.check_password(value):
            raise serializers.ValidationError("The new password must be different from the old password.")
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter, one lowercase letter,"
                " one digit, and one special character."
            )
        if ' ' in value:
            raise serializers.ValidationError("Password cannot contain spaces.")
        return value

    def save(self, **kwargs):
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
