import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

## Make sure these tables are created in the appropriate place
## We can populate them here as examples

################################################################
# Users Table

users = [
    { 
        "id": 1, 
        "role_id": 1, 
        "username": "johndoe", 
        "firstname": "John", 
        "lastname": "Doe"
    },
    { 
        "id": 2, 
        "role_id": 1, 
        "username": "janedoe", 
        "firstname": "Jane", 
        "lastname": "Doe" 
    },
    { 
        "id": 3, 
        "role_id": 1, 
        "username": "jimdoe", 
        "firstname": "Jim", 
        "lastname": "Doe" 
    },
    { 
        "id": 4, 
        "role_id": 1, 
        "username": "major", 
        "firstname": "Sergeant", 
        "lastname": "Major" 
    },
    { 
        "id": 5, 
        "role_id": 2, 
        "username": "counselor", 
        "firstname": "Dr.", 
        "lastname": "Counselor" 
    },
    { 
        "id": 6, 
        "role_id": 3, 
        "username": "admin", 
        "firstname": "The", 
        "lastname": "Administrator" 
    },
]

drop_table('users',c)
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        role_id INTEGER,
        username TEXT,
        firstname TEXT,
        lastname TEXT,
        FOREIGN KEY(role_id) REFERENCES roles(id)
    )
''')

c.executemany('INSERT INTO users VALUES (:id, :role_id, :username, :firstname, :lastname)', users)
conn.commit()

################################################################
## "Student Info" Table
# This table will contain information on students, including
#   - what stage they are in the app
#     stage = ['new', 'profiled', 'program_chosen', 'schedule_created']
#   - if a major is chosen (program_id)
#     program_id = 0 means major has not yet been chosen
#   - transfer_credits (0 or 1)
#   - financial_aid (0 or 1)
#   - if the student is in-state, out-of-state, or military
#   - profile: full-time, part-time, evening, unknown
# 

student_info = [
    { 
        "id": 1, 
        "user_id": 1, 
        "resident_status_id": 1,
        "transfer_credits": 0,
        "financial_aid": 0,
        "stage": "schedule_created",
        "program_id": 10, 
        "profile": "full-time",
        "notes": "John Doe new student program selected"
    },
    { 
        "id": 2, 
        "user_id": 3, 
        "resident_status_id": 1 , 
        "transfer_credits": 0,
        "financial_aid": 0,
        "stage": "new",
        "program_id": 0, 
        "profile": "unknown",
        "notes": "Jim Doe new student no program selected"
    },
    { 
        "id": 3, 
        "user_id": 2, 
        "resident_status_id": 2, 
        "transfer_credits": 0,
        "financial_aid": 0,
        "stage": "program_chosen",
        "program_id": 10, 
        "profile": "part-time",
        "notes": "Jane Doe with transfer credits" 
    },
    { 
        "id": 4, 
        "user_id": 4, 
        "resident_status_id": 3 , 
        "transfer_credits": 0,
        "financial_aid": 0,
        "stage": "new",
        "program_id": 0, 
        "profile": "evening",
        "notes": "Sergeant Major - evening school" 
    } 
]

drop_table('student_info',c)
c.execute('''
    CREATE TABLE student_info (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        resident_status_id INTEGER,
        transfer_credits INTEGER,
        financial_aid INTEGER,
        stage TEXT,
        program_id INTEGER,
        profile TEXT,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(resident_status_id) REFERENCES resident_status(id)
        FOREIGN KEY(program_id) REFERENCES programs(id)
    )
''')

c.executemany('''
    INSERT INTO student_info 
        VALUES (:id, :user_id, :resident_status_id, :transfer_credits, :financial_aid, :stage, :program_id, :profile, :notes)
    ''', student_info)
conn.commit()

# Close the connection
conn.close()
