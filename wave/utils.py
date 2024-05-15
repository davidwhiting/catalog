from h2o_wave import Q, ui
from typing import Optional, List

import logging
import warnings
import sqlite3
import asyncio
import time
import pandas as pd
import numpy as np

#import sys
#import traceback
#from h2o_wave import Q, ui, graphics as g
#import templates

#############################################################
####################  Initialize Functions ##################
#############################################################

## Note: moved initialize_app, initialize_user, initialize_client functions
## to app.py to avoid circular import references between utils.py and cards.py

######################################################################

def initialize_ge():
    '''
    Initialize General Education tracking for undergraduate students.
    '''
    ge = {
        'arts': {
            '1': None,
            '2': None
        },
        'beh': {
            '1': None,
            '2': None
        },
        'bio': {
            '1a': None,
            '1b': None,
            '1c': None,
            '2': None
        },
        'comm': {
            '1': 'WRTG 111',
            '2': 'WRTG 112',
            '3': None,
            '4': None
        },
        'math': None,
        'res': {
            '1': None,
            '2': 'LIBS 150',
            '3': None,
            '3a': None,
            '3b': None,
            '3c': None
        }
    }
    return ge

def initialize_student_info():
    '''
    Initialize new student information
    (This is not the same as populating from the database)
    '''
    student_info = {}
    # Initialize some attributes
    attributes = [        
        'user_id',
        'name', 
        'financial_aid', 
        'resident_status', 
        'student_profile', 
        'transfer_credits', 
        'app_stage', 
        'app_stage_id', 
        'first_term', 
        'program_id', 
        'degree_program'
    ]
    student_info.update({name: None for name in attributes})

    student_info['menu'] = {
        'degree': None,
        'area_of_study': None,
        'program': None
    }
    # 'required' used to be 'q.client.program_df'
    # 
    student_info['df'] = {
        'required': None,
        'periods': None,
        'schedule': None
    }
    
    return student_info

def reset_program(q):
    '''
    When program is changed, multiple variables need to be reset
    '''
    q.user.student_info['menu']['program'] = None
    q.user.student_info['program_id'] = None
    q.user.student_info['df']['required'] = None
    q.user.student_info['df']['schedule'] = None
    q.user.student_info['degree_program'] = None

    q.page['dropdown'].menu_program.value = None
    # reset program choices
    q.page['dropdown'].menu_program.choices = None


######################################################################
####################  STANDARD WAVE CARDS  ###########################
######################################################################

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card

# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)

######################################################################
####################  SQL-RELATED FUNCTIONS  #########################
######################################################################

class TimedSQLiteConnection:
    '''
    This class creates an SQLite connection that will disconnect after 
    'timeout' amount of inactivity. This is a lightweight way to manage 
    multiple sqlite connections without using a connection pool. It prepares
    for multiple users in Wave connecting to the same SQLite database.

    Methods include 
      - execute: executing commands (like create table), nothing returned
      - fetchone and fetchall use corresponding sqlite methods
      - fetchdict returns query results as a dictionary
      - fetchdf returns a Pandas DataFrame

    Notes: 
    (1) The async/await syntax here may not be needed yet, it defaults
        to synchronous. It is harmless and anticipates future improvements.
    '''
    def __init__(self, db_path, row_factory=True, timeout=1800):  # Default is 1800 seconds
        self.db_path = db_path
        self.timeout = timeout
        self.row_factory = row_factory # return dictionaries instead of tuples
        self.last_activity_time = time.time()  # Initialize last activity time
        self.connection = None

    async def _check_and_close(self):
        if self.connection is not None:
            current_time = time.time()
            if current_time - self.last_activity_time >= self.timeout:
                self.connection.close()
                self.connection = None

    async def _update_activity_time(self):
        self.last_activity_time = time.time()

    async def _get_cursor(self):
        '''
        Common code used in execute and fetch methods
        '''
        await self._check_and_close()
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            if self.row_factory:
                self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        return cursor

    async def execute(self, query, params=()):
        cursor = await self._get_cursor()
        cursor.execute(query, params)
        await self._update_activity_time()

    async def fetchone(self, query, params=()):
        cursor = await self._get_cursor()
        cursor.execute(query, params)
        await self._update_activity_time()

        return cursor.fetchone()

    async def fetchall(self, query, params=()):
        cursor = await self._get_cursor()
        cursor.execute(query, params)
        await self._update_activity_time()

        return cursor.fetchall()
    
    async def fetchdict(self, query, params=()):
        cursor = await self._get_cursor()
        cursor.execute(query, params)
        await self._update_activity_time()
    
        # Fetch column names
        column_names = [description[0] for description in cursor.description]    
        # Fetch all rows and convert each to a dictionary
        rows = cursor.fetchall()
        result = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            result.append(row_dict)

        return result

    async def fetchdf(self, query, params=()):
        cursor = await self._get_cursor()
        df = pd.read_sql_query(query, self.connection, params=params)
        await self._update_activity_time()

        return df

    async def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

