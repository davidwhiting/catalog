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
        abbr TEXT,
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
        course TEXT,
        note TEXT DEFAULT '',
        FOREIGN KEY(general_education_requirements_id) 
            REFERENCES general_education_requirements(id),        
        FOREIGN KEY(course_id) REFERENCES courses(id)
    )
''')

ge_req_query = '''
    INSERT INTO general_education_requirements (id, requirement, type, abbr, part, description, credits, note)
    SELECT ?, ?, ?, ?, ?, ?, ?, ?
'''

# General Education Requirement 1
## Communications: 12 credits

type = 'Communications'
abbr = 'comm'
req = 1

## 1. WRTG 111 or another writing course (3 credits)
##    (I am making the assumption that there are no prerequisites)

id = 1
part = '1'
description = 'WRTG 111 or another writing course'
credits = 3
note = ''
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

# Check whether 'COMM 390', 'COMM 492' really are ok substitutes for 'WRTG 111'.
# Seems odd.
query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		credits = '3' 
		AND (
		    course LIKE 'WRTG 111'  
			OR course IN ('ENGL 102','JOUR 201')
		)
		AND course NOT IN ('WRTG 112', 'WRTG 288', 'WRTG 388','WRTG 486%')
'''
#        AND pre == ''
c.execute(query, (id,))

## 2. WRTG 112
## Must be completed within the first 24 credits

id = 2
part = '2'
description = 'WRTG 112'
credits = 3
note = 'Must be completed within the first 24 credits'
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
        course = 'WRTG 112'
'''
c.execute(query, (id,))

## 3. A course in communication, writing, or speech
## 
id = 3
part = '3'
description = 'A course in communication, writing, or speech'
credits = 3
note = ''
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		credits = '3' 
		AND (
            course IN ('ENGL 102', 'ENGL 281', 'JOUR 201')
			OR course LIKE 'COMM %'
            OR course LIKE 'SPCH %'
            OR course LIKE 'WRTG %'
		)
		AND course NOT LIKE '% 486A'
		AND course NOT LIKE '% 486B'
		AND course NOT LIKE 'WRTG 111'
		AND course NOT LIKE 'WRTG 112'
'''
c.execute(query, (id,))

## 4. An upper-level advanced writing course
## 
query = '''
    INSERT INTO general_education_requirements (id, requirement, type, part, description, credits)
    SELECT 4, 1, 'Communications', '4', '', 3
'''
id = 4
part = '4'
description = 'An upper-level advanced writing course'
credits = 3
note = ''
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		credits = '3' 
		AND 
            course IN ('WRTG 391', 'WRTG 393','WRTG 394')
;
'''
c.execute(query, (id,))

## Mathematics: 3 credits
## Must be completed within the first 24 credits
type = 'Mathematics'
abbr = 'math'
req = 2

id = 5
part = '1'
description = type
credits = 3
note = 'Must be completed within the first 24 credits'
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		course IN ('MATH 105', 'MATH 107', 'MATH 115', 'MATH 140', 'STAT 200')
'''
c.execute(query, (id,))

## Arts and Humanities: 6 credits
type = 'Arts and Humanities'
abbr = 'arts'
req = 3

## Course 1
id = 6
part = '1'
description = type
credits = 3
note = ''
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		credits = '3' 
		AND (
 		       course LIKE 'ARTH %'
 			OR course LIKE 'ARTT %'
 			OR course LIKE 'ASTD %' 
 			OR course LIKE 'ENGL %' 
 			OR course LIKE 'GRCO %' 
 			OR course LIKE 'HIST %'
 			OR course LIKE 'HUMN %' 
 			OR course LIKE 'MUSC %' 
 			OR course LIKE 'PHIL %' 
 			OR course LIKE 'THET %' 
 			OR course IN (
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
 			OR course LIKE 'ARAB 11_'
 			OR course LIKE 'CHIN 11_'
 			OR course LIKE 'FREN 11_'
 			OR course LIKE 'GERM %'
               OR course LIKE 'JAPN 11_' 
               OR course LIKE 'JAPN 22_'
 			OR course IN (
                    'SPAN 111', 
                    'SPAN 112', 
                    'SPAN 211',
                    'SPAN 212', 
                    'SPAN 311', 
                    'SPAN 314'               
               ) 
          )
          AND course NOT IN ('ENGL 281', 'ENGL 384')
'''
c.execute(query, (id,))

## Course 2
id = 7
part = '2'
description = type
credits = 3
note = ''
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

c.execute(query, (id,))

# 8.
## Biological and Physical Sciences
## 1a. A science course combining lecture and laboratory (4 credits)
type = 'Biological and Physical Sciences'
abbr = 'bio'
req = 4

id = 8
part = '1a'
description = 'Science lecture with laboratory'
credits = 4
note = 'A science course combining lecture and laboratory (4 credits)'
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		course in (
            'BIOL 103', 
            'BIOL 230',
			'NSCI 103'
        )
'''
c.execute(query, (id,))

## 1b. A science course combining lecture and laboratory for science majors and minors (4 credits)

id = 9
part = '1b'
description = 'Science lecture with laboratory for science majors or minors'
credits = 4
note = 'A science course combining lecture and laboratory (4 credits)'
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		course in (
            'CHEM 103', 
            'PHYS 121',
			'PHYS 122'
        )
'''
c.execute(query, (id,))

## 1c. A science lecture course (3 credits) with related laboratory course (1 credit)

id = 10
part = '1c'
description = 'Science lecture with laboratory'
credits = 4
note = 'A science lecture course (3 credits) with related laboratory course (1 credit)'
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query1 = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course, note)
    SELECT 
        ?, id, course, 'Pair: BIOL 101 (3) & BIOL 102 (1)' 
	FROM courses
	WHERE 
		course in (
            'BIOL 101',
            'BIOL 102'
        )
'''

query2 = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course, note)
    SELECT 
        ?, id, course, 'Pair: BIOL 160 (3) & BIOL 161 (1)' 
	FROM courses
	WHERE 
		course in (
            'BIOL 160',
            'BIOL 161'
        )
