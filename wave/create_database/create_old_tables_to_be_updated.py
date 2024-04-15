import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

################################################################
# "Program Sequence" Table
# For now, this is the program sequence recommended by the catalog


# this table is old and should be replaced ???
# at minimum, this table should be created from program sequence table by adding course_type_id and source
# source will eventually include algorithm, coach, etc.

program_sequence = [
    { "seq":  1, "program_id": 5, "name": "PACE 111B", "course_type_id": 3, "source": "catalog" },
    { "seq":  2, "program_id": 5, "name": "LIBS 150", "course_type_id": 3, "source": "catalog" },
    { "seq":  3, "program_id": 5, "name": "WRTG 111", "course_type_id": 3, "source": "catalog" },
    { "seq":  4, "program_id": 5, "name": "WRTG 112", "course_type_id": 3, "source": "catalog" },
    { "seq":  5, "program_id": 5, "name": "NUTR 100", "course_type_id": 3, "source": "catalog" },
    { "seq":  6, "program_id": 5, "name": "BMGT 110", "course_type_id": 1, "source": "catalog" },
    { "seq":  7, "program_id": 5, "name": "SPCH 100", "course_type_id": 3, "source": "catalog" },
    { "seq":  8, "program_id": 5, "name": "STAT 200", "course_type_id": 2, "source": "catalog" },
    { "seq":  9, "program_id": 5, "name": "IFSM 300", "course_type_id": 2, "source": "catalog" },
    { "seq": 10, "program_id": 5, "name": "ACCT 220", "course_type_id": 1, "source": "catalog" },
    { "seq": 11, "program_id": 5, "name": "HUMN 100", "course_type_id": 3, "source": "catalog" },
    { "seq": 12, "program_id": 5, "name": "BIOL 103", "course_type_id": 3, "source": "catalog" },
    { "seq": 13, "program_id": 5, "name": "ECON 201", "course_type_id": 2, "source": "catalog" },
    { "seq": 14, "program_id": 5, "name": "ARTH 334", "course_type_id": 3, "source": "catalog" },
    { "seq": 15, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 16, "program_id": 5, "name": "ECON 203", "course_type_id": 2, "source": "catalog" },
    { "seq": 17, "program_id": 5, "name": "ACCT 221", "course_type_id": 1, "source": "catalog" },
    { "seq": 18, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 19, "program_id": 5, "name": "BMGT 364", "course_type_id": 1, "source": "catalog" },
    { "seq": 20, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 21, "program_id": 5, "name": "BMGT 365", "course_type_id": 1, "source": "catalog" },
    { "seq": 22, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 23, "program_id": 5, "name": "MRKT 310", "course_type_id": 1, "source": "catalog" },
    { "seq": 24, "program_id": 5, "name": "WRTG 394", "course_type_id": 3, "source": "catalog" },
    { "seq": 25, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 26, "program_id": 5, "name": "BMGT 380", "course_type_id": 1, "source": "catalog" },
    { "seq": 27, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 28, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 29, "program_id": 5, "name": "HRMN 300", "course_type_id": 1, "source": "catalog" },
    { "seq": 30, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 31, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 32, "program_id": 5, "name": "FINC 330", "course_type_id": 1, "source": "catalog" },
    { "seq": 33, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 34, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 35, "program_id": 5, "name": "BMGT 496", "course_type_id": 1, "source": "catalog" },
    { "seq": 36, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 37, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 38, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 39, "program_id": 5, "name": "ELECTIVE", "course_type_id": 4, "source": "catalog" },
    { "seq": 40, "program_id": 5, "name": "BMGT 495", "course_type_id": 1, "source": "catalog" },
    { "seq": 41, "program_id": 5, "name": "CAPSTONE", "course_type_id": 4, "source": "catalog" }
]

drop_table('program_sequence',c)
c.execute('''
    CREATE TABLE program_sequence (
        seq INTEGER,
        name TEXT,
        program_id INTEGER,
        class_id INTEGER DEFAULT 0,
        course_type_id INTEGER,
        source TEXT,
        FOREIGN KEY(program_id) REFERENCES programs(id),
        FOREIGN KEY(class_id) REFERENCES classes(id),          
        FOREIGN KEY(course_type_id) REFERENCES course_type(id)
    )
''')
c.executemany('''
    INSERT INTO program_sequence (seq, name, program_id, course_type_id, source) 
        VALUES (:seq, :name, :program_id, :course_type_id, :source)
    '''
    , program_sequence
)

