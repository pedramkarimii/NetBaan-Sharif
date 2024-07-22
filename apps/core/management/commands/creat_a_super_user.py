from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Creates a superuser with specified credentials if one does not already exist.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Username for the superuser')
        parser.add_argument('--email', type=str, default='admin@example.com', help='Email for the superuser')
        parser.add_argument('--password', type=str, default='adminpassword', help='Password for the superuser')
        parser.add_argument('--phone_number', type=str, default='1234567890', help='Phone number for the superuser')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']
        password = options['password']
        phone_number = options['phone_number']

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password, phone_number=phone_number)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists'))
