from django.urls import path, include

urlpatterns = [
    path("", include("apps.book.urls.book")),
    path("", include("apps.book.urls.score")),
]

"""
Defines the root URL patterns for the Django project, including URL configurations from other applications.

    - URL pattern: `""` (empty string)
    - This means that all paths starting with the root URL of this project will be handled by the URL patterns defined in `apps.book.urls.book`.
    - The `include` function imports the URL patterns from `apps.book.urls.book` and appends them to the root URL configuration.

    - URL pattern: `""` (empty string)
    - This means that all paths starting with the root URL of this project will be handled by the URL patterns defined in `apps.book.urls.score`.
    - The `include` function imports the URL patterns from `apps.book.urls.score` and appends them to the root URL configuration.
"""
