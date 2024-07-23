from rest_framework import status, response, views
from django.db import connection
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.account.throttling import CustomRateThrottle
from apps.book.serializers import book


class BookList(views.APIView):
    """
    API View for listing all books.

    This view allows:
    - Authenticated users to retrieve the list of all books.
    - Read-only access for unauthenticated users.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    throttle_classes = [CustomRateThrottle]
    throttle_scope = 'default'
    serializer_class = book.BookSerializer

    def get(self, request):  # noqa
        """
        Handles the GET request to retrieve the list of all books.

        This method:
        1. Executes a database query to fetch all books.
        2. Converts the query results into a list of dictionaries.
        3. Serializes the list of dictionaries into JSON format.
        4. Returns the serialized data in the response.

        Args:
        request (Request): The HTTP request object.

        Returns:
        Response: A response object containing the list of books in JSON format.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title, author, genre FROM books")
            rows = cursor.fetchall()

        books = [  # noqa
            {"id": row[0], "title": row[1], "author": row[2], "genre": row[3]}
            for row in rows
        ]

        serializer = self.serializer_class(data=books, many=True)
        if serializer.is_valid():
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailGenre(views.APIView):
    """
    API View for listing books based on a specific genre.

    This view allows:
    - Authenticated and unauthenticated users to retrieve a list of books filtered by genre.
    - Read-only access to all users.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = book.BookSerializer

    def get(self, request):  # noqa
        """
        Handles the GET request to retrieve a list of books filtered by genre.

        This method:
        1. Retrieves the 'genre' query parameter from the request.
        2. If the genre is provided, it queries the database for books of that genre.
        3. Converts the query results into a list of dictionaries.
        4. Serializes the list of dictionaries into JSON format.
        5. Returns the serialized data in the response.
        6. If no genre is provided, returns an error message.

        Args:
        request (Request): The HTTP request object containing the query parameter.

        Returns:
        Response: A response object containing the list of books filtered by genre in JSON format or an error
        message if the genre is missing.
        """
        genre = request.GET.get('genre')
        if genre:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, title, author, genre FROM books WHERE genre = %s", [genre])
                rows = cursor.fetchall()

            books = [ # noqa
                {"id": row[0], "title": row[1], "author": row[2], "genre": row[3]}
                for row in rows
            ]

            serializer = self.serializer_class(data=books, many=True)
            if serializer.is_valid():
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return response.Response({"error": "Genre query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
