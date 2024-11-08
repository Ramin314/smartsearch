from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create a superuser if one does not exist'

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                "admin",
                settings.SMART_SEARCH_ADMIN_EMAIL,
                settings.SMART_SEARCH_ADMIN_PASSWORD,
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
