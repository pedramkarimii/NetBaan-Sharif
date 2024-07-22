from django.urls import path
from apps.book.views import book


urlpatterns = [

    path('book-list/', book.BookList.as_view(), name='list-book'),
    path('book-genre/', book.BookDetailGenre.as_view(), name='genre-book'),
]

"""
Defines URL patterns for the book-related API endpoints.

    - URL: `book-list/`
    - Maps to the `BookList` view class from `apps.book.views.book`.
    - The `name='list-book'` provides a name to reference this URL pattern in Django templates and views.

    - URL: `book-genre/`
    - Maps to the `BookDetailGenre` view class from `apps.book.views.book`.
    - The `name='genre-book'` provides a name to reference this URL pattern in Django templates and views.
"""
