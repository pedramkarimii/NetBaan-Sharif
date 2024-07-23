from django.db import connection, transaction
from rest_framework import status, response, views
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from apps.book.serializers import score


class ScoreDelete(views.APIView):
    """
    API View for deleting a user's review for a specific book.

    This view allows authenticated users to delete their existing review for a book.
    It ensures that:
    - The user is authenticated before allowing the deletion.
    - The review to be deleted exists.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = score.ScoreSerializer

    def delete(self, request, book_id):  # noqa
        """
        Handles the DELETE request to remove an existing review for a specific book.

        This method:
        1. Verifies that the user is authenticated.
        2. Checks if the review exists before attempting to delete it.
        3. Deletes the review from the database.
        4. Returns a response indicating success or failure.

        Args:
        request (Request): The HTTP request object containing user details.
        book_id (int): The ID of the book whose review is to be deleted.

        Returns:
        Response: A response object with a success message or an error message.
        """

        user_id = request.user.id

        if user_id is None:
            raise PermissionDenied("User not authenticated")

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) FROM reviews WHERE book_id = %s AND account_user_id = %s",
                        [book_id, user_id]
                    )
                    exists = cursor.fetchone()[0]

                    if not exists:
                        raise NotFound("Review not found")

                    cursor.execute(
                        "DELETE FROM reviews WHERE book_id = %s AND account_user_id = %s",
                        [book_id, user_id]
                    )
                transaction.commit()
                return response.Response({"message": "Rating deleted successfully"}, status=status.HTTP_200_OK)
            except NotFound as e:
                raise e
            except PermissionDenied as e:
                raise e
            except Exception as e:
                transaction.rollback()
                return response.Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScoreUpdate(views.APIView):
    """
    API View for updating a user's review for a specific book.

    This view allows authenticated users to update their existing review for a book.
    It ensures that:
    - The user is authenticated before allowing the update.
    - The review to be updated exists.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = score.ScoreSerializer

    def put(self, request, book_id):  # noqa
        """
        Handles the PUT request to update an existing review for a specific book.

        This method:
        1. Validates the incoming review data.
        2. Checks if the user is authenticated.
        3. Ensures that the review to be updated exists.
        4. Updates the existing review with the new rating.
        5. Returns a response indicating success or failure.

        Args:
            request (Request): The HTTP request object containing the new review data and user details.
            book_id (int): The ID of the book whose review is being updated.

        Returns:
            Response: A response object with a success message or an error message.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            rating = serializer.validated_data['rating']
            user_id = request.user.id
            if user_id is None:
                return response.Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) FROM reviews WHERE book_id = %s AND account_user_id = %s",
                        [book_id, user_id]
                    )
                    exists = cursor.fetchone()[0]

                    if not exists:
                        return response.Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

                    cursor.execute(
                        "UPDATE reviews SET rating = %s WHERE book_id = %s AND account_user_id = %s",
                        [rating, book_id, user_id]
                    )
                transaction.commit()
                return response.Response({"message": "Review updated successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                transaction.rollback()
                return response.Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScoreAdd(views.APIView):
    """
    API View for managing book reviews and generating book recommendations.

    This view handles:
    - Adding a review for a specified book.
    - Generating recommendations based on user reviews and similar users' preferences.
    It ensures that the user is authenticated before allowing the review to be added.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = score.ScoreSerializer

    def post(self, request, book_id):
        """
        Handles the POST request to add a review for a specific book.

        This method:
        1. Validates the review data submitted in the request.
        2. Checks if the user is authenticated.
        3. Ensures the user has not previously reviewed the same book.
        4. Inserts the new review into the database.
        5. Retrieves and returns book recommendations based on the new review.

        Args:
            request (Request): The HTTP request object containing review data and user details.
            book_id (int): The ID of the book that is being reviewed.

        Returns:
            Response: A response object with a success message and book recommendations, or an error message.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            rating = serializer.validated_data['rating']
            user_id = request.user.id

            if user_id is None:
                return response.Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) FROM reviews WHERE book_id = %s AND account_user_id = %s",
                        [book_id, user_id]
                    )
                    exists = cursor.fetchone()[0]

                    if exists:
                        return response.Response({"error": "Review already exists"}, status=status.HTTP_400_BAD_REQUEST)

                    cursor.execute(
                        "INSERT INTO reviews (book_id, account_user_id, rating) VALUES (%s, %s, %s)",
                        [book_id, user_id, rating]
                    )
                transaction.commit()

                recommendations = self.get_recommendations(user_id, book_id)

                return response.Response({
                    "message": "Review added successfully",
                    "recommendations": recommendations
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                transaction.rollback()
                return response.Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_recommendations(self, user_id, book_id):  # noqa
        """
        Generates book recommendations based on the genre of the reviewed book and ratings from similar users.

        This method:
        1. Retrieves the genre of the reviewed book.
        2. Gathers a list of books that the user has already rated.
        3. Collects ratings from other users who have reviewed books in the same genre.
        4. Identifies users with similar reading preferences.
        5. Provides recommendations of books highly rated by similar users that the current user has not yet rated.

        Args:
            user_id (int): The ID of the user requesting recommendations.
            book_id (int): The ID of the book that was reviewed.

        Returns:
            list: A list of dictionaries containing recommended books with their IDs, titles, and average ratings.
        """
        recommendations = []

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT genre FROM books WHERE id = %s",
                    [book_id]
                )
                genre_row = cursor.fetchone()

                if not genre_row:
                    return {"message": "Genre not found"}

                genre = genre_row[0]

                cursor.execute(
                    "SELECT book_id FROM reviews WHERE account_user_id = %s",
                    [user_id]
                )
                rated_books = cursor.fetchall()

                if not rated_books:
                    return {"message": "There is not enough data about you"}

                rated_books_ids = [book[0] for book in rated_books]

                cursor.execute("""
                    SELECT r.account_user_id, r.book_id, r.rating
                    FROM reviews r
                    JOIN books b ON r.book_id = b.id
                    WHERE b.genre = %s AND r.account_user_id != %s
                """, [genre, user_id])

                similar_users_ratings = cursor.fetchall()

                user_profiles = {}
                for other_user_id, book_id, rating in similar_users_ratings:
                    if other_user_id not in user_profiles:
                        user_profiles[other_user_id] = {}
                    user_profiles[other_user_id][book_id] = rating

                similar_users = []
                for other_user_id, ratings in user_profiles.items():
                    common_books = set(ratings.keys()) & set(rated_books_ids)
                    if common_books:
                        similar_users.append(other_user_id)

                if similar_users:
                    cursor.execute("""
                        SELECT r.book_id, b.title, AVG(r.rating) as avg_rating
                        FROM reviews r
                        JOIN books b ON r.book_id = b.id
                        WHERE r.account_user_id IN %s AND r.book_id NOT IN %s
                        GROUP BY r.book_id, b.title
                        ORDER BY avg_rating DESC
                    """, [tuple(similar_users), tuple(rated_books_ids)])

                    potential_recommendations = cursor.fetchall()

                    recommendations = [{"book_id": book_id, "title": title, "rating": avg_rating} for
                                       book_id, title, avg_rating in potential_recommendations]

        except Exception as e:
            return {"error": str(e)}

        return recommendations
