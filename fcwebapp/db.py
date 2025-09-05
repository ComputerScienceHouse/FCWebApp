import uuid

import psycopg2
import psycopg2.extras
from psycopg2 import sql

from fcwebapp import app, UserInfo
from fcwebapp.models import users, Hammock, hammocks, Tent, tents

db: psycopg2._psycopg.connection

google_uuids: dict[str, uuid.UUID] = {}


def init_db():
    global db
    db = psycopg2.connect(app.config['DATABASE_URI'])
    psycopg2.extras.register_uuid()

    do_init_func(
        "CREATE TABLE IF NOT EXISTS hammocks (id uuid PRIMARY KEY, name varchar NOT NULL, occupant uuid NOT NULL)")
    do_init_func(
        "CREATE TABLE IF NOT EXISTS users (id uuid PRIMARY KEY, username varchar NOT NULL, name varchar NOT NULL, "
        "email varchar NOT NULL, occupying_uuid uuid, phone_number varchar, in_ride bool, diet text, "
        "allergies text, health text)")
    do_init_func("CREATE TABLE IF NOT EXISTS tents (id uuid PRIMARY KEY, name varchar NOT NULL, capacity int NOT NULL)")
    do_init_func(
        "CREATE TABLE IF NOT EXISTS tent_occupants (tent_id uuid, occupant_id uuid UNIQUE, PRIMARY KEY(tent_id, occupant_id))")
    do_init_func(
        "CREATE TABLE IF NOT EXISTS google_uuid (sub varchar PRIMARY KEY, id uuid NOT NULL)"
    )

    cursor = db.cursor()
    # LOAD DATA - users first, then other shit
    cursor.execute("SELECT * FROM google_uuid")
    entries = cursor.fetchall()
    for annoying in entries:
        google_uuids[annoying[0]] = annoying[1]

    cursor.execute("SELECT * FROM users")
    entries = cursor.fetchall()
    for person in entries:
        users[person[0]] = UserInfo(person[0], person[1], person[2], person[3], person[4], person[5], person[6],
                                    person[7], person[8], person[9])

    cursor.execute("SELECT * FROM hammocks")
    entries = cursor.fetchall()
    for hammock in entries:
        hammocks[hammock[0]] = Hammock(hammock[0], hammock[1], users[hammock[2]])

    cursor.execute("SELECT * FROM tent_occupants")
    entries = cursor.fetchall()
    occupancy: dict[uuid.UUID, list[UserInfo]] = {}
    for tent_occupant in entries:
        if tent_occupant[0] not in occupancy:
            occupancy[tent_occupant[0]] = []
        occupancy[tent_occupant[0]].append(users[tent_occupant[1]])

    cursor.execute("SELECT * FROM tents")
    entries = cursor.fetchall()
    for tent in entries:
        tents[tent[0]] = Tent(tent[0], tent[1], tent[2], occupancy.get(tent[0]))


# Effectively does implicit migrations every boot
def do_init_func(sql: str):
    try:
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
    except psycopg2.errors.DuplicateTable:
        pass
    except Exception as e:
        print(e)
    db.rollback()


def add_user(user: UserInfo):
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (id, username, name, email) VALUES (%s, %s, %s, %s)",
                       (user.uuid, user.username, user.name, user.email))
    except Exception as e:
        print(e)
        db.rollback()
        return
    db.commit()
    users[user.uuid] = user


def update_user(user: UserInfo):
    user.check()
    cursor = db.cursor()
    fields = [sql.Identifier(k) for k in user.__dict__.keys() if k not in ('uuid', 'first_name', 'met_requirements')]
    values = [v for k, v in user.__dict__.items() if k not in ('uuid', 'first_name', 'met_requirements')]

    set_clause = sql.SQL(', ').join(
        sql.SQL("{} = %s").format(f) for f in fields
    )
    query = sql.SQL("UPDATE users SET {} WHERE id = %s").format(set_clause)
    values.append(user.uuid)
    try:
        cursor.execute(query, values)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()


def add_google_user(sub: str, newid: uuid.UUID):
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO google_uuid (sub, id) VALUES (%s, %s)",
                       (sub, newid))
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
    google_uuids[sub] = newid


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


def add_tent(tent: Tent):
    cursor = db.cursor()
    cursor.execute("INSERT INTO tents (id, name, capacity) VALUES (%s, %s, %s)", (tent.uuid, tent.name, tent.capacity))
    db.commit()
    tents[tent.uuid] = tent


def join_tent(tent: Tent, user: UserInfo):
    cursor = db.cursor()
    cursor.execute("INSERT INTO tent_occupants (tent_id, occupant_id) VALUES (%s, %s)", (tent.uuid, user.uuid))
    tents[tent.uuid].add_occupant(user)
    user.occupying_uuid = tent.uuid
    update_user(user)


def leave_tent(tent: Tent, user: UserInfo):
    cursor = db.cursor()
    cursor.execute("DELETE FROM tent_occupants WHERE tent_id = %s AND occupant_id = %s", (tent.uuid, user.uuid))
    tents[tent.uuid].remove_occupant(user)
    user.occupying_uuid = None
    update_user(user)
