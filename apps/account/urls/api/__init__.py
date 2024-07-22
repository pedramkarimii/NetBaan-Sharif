from django.urls import path, include

urlpatterns = [
    path("", include("apps.account.urls.api.auth")),
    path("", include("apps.account.urls.api.user")),
]
"""
Includes all URL patterns defined in 'apps.account.urls.api.auth' at the root URL.
Includes all URL patterns defined in 'apps.account.urls.api.user' at the root URL.
"""