async def get_query(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return all rows

    timedConnection: an instantiation of TimeSQLiteConnection
    query: SQL query
    params: Optional parameters
    '''
    rows = await timedConnection.fetchall(query, params)
    if not rows:
        warnings.warn("Query returned no rows", category=Warning)
        return None
    else:
        return rows

async def get_query_one(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a row

    timedConnection: an instantiation of TimeSQLiteConnection
    query: SQL query
    params: Optional parameters
    '''
    row = await timedConnection.fetchone(query, params)
    if not row:
        warnings.warn("Query returned no row", category=Warning)
        return None
    else:
        return row

async def get_query_dict(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a 
    dictionary of all rows

    timedConnection: an instantiation of TimeSQLiteConnection
    query: SQL query
    params: Optional parameters
    '''
    result = await timedConnection.fetchdict(query, params)
    if not result:
        warnings.warn("Query did not return a dictionary", category=Warning)
        return None
    else:
        return result

async def get_query_df(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a dataframe

    timedConnection: an instantiation of TimeSQLiteConnection
    query: SQL query
    params: Optional parameters
    '''
    try:
        df = await timedConnection.fetchdf(query, params)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # or return a specific value or message
    if df.empty:
        warnings.warn("Query returned zero rows", category=Warning)
        return None
    else:
        return df

######################################################################
#####################  QUERIES & FUNCTIONS  ##########################
######################################################################

async def get_program_title(timedConnection, program_id):
    query = '''
        SELECT b.id, b.name || ' in ' || a.name as title
        FROM programs a, degrees b 
        WHERE a.id = ? AND a.degree_id = b.id 
    '''
    row = await get_query_one(timedConnection, query, params=(program_id,))
    if row:
        return row
    else:
        return None

async def get_role(q):
    '''
    Get role given a user id
    '''
    timedConnection = q.user.conn
    query = '''
        SELECT 
		    a.role_id,
		    b.type AS role,
		    a.username, 
		    a.firstname || ' ' || a.lastname AS fullname
        FROM 
			users a, roles b
		WHERE 
			a.role_id=b.id AND a.id = ?
    '''
    row = await get_query_one(timedConnection, query, params=(q.user.user_id,))
    q.user.role_id = row['role_id']
    q.user.role = row['role']
    q.user.username = row['username']
    q.user.name = row['fullname']

async def populate_student_info(q, user_id):
    '''
    Get information from student_info table and populate the q.user.student_info parameters
    '''
    timedConnection = q.user.conn
    attributes = ['resident_status', 'app_stage_id', 'app_stage', 'student_profile', 'financial_aid', 
        'transfer_credits', 'program_id']
    query = 'SELECT * FROM student_info_view WHERE user_id = ?'
    row = await get_query_one(timedConnection, query, params=(user_id,))
    if row:
        q.user.student_info.update({name: row[name] for name in attributes})
        if q.user.student_info['program_id'] is not None:
            row = await get_program_title(timedConnection, q.user.student_info['program_id'])
            if row:
                q.user.student_info['degree_program'] = row['title']
                q.user.student_info['degree_id'] = row['id']
    
    # Recreate dropdown menus for students
    # Need to do this only if dropdown menu status was not saved
    # (We should save this status in the future)
    if q.user.student_info['program_id'] is not None:
        # recreate dropdown menu for program if empty
        if q.user.student_info['menu']['program'] is None:
            q.user.student_info['menu']['program'] = q.user.student_info['program_id']
        # recreate dropdowns for degree and area_of_study if either is empty
        if (q.user.student_info['menu']['degree'] is None) or (q.user.student_info['menu']['area_of_study'] is None):
            query = '''
                SELECT menu_degree_id, menu_area_id 
                FROM menu_all_view
                WHERE program_id = ?
                LIMIT 1
            '''
            # limit 1 because there is not a strict 1:1 correspondence between study areas and programs
            row = await get_query_one(q.user.conn, query, params=(q.user.student_info['program_id'],))
            if row:
                q.user.student_info['menu']['degree'] = row['menu_degree_id']
                q.user.student_info['menu']['area_of_study'] = row['menu_area_id']

async def get_ge_choices(conn, query, params=()):
    rows = await get_query(conn, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['name'] + ': ' + row['title']) for row in rows]
    return choices

async def get_catalog_program_sequence(q):
    query = 'SELECT * FROM catalog_program_sequence_view WHERE program_id = ?'
    df = await get_query_df(q.user.conn, query, params=(q.user.student_info['program_id'],))
    return df

async def get_student_progress_d3(q):
    query = 'SELECT * FROM student_progress_d3_view WHERE user_id = ?'
    df = await get_query_df(q.user.conn, query, params=(q.user.student_info['user_id'],))
    return df

async def get_choices(timedConnection, query, params=()):
    rows = await get_query(timedConnection, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label']) for row in rows]
    return choices

async def get_choices_with_disabled(timedConnection, query, params=()):
    '''
    Note: consolidate with get_choices to add a disabled={} option
    '''
    disabled_items = {
        'Cybersecurity Technology',
        'Social Science',
        'Applied Technology',
        'Web and Digital Design',        
        'East Asian Studies',
        'English',
        'General Studies',
        'History'
    }
    rows = await get_query(timedConnection, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label'], \
        disabled=(str(row['label']) in disabled_items)) for row in rows]
    return choices

######################################################################
#################  EVENT AND HANDLER FUNCTIONS  ######################
######################################################################

async def recommend_a_major(q, choice):
    '''
    Placeholder for the render_major_recommendation_card event
    '''
    def _to_be_implemented(q, label, box='3 6 5 1', type='info'):
        message = label + ' has not been implemented yet'
        q.page['info'] = ui.form_card(box=box, items=[
            ui.message_bar(type='warning', text=message)
        ]) 
    if choice == 'A':
        label = 'Recommendation engine for "My interests"'
    elif choice == 'B':
        label = 'Recommendation engine for "My skills"'
    elif choice == 'C':
        label = 'Recommendation engine for "Students like me"'
    else: 
        label = '"Shortest time to graduate" function'
    # 
    # Need to add a dismiss function
    _to_be_implemented(q, label)

######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################

def generate_periods(start_term='SPRING 2024', years=8, max_courses=3, max_credits=15, summer=False, sessions=[1,3], as_df=True):
    '''
    A periods structure is a list of dictionaries (or a Pandas dataframe) containing information about terms and sessions,
    into which we will place classes when scheduling.

    Parameters:

    start_term: first term classes are to be scheduled into
    years: number of years to create periods for (this can be larger than needed)
    max_courses: maximum number of courses per session
    max_credits: maximum number of credits per term
    summer: whether attending summer (as default)
    sessions: which sessions (1-3) to schedule classes in (excluding summer term, which has only sessions 1 & 2)
    as_df: return results as Pandas dataframe, otherwise return as list of dictionaries

    Output includes 'previous', a value used to determine placement of prerequisites. Because Sessions 1 & 2 and 
    Sessions 2 & 3 overlap, a Session 2 class cannot have a Session 1 prerequisite, it's previous value is 2 (two
    time-slots previous). Similarly, Session 3 cannot have a Session 2 prerequisite, it's previous value is also 2.
    For all others, the 'previous' value is 1.
    
    Note: We create all terms a student could potentially attend and set max_courses=0 and max_credits=0 for periods they
    are not attending.
    '''
    
    # List terms
    terms = ['WINTER', 'SPRING', 'SUMMER', 'FALL']

    # Define the number of sessions for each term
    sessions_per_term = {
        'WINTER': 3,
        'SPRING': 3,
        'SUMMER': 2,
        'FALL': 3
    }

    # Split the start term into the term and the year
    start_term, start_year = start_term.split()

    # Convert the start year to an integer
    start_year = int(start_year)

    # Initialize the schedule and the id
    schedule = []
    id = 1

    # Loop over the next 'years' years
    for year in range(start_year, start_year + years):
        # Loop over each term
        for term in terms:
            # If the year is the start year and the term is before the start term, skip it
            if year == start_year and terms.index(term) < terms.index(start_term):
                continue
            # Loop over each session
            for session in range(1, sessions_per_term[term] + 1):
                # Set max_courses=0 and max_credits=0 if (term='SUMMER' and summer==False)
                if term=='SUMMER': 
                    if not summer:
                        max_courses_value = 0
                        max_credits_value = 0
                    else:
                        max_courses_value = max_courses
                        # only 2 sessions in summer, adjust max_credits accordingly
                        max_credits_value = 2*int(np.floor(max_credits/3))
                
                # Set max_courses=0 and max_credits=0 if session not in sessions
                else:
                    if session not in sessions:
                        max_courses_value = 0
                        max_credits_value = 0
                    else: # spring, fall, winter
                        max_courses_value = max_courses
                        max_credits_value = max_credits
                       
                # Calculate previous value
                # 
                previous = 1 if session == 1 else 2
 
                # Add the entry to the schedule
                schedule.append({
                    'id': id,
                    'term': term,
                    'session': session,
                    'year': year,
                    'max_courses': max_courses_value,
                    'max_credits': max_credits_value,
                    'previous': previous
                })
                # Increment the id
                id += 1
    # either return as a dataframe or as a list of dictionaries
    if as_df:
        return pd.DataFrame(schedule)
    else:
        return schedule

def update_periods(periods, condition, update_values):
    '''
    Update the 'periods' structure. Will return a DataFrame if a DataFrame is input,
    otherwise will return a list of dictionaries.

    periods: a list of dictionaries or a DataFrame with periods information returned from 'generate_periods'

    Example usage
    # Update max_courses for SPRING 2024 to 0
    update_periods(periods, "term == 'SPRING' and year == 2024", {"max_courses": 0})
    '''

    # Check whether input periods is a DataFrame
    if isinstance(periods, pd.DataFrame):
        return_as_list = False
    else:
        periods = pd.DataFrame(periods)
        return_as_list = True
    
    # Apply conditions
    mask = periods.eval(condition)
    
    # Update values
    for key, value in update_values.items():
        periods.loc[mask, key] = value

    # Convert DataFrame back to a list of dictionaries
    if return_as_list:
        return periods.to_dict(orient='records')
    else:
        return periods

# note: renamed 'prerequisite' to 'prerequisites' to follow changes in the db table

def prepare_d3_data(df, start_term='SPRING 2024'):
    green = '#3b8132'
    blue = '#135f96'
    red = '#a30606'
    yellow = '#fdbf38'
    def set_colors(row):
        if row['type'] == 'general':
            return pd.Series([green, 'white'])
        elif row['type'] == 'major':
            return pd.Series([blue, 'white'])
        # hack: fix the following 3 elifs
        elif row['type'] == 'required,elective':
            row['type'] = 'required'
            return pd.Series([red, 'white'])
        elif row['type'] == 'required,general':
            row['type'] = 'required'
            return pd.Series([red, 'white'])
        elif row['type'] == 'required':
            return pd.Series([red, 'white'])
        elif row['type'] == 'elective':
            return pd.Series([yellow, 'black'])
        else:
            return pd.Series(['white', 'black'])  # default colors

    def generate_header_data(start_semester, num_periods, data_df = df):
        seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
        semester_data = []
        start_season, start_year = start_semester.split(' ')
        start_year = int(start_year)
        season_index = seasons.index(start_season)
        year = start_year
        period = 0

        while period < num_periods:
            for j in range(season_index, len(seasons)):
                semester_data.append(f'{seasons[j]} {year}')
                period += 1

                # Break the loop when i equals num_periods
                if period == num_periods:
                    break

            # Reset the season index to start from 'WINTER' for the next year
            season_index = 0
            year += 1

        df = pd.DataFrame(semester_data, columns=['term'])
        df['width'] = df['term'].apply(lambda x: 190 if 'SUMMER' in x else 260)
        df['offset'] = df['term'].apply(lambda x: 2 if 'SUMMER' in x else 3)
        df['fontsize'] = '14px'
        df['description'] = ''
        df['space'] = 40
        df['xpos'] = df['width'] + df['space']

        x0 = 10
        # Calculate the cumulative sum of 'xpos'
        df['x'] = df['xpos'].cumsum()
        df['x'] = df['x'].shift(1)
        df.loc[0, 'x'] = 0
        df['x'] = df['x'] + x0
        df['y'] = 10
        df['color'] = 'lightgray'
        df['textcolor'] = 'black'
        df['period'] = np.arange(1, num_periods+1)

        df.drop
        # Sum credits per period and convert to a DataFrame
        total_credits = data_df.groupby('period')['credits'].sum().sort_index()
        total_credits_df = total_credits.reset_index()

        df = pd.merge(df, total_credits_df, on='period', how='inner')
        df['name'] = df['term']
        df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'

        return df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 
                   'fontsize', 'period', 'name', 'credits', 'description']]

    # Prepare data for the D3 figure

    max_period = max(df['period'])
    headers = generate_header_data(start_term, max_period)

    df['description'] = df['prerequisites']
    df['width'] = 120
    # Calculate 'x' column
    df = pd.merge(df, headers[['period','x']], on='period', how='left')
    df['x'] += 70*(df['session']-1)

    # Calculate 'y' column
    df = df.sort_values(by=['period', 'session', 'seq' ])
    df['y_row'] = df.groupby('period').cumcount() + 1
    df['y'] = 70 + 45 * (df['y_row'] - 1)

    # Create rectangle colors
    df[['color', 'textcolor']] = df.apply(set_colors, axis=1)

    # Set text offset multiplier to 1 and text fontsize
    df['offset'] = 1
    df['fontsize'] = '12px'
    df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'
    
    df = df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 'fontsize', 'period', 'session', 'type', 'name', 'credits', 'description']]

    return df, headers

