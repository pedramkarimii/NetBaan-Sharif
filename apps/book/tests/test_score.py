from django.contrib.auth import get_user_model
from django.db import transaction, connection
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class ScoreAddTestCase(APITestCase):

    def setUp(self):
        """Sets up the test environment by creating a user and logging them in."""
        self.user = User.objects.create_user(
            username='Netbann',
            password='qwertyQ@1',
            phone_number='09107654321',
            email='Netbann@example.com'
        )
        print(f"Created user: {self.user}")
        login_success = self.client.login(username='Netbann', password='qwertyQ@1')
        print(f"Login successful: {login_success}")
        self.book_id = 1

    def test_add_review_success(self):
        """Tests adding a review successfully with a valid rating."""
        url = reverse('add-score', args=[self.book_id])
        data = {'rating': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('message'), 'Review added successfully')
        self.assertIn('recommendations', response.data)

    def test_add_review_not_authenticated(self):
        """Tests adding a review when the user is not authenticated."""
        self.client.logout()
        url = reverse('add-score', args=[self.book_id])
        data = {'rating': 5}
        response = self.client.post(url, data, format='json')
        print("Add Review Not Authenticated Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_add_review_already_exists(self):
        """Tests adding a review when the review already exists for the book."""
        url = reverse('add-score', args=[self.book_id])
        data = {'rating': 5}
        response = self.client.post(url, data, format='json')
        print("First Add Review Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, data, format='json')
        print("Second Add Review Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data.get('error'), 'Review already exists')

    def test_update_review_success(self):
        """Tests updating a review successfully."""
        self.test_add_review_success()

        url = reverse('update-review', args=[self.book_id])
        data = {'rating': 4}
        response = self.client.put(url, data, format='json')
        print("Update Review Success Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'Review updated successfully')

    def test_update_review_not_authenticated(self):
        """Tests updating a review when the user is not authenticated."""
        self.test_add_review_success()
        self.client.logout()
        url = reverse('update-review', args=[self.book_id])
        data = {'rating': 4}
        response = self.client.put(url, data, format='json')
        print("Update Review Not Authenticated Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')


class ScoreUpdateTestCase(APITestCase):

    def setUp(self):
        """Sets up the test environment by creating or retrieving a user and adding an initial review."""
        if User.objects.filter(username='Sharif').exists():
            self.user = User.objects.get(username='Sharif')
        else:
            self.user = User.objects.create_user(
                username='Sharif',
                password='qwertyQ@1',
                phone_number='09107654322',
                email='Sharif@example.com'
            )
        self.client.login(username='Sharif', password='qwertyQ@1')  # noqa
        self.book_id = 1
        url = reverse('add-score', args=[self.book_id])
        data = {'rating': 5}
        response = self.client.post(url, data, format='json')
        print("Initial Add Review Response Data:", response.data)

    def test_update_review_success(self):
        """Tests updating a review successfully."""
        url = reverse('add-score', args=[self.book_id])
        data = {'rating': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('update-score', args=[self.book_id])
        data = {'rating': 4}
        response = self.client.put(url, data, format='json')
        print("Update Review Success Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'Review updated successfully')

    def test_update_review_not_authenticated(self):
        """Tests updating a review when the user is not authenticated."""
        self.client.logout()
        url = reverse('update-score', args=[self.book_id])
        data = {'rating': 4}
        response = self.client.put(url, data, format='json')
        print("Update Review Not Authenticated Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_update_review_not_found(self):
        """Tests updating a review when the review does not exist."""
        self.client.logout()
        url = reverse('update-score', args=[9999])
        data = {'rating': 4}
        response = self.client.put(url, data, format='json')
        print("Update Review Not Found Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Not found.')


class ScoreDeleteTestCase(APITestCase):

    def setUp(self):
        """Sets up the test environment by creating a user, logging in, and adding an initial review."""
        self.user = User.objects.create_user(
            username='Sharif',
            password='qwertyQ@1',
            phone_number='09107654322',
            email='Sharif@example.com'
        )
        self.client.login(username='Sharif', password='qwertyQ@1')  # noqa
        self.book_id = 1
        url = reverse('add-score', args=[self.book_id])
        data = {'rating': 5}
        response = self.client.post(url, data, format='json')
        print("Initial Add Review Response Data:", response.data)

    def test_delete_review_success(self):
        """Tests deleting a review successfully."""
        url = reverse('delete-score', args=[self.book_id])
        response = self.client.delete(url, format='json')
        print("Delete Review Success Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Rating deleted successfully')

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM reviews WHERE book_id = %s AND account_user_id = %s",
                    [self.book_id, self.user.id]
                )
                count = cursor.fetchone()[0]
                self.assertEqual(count, 0)

    def test_delete_review_not_authenticated(self):
        """Tests deleting a review when the user is not authenticated."""
        self.client.logout()
        url = reverse('delete-score', args=[self.book_id])
        response = self.client.delete(url, format='json')
        print("Delete Review Not Authenticated Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'User not authenticated')

    def test_delete_review_not_found(self):
        """Tests deleting a review when the review does not exist."""
        url = reverse('delete-score', args=[9999])  # Assuming this book ID does not exist
        response = self.client.delete(url, format='json')
        print("Delete Review Not Found Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Review not found')

    def tearDown(self):
        """Cleans up by deleting the user created for the tests."""
        User.objects.filter(username='Sharif').delete()
