import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

################################################################
# "General Education Requirements" Table

drop_table('general_education_requirements',c)
c.execute('''
    CREATE TABLE general_education_requirements (
        id INTEGER PRIMARY KEY,
        requirement INTEGER,
        type TEXT,
        part TEXT DEFAULT '',
        description TEXT,
        credits INTEGER,
        note TEXT DEFAULT ''
    )
''')

################################################################
# "General Education" Table

drop_table('general_education',c)
c.execute('''
    CREATE TABLE general_education (
        id INTEGER PRIMARY KEY,
        general_education_requirements_id INTEGER,
        course_id INTEGER,
        name TEXT,
        note TEXT DEFAULT '',
        FOREIGN KEY(general_education_requirements_id) 
            REFERENCES general_education_requirements(id),        
        FOREIGN KEY(course_id) REFERENCES classes(id)
    )
''')

# General Education Requirement 1
## Communications: 12 credits
## 1. WRTG 111 or another writing course (3 credits)
##    (I am making the assumption that there are no prerequisites)

query = '''
    INSERT INTO general_education_requirements (id, requirement, type, part, description, credits)
    SELECT 1, 1, 'Communications', '1', 'WRTG 111 or another writing course', 3
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        1, id, name 
	FROM classes
	WHERE 
		credits = '3' 
		AND (
		    name LIKE 'WRTG 111'  
			OR name IN ('COMM 390', 'COMM 492','ENGL 102','JOUR 201')
		)
		AND name NOT IN ('WRTG 112', 'WRTG 288', 'WRTG 388','WRTG 486%')
'''
#        AND pre == ''
c.execute(query)

## 2. WRTG 112
## Must be completed within the first 24 credits

query = '''
    INSERT INTO general_education_requirements (id, requirement, type, part, description, credits, note)
    SELECT 2, 1, 'Communications', '2', 'WRTG 112', 3, 'Must be completed within the first 24 credits'
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        2, id, name 
	FROM classes
	WHERE 
        name = 'WRTG 112'
'''
c.execute(query)

## 3. A course in communication, writing, or speech
## 

query = '''
    INSERT INTO general_education_requirements (id, requirement, type, part, description, credits)
    SELECT 3, 1, 'Communications', '3', 'A course in communication, writing, or speech', 3
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        3, id, name 
	FROM classes
	WHERE 
		credits = '3' 
		AND (
            name IN ('ENGL 102', 'ENGL 281', 'JOUR 201')
			OR name LIKE 'COMM %'
            OR name LIKE 'SPCH %'
            OR name LIKE 'WRTG %'
		)
		AND name NOT LIKE '% 486A'
		AND name NOT LIKE '% 486B'
		AND name NOT LIKE 'WRTG 111'
		AND name NOT LIKE 'WRTG 112'
'''
c.execute(query)

## 4. An upper-level advanced writing course
## 
query = '''
    INSERT INTO general_education_requirements (id, requirement, type, part, description, credits)
    SELECT 4, 1, 'Communications', '4', 'An upper-level advanced writing course', 3
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        4, id, name 
	FROM classes
	WHERE 
		credits = '3' 
		AND 
            name IN ('WRTG 391', 'WRTG 393','WRTG 394')
;
'''
c.execute(query)

## Mathematics: 3 credits
## Must be completed within the first 24 credits
query = '''
    INSERT INTO general_education_requirements (id, requirement, type, description, credits, note)
    SELECT 5, 2, 'Mathematics', 'Mathematics', 3, 'Must be completed within the first 24 credits'
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        5, id, name 
	FROM classes
	WHERE 
		name IN ('MATH 105', 'MATH 107', 'MATH 115', 'MATH 140', 'STAT 200')
'''
c.execute(query)

## Arts and Humanities: 6 credits
## Two 3-credit courses

