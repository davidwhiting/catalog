import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

################################################################
# Roles Table
# These are the roles for someone logging into the app
#   guest:   can do everything a student can do except save the schedule
#   student: can select a major and create a schedule
#   coach:   can select a student and do everything for them
#   admin:   can add users, change roles, plus everything a coach can do

roles = [
    { 'id': 1, 'role': 'admin' },
    { 'id': 2, 'role': 'coach' },
    { 'id': 3, 'role': 'student' },
    { 'id': 4, 'role': 'guest'  }
]

drop_table('roles', c)
c.execute('''
    CREATE TABLE roles (
        id INTEGER PRIMARY KEY,
        role TEXT
    )
''')

c.executemany('INSERT INTO roles VALUES (:id, :role)', roles)
conn.commit()

################################################################
# Users Table
# Except for admin, we will populate this elsewhere 
# (first from examples file, eventually from within the app)

users = [
    { 
        "id": 1, 
        "role_id": 1, 
        "username": "admin", 
        "firstname": "", 
        "lastname": "Admin",
        "sso_role": "staff",
        "notes": "default admin user"
    }
]

drop_table('users', c)
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        role_id INTEGER,
        username TEXT,
        firstname TEXT,
        lastname TEXT,
        sso_role TEXT,
        sso_notes TEXT,
        notes TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        FOREIGN KEY(role_id) REFERENCES roles(id)
    )
''')

c.executemany('''
    INSERT INTO users (id, role_id, username, firstname, lastname, sso_role, notes) 
        VALUES (:id, :role_id, :username, :firstname, :lastname, :sso_role, :notes)
    ''', users)
conn.commit()


################################################################
# Student Profile Table
# These are the roles for someone logging into the app
#   full-time
#   part-time
#   evening
#   unknown

profile = [
    { "id": 1, "type": "full-time", 'label': 'Full-time' },
    { "id": 2, "type": "part-time", 'label': 'Part-time' },
    { "id": 3, "type": "evening", 'label': 'Evening'  },
    { "id": 4, "type": "unknown", 'label': 'Unknown'  }
]

drop_table('student_profile', c)
c.execute('''
    CREATE TABLE student_profile (
        id INTEGER PRIMARY KEY,
        type TEXT,
        label TEXT
    )
''')

c.executemany('INSERT INTO student_profile VALUES (:id, :type, :label)', profile)
conn.commit()

################################################################
# Resident status Table

resident_status = [
    { "id": 1, "type": "in-state",     "label": "In-State" },
    { "id": 2, "type": "out-of-state", "label": "Out-of-State" },
    { "id": 3, "type": "military",     "label": "Military" }
]

drop_table('resident_status', c)
c.execute('''
    CREATE TABLE resident_status (
        id INTEGER PRIMARY KEY,
        type TEXT,
        label TEXT
    )
''')

c.executemany('INSERT INTO resident_status VALUES (:id, :type, :label)', resident_status)
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

drop_table('tuition', c)
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

c.executemany('''
    INSERT INTO tuition(term, program, resident_status_id, cost) 
    VALUES (:term, :program, :resident_status_id, :cost)
''', tuition )
conn.commit()

################################################################
## "Student Info" Table
# This table will contain information on students, including
#   - what stage they are in the app
#     app_stage_id (reference app_stage table in create_ui_tables.py)
#   - if a major is chosen (program_id)
#     program_id = 0 means major has not yet been chosen
#   - transfer_credits (0 or 1)
#   - financial_aid (0 or 1)
#   - resident_status_id if the student is in-state, out-of-state, or military
#   - student_profile_id: full-time, part-time, evening, unknown
# 

drop_table('student_info',c)
c.execute('''
    CREATE TABLE student_info (
        id INTEGER PRIMARY KEY,
        student_id INTEGER UNIQUE DEFAULT NULL,
        user_id INTEGER,
        resident_status_id INTEGER DEFAULT NULL,
        transfer_credits INTEGER DEFAULT NULL,
        financial_aid INTEGER DEFAULT NULL,
        app_stage_id INTEGER DEFAULT NULL,
        program_id INTEGER DEFAULT NULL,
        student_profile_id INTEGER DEFAULT NULL,
        notes TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(resident_status_id) REFERENCES resident_status(id),
        FOREIGN KEY(app_stage_id) REFERENCES app_stage(id),
        FOREIGN KEY(program_id) REFERENCES programs(id),
        FOREIGN KEY(student_profile_id) REFERENCES student_profile(id)
    )
''')

# Note: student_id is for internal student id (e.g., SS# replacement) to tie to university tables
# It is not being used currently.

# Close the connection
conn.close()