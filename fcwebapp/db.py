import psycopg2
import psycopg2.extras

from fcwebapp import app
from fcwebapp.models import users, Hammock, hammocks


db: psycopg2._psycopg.connection

def init_db():
    global db
    db = psycopg2.connect(app.config['DATABASE_URI'])
    psycopg2.extras.register_uuid()
    cursor = db.cursor()
    do_init_func(cursor, "CREATE TABLE hammocks (id uuid PRIMARY KEY, name varchar NOT NULL, occupant uuid NOT NULL)")
    db.commit()


    # LOAD DATA - users first, then other shit
    cursor.execute("SELECT * FROM hammocks")
    entries = cursor.fetchall()
    for hammock in entries:
        hammocks[hammock[0]] = Hammock(hammock[0], hammock[1], users[hammock[2]])



# Effectively does implicit migrations every boot
def do_init_func(cursor: psycopg2._psycopg.cursor, sql: str):
    try:
        cursor.execute(sql)
    except psycopg2.errors.DuplicateTable as e:
        return


def add_hammock(hammock: Hammock):
    cursor = db.cursor()
    cursor.execute("INSERT INTO hammocks (id, name, occupant) VALUES (%s, %s, %s)",
                   (hammock.uuid, hammock.name, hammock.occupant.uuid))
    db.commit()
    hammocks[hammock.uuid] = hammock

def rm_hammock(hammock: Hammock):
    cursor = db.cursor()
    cursor.execute("DELETE FROM hammocks WHERE uuid = %s",
                   (hammock.uuid,))
    db.commit()
    hammocks.pop(hammock.uuid)