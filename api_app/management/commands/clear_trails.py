from django.core.management.base import BaseCommand
from django.db import connection
from api_app.models import Trail

class Command(BaseCommand):
    help = 'Clears all trails and resets ID counter'

    def handle(self, *args, **kwargs):
        # 1. Delete all trails
        count, _ = Trail.objects.all().delete()
        self.stdout.write(f'Deleted {count} trails.')

        # 2. Reset the ID counter (SQLite specific)
        with connection.cursor() as cursor:
            # Note: The table name is usually 'appname_modelname'
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='api_app_trail';")
            
        self.stdout.write(self.style.SUCCESS('Success! Database cleared and IDs reset to 0.'))