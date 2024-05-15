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
        "notes": "example coach"
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
        "username": "sgtdoe", 
        "firstname": "Sgt", 
        "lastname": "Doe",
        "notes": "Example military student, evening classes only"
    },
]

c.executemany('''
    INSERT INTO users VALUES (:id, :role_id, :username, :firstname, :lastname, :notes)
''', users)
conn.commit()

################################################################
## Populate sample "Student Info" Table

student_info = [
    { 
        "user_id": 3,
        "resident_status_id": 1,
        "transfer_credits": 0,
        "financial_aid": 1,
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
        "user_id": 5, 
        "resident_status_id": None,
        "transfer_credits": None,
        "financial_aid": None,
        "app_stage_id": 1,
        "program_id": None,
        "student_profile_id": None,
        "notes": "Jim Doe new student no program selected"
    },
    { 
        "user_id": 6, 
        "resident_status_id": 3 , 
        "transfer_credits": 0,
        "financial_aid": 1,
        "app_stage_id": 2,
        "program_id": None, 
        "student_profile_id": 3,
        "notes": "Sgt Doe - evening school" 
    } 
]

c.executemany('''
    INSERT INTO student_info (user_id, resident_status_id, transfer_credits, financial_aid, 
        app_stage_id, program_id, student_profile_id, notes)
    VALUES (:user_id, :resident_status_id, :transfer_credits, :financial_aid, :app_stage_id, 
        :program_id, :student_profile_id, :notes)
    ''', student_info)
conn.commit()

#################################################################
# "Student History" Table                                       #
#                                                               #
# courses completed, including transfer credits                 #
#################################################################

student_history = [
    { 'user_id': 4, 'name': 'STAT 200', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'HUMN 100', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'ARTH 334', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'ELECTIVE', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'ELECTIVE', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'ELECTIVE', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'ELECTIVE', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'ELECTIVE', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'ELECTIVE', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'ELECTIVE', 'credits': 3, 'transfer': 1 },
    { 'user_id': 4, 'name': 'ELECTIVE', 'credits': 3, 'transfer': 1 },
]

c.executemany('''
    INSERT INTO student_history (user_id, name, credits, transfer)
        VALUES (:user_id, :name, :credits, :transfer)
    ''', student_history)

conn.commit()

#################################################################
# "Student Progress" Table                                      #
#                                                               #
# student_history mapped into selected program.                 #
#################################################################