def generate_schedule(course_list, periods):
    schedule = []
    max_credits_by_term_year = {}
    
    # Iterate over locked courses to update periods and max_credits_by_term_year
    for course in course_list:
        if course.get('locked', False):
            term_year = (course['term'], course['year'])
            session = course['session']
            
            # Find the corresponding period
            for period in periods:
                if (period['term'], period['year'], period['session']) == (course['term'], course['year'], course['session']):
                    if period['max_courses_remaining'] > 0:
                        period['max_courses_remaining'] -= 1
                        
                        # Update max_credits_by_term_year
                        if term_year not in max_credits_by_term_year:
                            max_credits_by_term_year[term_year] = period['max_credits']
                        else:
                            max_credits_by_term_year[term_year] -= course['credits']
                        
                        # Add the locked course to the schedule
                        schedule.append({
                            'seq': len(schedule) + 1,
                            'course': course['name'],
                            'term': course['term'],
                            'year': course['year'],
                            'session': course['session'],
                            'locked': True
                        })
                        
                    else:
                        print(f"Unable to assign locked course '{course['name']}' to period {period}.")
                    break  # Exit the inner loop once the corresponding period is found
    
    # Iterate over unlocked courses to schedule them
    for course in course_list:
        if not course.get('locked', False):
            assigned = False
            
            # Iterate over periods to find an appropriate slot
            for period in periods:
                term_year = (period['term'], period['year'])
                
                if period['max_courses_remaining'] > 0 and max_credits_by_term_year[term_year] >= course['credits']:
                    # Add the course to the schedule
                    schedule.append({
                        'seq': len(schedule) + 1,
                        'course': course['name'],
                        'term': period['term'],
                        'year': period['year'],
                        'session': period['session'],
                        'locked': False
                    })
                    
                    # Update period information
                    period['max_courses_remaining'] -= 1
                    max_credits_by_term_year[term_year] -= course['credits']
                    
                    assigned = True
                    break  # Exit the inner loop once a slot is found
            
            if not assigned:
                print(f"Unable to assign unlocked course '{course['name']}' to any period.")
    
    return schedule

