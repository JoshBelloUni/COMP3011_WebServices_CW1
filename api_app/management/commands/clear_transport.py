from django.core.management.base import BaseCommand
from django.db import connection
from api_app.models import TransportLink

class Command(BaseCommand):
    help = 'Deletes all Transport Links and resets the ID counter to 1'

    def handle(self, *args, **kwargs):
        # 1. Delete all rows
        count, _ = TransportLink.objects.all().delete()
        
        # 2. Reset ID counter
        table_name = 'api_app_transportlink'
        
        with connection.cursor() as cursor:
            if connection.vendor == 'sqlite':
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")
                self.stdout.write(self.style.SUCCESS(f"ID counter reset for '{table_name}'."))
            else:
                self.stdout.write(self.style.WARNING("Skipped ID reset (Database is not SQLite)."))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} transport links.'))