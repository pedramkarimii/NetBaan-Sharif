from rest_framework import generics, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from apps.account.serializers import user
from django.contrib.auth import get_user_model
from apps.core.permissions import IsOwnerOrAdminPermission

User = get_user_model()


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


class UserListView(generics.ListAPIView):
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


class DetailView(generics.RetrieveAPIView):
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
    permission_classes = (IsOwnerOrAdminPermission,)


class ChangePasswordView(generics.UpdateAPIView):
    """
    API view to allow users to change their password.
    This view handles the process of updating a user's password. It requires the user to provide their old
    password and a new password, and it enforces the rule that only the owner of the account or an admin
    can change the password.
    """
    serializer_class = user.ChangePasswordSerializer
    model = User
    permission_classes = (IsOwnerOrAdminPermission,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Handles the request to update the user's password.

        - Validates the provided passwords using the serializer.
        - Checks if the old password is correct.
        - Sets the new password and saves the user instance if the old password is correct.
        - Returns a success response if the password is updated successfully, or an error response if validation fails.

        - Parameters:
            - `request`: The HTTP request containing the old and new passwords.
            - `args` and `kwargs`: Additional arguments and keyword arguments passed to the method.
        - Returns: A `Response` object containing the status of the operation.
        """
        self.object = self.get_object()  # noqa
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password1"))
            self.object.save()
            response = {
                'status': 'success',
                'message': 'Password updated successfully',
            }
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(generics.UpdateAPIView):
    """
    API view to update user details.
    This view allows users to update their own details or an admin to update details of any user.
    It provides functionality for updating user information with access control based on ownership
    or administrative privileges.
    """
    queryset = User.objects.all()
    serializer_class = user.UserUpdateSerializer
    permission_classes = (IsOwnerOrAdminPermission,)


class UserDeleteView(generics.DestroyAPIView):
    """
    API view to delete a user.

    This view allows for the deletion of a user account. It is restricted to the user who owns the account
    or an admin who has the permissions to delete user records.
    """
    queryset = User.objects.all()
    permission_classes = (IsOwnerOrAdminPermission,)
