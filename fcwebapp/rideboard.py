from fcwebapp.db import rbdb


def read_event():
    cursor = rbdb.cursor()
    cursor.execute("SELECT * FROM events WHERE id = %s", (561,))
    r = cursor.fetchone()
    print(r)