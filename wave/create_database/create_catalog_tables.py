import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

################################################################
# Degrees Table

degrees = [
    { "id":  1, "name": "AA", "type": "Associate's" },
    { "id":  2, "name": "BA", "type": "Bachelor's" },
    { "id":  3, "name": "BS", "type": "Bachelor's" },
    { "id":  4, "name": "BSN", "type": "Bachelor's" },
    { "id":  5, "name": "Minor", "type": "Bachelor's Minor" },
    { "id":  6, "name": "MA", "type": "Master's" },
    { "id":  7, "name": "MAT", "type": "Master's" },
    { "id":  8, "name": "MBA", "type": "Master's" },
    { "id":  9, "name": "MDE", "type": "Master's" },
    { "id": 10, "name": "MEd", "type": "Master's" },
    { "id": 11, "name": "MS", "type": "Master's" },
    { "id": 12, "name": "DBA", "type": "Doctorate" },
    { "id": 13, "name": "DM", "type": "Doctorate" },
    { "id": 14, "name": "UC", "type": "Undergraduate Certificate" },
    { "id": 15, "name": "GC", "type": "Graduate Certificate"}
]

drop_table('degrees',c)
c.execute('''
    CREATE TABLE degrees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT
    )
''')

c.executemany('INSERT INTO degrees VALUES (:id, :name, :type)', degrees)
conn.commit()

################################################################
# "Course Type" Table

course_type = [
    { "id":  1, "name": "major", "label": "Major" },
    { "id":  2, "name": "required", "label": "Required" },
    { "id":  3, "name": "general", "label": "General" },
    { "id":  4, "name": "elective", "label": "Elective" },
    { "id":  5, "name": "related", "label": "Related" },    
    { "id":  6, "name": "required_ge", "label": "Required,General" },
    { "id":  7, "name": "required_elective", "label": "Required,Elective" }
]

drop_table('course_type',c)
c.execute('''
    CREATE TABLE course_type (
        id INTEGER PRIMARY KEY,
        name TEXT,
        label TEXT
    )
''')

c.executemany('INSERT INTO course_type VALUES (:id, :name, :label)', course_type)
conn.commit()

# Close the connection
conn.close()