query = '''
    INSERT INTO general_education_requirements (id, requirement, type, description, credits, note)
    SELECT 6, 3, 'Arts and Humanities', 'Arts and Humanities', 6, 'Two 3-credit courses'
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        6, id, name 
	FROM classes
	WHERE 
		credits = '3' 
		AND (
 		       name LIKE 'ARTH %'
 			OR name LIKE 'ARTT %'
 			OR name LIKE 'ASTD %' 
 			OR name LIKE 'ENGL %' 
 			OR name LIKE 'GRCO %' 
 			OR name LIKE 'HIST %'
 			OR name LIKE 'HUMN %' 
 			OR name LIKE 'MUSC %' 
 			OR name LIKE 'PHIL %' 
 			OR name LIKE 'THET %' 
 			OR name IN (
                    'ENGL 250', 
                    'ENGL 303', 
                    'ENGL 310',
                    'ENGL 430', 
                    'ENGL 363', 
                    'ENGL 364',
                    'ENGL 433',
                    'ENGL 441',
                    'ENGL 311',
                    'ENGL 312',
                    'ENGL 386', 
                    'ENGL 406',
                    'ENGL 459',
                    'ENGL 495' 
               ) 
 			OR name LIKE 'ARAB 11_'
 			OR name LIKE 'CHIN 11_'
 			OR name LIKE 'FREN 11_'
 			OR name LIKE 'GERM %'
               OR name LIKE 'JAPN 11_' 
               OR name LIKE 'JAPN 22_'
 			OR name IN (
                    'SPAN 111', 
                    'SPAN 112', 
                    'SPAN 211',
                    'SPAN 212', 
                    'SPAN 311', 
                    'SPAN 314'               
               ) 
          )
          AND name NOT IN ('ENGL 281', 'ENGL 384')
'''
c.execute(query)

# 7.
## Biological and Physical Sciences
## 1a. A science course combining lecture and laboratory (4 credits)
## 1b. A science course combining lecture and laboratory for science majors and minors (4 credits)
## 1c. A science lecture course (3 credits) with related laboratory course (1 credit)

query = '''
    INSERT INTO general_education_requirements (id, requirement, type, part, description, credits, note)
    VALUES 
        (7, 4, 'Biological and Physical Sciences', '1a', 'Science lecture with laboratory', 4, 
            'A science course combining lecture and laboratory (4 credits)'),
        (8, 4, 'Biological and Physical Sciences', '1b', 'Science lecture with laboratory for science majors or minors', 4, 
            'A science course combining lecture and laboratory (4 credits)'),
        (9, 4, 'Biological and Physical Sciences', '1c', 'Science lecture with laboratory', 4, 
            'A science lecture course (3 credits) with related laboratory course (1 credit)')
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        7, id, name 
	FROM classes
	WHERE 
		name in (
            'BIOL 103', 
            'BIOL 230',
			'NSCI 103'
        )
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        8, id, name 
	FROM classes
	WHERE 
		name in (
            'CHEM 103', 
            'PHYS 121',
			'PHYS 122'
        )
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name, note)
    SELECT 
        9, id, name, 'Pair: BIOL 101 (3) & BIOL 102 (1)' 
	FROM classes
	WHERE 
		name in (
            'BIOL 101',
            'BIOL 102'
        )
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name, note)
    SELECT 
        9, id, name, 'Pair: BIOL 160 (3) & BIOL 161 (1)' 
	FROM classes
	WHERE 
		name in (
            'BIOL 160',
            'BIOL 161'
        )
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name, note)
    SELECT 
        9, id, name, 'Pair: NSCI 100 (3) & NSCI 101 (1)' 
	FROM classes
	WHERE 
		name in (
            'NSCI 100',
            'NSCI 101'
        )
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name, note)
    SELECT 
        9, id, name, 'Pair: NSCI 170 (3) & NSCI 171 (1)' 
	FROM classes
	WHERE 
		name IN (
            'NSCI 170',
            'NSCI 171'
        )
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name, note)
    SELECT 
        9, id, name, 'Pair: NUTR 100 (3) & NUTR 101 (1)' 
	FROM classes
	WHERE 
		name in (
            'NUTR 100',
            'NUTR 101'
        )
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name, note)
    SELECT 
        9, id, name, '' 
	FROM classes
	WHERE 
		name in (
            'NSCI 120'
        )
'''
c.execute(query)

## 2. Any other science course (3 credits)
## Courses from the following disciplines apply: ASTR, BIOL, CHEM, GEOL, NSCI, NUTR, or PHYS. 

