import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

################################################################
# Degrees Table

degrees = [
    { "id":  1, "degree": "AA", "type": "Associate's" },
    { "id":  2, "degree": "BA", "type": "Bachelor's" },
    { "id":  3, "degree": "BS", "type": "Bachelor's" },
    { "id":  4, "degree": "BSN", "type": "Bachelor's" },
    { "id":  5, "degree": "Minor", "type": "Bachelor's Minor" },
    { "id":  6, "degree": "MA", "type": "Master's" },
    { "id":  7, "degree": "MAT", "type": "Master's" },
    { "id":  8, "degree": "MBA", "type": "Master's" },
    { "id":  9, "degree": "MDE", "type": "Master's" },
    { "id": 10, "degree": "MEd", "type": "Master's" },
    { "id": 11, "degree": "MS", "type": "Master's" },
    { "id": 12, "degree": "DBA", "type": "Doctorate" },
    { "id": 13, "degree": "DM", "type": "Doctorate" },
    { "id": 14, "degree": "UC", "type": "Undergraduate Certificate" },
    { "id": 15, "degree": "GC", "type": "Graduate Certificate"}
]

drop_table('degrees',c)
c.execute('''
    CREATE TABLE degrees (
        id INTEGER PRIMARY KEY,
        degree TEXT,
        type TEXT
    )
''')

c.executemany('INSERT INTO degrees VALUES (:id, :degree, :type)', degrees)
conn.commit()

################################################################
# "Course Type" Table

course_type = [
    { "id":  1, "type": "major", "label": "Major" },
    { "id":  2, "type": "required", "label": "Required" },
    { "id":  3, "type": "general", "label": "General" },
    { "id":  4, "type": "elective", "label": "Elective" },
    { "id":  5, "type": "related", "label": "Related" },    
    { "id":  6, "type": "required_ge", "label": "Required,General" },
    { "id":  7, "type": "required_elective", "label": "Required,Elective" }
]

drop_table('course_type',c)
c.execute('''
    CREATE TABLE course_type (
        id INTEGER PRIMARY KEY,
        type TEXT,
        label TEXT
    )
''')

c.executemany('INSERT INTO course_type VALUES (:id, :type, :label)', course_type)
conn.commit()

# Close the connection
conn.close()