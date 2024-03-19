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





@api.get("simulations/{simulation_id}/graph")
def convergence_graph(request, simulation_id: int):
    """
    Get the convergence graph for a specific simulation
    :return:
    """

    try:
        get_loss_data_sql = "SELECT seconds, loss FROM lossdata WHERE simulation_id = (%s) ORDER BY seconds ASC"
        conn = connections['default']
        conn.ensure_connection()
        with conn.connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(get_loss_data_sql, (simulation_id,))
            results = cur.fetchall()
        return results

    except Exception as e:
        return JsonResponse({"OK": False, "error": str(e)}, status=400)

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
def add_simulation(request, data:CreateSimulationSchema):
    try:
        insert_sql = """INSERT INTO simulation (name, state, machine_id, date_updated) 
                        VALUES (%s, %s, (SELECT id FROM machine WHERE name = %s), NOW())
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


class SortFields(str, Enum):
    NAME_ASC: 'name'
    NAME_DESC: '-name'
    CREATION_ASC: 'date_created'
    CREATION_DESC: '-date_created'
    UPDATE_ASC: 'date_updates'
    UPDATE_DESC: '-date_updates'


class ItemFilter(Schema):
    sort: Optional[str] = None
    status: Optional[State] = None

@api.get("/simulations")
def simulations(request):
    """
    List of machines, filterable and sortable
    :param request:
    :return:
    """
    # TODO add filtering and ordering
    # add a link to the simulation detail
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

