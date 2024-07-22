from django.test import TestCase
from django.db.utils import IntegrityError
from apps.account.models import User


class UserModelTests(TestCase):

    def setUp(self):
        """
        Create a User instance to be used in tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            phone_number='12345678901',
            password='securepassword123'
        )

    def test_user_creation(self):
        """
        Test user creation with valid data.
        """
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(phone_number='12345678901')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_default_values(self):
        """
        Test default values for boolean fields.
        """
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            phone_number='10987654321',
            password='anotherpassword123'
        )
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_unique_constraints(self):
        """
        Test the unique constraints on username, email, and phone_number fields.
        """
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser',
                email='unique@example.com',
                phone_number='09876543210',
                password='anotherpassword123'
            )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='newuser',
                email='testuser@example.com',
                phone_number='09876543210',
                password='anotherpassword123'
            )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='newuser',
                email='newuser@example.com',
                phone_number='12345678901',
                password='anotherpassword123'
            )

    def test_required_fields(self):
        """
        Test missing required fields raise validation errors.
        """
        with self.assertRaises(TypeError):
            User.objects.create_user(username='missing_email')

    def test_string_representation(self):
        """
        Test the string representation of the user.
        """
        self.assertEqual(str(self.user), 'testuser - 12345678901')
