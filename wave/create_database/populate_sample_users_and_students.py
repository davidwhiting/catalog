import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

## Make sure these tables are created in the appropriate place
## We can populate them here as examples

################################################################
# populate Users Table

users = [
    { 
        "id": 2, 
        "role_id": 2, 
        "username": "counselor", 
        "firstname": "Dr.", 
        "lastname": "Counselor",
    },
    { 
        "id": 3, 
        "role_id": 3, 
        "username": "johndoe", 
        "firstname": "John", 
        "lastname": "Doe",
        "notes": "Example new undergrad student, major selected"
    },
    { 
        "id": 4, 
        "role_id": 3, 
        "username": "janedoe", 
        "firstname": "Jane", 
        "lastname": "Doe",
        "notes": "Example transfer undergrad student, major selected and transfer credits applied"
    },
    { 
        "id": 5, 
        "role_id": 3, 
        "username": "jimdoe", 
        "firstname": "Jim", 
        "lastname": "Doe",
        "notes": "Example undergrad student, new to UMGC and no major selected" 
    },
    { 
        "id": 6, 
        "role_id": 3, 
        "username": "major", 
        "firstname": "Sergeant", 
        "lastname": "Major",
        "notes": "Example military student, evening classes only"
    },
]

c.executemany('INSERT INTO users VALUES (:id, :role_id, :username, :firstname, :lastname)', users)
conn.commit()

################################################################
## Sample "Student Info" Table

student_info = [
    { 
        "user_id": 3,
        "resident_status_id": 1,
        "transfer_credits": 0,
        "financial_aid": 0,
        "app_stage_id": 4, 
        "program_id": 5, 
        "student_profile_id": 1,
        "notes": "John Doe in-state full-time student, no transfer credit, no financial aid, schedule created, program selected"
    },
    { 
        "user_id": 4,
        "resident_status_id": 2,
        "transfer_credits": 1,
        "financial_aid": 0,
        "app_stage_id": 3, 
        "program_id": 5, 
        "student_profile_id": 2,
        "notes": "Jane Doe, student with transfer credits"
    },
    { 
        "id": 2, 
        "user_id": 3, 
        "resident_status_id": 1 , 
        "transfer_credits": 0,
        "financial_aid": 0,
        "app_stage_id": 1,
        "program_id": 0,
        "student_profile_id": "unknown",
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

c.executemany('''
    INSERT INTO student_info 
        VALUES (:id, :user_id, :resident_status_id, :transfer_credits, :financial_aid, :stage, :program_id, :profile, :notes)
    ''', student_info)
conn.commit()

# Close the connection
conn.close()