def handle_prerequisites(course_list):
    # Create a dictionary to store courses by their name for easy lookup
    courses_dict = {course['name']: course for course in course_list}
    
    # Iterate over the course list to handle prerequisites
    for course in course_list:
        # Check if the course has prerequisites
        if course.get('pre', ''):
            # Split the prerequisites string into individual courses
            prerequisites = course['pre'].split('&')
            
            # Iterate over the prerequisites
            for prereq_group in prerequisites:
                prereq_group = prereq_group.strip()
                
                # Split the prerequisites group into individual prerequisites
                prereqs = prereq_group.split('|')
                
                # Initialize a list to store prerequisite information for each branch
                branch_prereqs_info = []
                
                # Iterate over the prerequisites in the group
                for prereq_name in prereqs:
                    prereq_name = prereq_name.strip()
                    
                    # Check if the prerequisite is not already in the course list
                    if prereq_name not in courses_dict:
                        # Call update_prerequisites function to get information for the prerequisite
                        prereq_info = update_prerequisites(prereq_name)
                        
                        # Add the prerequisite to the branch_prereqs_info list
                        if prereq_info:
                            branch_prereqs_info.append(prereq_info)
                    else:
                        # If the prerequisite is already in the course list, find its index
                        prereq_index = course_list.index(courses_dict[prereq_name])
                        
                        # Add the prerequisite information to the branch_prereqs_info list
                        branch_prereqs_info.append(course_list[prereq_index])
                
                # Insert the branch_prereqs_info into the course_list before the current course
                if branch_prereqs_info:
                    course_list.insert(course_list.index(course), branch_prereqs_info)
    
    return course_list

