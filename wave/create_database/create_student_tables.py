import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

################################################################
# Resident status Table

resident_status = [
    { "id": 1, "type": "in-state" },
    { "id": 2, "type": "out-of-state" },
    { "id": 3, "type": "military" }
]

drop_table('resident_status',c)
c.execute('''
    CREATE TABLE resident_status (
        id INTEGER PRIMARY KEY,
        type TEXT
    )
''')

c.executemany('INSERT INTO resident_status VALUES (:id, :type)', resident_status)
conn.commit()

################################################################
# Tuition Table

tuition = [
    { "term": "Winter 2024", "program": "undergraduate",       "resident_status_id": 1, "cost":  318 },
    { "term": "Winter 2024", "program": "graduate",            "resident_status_id": 1, "cost":  524 },
    { "term": "Winter 2024", "program": "specialty_graduate",  "resident_status_id": 1, "cost":  694 },
    { "term": "Winter 2024", "program": "doctoral",            "resident_status_id": 1, "cost": 1087 },
    { "term": "Spring 2024", "program": "undergraduate",       "resident_status_id": 1, "cost":  318 },
    { "term": "Spring 2024", "program": "graduate",            "resident_status_id": 1, "cost":  524 },
    { "term": "Spring 2024", "program": "specialty_graduate",  "resident_status_id": 1, "cost":  694 },
    { "term": "Spring 2024", "program": "doctoral",            "resident_status_id": 1, "cost": 1087 },
    { "term": "Summer 2024", "program": "undergraduate",       "resident_status_id": 1, "cost":  324 },
    { "term": "Summer 2024", "program": "graduate",            "resident_status_id": 1, "cost":  534 },
    { "term": "Summer 2024", "program": "specialty_graduate",  "resident_status_id": 1, "cost":  694 },
    { "term": "Summer 2024", "program": "doctoral",            "resident_status_id": 1, "cost": 1087 },
    { "term": "Winter 2024", "program": "undergraduate",       "resident_status_id": 2, "cost":  499 },
    { "term": "Winter 2024", "program": "graduate",            "resident_status_id": 2, "cost":  659 },
    { "term": "Winter 2024", "program": "specialty_graduate",  "resident_status_id": 2, "cost":  694 },
    { "term": "Winter 2024", "program": "doctoral",            "resident_status_id": 2, "cost": 1087 },
    { "term": "Spring 2024", "program": "undergraduate",       "resident_status_id": 2, "cost":  499 },
    { "term": "Spring 2024", "program": "graduate",            "resident_status_id": 2, "cost":  659 },
    { "term": "Spring 2024", "program": "specialty_graduate",  "resident_status_id": 2, "cost":  694 },
    { "term": "Spring 2024", "program": "doctoral",            "resident_status_id": 2, "cost": 1087 },
    { "term": "Summer 2024", "program": "undergraduate",       "resident_status_id": 2, "cost":  499 },
    { "term": "Summer 2024", "program": "graduate",            "resident_status_id": 2, "cost":  659 },
    { "term": "Summer 2024", "program": "specialty_graduate",  "resident_status_id": 2, "cost":  694 },
    { "term": "Summer 2024", "program": "doctoral",            "resident_status_id": 2, "cost": 1087 },
    { "term": "Winter 2024", "program": "undergraduate",       "resident_status_id": 3, "cost":  250 },
    { "term": "Winter 2024", "program": "graduate",            "resident_status_id": 3, "cost":  480 },
    { "term": "Winter 2024", "program": "specialty_graduate",  "resident_status_id": 3, "cost":  480 },
    { "term": "Winter 2024", "program": "doctoral",            "resident_status_id": 3, "cost": 1087 },
    { "term": "Spring 2024", "program": "undergraduate",       "resident_status_id": 3, "cost":  250 },
    { "term": "Spring 2024", "program": "graduate",            "resident_status_id": 3, "cost":  480 },
    { "term": "Spring 2024", "program": "specialty_graduate",  "resident_status_id": 3, "cost":  480 },
    { "term": "Spring 2024", "program": "doctoral",            "resident_status_id": 3, "cost": 1087 },
    { "term": "Summer 2024", "program": "undergraduate",       "resident_status_id": 3, "cost":  250 },
    { "term": "Summer 2024", "program": "graduate",            "resident_status_id": 3, "cost":  336 },
    { "term": "Summer 2024", "program": "specialty_graduate",  "resident_status_id": 3, "cost":  336 },
    { "term": "Summer 2024", "program": "doctoral",            "resident_status_id": 3, "cost": 1087 }
]

drop_table('tuition',c)
c.execute('''
    CREATE TABLE tuition (
        id INTEGER PRIMARY KEY,
        term TEXT,
        program TEXT,
        resident_status_id INTEGER,
        cost INTEGER,
        FOREIGN KEY(resident_status_id) REFERENCES resident_status(id)
    )
''')

c.executemany('INSERT INTO tuition(term, program, resident_status_id, cost) VALUES (:term, :program, :resident_status_id, :cost)', tuition )
conn.commit()

# Close the connection
conn.close()