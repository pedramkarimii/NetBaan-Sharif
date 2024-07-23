from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserListViewTests(APITestCase):

    def setUp(self):
        """
        Create users and an admin user for testing.
        """
        self.user1, _ = User.objects.get_or_create(
            username='Sharif',
            defaults={
                'password': 'qwertyQ@1',
                'phone_number': '09107654322',
                'email': 'Sharif@example.com'
            }
        )
        self.user2, _ = User.objects.get_or_create(
            username='netbaan',
            defaults={
                'password': 'qwertyQ@1',
                'phone_number': '09107654321',
                'email': 'netbaan@example.com'
            }
        )

        self.admin_user, _ = User.objects.get_or_create(
            username='pedramkarimi',
            defaults={
                'password': 'qwertyQ@1',
                'phone_number': '09128355747',
                'email': 'pedramkarimi@gmail.com'
            }
        )
        self.admin_user.set_password('qwertyQ@1')
        self.admin_user.is_superuser = True
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
        self.user_token, _ = Token.objects.get_or_create(user=self.user1)
        self.url = reverse('list-user')

    def test_list_users_admin(self):
        """
        Test that admin can list users.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(self.url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_list_users_non_admin(self):
        """
        Test that non-admin users cannot list users.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_users(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

        response = self.client.get(self.url, {'search': 'Sharif'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'Sharif')

        response = self.client.get(self.url, {'search': 'netbaan@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'netbaan@example.com')

    def test_pagination(self):
        """
        Test pagination in the user list view.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

        response = self.client.get(self.url, {'page_size': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('next' in response.data)

    def test_filtering_by_is_active(self):
        """
        Test filtering users by `is_active` status.
        """
        self.user1.is_active = False
        self.user1.save()

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(self.url, {'is_active': 'true'})
        print(response.status_code)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('netbaan', [user['username'] for user in response.data['results']])
        self.assertNotIn('Sharif', [user['username'] for user in response.data['results']])


class UserDetailViewTests(APITestCase):

    def setUp(self):
        """
        Create users and an admin user for testing.
        """
        self.user1 = User.objects.create_user(
            username='Sharif',
            password='qwertyQ@1',
            phone_number='09107654322',
            email='Sharif@example.com'
        )
        self.user2 = User.objects.create_user(
            username='netbaan',
            password='qwertyQ@1',
            phone_number='09107654321',
            email='netbaan@example.com'
        )

        self.admin_user = User.objects.create_superuser(
            username='pedramkarimi',
            password='qwertyQ@1',
            phone_number='09128355747',
            email='pedramkarimi@gmail.com'
        )

        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
        self.user1_token, _ = Token.objects.get_or_create(user=self.user1)
        self.user2_token, _ = Token.objects.get_or_create(user=self.user2)

        self.user1_url = reverse('detail-user', args=[self.user1.id])
        self.user2_url = reverse('detail-user', args=[self.user2.id])

    def test_retrieve_user_detail_admin(self):
        """
        Test that admin can retrieve details of any user.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(self.user1_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'Sharif')

        response = self.client.get(self.user2_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'netbaan')

    def test_retrieve_user_detail_owner(self):
        """
        Test that users can retrieve their own details.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        response = self.client.get(self.user1_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'Sharif')

    def test_retrieve_user_detail_non_owner(self):
        """
        Test that users cannot retrieve details of other users.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        response = self.client.get(self.user2_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_detail_nonexistent_user(self):
        """
        Test that attempting to retrieve details for a nonexistent user returns a 404 error.
        """
        nonexistent_user_url = reverse('detail-user', args=[99999])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(nonexistent_user_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class UserChangePasswordViewTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(
            username='Sharif',
            password='password1@23',
            phone_number='09107654322',
            email='Sharif@gmail.com'
        )
        self.user2 = self.User.objects.create_user(
            username='netbaan',
            password='password1@23',
            phone_number='09107654321',
            email='netbaan@gmail.com'
        )
        self.admin_user = self.User.objects.create_superuser(
            username='admin',
            password='adminpassword@123',
            phone_number='09128355747',
            email='admin@gmail.com'
        )
        self.user1_token, _ = Token.objects.get_or_create(user=self.user1)
        self.user2_token, _ = Token.objects.get_or_create(user=self.user2)
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
        self.user1_url = reverse('change-password', args=[self.user1.id])
        self.user2_url = reverse('change-password', args=[self.user2.id])
        self.nonexistent_user_url = reverse('change-password', args=[99999])

    def test_change_pass_details_success_owner(self):
        """
        Test that a user can successfully update their own password.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        data = {
            'old_password': 'password1@23',
            'new_password1': 'Newpassword@123!',
            'new_password2': 'Newpassword@123!'
        }
        response = self.client.put(self.user1_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_change_pass_details_success_admin(self):
        """
        Test that an admin can successfully update the password of another user.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = {
            'old_password': 'password1@23',
            'new_password1': 'Newpassword@123!',
            'new_password2': 'Newpassword@123!'
        }
        response = self.client.put(self.user2_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_change_pass_details_invalid_data(self):
        """
        Test that updating user password fails with invalid data.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        data = {
            'old_password': '',
            'new_password1': '',
            'new_password2': ''
        }
        response = self.client.put(self.user1_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)
        self.assertIn('new_password1', response.data)
        self.assertIn('new_password2', response.data)

    def test_change_pass_details_non_owner(self):
        """
        Test that a user cannot update the password of another user.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        data = {
            'old_password': 'password1@23',
            'new_password1': 'Newpassword@123!',
            'new_password2': 'Newpassword@123!'
        }
        response = self.client.put(self.user2_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_password_details_unauthorized(self):
        """
        Test that an unauthenticated request cannot update user password.
        """
        data = {
            'old_password': 'password1@23',
            'new_password1': 'Newpassword@123!',
            'new_password2': 'Newpassword@123!'
        }
        response = self.client.put(self.user1_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_pass_details_nonexistent_user(self):
        """
        Test that attempting to update password for a nonexistent user returns a 404 error.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = {
            'old_password': 'password1@23',
            'new_password1': 'Newpassword@123!',
            'new_password2': 'Newpassword@123!'
        }
        response = self.client.put(self.nonexistent_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_change_pass_details_unauthorized(self):
        """
        Test that an unauthenticated request cannot update user details.
        """
        data = {
            'old_password': 'password@123',
            'new_password1': 'Newpassword@123!',
            'new_password2': 'Newpassword@123!'
        }
        response = self.client.put(self.user1_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_details_nonexistent_user(self):
        """
        Test that attempting to update details for a nonexistent user returns a 404 error.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = {
            'old_password': 'password@123',
            'new_password1': 'Newpassword@123!',
            'new_password2': 'Newpassword@123!'
        }
        response = self.client.put(self.nonexistent_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserUpdateViewTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(
            username='Sharif',
            password='password@123',
            phone_number='09107654322',
            email='Sharif@gmail.com'
        )
        self.user2 = self.User.objects.create_user(
            username='netbaan',
            password='password@123',
            phone_number='09107654321',
            email='netbaan@gmail.com'
        )
        self.admin_user = self.User.objects.create_superuser(
            username='admin',
            password='adminpassword@123',
            phone_number='09128355747',
            email='admin@gmail.com'
        )

        self.user1_token, _ = Token.objects.get_or_create(user=self.user1)
        self.user2_token, _ = Token.objects.get_or_create(user=self.user2)
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)

        self.user1_url = reverse('update-user', args=[self.user1.id])
        self.user2_url = reverse('update-user', args=[self.user2.id])
        self.nonexistent_user_url = reverse('update-user', args=[99999])

    def test_update_user_details_success_owner(self):
        """
        Test that a user can successfully update their own details.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        data = {
            'username': 'SharifUpdated',
            'email': 'SharifUpdated@gmail.com',
            'phone_number': '09107654323'
        }
        response = self.client.put(self.user1_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'SharifUpdated')
        self.assertEqual(response.data['email'], 'SharifUpdated@gmail.com')
        self.assertEqual(response.data['phone_number'], '09107654323')

    def test_update_user_details_success_admin(self):
        """
        Test that an admin can successfully update the details of another user.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = {
            'username': 'netbaanUpdated',
            'email': 'netbaanUpdated@gmail.com',
            'phone_number': '09107654324'
        }
        response = self.client.put(self.user2_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'netbaanUpdated')
        self.assertEqual(response.data['email'], 'netbaanUpdated@gmail.com')
        self.assertEqual(response.data['phone_number'], '09107654324')

    def test_update_user_details_invalid_data(self):
        """
        Test that updating user details fails with invalid data.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        data = {
            'username': '',
            'email': 'invalid-email',
            'phone_number': 'invalid-phone'
        }
        response = self.client.put(self.user1_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertIn('phone_number', response.data)

    def test_update_user_details_non_owner(self):
        """
        Test that a user cannot update the details of another user.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user1_token.key)
        data = {
            'username': 'netbaanUpdatedByOtherUser',
            'email': 'netbaanUpdatedByOtherUser@gmail.com',
            'phone_number': '09107654325'
        }
        response = self.client.put(self.user2_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_details_nonexistent_user(self):
        """
        Test that attempting to update a nonexistent user returns a 404 error.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = {
            'username': 'nonexistent',
            'email': 'nonexistent@gmail.com',
            'phone_number': '09107654327'
        }
        response = self.client.put(self.nonexistent_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            phone_number='11111111111',
            password='password123'
        )
        self.user_token, _ = Token.objects.get_or_create(user=self.user)
        self.url = reverse('logout')

    def test_logout_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
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