student_progress_d3 = [
    { 'user_id': 3, 'seq':  1, 'name': 'PACE 111B', 'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  1, 'session': 1, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq':  2, 'name': 'LIBS 150',  'credits': 1, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  1, 'session': 1, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq':  3, 'name': 'WRTG 111',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  1, 'session': 3, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq':  4, 'name': 'NUTR 100',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  1, 'session': 3, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq':  5, 'name': 'WRTG 112',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  2, 'session': 1, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq':  6, 'name': 'BMGT 110',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  2, 'session': 2, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq':  7, 'name': 'SPCH 100',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  3, 'session': 1, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq':  8, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  3, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq':  9, 'name': 'STAT 200',  'credits': 3, 'course_type': 'required,general', 'type': 'required', 'completed': 0, 'term':  3, 'session': 3, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq': 10, 'name': 'IFSM 300',  'credits': 3, 'course_type': 'required,general', 'type': 'required', 'completed': 0, 'term':  3, 'session': 3, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq': 11, 'name': 'ACCT 220',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  4, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 12, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  4, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 13, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  4, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 14, 'name': 'HUMN 100',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  4, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 15, 'name': 'BIOL 103',  'credits': 4, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  5, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 16, 'name': 'ECON 201',  'credits': 3, 'course_type': 'required,general', 'type': 'required', 'completed': 0, 'term':  5, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 17, 'name': 'ARTH 334',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  5, 'session': 3, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq': 18, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  5, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 19, 'name': 'ECON 203',  'credits': 3, 'course_type': 'required,general', 'type': 'required', 'completed': 0, 'term':  6, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 20, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  6, 'session': 2, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 17, 'name': 'ACCT 221',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  7, 'session': 1, 'prerequisites': 'ACCT 220'                        }, 
    { 'user_id': 3, 'seq': 19, 'name': 'BMGT 364',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  7, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 20, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  7, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 21, 'name': 'BMGT 365',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  7, 'session': 3, 'prerequisites': 'BMGT 364'                        }, 
    { 'user_id': 3, 'seq': 22, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  8, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 23, 'name': 'MRKT 310',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  8, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 24, 'name': 'WRTG 394',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  8, 'session': 3, 'prerequisites': 'WRTG 112'                        }, 
    { 'user_id': 3, 'seq': 25, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  8, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 26, 'name': 'BMGT 380',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  9, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 27, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  9, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 28, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  9, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 29, 'name': 'HRMN 300',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  9, 'session': 3, 'prerequisites': ''                                },
    { 'user_id': 3, 'seq': 30, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term': 10, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 31, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term': 10, 'session': 2, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 32, 'name': 'FINC 330',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term': 11, 'session': 1, 'prerequisites': 'ACCT 221 & STAT 200'             }, 
    { 'user_id': 3, 'seq': 33, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term': 11, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 34, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term': 11, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 35, 'name': 'BMGT 496',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term': 11, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 36, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term': 12, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 3, 'seq': 40, 'name': 'BMGT 495',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term': 12, 'session': 1, 'prerequisites': 'BMGT 365 & MRKT 310 & FINC 330'  }, 
    { 'user_id': 3, 'seq': 41, 'name': 'CAPL 398A', 'credits': 1, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term': 12, 'session': 3, 'prerequisites': 'FINC 330'                        }, 
    { 'user_id': 4, 'seq':  0, 'name': 'STAT 200',  'credits': 3, 'course_type': 'required,general', 'type': 'required', 'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  0, 'name': 'HUMN 100',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq':  0, 'name': 'ARTH 334',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  0, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq':  0, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq':  0, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq':  0, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq':  0, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq':  0, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq':  0, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq':  0, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 1, 'term':  0, 'session': 0, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq':  1, 'name': 'PACE 111B', 'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  1, 'session': 1, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  2, 'name': 'LIBS 150',  'credits': 1, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  1, 'session': 2, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  3, 'name': 'WRTG 111',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  1, 'session': 3, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  4, 'name': 'WRTG 112',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  2, 'session': 1, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  5, 'name': 'NUTR 100',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  2, 'session': 2, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  6, 'name': 'BMGT 110',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  3, 'session': 3, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  7, 'name': 'SPCH 100',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  3, 'session': 1, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  8, 'name': 'IFSM 300',  'credits': 3, 'course_type': 'required,general', 'type': 'required', 'completed': 0, 'term':  3, 'session': 2, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq':  9, 'name': 'ACCT 220',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  4, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 10, 'name': 'BIOL 103',  'credits': 4, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  4, 'session': 2, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 11, 'name': 'ECON 201',  'credits': 3, 'course_type': 'required,general', 'type': 'required', 'completed': 0, 'term':  4, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 12, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  5, 'session': 2, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 13, 'name': 'ECON 203',  'credits': 3, 'course_type': 'required,general', 'type': 'required', 'completed': 0, 'term':  5, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 14, 'name': 'ACCT 221',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  5, 'session': 3, 'prerequisites': 'ACCT 220'                        }, 
    { 'user_id': 4, 'seq': 15, 'name': 'BMGT 364',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  6, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 16, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  6, 'session': 2, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 17, 'name': 'BMGT 365',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  7, 'session': 1, 'prerequisites': 'BMGT 364'                        }, 
    { 'user_id': 4, 'seq': 18, 'name': 'MRKT 310',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  7, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 19, 'name': 'WRTG 394',  'credits': 3, 'course_type': 'general',          'type': 'general',  'completed': 0, 'term':  7, 'session': 2, 'prerequisites': 'WRTG 112'                        }, 
    { 'user_id': 4, 'seq': 20, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  8, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 21, 'name': 'BMGT 380',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  8, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 22, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  8, 'session': 2, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 23, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term':  9, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 24, 'name': 'HRMN 300',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term':  9, 'session': 2, 'prerequisites': ''                                },
    { 'user_id': 4, 'seq': 25, 'name': 'FINC 330',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term': 10, 'session': 1, 'prerequisites': 'ACCT 221 & STAT 200'             }, 
    { 'user_id': 4, 'seq': 26, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term': 10, 'session': 1, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 27, 'name': 'ELECTIVE',  'credits': 3, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term': 10, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 28, 'name': 'BMGT 496',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term': 10, 'session': 3, 'prerequisites': ''                                }, 
    { 'user_id': 4, 'seq': 29, 'name': 'BMGT 495',  'credits': 3, 'course_type': 'major',            'type': 'major',    'completed': 0, 'term': 11, 'session': 1, 'prerequisites': 'BMGT 365 & MRKT 310 & FINC 330'  }, 
    { 'user_id': 4, 'seq': 30, 'name': 'CAPL 398A', 'credits': 1, 'course_type': 'elective',         'type': 'elective', 'completed': 0, 'term': 11, 'session': 1, 'prerequisites': 'FINC 330'                        },    
]


c.execute('DELETE FROM student_progress_d3')
c.execute('DELETE FROM student_progress_d3_old')

c.executemany('''
    INSERT INTO student_progress_d3 (user_id, seq, name, credits, course_type, type, completed, term, session, prerequisites)
        VALUES (:user_id, :seq, :name, :credits, :course_type, :type, :completed, :term, :session, :prerequisites)
    ''', student_progress_d3)
conn.commit()

c.executemany('''
    INSERT INTO student_progress_d3_old (user_id, seq, name, credits, course_type, type, completed, term, session, prerequisites)
        VALUES (:user_id, :seq, :name, :credits, :course_type, :type, :completed, :term, :session, :prerequisites)
    ''', student_progress_d3)
conn.commit()

# Close the connection
conn.close()
