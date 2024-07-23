from django.test import TestCase
from django.db import IntegrityError, transaction
from apps.account.models import User


class UserModelTests(TestCase):

    def setUp(self):
        """
        Create a User instance to be used in tests.
        """
        self.user = User.objects.create_user(
            username='PedramKarimi',
            email='pedram.9060@gmail.com',
            phone_number='09128355747',
            password='qwertyQ@11'
        )

    def test_user_creation(self):
        """
        Test user creation with valid data.
        """
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(phone_number='09128355747')
        self.assertEqual(user.username, 'PedramKarimi')
        self.assertEqual(user.email, 'pedram.9060@gmail.com')
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_default_values(self):
        """
        Test default values for boolean fields.
        """
        user = User.objects.create_user(
            username='AnotherUser',
            email='another.email@gmail.com',
            phone_number='09128355748',
            password='differentPassword'
        )
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_unique_constraints(self):
        """
        Test the unique constraints on username, email, and phone_number fields.
        """
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    username='PedramKarimi',
                    email='unique.email1@gmail.com',
                    phone_number='09128355748',
                    password='newPassword1'
                )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    username='UniqueUsername1',
                    email='pedram.9060@gmail.com',
                    phone_number='09128355749',
                    password='newPassword2'
                )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    username='UniqueUsername2',
                    email='unique.email2@gmail.com',
                    phone_number='09128355747',
                    password='newPassword3'
                )

    def test_required_fields(self):
        """
        Test missing required fields raise validation errors.
        """
        with self.assertRaises(TypeError):
            User.objects.create_user(username='missing_email', password='password')

    def test_string_representation(self):
        """
        Test the string representation of the user.
        """
        self.assertEqual(str(self.user), 'PedramKarimi - 09128355747')
