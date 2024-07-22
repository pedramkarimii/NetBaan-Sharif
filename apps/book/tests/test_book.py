from django.test import TestCase
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse


class BookAPITestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    author VARCHAR(200) NOT NULL,
                    genre VARCHAR(50) NOT NULL
                )
            """)

    def setUp(self):
        """Sets up the test environment by initializing the API client and creating sample data."""
        self.client = APIClient()
        self.book_list_url = reverse('list-book')
        self.book_genre_url = reverse('genre-book')

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)",
                           ('Test Book 1', 'Author 1', 'Fiction'))
            cursor.execute("INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)",
                           ('Test Book 2', 'Author 2', 'Non-Fiction'))
            cursor.execute("INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)",
                           ('Test Book 3', 'Author 3', 'Fiction'))

    def test_book_list_authenticated(self):
        """Tests the book list endpoint when the user is authenticated."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_book_list_unauthenticated(self):
        """Tests the book list endpoint when the user is not authenticated."""
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_book_genre_authenticated(self):
        """Tests the book genre endpoint when the user is authenticated."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.book_genre_url, {'genre': 'Fiction'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_book_genre_unauthenticated(self):
        """Tests the book genre endpoint when the user is not authenticated."""
        response = self.client.get(self.book_genre_url, {'genre': 'Fiction'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_book_genre_missing_param(self):
        """Tests the book genre endpoint when the genre query parameter is missing."""
        response = self.client.get(self.book_genre_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Genre query parameter is required'})
