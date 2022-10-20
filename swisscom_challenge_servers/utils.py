import sqlite3 as sql
import time
import random
from typing import Optional, Union

from flask import Response, jsonify


def create_dbs():
    with sql.connect("database_one.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS groups (groupId INT UNIQUE)"
        )

    with sql.connect("database_two.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS groups (groupId INT UNIQUE)"
        )

    with sql.connect("database_three.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS groups (groupId INT UNIQUE)"
        )

# Possible responses
create = Response(status=201, mimetype='application/json')
not_found = Response(status=404, mimetype='application/json')
bad_request = Response(status=400, mimetype='application/json')
success_w_data = lambda data: jsonify(data)
success = Response(status=200, mimetype='application/json')
# Mimics timeout error if calling request timeout is set to less.
# Throwaway variable added so signature is uniform with `success_w_data`
sleep = lambda _ = None: time.sleep(4)

# success responses kept at zero index intentioanally
response_list = {
    "create": [create, sleep, bad_request],
    "get": [success_w_data, not_found, sleep],
    "delete": [success, sleep, not_found]
}

def is_lambda(v):
    """Simple logic to check if a function is a lambda"""

    LAMBDA = lambda:0
    return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__


# When an item in this list is selected at random, it will return 0 most of the time.
# Used to ensure response (from `response_list`) is mostly successful.
zero_biased_list = [0,0,0,0,0,0,1,0,0,0,2]

def randomized_response(
    response_type: str, view_type: Optional[str] = None, data=None
) -> Union[Response, list]:
    """Returns random response"""

    responses = response_list[response_type]
    choice = responses[random.choice(zero_biased_list)]
    if is_lambda(choice):
        if view_type is not None and view_type == "get":
            resp = choice(data)
            return resp if resp is not None else []
        else:
            print("sleeping...")
            choice()
            return []
    else:
        return choice