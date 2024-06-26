from django.core.management.base import BaseCommand
from simulations.create_tables import ddl
from django.db import connections


class Command(BaseCommand):
    help = 'Creates the database tables'

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.SUCCESS('About to create tables'))
        conn = connections['default']
        cursor = conn.cursor()
        result = cursor.execute(ddl)

        self.stdout.write("created database tables")
