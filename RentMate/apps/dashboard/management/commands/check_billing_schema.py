from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Check the MonthlyBilling table schema in the database'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            # Check if table exists
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'dashboard_monthlybilling'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            
            if columns:
                self.stdout.write(self.style.SUCCESS('Table dashboard_monthlybilling exists with columns:'))
                for col_name, col_type in columns:
                    self.stdout.write(f'  - {col_name}: {col_type}')
            else:
                self.stdout.write(self.style.ERROR('Table dashboard_monthlybilling does not exist'))
