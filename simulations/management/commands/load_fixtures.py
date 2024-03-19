import json
from django.core.management.base import BaseCommand
from django.apps import apps
from simulations.api import CreateMachineSchema, add_machine

class Command(BaseCommand):
    help = 'Loads the database tables from fixtures'

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.SUCCESS('About to load tables'))
        app_config = apps.get_app_config('simulations')

        # Build the path to the fixture file
        fixture_path = app_config.path + '/fixtures/machines.json'
        self.stdout.write(self.style.SUCCESS('Loading fixture: {}'.format(fixture_path)))

        with open(fixture_path, 'r') as file:
            # Load the JSON data into a Python dictionary
            machine_list_json = json.load(file)

            # As we are not using Django models and SQL directly, I will
            # load the fixtures via the endpoint function to get some data validation
            for machine_json in machine_list_json:
                machine_data = CreateMachineSchema(**machine_json)
                resp = add_machine(None, data=machine_data)
                #self.stdout.write(resp.status_code)

        self.stdout.write(self.style.SUCCESS('Fixture loaded successfully!'))