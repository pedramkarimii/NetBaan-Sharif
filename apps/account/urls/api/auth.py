from django.urls import path
from apps.account.views.views_api import auth

urlpatterns = [
    path('login/', auth.Login.as_view(), name='login'),
    path('logout/', auth.Logout.as_view(), name='logout'),
    path('register/', auth.UserRegister.as_view(), name='register'),
    path('verify-login/', auth.LoginVerifyCode.as_view(), name='verify-code-login'),
    path('verify-code/', auth.UserRegistrationVerifyCode.as_view(), name='verify-code-register'),
]
"""
Maps the URL 'login/' to the Login view.
Maps the URL 'logout/' to the Logout view.
Maps the URL 'register/' to the UserRegister view.
Maps the URL 'verify-login/' to the LoginVerifyCode view.
Maps the URL 'verify-code/' to the UserRegistrationVerifyCode view.
"""
