from rest_framework import serializers
from apps.account.users_auth.token import verify_token, refresh_access_token
from django.contrib.auth import get_user_model

User = get_user_model()


class TokenVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying a provided token. It contains:
    - `token`: The token to be verified.

    The `validate_token` method is used to check if the provided token is valid.
    If the token is not valid, a `ValidationError` is raised.
    """
    token = serializers.CharField()

    def validate_token(self, token):
        if not verify_token(request=self.context["request"], raw_token=token):
            raise serializers.ValidationError("Invalid token")
        return token


class RefreshTokenSerializer(serializers.Serializer):
    """
    Serializer for handling token refresh requests. It contains:
    - `refresh_token`: The refresh token used to obtain a new access token.
    """
    refresh_token = serializers.CharField()
