from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from unittest.mock import patch
User = get_user_model()


class UserListViewTests(APITestCase):

    def setUp(self):
        """
        Create users and an admin user for testing.
        """
        # Create non-admin users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            phone_number='11111111111',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            phone_number='22222222222',
            password='password123'
        )

        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            phone_number='33333333333',
            password='adminpassword123'
        )

        # Generate tokens for authentication
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
        self.user_token, _ = Token.objects.get_or_create(user=self.user1)

        # Define URL for the list view
        self.url = reverse('list-user')  # Adjusted to match the URL pattern name

    def test_list_users_admin(self):
        """
        Test that admin can list users.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Check the number of users returned

    def test_list_users_non_admin(self):
        """
        Test that non-admin users cannot list users.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_users(self):
        """
        Test searching users by username, email, and phone_number.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

        response = self.client.get(self.url, {'search': 'user1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'user1')

        response = self.client.get(self.url, {'search': 'user2@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'user2@example.com')

    def test_pagination(self):
        """
        Test pagination in the user list view.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

        response = self.client.get(self.url, {'page_size': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Should return 1 user per page

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('next' in response.data)  # Check if pagination links are present

    def test_filtering_by_is_active(self):
        """
        Test filtering users by `is_active` status.
        """
        # Set some users as inactive
        self.user1.is_active = False
        self.user1.save()

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(self.url, {'is_active': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user2', [user['username'] for user in response.data['results']])
        self.assertNotIn('user1', [user['username'] for user in response.data['results']])
#
#
# class DetailViewTests(APITestCase):
#
#     def setUp(self):
#         """
#         Create users and generate tokens for authentication.
#         """
#         # Create non-admin users
#         self.user1 = User.objects.create_user(
#             username='user1',
#             email='user1@example.com',
#             phone_number='11111111111',
#             password='password123'
#         )
#         self.user2 = User.objects.create_user(
#             username='user2',
#             email='user2@example.com',
#             phone_number='22222222222',
#             password='password123'
#         )
#
#         # Create an admin user
#         self.admin_user = User.objects.create_superuser(
#             username='admin',
#             email='admin@example.com',
#             phone_number='33333333333',
#             password='adminpassword123'
#         )
#
#         # Generate tokens for authentication
#         self.user1_token, _ = Token.objects.get_or_create(user=self.user1)
#         self.user2_token, _ = Token.objects.get_or_create(user=self.user2)
#         self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
#
#         # Define URLs for the detail view
#         self.user1_url = reverse('detail-user', kwargs={'pk': self.user1.pk})
#         self.user2_url = reverse('detail-user', kwargs={'pk': self.user2.pk})
#
#     def test_get_user_detail_as_owner(self):
#         """
#         Test that a user can retrieve their own details.
#         """
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
#         response = self.client.get(self.user1_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['username'], 'user1')
#         self.assertEqual(response.data['email'], 'user1@example.com')
#         self.assertEqual(response.data['phone_number'], '11111111111')
#
#     def test_get_user_detail_as_admin(self):
#         """
#         Test that an admin can retrieve any user's details.
#         """
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
#         response = self.client.get(self.user2_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['username'], 'user2')
#         self.assertEqual(response.data['email'], 'user2@example.com')
#         self.assertEqual(response.data['phone_number'], '22222222222')
#
#     def test_get_user_detail_as_non_owner_non_admin(self):
#         """
#         Test that a non-admin user cannot retrieve another user's details.
#         """
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
#         response = self.client.get(self.user2_url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Forbidden access
#
#     def test_get_user_detail_non_existent_user(self):
#         """
#         Test that retrieving a non-existent user returns a 404 error.
#         """
#         non_existent_url = reverse('detail-user', kwargs={'pk': 9999})  # Assume 9999 does not exist
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
#         response = self.client.get(non_existent_url)
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)




class LogoutTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            phone_number='11111111111',
            password='password123'
        )
        self.client.login(email='testuser@example.com', password='password123')
        self.url = reverse('logout')

    def test_logout_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'You have been logged out successfully')

    def test_logout_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'You are not logged in')


class LoginTests(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.email = 'pedram.9060@gmail.com'

        # Ensure no existing user with the same username or email
        User = get_user_model()
        User.objects.filter(email=self.email).delete()  # Delete existing user with this email

        self.user = User.objects.create_user(
            username='PedramKarimi',  # Ensure this username does not conflict
            email=self.email,
            phone_number='09128355747',
            password='qwertyQ@!'
        )

    @patch('django.core.mail.send_mail')
    def test_login_success(self, mock_send_mail):
        data = {'email': self.email}
        response = self.client.post(self.url, data, format='json')

        # Debugging: Print response content for troubleshooting
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Code sent to your email')
        mock_send_mail.assert_called_once()

    def test_login_invalid_email(self):
        data = {'email': 'invalidemail@example.com'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class LoginVerifyCodeTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123'
        )
        self.url = reverse('login-verify-code')
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    @patch('django.core.mail.send_mail')
    def test_login_verify_code_success(self, mock_send_mail):
        # Simulate sending the code
        self.redis_client.set('testuser@example.com', '123456')
        data = {'code': '123456'}
        self.client.login(email='testuser@example.com', password='password123')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Code verified successfully')

    def test_login_verify_code_invalid(self):
        data = {'code': 'wrongcode'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)




class UserRegisterTests(APITestCase):
    def setUp(self):
        self.url = reverse('user-register')

    @patch('django.core.mail.send_mail')
    def test_user_register_success(self, mock_send_mail):
        data = {
            'email': 'newuser@example.com',
            'phone_number': '1234567890',
            'username': 'newuser',
            'password': 'password123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Code sent to your email')
        mock_send_mail.assert_called_once()

    def test_user_register_invalid(self):
        data = {
            'email': 'invalidemail',
            'phone_number': '1234567890',
            'username': 'newuser',
            'password': 'password123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserRegistrationVerifyCodeTests(APITestCase):
    def setUp(self):
        self.url = reverse('user-registration-verify-code')
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.redis_client.set('newuser@example.com', '123456')

    def test_user_registration_verify_code_success(self):
        data = {'code': '123456'}
        session_data = {
            'phone_number': '1234567890',
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'password123'
        }
        self.client.session['user_registration_info'] = session_data
        self.client.session.save()
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'User created successfully')

    def test_user_registration_verify_code_invalid(self):
        data = {'code': 'wrongcode'}
        session_data = {
            'phone_number': '1234567890',
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'password123'
        }
        self.client.session['user_registration_info'] = session_data
        self.client.session.save()
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)