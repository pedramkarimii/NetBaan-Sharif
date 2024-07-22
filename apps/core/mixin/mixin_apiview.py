from rest_framework.views import APIView
from rest_framework import permissions


class CustomAPIViewIsAuthenticated(APIView):
    """
    A custom API view that requires the user to be authenticated.

    Attributes:
        permission_classes (list): A list of permission classes that are used to
        determine if the user has permission to access the view. In this case, it
        only includes IsAuthenticated, which means only authenticated users can
        access this view.
    """
    permission_classes = [permissions.IsAuthenticated]


class CustomAPIViewIsAuthenticatedOrReadOnly(APIView):
    """
    A custom API view that allows read-only access for unauthenticated users and full
    access for authenticated users.

    Attributes:
        permission_classes (list): A list of permission classes that are used to
        determine if the user has permission to access the view. In this case, it
        includes IsAuthenticatedOrReadOnly, which means unauthenticated users can
        only perform read-only actions (such as GET requests), while authenticated
        users can perform any action (such as POST, PUT, DELETE requests).
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
