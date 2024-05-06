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
#import pandas as pd
#import numpy as np


class TimedSQLiteConnection:
    '''
    This class creates an SQLite connection that will disconnect after 
    'timeout' amount of inactivity. This is a lightweight way to manage 
    multiple sqlite connections without using a connection pool. It prepares
    for multiple users in Wave connecting to the same SQLite database.

    Methods include 
      - execute: executing commands (like create table), nothing returned
      - fetchone and fetchall use corresponding sqlite methods
      - (methods for pandas using ... df.to_sql and df.read_sql_query )
    Note: The async/await syntax here is not really needed yet and defaults
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

    async def execute(self, query, params=()):
        await self._check_and_close()
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            if self.row_factory:
                self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        await self._update_activity_time()
        #return cursor.fetchall()

    async def fetchone(self, query, params=()):
        await self._check_and_close()
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            if self.row_factory:
                self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        await self._update_activity_time()
        return cursor.fetchone()

    async def fetchall(self, query, params=()):
        await self._check_and_close()
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            if self.row_factory:
                self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        await self._update_activity_time()
        return cursor.fetchall()

    async def pd_read_sql(self, query, params=()):
        await self._check_and_close()
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            if self.row_factory:
                self.connection.row_factory = sqlite3.Row
        df = pd.read_sql_query(query, self.connection, params)
        await self._update_activity_time()
        return df

    async def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

async def get_timed_query_one(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class
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
    
async def get_query_one(q, query, params=()):
    c = q.user.c 
    c.execute(query, params)
    row = c.fetchone()
    if not row:
        warnings.warn("Query returned no row", category=Warning)
        return None
    else:
        return row

async def get_timed_query(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class
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
    
async def get_query(q, query, params=()):
    c = q.user.c 
    c.execute(query, params)
    rows = c.fetchall()
    if not rows:
        warnings.warn("Query returned no rows", category=Warning)
        return None
    else:
        return rows

async def get_program_title(q, program_id):
    query = '''
        SELECT b.name || ' in ' || a.name as title
        FROM programs a, degrees b 
        WHERE a.id = ? AND a.degree_id = b.id 
    '''
    row = await get_query_one(q, query, params=(program_id,))
    if row:
        return row['title']
    else:
        return None

async def get_program_title_new(q, program_id):
    query = '''
        SELECT b.id, b.name || ' in ' || a.name as title
        FROM programs a, degrees b 
        WHERE a.id = ? AND a.degree_id = b.id 
    '''
    row = await get_query_one(q, query, params=(program_id,))
    if row:
        return row
    else:
        return None

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

## Need to update this

def schedule_courses(courses, periods, max_courses_default, max_credits_default):
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
    ##        q.user.user_id, q.user.role_id = utils.find_or_add_user(q)
    ##    else:
    ##        # fake it for now