'''

query3 = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course, note)
    SELECT 
        ?, id, course, 'Pair: NSCI 100 (3) & NSCI 101 (1)' 
	FROM courses
	WHERE 
		course in (
            'NSCI 100',
            'NSCI 101'
        )
'''

query4 = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course, note)
    SELECT 
        ?, id, course, 'Pair: NSCI 170 (3) & NSCI 171 (1)' 
	FROM courses
	WHERE 
		course IN (
            'NSCI 170',
            'NSCI 171'
        )
'''

query5 = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course, note)
    SELECT 
        ?, id, course, 'Pair: NUTR 100 (3) & NUTR 101 (1)' 
	FROM courses
	WHERE 
		course in (
            'NUTR 100',
            'NUTR 101'
        )
'''

query6 = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course, note)
    SELECT 
        ?, id, course, '' 
	FROM courses
	WHERE 
		course in (
            'NSCI 120'
        )
'''

c.execute(query1, (id,))
c.execute(query2, (id,))
c.execute(query3, (id,))
c.execute(query4, (id,))
c.execute(query5, (id,))
c.execute(query6, (id,))

## 2. Any other science course (3 credits)
## Courses from the following disciplines apply: ASTR, BIOL, CHEM, GEOL, NSCI, NUTR, or PHYS. 

id = 11
part = '2'
description = 'Any other science course'
credits = 3
note = 'Courses from the following disciplines apply: ASTR, BIOL, CHEM, GEOL, NSCI, NUTR, or PHYS.'
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		credits = '3' 
		AND (
 		       course LIKE 'ASTR %'
 			OR course LIKE 'BIOL %'
 			OR course LIKE 'CHEM %'
 			OR course LIKE 'GEOL %'
 			OR course LIKE 'NSCI %'
 			OR course LIKE 'NUTR %'
 			OR course LIKE 'PHYS %'
        )
'''
c.execute(query, (id,))

# 8.
## Behavioral and Social Sciences: 6 credits
## Two 3-credit hour courses 
type = 'Behavioral and Social Sciences'
abbr = 'beh'
req = 5

# Course 1
id = 12
part = '1'
description = type
credits = 3
note = ''
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		credits = '3' 
		AND (
            course IN ('AASP 201', 'CCJS 100', 'CCJS 105', 'CCJS 350', 'CCJS 360', 'CCJS 461', 'WMST 200')
 			OR course LIKE 'ANTH %'
 			OR course LIKE 'ASTD %'
 			OR course LIKE 'BEHS %' 
 			OR course LIKE 'ECON %' 
 			OR course LIKE 'GEOG %' 
 			OR course LIKE 'GERO %'
 			OR course LIKE 'GVPT %' 
 			OR course LIKE 'PSYC %' 
 			OR course LIKE 'SOCY %')
        AND course NOT IN ('GERO 342', 'GERO 351')
        AND course NOT LIKE '% 486A'
'''
c.execute(query, (id,))

# Course 2
id = 13
part = '2'
description = type
credits = 3
note = ''
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

c.execute(query, (id,))


## Research and Computing Literacy: 7 credits
type = 'Research and Computing Literacy'
abbr = 'res'
req = 6

## 1. Professional exploration course (3 credits)
## PACE 111B, PACE 111C, PACE 111M, PACE 111P, PACE 111S, and PACE 111T apply. To be taken as the first course.

id = 14
part = '1'
description = 'Professional exploration course'
credits = 3
note = 'To be taken as the first course'
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		credits = '3' 
		AND course LIKE 'PACE 111_'
'''
c.execute(query, (id,))

## 2. Research skills and professional development course
id = 15
part = '2'
description = 'Research skills and professional development course'
credits = 1
note = 'LIBS 150, CAPL 398A, and any general education course apply'
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		credits = '1' 
		AND course IN ('LIBS 150', 'CAPL 398A')
'''
c.execute(query, (id,))

## 3. Computing or information technology course
id = 16
part = '3'
description = 'Computing or information technology course'
credits = 3
note = 'One 3-credit course or three 1-credit courses'
c.execute(ge_req_query, (id, req, type, abbr, part, description, credits, note))

query = '''
INSERT INTO general_education (general_education_requirements_id, course_id, course)
    SELECT 
        ?, id, course 
	FROM courses
	WHERE 
		credits IN ('1', '3') 
		AND (
            course IN ('DATA 200', 'IFSM 201')
 			OR course LIKE 'CMIT %'
 			OR course LIKE 'CMSC %'
 			OR course LIKE 'CMST %' 
 			OR course LIKE 'CSIA %' 
 			OR course LIKE 'IFSM %' 
 			OR course LIKE 'SDEV %')
        AND course NOT LIKE '% 486A'
'''
c.execute(query, (id,))

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