query = '''
    INSERT INTO general_education_requirements (id, requirement, type, part, description, credits, note)
    SELECT 10, 4, 'Biological and Physical Sciences', '2', 'Any other science course', 3, 
        'Courses from the following disciplines apply: ASTR, BIOL, CHEM, GEOL, NSCI, NUTR, or PHYS.'
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        10, id, name 
	FROM classes
	WHERE 
		credits = '3' 
		AND (
 		       name LIKE 'ASTR %'
 			OR name LIKE 'BIOL %'
 			OR name LIKE 'CHEM %'
 			OR name LIKE 'GEOL %'
 			OR name LIKE 'NSCI %'
 			OR name LIKE 'NUTR %'
 			OR name LIKE 'PHYS %'
        )
'''
c.execute(query)

# 8.
## Behavioral and Social Sciences: 6 credits
## Two 3-credit hour courses from the following:

query = '''
    INSERT INTO general_education_requirements (id, requirement, type, description, credits, note)
    VALUES 
        (11, 5, 'Behavioral and Social Sciences', 'Behavioral and Social Sciences', 6, 'Two 3-credit hour courses') 
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        11, id, name 
	FROM classes
	WHERE 
		credits = '3' 
		AND (
            name IN ('AASP 201', 'CCJS 100', 'CCJS 105', 'CCJS 350', 'CCJS 360', 'CCJS 461', 'WMST 200')
 			OR name LIKE 'ANTH %'
 			OR name LIKE 'ASTD %'
 			OR name LIKE 'BEHS %' 
 			OR name LIKE 'ECON %' 
 			OR name LIKE 'GEOG %' 
 			OR name LIKE 'GERO %'
 			OR name LIKE 'GVPT %' 
 			OR name LIKE 'PSYC %' 
 			OR name LIKE 'SOCY %')
        AND name NOT IN ('GERO 342', 'GERO 351')
        AND name NOT LIKE '% 486A'
'''
c.execute(query)

## Research and Computing Literacy: 7 credits

## Professional exploration course (3 credits)
## PACE 111B, PACE 111C, PACE 111M, PACE 111P, PACE 111S, and PACE 111T apply. To be taken as the first course.

query = '''
    INSERT INTO general_education_requirements (id, requirement, type, part, description, credits, note)
    VALUES 
        (12, 6, 'Research and Computing Literacy', '1', 'Professional exploration course', 3, 
            'To be taken as the first course'),
        (13, 6, 'Research and Computing Literacy', '2', 'Research skills and professional development course', 1, 
            'LIBS 150, CAPL 398A, and any general education course apply'),
        (14, 6, 'Research and Computing Literacy', '3', 'Computing or information technology course', 3, 
            'One 3-credit course or three 1-credit courses')
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        12, id, name 
	FROM classes
	WHERE 
		credits = '3' 
		AND name LIKE 'PACE 111_'
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        13, id, name 
	FROM classes
	WHERE 
		credits = '1' 
		AND name IN ('LIBS 150', 'CAPL 398A')
'''
c.execute(query)

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, name)
    SELECT 
        14, id, name 
	FROM classes
	WHERE 
		credits IN ('1', '3') 
		AND (
            name IN ('DATA 200', 'IFSM 201')
 			OR name LIKE 'CMIT %'
 			OR name LIKE 'CMSC %'
 			OR name LIKE 'CMST %' 
 			OR name LIKE 'CSIA %' 
 			OR name LIKE 'IFSM %' 
 			OR name LIKE 'SDEV %')
        AND name NOT LIKE '% 486A'
