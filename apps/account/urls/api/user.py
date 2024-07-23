from django.urls import path
from apps.account.views.views_api import user

urlpatterns = [
    path('user-update/<int:pk>/', user.UserUpdateAPI.as_view(), name='update-user'),
    path('user-detail/<int:pk>/', user.DetailAPI.as_view(), name='detail-user'),
    path('user-list/', user.UserListAPI.as_view(), name='list-user'),
    path("user-change-password/<int:pk>/", user.ChangePasswordAPI.as_view(), name="change-password"),
    path('user-delete/<int:pk>/', user.UserDeleteAPI.as_view(), name='delete-user'),
]
"""
Maps the URL 'user-update/<int:pk>/' to the UserUpdateAPI.
Maps the URL 'user-detail/<int:pk>/' to the DetailAPI.
Maps the URL 'user-list/' to the UserListAPI.
Maps the URL 'user-change-password/<int:pk>/' to the ChangePasswordAPI.
Maps the URL 'user-delete/<int:pk>/' to the UserDeleteAPI.
"""
