import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

################################################################
# "Program Requirements" Table
# Bachelor's program requirement summary

program_requirements = [
    { "program_id":  2, "major": 36, "related_ge": 12, "related_elective": 15, "remaining_ge": 29, "remaining_elective": 28 },
    { "program_id":  3, "major": 30, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 49 },
    { "program_id":  4, "major": 36, "related_ge":  8, "related_elective":  9, "remaining_ge": 33, "remaining_elective": 34 },
    { "program_id":  5, "major": 33, "related_ge": 12, "related_elective":  0, "remaining_ge": 29, "remaining_elective": 46 },
    { "program_id":  6, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id":  7, "major": 36, "related_ge":  7, "related_elective":  7, "remaining_ge": 34, "remaining_elective": 36 },
    { "program_id":  8, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id":  9, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id": 10, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id": 11, "major": 39, "related_ge":  6, "related_elective":  0, "remaining_ge": 35, "remaining_elective": 40 },
    { "program_id": 12, "major": 30, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 49 },
    { "program_id": 13, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id": 14, "major": 36, "related_ge":  6, "related_elective":  0, "remaining_ge": 35, "remaining_elective": 43 },
    { "program_id": 15, "major": 39, "related_ge":  9, "related_elective":  0, "remaining_ge": 32, "remaining_elective": 40 },
    { "program_id": 16, "major": 30, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 49 },
    { "program_id": 17, "major": 33, "related_ge":  3, "related_elective":  0, "remaining_ge": 38, "remaining_elective": 46 },
    { "program_id": 18, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id": 19, "major": 33, "related_ge":  6, "related_elective":  0, "remaining_ge": 35, "remaining_elective": 46 },
    { "program_id": 20, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id": 21, "major": 33, "related_ge":  3, "related_elective":  0, "remaining_ge": 38, "remaining_elective": 46 },
    { "program_id": 22, "major": 36, "related_ge":  3, "related_elective":  0, "remaining_ge": 38, "remaining_elective": 43 },
    { "program_id": 23, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id": 24, "major": 36, "related_ge":  8, "related_elective":  6, "remaining_ge": 33, "remaining_elective": 37 },
    { "program_id": 25, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id": 26, "major": 33, "related_ge":  3, "related_elective":  0, "remaining_ge": 38, "remaining_elective": 46 },
    { "program_id": 27, "major": 33, "related_ge":  9, "related_elective":  0, "remaining_ge": 32, "remaining_elective": 46 },
    { "program_id": 28, "major": 36, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 43 },
    { "program_id": 29, "major": 30, "related_ge": 17, "related_elective":  4, "remaining_ge": 24, "remaining_elective": 45 },
    { "program_id": 30, "major": 30, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 49 },
    { "program_id": 31, "major": 33, "related_ge":  3, "related_elective":  0, "remaining_ge": 38, "remaining_elective": 46 },
    { "program_id": 32, "major": 30, "related_ge":  3, "related_elective":  0, "remaining_ge": 38, "remaining_elective": 49 },
    { "program_id": 33, "major": 30, "related_ge":  3, "related_elective":  0, "remaining_ge": 38, "remaining_elective": 49 },
    { "program_id": 34, "major": 33, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 46 },
    { "program_id": 35, "major": 30, "related_ge":  0, "related_elective":  0, "remaining_ge": 41, "remaining_elective": 49 }
]

drop_table('program_requirements',c)
c.execute('''
    CREATE TABLE program_requirements (
        id INTEGER PRIMARY KEY,
        program_id INTEGER,
        major INTEGER,
        related_ge INTEGER,
        related_elective INTEGER,
        remaining_ge INTEGER,
        remaining_elective INTEGER,
        total INTEGER DEFAULT 120,
        FOREIGN KEY(program_id) REFERENCES programs(id)
    )
''')

c.executemany('''
    INSERT INTO program_requirements (program_id, major, related_ge, related_elective, remaining_ge, remaining_elective)
        VALUES (:program_id, :major, :related_ge, :related_elective, :remaining_ge, :remaining_elective )
''', program_requirements)
#c.execute('UPDATE program_requirements SET total=120')
conn.commit()

# Close the connection
conn.close()
