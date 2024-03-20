import json

from django.apps import apps
from django.test import TestCase
from django.core.management import call_command

from simulations.api import CreateLossData, add_loss_data, CreateMachineSchema, add_machine, CreateSimulationSchema, \
    add_simulation, simulations


# Create your tests here.
class SimulationTestCase(TestCase):
    # fixtures = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Your setup code here
        print("Setting up databasse and loading fixtures...")
        call_command('setup_database')
        call_command('load_fixtures')

    def test_api_hello(self):
        """
        Test the hello endpoint to make sure we can connect
        """
        response = self.client.get("/api/hello")
        print(response.status_code)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"msg": "Hello World"})

    def test_list_machines(self):
        response = self.client.get('/api/machines')
        self.assertEqual(response.status_code, 200)
        expected_response = [{'id': 1, 'name': 'machine-1', 'location': 'https://some-machine-1.in.the.cloud.aws.com'},
                             {'id': 2, 'name': 'machine-2', 'location': 'https://some-machine-2.in.the.cloud.aws.com'},
                             {'id': 3, 'name': 'machine-3', 'location': 'https://some-machine-3.in.the.cloud.aws.com'},
                             {'id': 4, 'name': 'machine-4', 'location': 'https://some-machine-4.in.the.cloud.aws.com'}]
        self.assertEqual(expected_response, response.json())

    def test_add_simulations(self):
        simulation_data = {"name": "my_first-simulation",
                           "machine_name": "machine-2",
                           "state": "pending"
                           }

        response = self.client.post('/api/simulations/add',
                                    simulation_data,
                                    content_type="application/json"
                                    )
        print(response.status_code)

    def test_add_simulation_validation(self):
        """Should test with some bad inputs to make sure the data validations works
            Also some duplicates on unique feilds
        """
        pass

    def test_get_simulations(self):
        ## django isolates test cases so they run in a transaction, and data is deleted between tests
        ## (I probably didn't pick  the best framework, but it's what I am most familar with,
        # and I have already completed most of the task)

        # skeleton of a test
        ## enter some data here
        response = self.client.get('/api/simulations')
        self.assertEqual(response.status_code, 200)
        # check response data matches here

    def test_simulation_filters(self):
        """make some calls to the simulations endpoint with the filters for sort and search added"""
        pass

    def test_update_simulation(self):
        """ Test that teh triggesr works (it did when I updated manually in postgres)"""
        pass


    def test_add_loss_data(self):

        # first add a simulation (django test cases are transactions, so previous steps get deleted)
        simulation_data = {"name": "my_first-simulation",
                           "machine_name": "machine-2",
                           "state": "pending"
                           }

        response = self.client.post('/api/simulations/add',
                                    simulation_data,
                                    content_type="application/json"
                                    )
        print(response.status_code)
        print(response.json)
        simulation_id = response.json()['id']


        loss_data_list = [
              {"seconds": 10, "loss": 0.8}, {"seconds": 20, "loss": 0.7}, {"seconds": 30, "loss": 0.65},
              {"seconds": 40, "loss": 0.61}, {"seconds": 50, "loss": 0.615}, {"seconds": 60, "loss": 0.60},
              {"seconds": 70, "loss": 0.58}, {"seconds": 80, "loss": 0.575}, {"seconds": 90, "loss": 0.58},
              {"seconds": 100, "loss": 0.56}, {"seconds": 110, "loss": 0.555}, {"seconds": 120, "loss": 0.54},
              {"seconds": 130, "loss": 0.551}, {"seconds": 140, "loss": 0.55}, {"seconds": 150, "loss": 0.553},
              {"seconds": 160, "loss": 0.552}, {"seconds": 170, "loss": 0.555}, {"seconds": 180, "loss": 0.546},
              {"seconds": 190, "loss": 0.55}
        ]
        for loss_data in loss_data_list:
            loss_data.update({'simulation_id': simulation_id})
            response = self.client.post('/api/lossdata/add',
                                        loss_data,
                                        content_type="application/json"
                                        )
            print(response.status_code)
            self.assertEqual(response.status_code, 200)


    def test_get_graph(self):
        """
        Test the endpoint to get the graph data
        """
        simulation_id = self.load_loss_data()

        response = self.client.get(f"/api/simulations/{simulation_id}/graph")
        self.assertEqual(response.status_code, 200)
        expected_response = [{'seconds': 10, 'loss': '0.80000'}, {'seconds': 20, 'loss': '0.70000'},
                             {'seconds': 30, 'loss': '0.65000'}, {'seconds': 40, 'loss': '0.61000'},
                             {'seconds': 50, 'loss': '0.61500'}, {'seconds': 60, 'loss': '0.60000'},
                             {'seconds': 70, 'loss': '0.58000'}, {'seconds': 80, 'loss': '0.57500'},
                             {'seconds': 90, 'loss': '0.58000'}, {'seconds': 100, 'loss': '0.56000'},
                             {'seconds': 110, 'loss': '0.55500'}, {'seconds': 120, 'loss': '0.54000'},
                             {'seconds': 130, 'loss': '0.55100'}, {'seconds': 140, 'loss': '0.55000'},
                             {'seconds': 150, 'loss': '0.55300'}, {'seconds': 160, 'loss': '0.55200'},
                             {'seconds': 170, 'loss': '0.55500'}, {'seconds': 180, 'loss': '0.54600'},
                             {'seconds': 190, 'loss': '0.55000'}]

        actual_response = list(response.json())
        self.assertEqual(expected_response, actual_response)

    #----------------------------------------------------
    # -- methods to load data from fixtures for testing --
    # -- not the nicest code please don't judge too harshly
    def load_machines(self):
        app_config = apps.get_app_config('simulations')

        # Build the path to the fixture file
        fixture_path = app_config.path + '/fixtures/machines.json'

        ids = []
        with open(fixture_path, 'r') as file:
            # Load the JSON data into a Python dictionary
            machine_list_json = json.load(file)

            # As we are not using Django models and SQL directly, I will
            # load the fixtures via the endpoint function to get some data validation
            for machine_json in machine_list_json:
                print("--", machine_json)
                machine_data = CreateMachineSchema(**machine_json)
                resp = add_machine(None, data=machine_data)
                # self.stdout.write(resp.status_code)
                ids.append(resp.json()['id'])
            return ids

    def load_simulations(self):
        app_config = apps.get_app_config('simulations')

        # Build the path to the fixture file
        fixture_path = app_config.path + '/fixtures/simulations.json'

        ids = []
        with open(fixture_path, 'r') as file:
            # Load the JSON data into a Python dictionary
            simulation_list_json = json.load(file)

            # As we are not using Django models and SQL directly, I will
            # load the fixtures via the endpoint function to get some data validation
            for simulation_json in simulation_list_json:
                simulation_data = CreateSimulationSchema(**simulation_json)
                resp = add_simulation(None, data=simulation_data)
                print(resp)
                if hasattr(resp, 'status_code'):
                    print(resp.json())
                ids.append(resp['id'])
            print("ids:---",ids)
        return ids

    def load_loss_data(self):

        simulation_ids = self.load_simulations()
        app_config = apps.get_app_config('simulations')
        fixture_path = app_config.path + '/fixtures/loss_data.json'

        # Load the JSON data into a Python dictionary
        with open(fixture_path, 'r') as file:
            # Load the JSON data into a Python dictionary
            loss_data_list_json = json.load(file)

            # As we are not using Django models and SQL directly, I will
            # load the fixtures via the endpoint function to get some data validation
            sim_id = simulation_ids[0]
            print("using simulation id", sim_id)
            for loss_data_json in loss_data_list_json:
                loss_data_json.update({"simulation_id": sim_id})
                print(loss_data_json)
                loss_data = CreateLossData(**loss_data_json)
                resp = add_loss_data(None, data=loss_data)
        return sim_id
