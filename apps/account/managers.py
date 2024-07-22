from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone_number, email, username, password):
        """
        Creates and saves a regular user with the given phone number, email, username, and password.
        """
        if not phone_number:
            raise ValueError('The phone number must be set')
        elif not email:
            raise ValueError('The Email must be set')
        elif not username:
            raise ValueError('The username must be set')
        user = self.model(phone_number=phone_number, email=self.normalize_email(email), username=username)
        user.is_admin = False
        user.is_superuser = False
        user.is_superuser = False
        user.set_password(password)
        user.save()
        return user

    def create_admin(self, phone_number, email, username, password):
        """
        Creates and saves an admin user with the given phone number, email, username, and password.
        """
        user = self.create_user(phone_number, email, username, password)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = False
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, email, username, password):
        """
        Creates and saves a superuser with the given phone number, email, username, and password.
        """
        user = self.create_user(phone_number, email, username, password)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.set_password(password)
        user.save()
        return user


class UserAuthQuerySet(models.QuerySet):
    pass


class UserAuthManager(models.Manager):
    """Manager for handling address operations."""

    def get_queryset(self):
        """Get the queryset object associated with this manager."""
        if not hasattr(self.__class__, '__queryset'):
            self.__class__.__queryset = UserAuthQuerySet(self.model)
        return self.__queryset