## Need to update this

def schedule_courses_old(courses, periods, max_courses_default, max_credits_default):
    scheduled_courses = []

    for course in courses:
        while True:
            prerequisites_scheduled = all(pre_course.id in scheduled_courses for pre_course in course.pre)

            if prerequisites_scheduled:
                period_index = find_period_index(course, periods, scheduled_courses)

                if period_index is not None:
                    periods[period_index]['courses'].append(course)
                    scheduled_courses.append(course.id)
                    break
                else:
                    # Add a new period with default values and try scheduling again
                    previous_id = periods[-1]['id'] if periods else 0
                    new_period = {"id": previous_id + 1,
                                  "max_courses": max_courses_default,
                                  "max_credits": max_credits_default,
                                  "previous": previous_id,
                                  "courses": []}
                    periods.append(new_period)

            else:
                # Iterate through prerequisites first
                for pre_course in course.pre:
                    if pre_course.id not in scheduled_courses:
                        # Schedule the prerequisite course first
                        schedule_courses([pre_course], periods, max_courses_default, max_credits_default)
                
                # After scheduling prerequisites, retry scheduling the current course
                continue

    return periods

def update_courses(course, new_period, previous_period, courses, periods, max_courses_default, max_credits_default):
    # Remove the course from its previous period
    previous_period_index = previous_period - 1
    if course in periods[previous_period_index]['courses']:
        periods[previous_period_index]['courses'].remove(course)
    
    # Try to schedule the course in the new period
    new_period_index = new_period - 1
    scheduled_courses = []
    while True:
        prerequisites_scheduled = all(pre_course.id in scheduled_courses for pre_course in course.pre)

        if prerequisites_scheduled:
            if sum(course.credits for course in periods[new_period_index]['courses']) + course.credits <= periods[new_period_index]['max_credits']:
                if all(pre_course.id in scheduled_courses and
                        scheduled_courses.index(pre_course.id) <= periods[new_period_index]['previous']
                        for pre_course in course.pre):
                    periods[new_period_index]['courses'].append(course)
                    scheduled_courses.append(course.id)
                    break
                else:
                    # Move the course to the earliest possible period based on prerequisites
                    earliest_period = max(pre_course.id in scheduled_courses and
                                          scheduled_courses.index(pre_course.id) + 1
                                          for pre_course in course.pre)
                    print(f"Cannot move to period {new_period}: Prerequisites not met. Moving to period {earliest_period} instead.")
                    update_courses(course, earliest_period, new_period, courses, periods, max_courses_default, max_credits_default)
                    return
            else:
                print(f"Cannot move to period {new_period}: Max credits exceeded. Moving other courses forward.")
                move_courses_forward(new_period_index, periods, scheduled_courses)
                continue
        else:
            print(f"Cannot move to period {new_period}: Prerequisites not met.")
            return

    # Cascade changes from the new period onwards
    for i in range(new_period_index + 1, len(periods)):
        for scheduled_course in periods[i]['courses']:
            update_courses(scheduled_course, i + 1, i, courses, periods, max_courses_default, max_credits_default)

    return periods

