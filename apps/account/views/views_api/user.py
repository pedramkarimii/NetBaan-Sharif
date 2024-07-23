from django.http import Http404
from rest_framework import generics, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from apps.account.serializers import user
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

User = get_user_model()


class IsOwnerOrAdminPermission(BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to view or edit it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Returns `True` if the request user is an admin or the owner of the object.
        """
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return request.user.pk == view.kwargs.get('pk')
        return False

    def has_permission(self, request, view):
        """
        Returns `True` if the request user is an admin.
        """
        if request.user.is_authenticated and request.user.pk == view.kwargs.get('pk'):
            return True
        if request.user.is_superuser:
            return True
        return False


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class for Django REST Framework.
    This class configures pagination settings for API responses, allowing for customization of page sizes and
    page size parameters.
        - `10`: Specifies that the default page size is 10 items per page.
        - `page_size`: Allows clients to customize the number of items per page by including this parameter
        in their request.
        - `100`: Ensures that clients cannot request more than 100 items per page, even if they specify
        a larger value in the `page_size` query parameter.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserListAPI(generics.ListAPIView):
    """
    API view to list all users with pagination, searching, and ordering.
    This view provides a list of users and supports pagination, searching, and ordering. It requires admin
    privileges to access the list of users.
        - `User.objects.all()`: Retrieves all user records from the database.
        - `UserDetailSerializer`: Specifies the serializer to use for converting user data.
        - `permissions.IsAdminUser`: Ensures that only users with admin privileges can access this view.
        - `CustomPagination`: Uses the custom pagination class defined in `pagination.py` to control page size,
         query parameters, and maximum page size.
        - `filters.OrderingFilter`: Allows ordering of results based on specified fields.
        - `filters.SearchFilter`: Allows searching within specified fields.
        - `username`: Allows searching by username.
        - `email`: Allows searching by email address.
        - `phone_number`: Allows searching by phone number.
        - `__all__`: Allows ordering by all fields in the model.
        - `-create_time`: Orders the users by creation time in descending order.
    """
    queryset = User.objects.all()
    serializer_class = user.UserDetailSerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ('username', 'email', 'phone_number')
    ordering_fields = '__all__'
    rdering = ['-create_time']

    def get_queryset(self):
        """
        Customize the queryset based on query parameters.
            - `is_active`: Filter the queryset based on the `is_active` query parameter if provided.
        """
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class DetailAPI(generics.RetrieveAPIView):
    """
    API view to retrieve the details of a single user.
    This view provides the ability to retrieve detailed information for a specific user, with access control
    based on ownership or admin privileges.
    - `User.objects.all()`: Retrieves all user records from the database. This queryset is filtered later
      based on the provided `pk` (primary key) in the request to return a single user.
    - `UserDetailSerializer`: Specifies the serializer to use for converting user data into JSON format and for
      validating the input data.
    - `IsOwnerOrAdminPermission`: Custom permission class that ensures the requesting user either owns the user
      record being retrieved or has admin privileges to view the record.
    """
    queryset = User.objects.all()
    serializer_class = user.UserDetailSerializer
    permission_classes = [IsOwnerOrAdminPermission]


class ChangePasswordAPI(generics.UpdateAPIView):
    """
    API view to allow users to change their password.
    This view handles the process of updating a user's password. It requires the user to provide their old
    password and a new password, and it enforces the rule that only the owner of the account or an admin
    can change the password.
    """
    serializer_class = user.ChangePasswordSerializer
    permission_classes = (IsOwnerOrAdminPermission,)
    model = get_user_model()

    def get_object(self, queryset=None):
        """
        Retrieve the user object based on the provided primary key (`pk`). If the user does
        not exist, raise an HTTP 404 exception.
        Returns:
            User: The user object if found.
        Raises:
            Http404: If the user is not found.
        """
        user_id = self.kwargs.get('pk')
        try:
            user = self.model.objects.get(pk=user_id)  # noqa
            return user
        except self.model.DoesNotExist:
            raise Http404

    def update(self, request, *args, **kwargs):
        """
        Handle the update request for changing the user's password.
        Returns:
            Response: A response indicating the success or failure of the password change operation.
            If the old password is incorrect, it returns a 400 Bad Request response with an error message.
            If the update is successful, it returns a 200 OK response with a success message.
        Raises:
            Response: If the serializer is invalid, it returns a 400 Bad Request response with the serializer errors.
        """
        user = self.get_object()  # noqa
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({'status': 'success', 'message': 'Password updated successfully'},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateAPI(generics.UpdateAPIView):
    """
    API view to update user details.
    This view allows users to update their own details or an admin to update details of any user.
    It provides functionality for updating user information with access control based on ownership
    or administrative privileges.
    """
    queryset = User.objects.all()
    serializer_class = user.UserUpdateSerializer
    permission_classes = (IsOwnerOrAdminPermission,)


class UserDeleteAPI(generics.DestroyAPIView):
    """
    API view to delete a user.

    This view allows for the deletion of a user account. It is restricted to the user who owns the account
    or an admin who has the permissions to delete user records.
    """
    queryset = User.objects.all()
    permission_classes = (IsOwnerOrAdminPermission,)
