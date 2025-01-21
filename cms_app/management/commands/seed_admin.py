from django.core.management.base import BaseCommand
from cms_app.models import User

class Command(BaseCommand):
    help = 'Seeds the database with an admin user'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(
                email='admin@example.com',
                password='AdminPass123',
                is_admin=True
            )
            self.stdout.write(self.style.SUCCESS('Admin user created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
