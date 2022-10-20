import sqlite3 as sql

databases = [
    "database_one.db", "database_two.db", "database_three.db"
]

for database in databases:
    try:
        with sql.connect(database) as conn:
            # delete item
            cur = conn.cursor()
            cur.execute("DELETE FROM groups")
            conn.commit()
    except sql.OperationalError:
        # table doesn't exist, thats fine.
        pass