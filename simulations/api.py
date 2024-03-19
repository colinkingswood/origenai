import json
import logging
from enum import Enum
from typing import List, Optional

from django.http import JsonResponse
from ninja import NinjaAPI, Router, Schema
# from simulations.database_connection import conn
from django.db import connections
from psycopg2.extras import RealDictCursor
from pydantic import condecimal

logger = logging.getLogger(__name__)

api = NinjaAPI()
router = Router()


@api.get("/hello")
def hello(request):
    """
    A simple endpoint to test connectivity
    :param request:
    :return: dictionary containg a welcome message
    """
    return {"msg": "Hello World"}

class CreateMachineSchema(Schema):
    name: str
    location: str
    # we could add other fields like status to the machine depending on the needs

@api.post("/machines/add")
def add_machine(request, data:CreateMachineSchema):
    """
    Add a machine
    """
    try:
        insert_sql = "INSERT INTO machine (name, location) values (%s,%s) RETURNING id"
        insert_values = (data.name, data.location)
        conn = connections['default']
        with conn.cursor() as cur:
            cur.execute(insert_sql, insert_values)
            new_id = cur.fetchone()[0]
            logger.info(f"New machine added id: {new_id}")
        return {"OK": True, "message": "created new machine",  "id": new_id}

    except Exception as e:
        # could be more specific with error trapping, but for the purpose of a technical test
        # I will just catch a standard exception
        conn.rollback()
        logger.error(str(e))
        return JsonResponse({"OK": False, "error": str(e)}, status=400)


@api.put("/machines/{machine_id}/change")
def update_machines(request):
    ## This would work similar to add_machine)_ above,
    # though the machine id would be included, and an update query would be issued
    return [{"message": "success" }]


@api.get("/machines")
def machines(request):
    """
    Get the list of machines
    :param request:
    :return: A list of machines
    """
    try:
        get_machines_sql = "SELECT * FROM machine ORDER BY ID"
        conn = connections['default']
        conn.ensure_connection()
        with conn.connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(get_machines_sql)
            results = cur.fetchall()
        return results

    except Exception as e:
        # could be more specific with error trapping, but for the purpose of a technical test
        # I will just catch a standard exception
        return JsonResponse({"OK": False, "error": str(e)}, status=400)





@api.get("simulation/{simulation_id}/graph")
def convergence_graph(request):
    """
    Get the convergence graph for a specific simulation
    :return:
    """

    # TODO get the list of loss data from teh database, for that simulation id

    response = {
        "data": [
            {"seconds": 10, "loss": 0.8}, {"seconds": 20, "loss": 0.7}, {"seconds": 30, "loss": 0.65},
            {"seconds": 40, "loss": 0.61}, {"seconds": 50, "loss": 0.615}, {"seconds": 60, "loss": 0.60},
            {"seconds": 70, "loss": 0.58}, {"seconds": 80, "loss": 0.575}, {"seconds": 90, "loss": 0.58},
            {"seconds": 100, "loss": 0.56}, {"seconds": 110, "loss": 0.555}, {"seconds": 120, "loss": 0.54},
            {"seconds": 130, "loss": 0.551}, {"seconds": 140, "loss": 0.55}, {"seconds": 150, "loss": 0.553},
            {"seconds": 160, "loss": 0.552}, {"seconds": 170, "loss": 0.555}, {"seconds": 180, "loss": 0.546},
            {"seconds": 190, "loss": 0.55}
        ]
    }
    return response

@api.get("/simulations/{simulation_id}/detail")
def simulation_detail(request):
    """ Get detail for one simulation"""
    return {"msg": "TODO"}


class State(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'


class CreateSimulationSchema(Schema):
    name: str
    state: State
    machine_name: str = 'pending'

@api.post("simulations/add")
def simulations_add(request, data:CreateSimulationSchema):
    try:
        insert_sql = """INSERT INTO simulation (name, state, machine_id ) 
                        VALUES (%s, %s, (SELECT id FROM machine WHERE name = %s))
                         RETURNING id
                        """
        insert_values = (data.name, data.state, data.machine_name)
        conn = connections['default']
        with conn.cursor() as cur:
            cur.execute(insert_sql, insert_values)
            new_id = cur.fetchone()[0]
            return {"OK": True, "message": "created new simulation", "id": new_id}

    except Exception as e:
        logger.error(str(e))
        conn.rollback()
        return JsonResponse({"OK": False, "error": str(e)}, status=400)


@api.get("/simulations")
def simulations(request):
    """
    List of machines, filterable and sortable
    :param request:
    :return:
    """
    # TODO add filtering and ordering
    try:
        get_machines_sql = "SELECT * FROM simulation ORDER BY date_created"
        conn = connections['default']
        conn.ensure_connection()
        with conn.connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(get_machines_sql)
            results = cur.fetchall()
        return results

    except Exception as e:
        return JsonResponse({"OK": False, "error": str(e)}, status=400)


class CreateLossData(Schema):
    seconds: int
    loss: condecimal(max_digits=10, decimal_places=5)
    simulation_id: int

@api.post("lossdata/add")
def add_loss_data(request, data:CreateLossData):
    try:
        insert_sql = """INSERT INTO lossdata (seconds, loss, simulation_id) 
                        VALUES (%s, %s, %s)
                        RETURNING id
                        """
        insert_values = (data.seconds, data.loss , data.simulation_id)
        conn = connections['default']
        with conn.cursor() as cur:
            cur.execute(insert_sql, insert_values)
            new_id = cur.fetchone()[0]
            return {"OK": True, "message": "created new loss data", "id": new_id}

    except Exception as e:
        logger.error(str(e))
        conn.rollback()
        return JsonResponse({"OK": False, "error": str(e)}, status=400)





# from simulations.database_connection import conn
# cur = conn.cursor()
# cur.execute("""SELECT table_name FROM information_schema.tables
#        WHERE table_schema = 'public'""")
# for table in cur.fetchall():
#     print(table)