def move_courses_forward(period_index, periods, scheduled_courses):
    # Find courses in the current period that can be moved forward
    movable_courses = [course for course in periods[period_index]['courses'] if
                       not any(course.id in pre_course.id for pre_course in scheduled_courses)]

    if not movable_courses:
        # If all courses are prerequisites for other courses, move the last one forward
        movable_courses = [periods[period_index]['courses'][-1]]

    # Move the first movable course forward to the next period
    if movable_courses:
        course_to_move = movable_courses[0]
        next_period_index = period_index + 1
        if next_period_index < len(periods):
            periods[next_period_index]['courses'].append(course_to_move)
            scheduled_courses.append(course_to_move.id)
            periods[period_index]['courses'].remove(course_to_move)
            print(f"Moved {course_to_move.name} forward to period {next_period_index + 1}.")
            # Recursively check if more courses can be moved forward
            move_courses_forward(period_index + 1, periods, scheduled_courses)
    else:
        print("No movable courses found.")

    return

    #############################################################################
    ## keycloak implementation code found in utils.py goes here after updating ##
    #############################################################################
    
    ##keycloak_implemented = False
    ###### KEYCLOAK CODE ##############
    ## temporary until keycloak login fully implemented
    ##    if keycloak_implemented:
    ##        #Decode the access token without verifying the signature
    ##        #Connects SSO to our user and student_info tables
    ##        user_details = jwt.decode(q.auth.access_token, options={"verify_signature": False})
    ##
    ##        q.user.username = user_details['preferred_username']
    ##        q.user.name = user_details['name']
    ##        q.user.firstname = user_details['given_name']
    ##        q.user.lastname = user_details['family_name']
    ##
    ## check whether user is in the sqlite3 db
    ## if so, get role and id
    ## if not, add user to db as a new student
    ##        q.user.user_id, q.user.role_id = find_or_add_user(q)
    ##    else:
    ##        # fake it for now