'''
c.execute(query)
conn.commit()

################################################################
# "GE Defaults" Table
# Defaults for ge courses by program_id

ge_defaults = [
    { 'program_id':  2, 'ge': 'res_1', 'course': 'PACE 111B' },
    { 'program_id':  3, 'ge': 'res_1', 'course': 'PACE 111T' },
    { 'program_id':  4, 'ge': 'res_1', 'course': 'PACE 111T' },
    { 'program_id':  5, 'ge': 'res_1', 'course': 'PACE 111B' },
    { 'program_id':  6, 'ge': 'res_1', 'course': 'PACE 111C' },
    { 'program_id':  7, 'ge': 'res_1', 'course': 'PACE 111T' },
    { 'program_id':  8, 'ge': 'res_1', 'course': 'PACE 111P' },
    { 'program_id':  9, 'ge': 'res_1', 'course': 'PACE 111T' },
    { 'program_id': 10, 'ge': 'res_1', 'course': 'PACE 111T' },
    { 'program_id': 11, 'ge': 'res_1', 'course': 'PACE 111T' },
    { 'program_id': 12, 'ge': 'res_1', 'course': 'PACE 111C' },
    { 'program_id': 13, 'ge': 'res_1', 'course': 'PACE 111C' },
    { 'program_id': 14, 'ge': 'res_1', 'course': 'PACE 111S' },
    { 'program_id': 15, 'ge': 'res_1', 'course': 'PACE 111B' },
    { 'program_id': 16, 'ge': 'res_1', 'course': 'PACE 111M' },
    { 'program_id': 17, 'ge': 'res_1', 'course': 'PACE 111S' },
    { 'program_id': 18, 'ge': 'res_1', 'course': 'PACE 111C' },
    { 'program_id': 19, 'ge': 'res_1', 'course': 'PACE 111S' },
    { 'program_id': 20, 'ge': 'res_1', 'course': 'PACE 111C' },
    { 'program_id': 21, 'ge': 'res_1', 'course': 'PACE 111P' },
    { 'program_id': 22, 'ge': 'res_1', 'course': 'PACE 111B' },
    { 'program_id': 23, 'ge': 'res_1', 'course': 'PACE 111C' },
    { 'program_id': 25, 'ge': 'res_1', 'course': 'PACE 111P' },
    { 'program_id': 26, 'ge': 'res_1', 'course': 'PACE 111T' },
    { 'program_id': 27, 'ge': 'res_1', 'course': 'PACE 111B' },
    { 'program_id': 28, 'ge': 'res_1', 'course': 'PACE 111B' },
    { 'program_id': 30, 'ge': 'res_1', 'course': 'PACE 111C' },
    { 'program_id': 31, 'ge': 'res_1', 'course': 'PACE 111S' },
    { 'program_id': 32, 'ge': 'res_1', 'course': 'PACE 111P' },
    { 'program_id': 33, 'ge': 'res_1', 'course': 'PACE 111S' },
    { 'program_id': 34, 'ge': 'res_1', 'course': 'PACE 111T' },
    { 'program_id': 35, 'ge': 'res_1', 'course': 'PACE 111T' },
    { 'program_id':  2, 'ge': 'comm_4', 'course': 'WRTG 394' },
    { 'program_id':  3, 'ge': 'comm_4', 'course': 'WRTG 393' },
    { 'program_id':  4, 'ge': 'comm_4', 'course': 'WRTG 393' },
    { 'program_id':  5, 'ge': 'comm_4', 'course': 'WRTG 394' },
    { 'program_id':  6, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id':  7, 'ge': 'comm_4', 'course': 'WRTG 393' },
    { 'program_id':  8, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id':  9, 'ge': 'comm_4', 'course': 'WRTG 393' },
    { 'program_id': 10, 'ge': 'comm_4', 'course': 'WRTG 393' },
    { 'program_id': 11, 'ge': 'comm_4', 'course': 'WRTG 393' },
    { 'program_id': 12, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 13, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 14, 'ge': 'comm_4', 'course': 'WRTG 393' },
    { 'program_id': 15, 'ge': 'comm_4', 'course': 'WRTG 394' },
    { 'program_id': 17, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 18, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 19, 'ge': 'comm_4', 'course': 'WRTG 394' },
    { 'program_id': 20, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 21, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 22, 'ge': 'comm_4', 'course': 'WRTG 394' },
    { 'program_id': 23, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 25, 'ge': 'comm_4', 'course': 'WRTG 394' },
    { 'program_id': 26, 'ge': 'comm_4', 'course': 'WRTG 393' },
    { 'program_id': 27, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 28, 'ge': 'comm_4', 'course': 'WRTG 394' },
    { 'program_id': 30, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 31, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 32, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 33, 'ge': 'comm_4', 'course': 'WRTG 391' },
    { 'program_id': 34, 'ge': 'comm_4', 'course': 'WRTG 393' },
    { 'program_id': 35, 'ge': 'comm_4', 'course': 'WRTG 393' }
]

drop_table('ge_defaults',c)
c.execute('''
    CREATE TABLE ge_defaults (
        id INTEGER PRIMARY KEY,
        program_id INTEGER,
        ge TEXT,
        course TEXT,
        FOREIGN KEY(program_id) REFERENCES programs(id)
    )
''')

c.executemany('''
    INSERT INTO ge_defaults (program_id, ge, course)
        VALUES (:program_id, :ge, :course )
''', ge_defaults )
conn.commit()

# Close the connection
conn.close()