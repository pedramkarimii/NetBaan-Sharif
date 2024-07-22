from django.contrib import admin
from apps.account.models import User, UserAuth
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(UserAuth)
class UserAuthModelAdmin(admin.ModelAdmin):
    """Admin configuration for UserAuth model."""
    list_display = ['user_id', 'token_type', 'uuid', 'create_time', 'update_time', 'is_active', 'is_deleted']
    list_filter = ['user_id', 'token_type', 'is_active']
    search_fields = ['user_id', 'token_type', 'is_active']
    readonly_fields = ('create_time', 'update_time', 'is_active', 'is_deleted')
    ordering = ['-create_time']
    date_hierarchy = 'create_time'
    list_per_page = 30
    fieldsets = (
        ('Creation User Auth',
         {'fields': ('user_id', 'token_type', 'uuid')}),
        ('Data', {'fields': ('create_time', 'update_time', 'is_active', 'is_deleted')
                  }),
    )
    add_fieldsets = (
        ('Creation User Auth', {
            'classes': ('wide',),
            'fields': ('user_id', 'token_type', 'uuid')
        }),
        ('Data', {'fields': ('create_time', 'update_time', 'is_active', 'is_deleted')
                  })
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for managing users."""

    fieldsets = (
        ('Change personal info',
         {'fields': ('email', 'phone_number', 'username', 'password')}),
        ('Permissions',
         {'fields': ('is_admin', 'is_superuser', 'is_staff', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'create_time', 'update_time', 'is_active', 'is_deleted',)}),
    )

    add_fieldsets = (
        ('Creation User', {
            'fields': ('email', 'phone_number', 'username', 'password1', 'password2')}
         ),
    )
    row_id_fields = ('phone_number',)
    list_display = ('username', 'email', 'phone_number', 'is_deleted', 'is_admin', 'is_active')
    list_filter = ['username', 'email', 'phone_number', 'is_deleted', 'is_active']
    search_fields = ['username', 'email', 'phone_number']
    date_hierarchy = 'create_time'
    list_per_page = 30
    ordering = ['-username']
    readonly_fields = ('create_time', 'update_time', 'last_login', 'is_active', 'is_deleted',)
    filter_horizontal = ('groups', 'user_permissions')

    def get_form(self, request, obj=None, **kwargs):
        """Get the form for the admin interface."""
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser and 'is_superuser' in form.base_fields:
            form.base_fields["is_superuser"].disabled = True
            form.base_fields["is_admin"].disabled = True
            form.base_fields["is_staff"].disabled = True
            form.base_fields["is_active"].disabled = True
            form.base_fields["is_deleted"].disabled = True
        return form
