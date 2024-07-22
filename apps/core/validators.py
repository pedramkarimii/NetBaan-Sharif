from django.core import validators
from django.utils.translation import gettext_lazy as _


class CustomRegexValidator(validators.RegexValidator):
    """
    Custom RegexValidator with enhanced error messages
    """

    def __init__(self, regex, message):
        super().__init__(regex, message=message)


class UsernameValidator(CustomRegexValidator):
    """
    Validator for username field
    """

    def __init__(self):
        super().__init__(
            r'^[a-zA-Z0-9_.+-]+$',
            _('Username can contain letters, numbers, underscores, dots, '
              'hyphens, and must be at least 4 characters long.')
        )


class EmailValidator(CustomRegexValidator):
    """
    Validator for email field
    """

    def __init__(self):
        super().__init__(
            r'^[a-zA-Z0-9._%+-]+@(?:gmail|yahoo)\.com$',
            _('Please enter a valid Gmail or Yahoo email address.')
        )


class PhoneNumberMobileValidator(CustomRegexValidator):
    """
    Validator for phone number field
    """

    def __init__(self):
        super().__init__(
            r"09(1[0-9]|3[0-9]|2[0-9]|0[1-9]|9[0-9])[0-9]{7}$",
            _('Please enter a valid phone number in the format 09121234567.')
        )


class PasswordValidator(CustomRegexValidator):
    """
    Validator for password field
    """

    def __init__(self):
        super().__init__(
            regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$",
            message='Password must contain at least one lowercase letter, one uppercase letter, one digit, '
                    'one special character, and be at least 8 characters long.'
        )
