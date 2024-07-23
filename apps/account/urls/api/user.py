from django.urls import path
from apps.account.views.views_api import user

urlpatterns = [
    path('user-update/<int:pk>/', user.UserUpdateView.as_view(), name='update-user'),
    path('user-detail/<int:pk>/', user.DetailView.as_view(), name='detail-user'),
    path('user-list/', user.UserListView.as_view(), name='list-user'),
    path("user-change-password/<int:pk>/", user.ChangePasswordView.as_view(), name="change-password"),
    path('user-delete/<int:pk>/', user.UserDeleteView.as_view(), name='delete-user'),
]
"""
Maps the URL 'user-update/<int:pk>/' to the UserUpdateView view.
Maps the URL 'user-detail/<int:pk>/' to the DetailView view.
Maps the URL 'user-list/' to the UserListView view.
Maps the URL 'user-change-password/<int:pk>/' to the ChangePasswordView view.
Maps the URL 'user-delete/<int:pk>/' to the UserDeleteView view.
"""
