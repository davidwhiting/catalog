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
        student_info_id INTEGER,
        name TEXT,
        credits INTEGER,
        transfer INTEGER,
        FOREIGN KEY(student_info_id) REFERENCES student_info(id)
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

drop_table('student_progress', c)
c.execute('''
    CREATE TABLE student_progress (
        id INTEGER PRIMARY KEY,
        student_info_id INTEGER,
        seq INTEGER,
        name TEXT,
        credits INTEGER,
        type TEXT,
        completed INTEGER DEFAULT 0,
        term INTEGER DEFAULT 0,
        session INTEGER DEFAULT 0,
        locked INTEGER DEFAULT 0,
        prerequisites TEXT,
        pre TEXT DEFAULT NULL,
        pre_credits TEXT DEFAULT NULL,
        FOREIGN KEY(student_info_id) REFERENCES student_info(id)
    )
''')

conn.commit()

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
