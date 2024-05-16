import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

## Taxonomy of Student progress tables/views
## 
## (1) student_history: courses completed (including transfer credits)
##     this is independent of chosen program, thus allowing students 
##     to change programs in the future
## (2) student_progress: student_history mapped into selected program 
##     requirements, thus includes completed classes and remaining 
##     coursework required for selected program and GE / elective credits.
##     Will eventually need methods to 
##      - create student_progress from student_history and program_id
##      - ?
## (3) student_schedule_view: student_progress + term/session information. 
##     These are the data that will be fed to D3 for display. 
##     - create_schedule method will take as input student_progress and 
##       output/update fields term, session, and locked
##     - 'locked' will prevent the optimization algorithm from moving that
##       course to another term or session.

##################################################################
# "Program Sequence" Table                                       #
#                                                                #
# program_sequence is now replaced with catalog_program_sequence #
##################################################################

#################################################################
# "Student History" Table                                       #
#                                                               #
# courses completed, including transfer credits                 #
#################################################################

## type mapping (e.g., major, ge, elective) should be done at the 
## student_progress table level, not in the history

drop_table('student_history', c)
c.execute('''
    CREATE TABLE student_history (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        course TEXT,
        credits INTEGER,
        transfer INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

conn.commit()

#################################################################
# "Student Progress" Table                                      #
#                                                               #
# student_history mapped into selected program.                 #
#################################################################

## Need a method to populate student_progress given program_id and 
## student_history
##  - type mapping (e.g., major, ge, elective) should be done at the 
##    student_progress table level, not in student_history
##  - need to update required to required/ge or required/elective?
##  - need to update prerequisites with pre and pre_credits
##  - note: term and session are initially NULL until updated prior 
##    to viewing with D3
##  I may have included more than I need here. We will see and perhaps 
##  make this a view instead of a table.

## bare minimum:
##   user_id
##   program_id
##   seq
##   course
##   course_type_id
##   completed
##   term
##   session
##   locked

## everything else in a view: student_progress_view

drop_table('student_progress', c)
c.execute('''
    CREATE TABLE student_progress (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        program_id INTEGER,
        seq INTEGER,
        course TEXT,
        credits INTEGER,
        course_type_id INTEGER,
        completed INTEGER DEFAULT 0,
        term INTEGER DEFAULT 0,
        session INTEGER DEFAULT 0,
        locked INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        FOREIGN KEY(program_id) REFERENCES users(id),          
        FOREIGN KEY(user_id) REFERENCES programs(id)
    )
''')
conn.commit()

## This is the old table that currently works with D3. Need to adapt tne new table a bit.

#drop_table('student_progress_d3', c)
#c.execute('''
#    CREATE TABLE student_progress_d3 (
#        id INTEGER PRIMARY KEY,
#        user_id INTEGER,
#        seq INTEGER,
#        name TEXT,
#        credits INTEGER,
#        course_type TEXT,
#        type TEXT,
#        completed INTEGER DEFAULT 0,
#        term INTEGER DEFAULT 0,
#        session INTEGER DEFAULT 0,
#        locked INTEGER DEFAULT 0,
#        prerequisites TEXT,
#        FOREIGN KEY(user_id) REFERENCES users(id)
#    )
#''')
#
#conn.commit()

#################################################################
# "Student Schedule" View                                       #
#                                                               #
# student_progress mapped into selected program.                #
# (for efficiency, this should be a view instead of a separate  #
#  table, with student_progress including period and session    #
#  fields, initially set to NULL)                               #
# The student_schedule_view would be fed into D3 for            #
# visualization                                                 #
#################################################################

# Close the connection
conn.close()
