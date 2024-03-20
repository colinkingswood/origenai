import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional

from django.http import JsonResponse
from django.urls import reverse
from ninja import NinjaAPI, Router, Schema, Query
from django.db import connections
from psycopg2.extras import RealDictCursor
from pydantic import condecimal, BaseModel, HttpUrl

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
def add_machine(request, data: CreateMachineSchema):
    """
    Add a machine
    """
    try:
        insert_sql = "INSERT INTO machine (name, location) values (%s,%s) RETURNING id"
        insert_values = (data.name, data.location)
        conn = connections['default']  # I ran into problems with tests and transactions, hence doing it this way
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



class UpdateMachineSchema(Schema):
    name: str
    location: str


@api.put("/machines/{machine_id}/change")
def update_machines(request, data: UpdateMachineSchema):
    ## This would work similar to add_machine)_ above,
    # though the machine id would be included, and an update query would be issued rather than an insert
    # the spec said not to repeat too much code
    pass


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

@api.get("/simulations/{simulation_id}/detail", url_name="simulation_detail")
def simulation_detail(request, simulation_id: int):
    """ Get detail for one simulation"""

    get_machines_sql = ("SELECT * FROM simulation a "
                        "LEFT JOIN machine m ON m.simulation_id = s.id "
                        "WHERE id = (%s)")
    conn = connections['default']
    conn.ensure_connection()
    with conn.connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(get_machines_sql, (simulation_id,))
        results = cur.fetchone()
    return results


class State(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'


class CreateSimulationSchema(Schema):
    name: str
    state: State
    machine_name: str = None


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
            return {"OK": True,
                    "message": "created new simulation", "id": new_id}

    except Exception as e:
        logger.error(str(e))
        conn.rollback()
        return JsonResponse({"OK": False, "error": str(e)}, status=400)


class SortFields(str, Enum):
    NAME_AS = 'name'
    NAME_DESC = '-name'
    CREATION_ASC = 'created'
    CREATION_DESC = '-created'
    UPDATE_ASC = 'updated'
    UPDATE_DESC = '-updated'


# dictionary lookup  to avoid SQL injection
sort_to_sql = {
    "name": "ORDER BY name ASC",
    "-name": "ORDER BY name DESC",
    "created": "ORDER BY date_created ASC",
    "-created": "ORDER BY date_created DESC",
    "updated": "ORDER BY date_updated ASC",
    "-updated": "ORDER BY date_updated DESC"
}


class SearchSortFilter(Schema):
    sort: Optional[str] = None
    state: Optional[str] = None


class SimulationResponse(BaseModel):
    id: int
    name: str
    state: str
    date_created: datetime
    date_updated: Optional[datetime]
    machine_id: Optional[int]
    link: str   # this should use HTTPUrl, but it gives me an error


@api.get("/simulations", response=List[SimulationResponse])
def simulations(request, filters: Query[SearchSortFilter] = None):
    """
    List of machines, filterable and sortable
    :param response:
    :param request:
    :return:A list of simulation objects as json
    """

    try:
        get_machines_sql = "SELECT * FROM simulation "
        placeholder_vars = []
        if filters.state:
            get_machines_sql += " WHERE state = %s "
            placeholder_vars.append(filters.state)

        if filters.sort:
            get_machines_sql += sort_to_sql.get(filters.sort, "")

        conn = connections['default']
        conn.ensure_connection()
        with conn.connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(get_machines_sql, placeholder_vars)
            results = cur.fetchall()
            for result in results:

                # add the clickable link
                current_scheme = request.scheme  # 'http' or 'https'
                current_domain = request.get_host()  # Domain or IP

                url = reverse("api-1.0.0:simulation_detail",
                              kwargs={"simulation_id": result['id']})
                full_url = f"{current_scheme}://{current_domain}{url}"

                result.update({"link": full_url})

        return results

    except Exception as e:
        return JsonResponse({"OK": False, "error": str(e)}, status=400)


class CreateLossData(Schema):
    seconds: int
    loss: condecimal(max_digits=10, decimal_places=5)
    simulation_id: int


@api.post("lossdata/add")
def add_loss_data(request, data: CreateLossData):
    try:
        insert_sql = """INSERT INTO lossdata (seconds, loss, simulation_id)
                        VALUES (%s, %s, %s)
                        RETURNING id
                        """
        insert_values = (data.seconds, data.loss, data.simulation_id)
        conn = connections['default']
        with conn.cursor() as cur:
            cur.execute(insert_sql, insert_values)
            new_id = cur.fetchone()[0]
            return {"OK": True,
                    "message": "created new loss data", "id": new_id}

    except Exception as e:
        logger.error(str(e))
        conn.rollback()
        return JsonResponse({"OK": False, "error": str(e)}, status=400)