c.execute('''
    UPDATE program_sequence
        SET class_id = (
            SELECT id
            FROM classes
            WHERE classes.name = program_sequence.name
        )
''')
conn.commit()

################################################################
# "Student Progress" Table
# This is the table that will store student programs and progress for different students
# This is the database table that the D3 script pulls from currently
# Will need to rebuild and overwrite as optimization, etc. occurs

student_progress = [
    { "student_info_id": 10, "seq":  1, "name": "PACE 111B", "credits": 3, "type": "general",  "completed": 0, "period":  1, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 10, "seq":  2, "name": "LIBS 150",  "credits": 1, "type": "general",  "completed": 0, "period":  1, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 10, "seq":  3, "name": "WRTG 111",  "credits": 3, "type": "general",  "completed": 0, "period":  1, "session": 3, "prerequisite": ""                                },
    { "student_info_id": 10, "seq":  4, "name": "WRTG 112",  "credits": 3, "type": "general",  "completed": 0, "period":  2, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 10, "seq":  5, "name": "NUTR 100",  "credits": 3, "type": "general",  "completed": 0, "period":  1, "session": 3, "prerequisite": ""                                },
    { "student_info_id": 10, "seq":  6, "name": "BMGT 110",  "credits": 3, "type": "major",    "completed": 0, "period":  2, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 10, "seq":  7, "name": "SPCH 100",  "credits": 3, "type": "general",  "completed": 0, "period":  3, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 10, "seq":  8, "name": "STAT 200",  "credits": 3, "type": "required", "completed": 0, "period":  3, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 10, "seq":  9, "name": "IFSM 300",  "credits": 3, "type": "required", "completed": 0, "period":  4, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 10, "seq": 10, "name": "ACCT 220",  "credits": 3, "type": "major",    "completed": 0, "period":  4, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 11, "name": "HUMN 100",  "credits": 3, "type": "general",  "completed": 0, "period":  4, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 12, "name": "BIOL 103",  "credits": 4, "type": "general",  "completed": 0, "period":  5, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 13, "name": "ECON 201",  "credits": 3, "type": "required", "completed": 0, "period":  5, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 14, "name": "ARTH 334",  "credits": 3, "type": "general",  "completed": 0, "period":  5, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 10, "seq": 15, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  6, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 16, "name": "ECON 203",  "credits": 3, "type": "required", "completed": 0, "period":  6, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 17, "name": "ACCT 221",  "credits": 3, "type": "major",    "completed": 0, "period":  7, "session": 1, "prerequisite": "ACCT 220"                        }, 
    { "student_info_id": 10, "seq": 18, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  7, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 19, "name": "BMGT 364",  "credits": 3, "type": "major",    "completed": 0, "period":  7, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 20, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  8, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 21, "name": "BMGT 365",  "credits": 3, "type": "major",    "completed": 0, "period":  8, "session": 1, "prerequisite": "BMGT 364"                        }, 
    { "student_info_id": 10, "seq": 22, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  9, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 23, "name": "MRKT 310",  "credits": 3, "type": "major",    "completed": 0, "period":  8, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 24, "name": "WRTG 394",  "credits": 3, "type": "general",  "completed": 0, "period":  9, "session": 2, "prerequisite": "WRTG 112"                        }, 
    { "student_info_id": 10, "seq": 25, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  9, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 26, "name": "BMGT 380",  "credits": 3, "type": "major",    "completed": 0, "period": 10, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 27, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 10, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 28, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 11, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 29, "name": "HRMN 300",  "credits": 3, "type": "major",    "completed": 0, "period": 11, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 10, "seq": 30, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 11, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 31, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 12, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 32, "name": "FINC 330",  "credits": 3, "type": "major",    "completed": 0, "period": 12, "session": 1, "prerequisite": "ACCT 221 & STAT 200"             }, 
    { "student_info_id": 10, "seq": 33, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 12, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 34, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 13, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 35, "name": "BMGT 496",  "credits": 3, "type": "major",    "completed": 0, "period": 13, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 36, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 13, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 37, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 14, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 38, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 14, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 39, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 15, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 10, "seq": 40, "name": "BMGT 495",  "credits": 3, "type": "major",    "completed": 0, "period": 15, "session": 2, "prerequisite": "BMGT 365 & MRKT 310 & FINC 330"  }, 
    { "student_info_id": 10, "seq": 41, "name": "CAPSTONE",  "credits": 1, "type": "elective", "completed": 0, "period": 15, "session": 3, "prerequisite": "FINC 330"                        }, 
    { "student_info_id": 3, "seq":  0, "name": "STAT 200",  "credits": 3, "type": "required", "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  0, "name": "HUMN 100",  "credits": 3, "type": "general",  "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq":  0, "name": "ARTH 334",  "credits": 3, "type": "general",  "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  0, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq":  0, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq":  0, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq":  0, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq":  0, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq":  0, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq":  0, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq":  0, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 1, "period":  0, "session": 0, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq":  1, "name": "PACE 111B", "credits": 3, "type": "general",  "completed": 0, "period":  1, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  2, "name": "LIBS 150",  "credits": 1, "type": "general",  "completed": 0, "period":  1, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  3, "name": "WRTG 111",  "credits": 3, "type": "general",  "completed": 0, "period":  1, "session": 3, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  4, "name": "WRTG 112",  "credits": 3, "type": "general",  "completed": 0, "period":  2, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  5, "name": "NUTR 100",  "credits": 3, "type": "general",  "completed": 0, "period":  2, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  6, "name": "BMGT 110",  "credits": 3, "type": "major",    "completed": 0, "period":  3, "session": 3, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  7, "name": "SPCH 100",  "credits": 3, "type": "general",  "completed": 0, "period":  3, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  8, "name": "IFSM 300",  "credits": 3, "type": "required", "completed": 0, "period":  3, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 3, "seq":  9, "name": "ACCT 220",  "credits": 3, "type": "major",    "completed": 0, "period":  4, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 10, "name": "BIOL 103",  "credits": 4, "type": "general",  "completed": 0, "period":  4, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 11, "name": "ECON 201",  "credits": 3, "type": "required", "completed": 0, "period":  4, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 12, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  5, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 13, "name": "ECON 203",  "credits": 3, "type": "required", "completed": 0, "period":  5, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 14, "name": "ACCT 221",  "credits": 3, "type": "major",    "completed": 0, "period":  5, "session": 3, "prerequisite": "ACCT 220"                        }, 
    { "student_info_id": 3, "seq": 15, "name": "BMGT 364",  "credits": 3, "type": "major",    "completed": 0, "period":  6, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 16, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  6, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 17, "name": "BMGT 365",  "credits": 3, "type": "major",    "completed": 0, "period":  7, "session": 1, "prerequisite": "BMGT 364"                        }, 
    { "student_info_id": 3, "seq": 18, "name": "MRKT 310",  "credits": 3, "type": "major",    "completed": 0, "period":  7, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 19, "name": "WRTG 394",  "credits": 3, "type": "general",  "completed": 0, "period":  7, "session": 2, "prerequisite": "WRTG 112"                        }, 
    { "student_info_id": 3, "seq": 20, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  8, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 21, "name": "BMGT 380",  "credits": 3, "type": "major",    "completed": 0, "period":  8, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 22, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  8, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 23, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  9, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 24, "name": "HRMN 300",  "credits": 3, "type": "major",    "completed": 0, "period":  9, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 3, "seq": 25, "name": "FINC 330",  "credits": 3, "type": "major",    "completed": 0, "period":  9, "session": 3, "prerequisite": "ACCT 221 & STAT 200"             }, 
    { "student_info_id": 3, "seq": 26, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 10, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 27, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 11, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 28, "name": "BMGT 496",  "credits": 3, "type": "major",    "completed": 0, "period": 10, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 3, "seq": 29, "name": "BMGT 495",  "credits": 3, "type": "major",    "completed": 0, "period": 11, "session": 2, "prerequisite": "BMGT 365 & MRKT 310 & FINC 330"  }, 
    { "student_info_id": 3, "seq": 30, "name": "CAPSTONE",  "credits": 1, "type": "elective", "completed": 0, "period": 11, "session": 3, "prerequisite": "FINC 330"                        },    
    { "student_info_id": 1, "seq":  1, "name": "PACE 111B", "credits": 3, "type": "general",  "completed": 0, "period":  1, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 1, "seq":  2, "name": "LIBS 150",  "credits": 1, "type": "general",  "completed": 0, "period":  1, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 1, "seq":  3, "name": "WRTG 111",  "credits": 3, "type": "general",  "completed": 0, "period":  1, "session": 3, "prerequisite": ""                                },
    { "student_info_id": 1, "seq":  4, "name": "WRTG 112",  "credits": 3, "type": "general",  "completed": 0, "period":  2, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 1, "seq":  5, "name": "NUTR 100",  "credits": 3, "type": "general",  "completed": 0, "period":  2, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 1, "seq":  6, "name": "BMGT 110",  "credits": 3, "type": "major",    "completed": 0, "period":  3, "session": 3, "prerequisite": ""                                },
    { "student_info_id": 1, "seq":  7, "name": "SPCH 100",  "credits": 3, "type": "general",  "completed": 0, "period":  3, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 1, "seq":  8, "name": "STAT 200",  "credits": 3, "type": "required", "completed": 0, "period":  3, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 1, "seq":  9, "name": "IFSM 300",  "credits": 3, "type": "required", "completed": 0, "period":  4, "session": 1, "prerequisite": ""                                },
    { "student_info_id": 1, "seq": 10, "name": "ACCT 220",  "credits": 3, "type": "major",    "completed": 0, "period":  4, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 11, "name": "HUMN 100",  "credits": 3, "type": "general",  "completed": 0, "period":  4, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 12, "name": "BIOL 103",  "credits": 4, "type": "general",  "completed": 0, "period":  5, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 13, "name": "ECON 201",  "credits": 3, "type": "required", "completed": 0, "period":  5, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 14, "name": "ARTH 334",  "credits": 3, "type": "general",  "completed": 0, "period":  5, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 1, "seq": 15, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  6, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 16, "name": "ECON 203",  "credits": 3, "type": "required", "completed": 0, "period":  6, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 17, "name": "ACCT 221",  "credits": 3, "type": "major",    "completed": 0, "period":  7, "session": 1, "prerequisite": "ACCT 220"                        }, 
    { "student_info_id": 1, "seq": 18, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  7, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 19, "name": "BMGT 364",  "credits": 3, "type": "major",    "completed": 0, "period":  7, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 20, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  8, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 21, "name": "BMGT 365",  "credits": 3, "type": "major",    "completed": 0, "period":  8, "session": 1, "prerequisite": "BMGT 364"                        }, 
    { "student_info_id": 1, "seq": 22, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  9, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 23, "name": "MRKT 310",  "credits": 3, "type": "major",    "completed": 0, "period":  8, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 24, "name": "WRTG 394",  "credits": 3, "type": "general",  "completed": 0, "period":  9, "session": 2, "prerequisite": "WRTG 112"                        }, 
    { "student_info_id": 1, "seq": 25, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period":  9, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 26, "name": "BMGT 380",  "credits": 3, "type": "major",    "completed": 0, "period": 10, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 27, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 10, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 28, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 11, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 29, "name": "HRMN 300",  "credits": 3, "type": "major",    "completed": 0, "period": 11, "session": 2, "prerequisite": ""                                },
    { "student_info_id": 1, "seq": 30, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 11, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 31, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 12, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 32, "name": "FINC 330",  "credits": 3, "type": "major",    "completed": 0, "period": 12, "session": 1, "prerequisite": "ACCT 221 & STAT 200"             }, 
    { "student_info_id": 1, "seq": 33, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 12, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 34, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 13, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 35, "name": "BMGT 496",  "credits": 3, "type": "major",    "completed": 0, "period": 13, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 36, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 13, "session": 3, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 37, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 14, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 38, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 14, "session": 2, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 39, "name": "ELECTIVE",  "credits": 3, "type": "elective", "completed": 0, "period": 15, "session": 1, "prerequisite": ""                                }, 
    { "student_info_id": 1, "seq": 40, "name": "BMGT 495",  "credits": 3, "type": "major",    "completed": 0, "period": 15, "session": 2, "prerequisite": "BMGT 365 & MRKT 310 & FINC 330"  }, 
    { "student_info_id": 1, "seq": 41, "name": "CAPSTONE",  "credits": 1, "type": "elective", "completed": 0, "period": 15, "session": 3, "prerequisite": "FINC 330"                        }, 
]

drop_table('student_progress',c)
c.execute('''
    CREATE TABLE student_progress (
        id INTEGER PRIMARY KEY,
        student_info_id INTEGER,
        seq INTEGER,
        name TEXT,
        credits INTEGER,
        type TEXT,
        completed INTEGER,
        period INTEGER,
        session INTEGER,
        prerequisite TEXT,
        FOREIGN KEY(student_info_id) REFERENCES student_info(id)
    )
''')

c.executemany('''
    INSERT INTO student_progress (student_info_id, seq, name, credits, type, completed, period, session, prerequisite)
        VALUES (:student_info_id, :seq, :name, :credits, :type, :completed, :period, :session, :prerequisite)
    ''', student_progress)

conn.commit()

# Close the connection
conn.close()
