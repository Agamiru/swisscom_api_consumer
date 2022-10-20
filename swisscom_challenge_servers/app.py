"""
This application serves to mimic 3 hosts: group_one, group_two and group_three.
Each of these 'hosts' are tied to their own databases: database_one, database_two
and database_three.
Each of these 'hosts' support POST, GET and DELETE http methods.
Each of these methods can return a successful HTTP response or unsuccessful.
"""


from typing import Optional
from flask import Flask, request
import json
import redis


from utils import (
    create_dbs, randomized_response, sql, not_found
)

r = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)

create_dbs()

# create function
def create(database: str):
    data = json.loads(request.data)
    grp_id: str = data["groupId"]

    # persist item
    with sql.connect(database) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO groups (groupId) VALUES (?)", [grp_id])
        conn.commit()

    # retuern response
    return randomized_response("create")

# create views
@app.route("/v1/group_one/", methods=["POST"])
def create_one():
    return create("database_one.db")

@app.route("/v1/group_two/", methods=["POST"])
def create_two():
    return create("database_two.db")

@app.route("/v1/group_three/", methods=["POST"])
def create_three():
    return create("database_three.db")


# retrieve function
def get(grp_id, database: str):
    with sql.connect(database) as con:
        # retrieve item
        cur = con.cursor()
        cur.execute("SELECT * FROM groups WHERE groupId = (?)", [grp_id])
        data: Optional[dict] = cur.fetchone()

        if data is not None:
            data = {"groupId": data[0]}
        else:
            print("Found no record for grp_id: ", grp_id)
            return not_found

        # return response
        return randomized_response("get", "get", data)


# retrieve Views
@app.route("/v1/group_one/<grp_id>/")
def get_one(grp_id):
    return get(grp_id, "database_one.db")

@app.route("/v1/group_two/<grp_id>/")
def get_two(grp_id):
    return get(grp_id, "database_two.db")

@app.route("/v1/group_three/<grp_id>/")
def get_three(grp_id):
    return get(grp_id, "database_three.db")


# delete function
def delete(database: str):
    data = json.loads(request.data)
    grp_id: str = data["groupId"]

    with sql.connect(database) as conn:
        # delete item
        cur = conn.cursor()
        cur.execute("DELETE FROM groups WHERE groupId = (?)", [grp_id])
        conn.commit()
        
        # return response
        return randomized_response("delete")

# delete views
@app.route("/v1/group_one/", methods=["DELETE"])
def delete_one():
    return delete("database_one.db")

@app.route("/v1/group_two/", methods=["DELETE"])
def delete_two():
    return delete("database_two.db")

@app.route("/v1/group_three/", methods=["DELETE"])
def delete_three():
    return delete("database_three.db")


if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port=5000)
