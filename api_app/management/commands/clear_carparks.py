from django.core.management.base import BaseCommand
from django.db import connection
from api_app.models import CarPark

class Command(BaseCommand):
    help = 'Deletes all Car Parks and resets the ID counter to 1'

    def handle(self, *args, **kwargs):
        # 1. Delete all rows
        count, _ = CarPark.objects.all().delete()
        
        # 2. Reset the ID counter (SQLite specific)
        # Note: The table name is usually 'appname_modelname' (lowercase)
        table_name = 'api_app_carpark'
        
        with connection.cursor() as cursor:
            # Check if we are using SQLite before running SQLite-specific SQL
            if connection.vendor == 'sqlite':
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")
                self.stdout.write(self.style.SUCCESS(f"ID counter reset for '{table_name}'."))
            else:
                self.stdout.write(self.style.WARNING("Skipped ID reset (Database is not SQLite)."))

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} car parks.'))