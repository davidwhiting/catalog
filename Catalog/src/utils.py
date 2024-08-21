from h2o_wave import Q, ui

from typing import Any, Optional, Dict, List

import asyncio
import logging
import numpy as np
import pandas as pd
import sqlite3
import time
import warnings

#import sys
#import traceback

import templates

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

##############################################################
####################  Initialize Functions  ##################
##############################################################

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

    return student_info

def initialize_student_data():
    '''
    Initialize new student data
    (This is not the same as populating from the database)
    Moved this from student_info for ease in debugging student_info
    '''
    student_data = {}
    # Initialize some attributes
    attributes = [        
        'user_id',
        'required',
        'periods',
        'schedule'
    ]
    student_data.update({name: None for name in attributes})    
    return student_data

def initialize_ge():
    '''
    Initialize General Education tracking for undergraduate students.
    '''
    ge = {
        'arts': {
            '1': None,
            '2': None,
            'nopre': False
        },
        'beh': {
            '1': None,
            '2': None,
            'nopre': False
        },
        'bio': {
            '1a': None,
            '1b': None,
            '1c': None,
            '2': None,
            'nopre': False
        },
        'comm': {
            '1': 'WRTG 111',
            '2': 'WRTG 112',
            '3': None,
            '4': None,
            'nopre': False
        },
        'math': {
            '1': None,
            'nopre': False
        },
        'res': {
            '1': None,
            '2': 'LIBS 150',
            '3': None,
            '3a': None,
            '3b': None,
            '3c': None,
            'nopre': False
        }
    }
    return ge

def reset_program(q):
    '''
    When program is changed, multiple variables need to be reset
    '''
    q.user.student_info['menu']['program'] = None
    q.user.student_info['program_id'] = None
    q.user.student_info['degree_program'] = None

    q.user.student_data['required'] = None
    q.user.student_data['schedule'] = None

    q.page['dropdown'].menu_program.value = None
    q.page['dropdown'].menu_program.choices = None

############################################################
####################  Populate Functions  ##################
############################################################

async def populate_student_info(q, user_id):
    '''
    Get information from student_info table and populate the q.user.student_info variables
    and q.user.student_data dataframes
    '''
    timedConnection = q.user.conn
    attributes = ['resident_status', 'app_stage_id', 'app_stage', 'student_profile', 'financial_aid', 
        'transfer_credits', 'program_id']
    query = '''
    SELECT user_id, fullname AS name, resident_status, app_stage_id, app_stage, student_profile,
        transfer_credits, financial_aid, program_id
    FROM student_info_view WHERE user_id = ?
    '''
    row = await get_query_one(timedConnection, query, params=(user_id,))
    if row:
        q.user.student_info.update({name: row[name] for name in attributes})
#                q.user.student_data['user_id'] = user_id

        q.user.student_info['user_id'] = user_id
        q.user.student_info['name'] = row['name']
        q.user.student_data['user_id'] = user_id

        if q.user.student_info['program_id'] is not None:
            row = await get_program_title(timedConnection, q.user.student_info['program_id'])
            if row:
                q.user.student_info['degree_program'] = row['title']
                q.user.student_info['degree_id'] = row['id']
            q.user.student_data['required'] = await get_required_program_courses(q)

        if q.user.student_info['app_stage_id'] == 4:
            q.user.student_data['schedule'] = await get_student_progress_d3(q)
    
        if q.user.student_info['first_term'] is None:
            q.user.student_info['first_term'] = q.app.default_first_term

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

#######################################################
####################  Get Functions  ##################
#######################################################

async def get_student_progress_d3(q):
    timedConnection = q.user.conn
    user_id = q.user.student_info['user_id']
    query = 'SELECT * FROM student_progress_d3_view WHERE user_id = ?'
    # note: 'course' is named 'name' in student_progress_d3_view 
    df = await get_query_df(timedConnection, query, params=(user_id,))
    return df

async def get_required_program_courses(q):
    timedConnection = q.user.conn
    program_id = q.user.student_info['program_id']
    query = '''
        SELECT 
            id,
            course, 
            course_type as type,
            title,
            credits,
            pre,
            pre_credits,
            substitutions,
            description
        FROM program_requirements_view
        WHERE program_id = ?
    '''
    df = await get_query_df(timedConnection, query, params=(program_id,))
    return df

async def get_catalog_program_sequence(q):
    timedConnection = q.user.conn
    query = 'SELECT * FROM catalog_program_sequence_view WHERE program_id = ?'
    program_id = q.user.student_info['program_id']
    df = await get_query_df(timedConnection, query, params=(program_id,))
    return df

async def get_choices(timedConnection, query, params=(), disabled=None, enabled=None):
    '''
    Return choices for dropdown menus and other ui elements.
    
    timedConnection: Database connection object
    query: SQL query to fetch choices from the database
    params: Parameters for the SQL query
    disabled: Iterable of labels that should be disabled in the menu
    enabled: Iterable of labels that should be enabled in the menu
    
    Either `disabled` or `enabled` should be provided, not both.
    
    Example:
        disabled = {'Option A', 'Option B'}
        enabled = {'Option C', 'Option D'}
    '''

    # Ensure both disabled and enabled are not provided at the same time
    if (disabled is not None) and (enabled is not None):
        raise ValueError("Only one of `disabled` or `enabled` should be provided, not both.")
    
    rows = await get_query(timedConnection, query, params)
    
    # Convert disabled and enabled to sets for efficient look-up
    if disabled is not None:
        if not isinstance(disabled, (list, tuple, set)):
            raise ValueError("`disabled` should be a list, tuple, or set")
        status_set = set(disabled)
        disable = True
    elif enabled is not None:
        if not isinstance(enabled, (list, tuple, set)):
            raise ValueError("`enabled` should be a list, tuple, or set")
        status_set = set(enabled)
        disable = False
    else:
        status_set = set()
        disable = True

    choices = [
        ui.choice(
            name=str(row['name']), 
            label=row['label'], 
            disabled=(disable if row['label'] in status_set else not disable)
        ) 
        for row in rows
    ]
    return choices

async def get_choices_disable_all(timedConnection, query, params=()):
    '''
    Return choices for dropdown menus and other ui elements
    disabled: Needs to be formatted as
        disabled = {'Social Science', 'English', 'General Studies'}
        These items will be disabled in the menu so they cannot be chosen
    '''
    rows = await get_query(timedConnection, query, params)

        # might have to add error checking here to make sure `disabled` is formatted correctly
    choices = [ui.choice(
        name = str(row['name']), 
        label = row['label'], 
        disabled = True 
        ) for row in rows]

    return choices

async def get_choices_with_disabled(timedConnection, query, params=()):
    '''
    Return choices for dropdown menus and other ui elements
    This is a quick-and-dirty solution for something I can make more elegant
    Used specifically with menu_program dropdown.

    Not working for some reason
    '''
    rows = await get_query(timedConnection, query, params)

        # might have to add error checking here to make sure `disabled` is formatted correctly
    choices = [ui.choice(
        name = str(row['name']), 
        label = row['label'], 
        disabled = bool(row['disabled'])
        ) for row in rows]

    return choices

async def populate_summarize_ge(q):
    '''
    Summarize GE to keep our dashboard updated
    '''
    ge = q.user.student_info['ge']

    ge['total']['arts'] = 6
    ge['summary']['arts'] = ((ge['arts']['1'] is not None) + (ge['arts']['2'] is not None)) * 3

    ge['total']['beh'] = 6
    ge['summary']['beh'] = ((ge['beh']['1'] is not None) + (ge['beh']['2'] is not None)) * 3

    ge['total']['bio'] = 7
    ge['summary']['bio'] = ((ge['bio']['1a'] is not None) or 
                            (ge['bio']['1b'] is not None) or 
                            (ge['bio']['1c'] is not None)) * 4 + (ge['bio']['2'] is not None) * 3

    ge['total']['comm'] = 12
    ge['summary']['comm'] = ((ge['comm']['1'] is not None) + (ge['comm']['2'] is not None) + 
                             (ge['comm']['3'] is not None) + (ge['comm']['4'] is not None)) * 3

    ge['total']['math'] = 3
    ge['summary']['beh'] = (ge['math']['1'] is not None) * 3

    ge['total']['res'] = 7
    ge['summary']['res'] = ((ge['res']['1'] is not None) * 3 + (ge['res']['2'] is not None) * 1 +
                            (3 if (ge['res']['3'] is not None) else (
                                (ge['res']['3a'] is not None) + 
                                (ge['res']['3b'] is not None) + 
                                (ge['res']['3c'] is not None))))

async def get_choices_old(timedConnection, query, params=(), disabled=None):
    '''
    Return choices for dropdown menus and other ui elements
    disabled: Needs to be formatted as
        disabled = {'Social Science', 'English', 'General Studies'}
        These items will be disabled in the menu so they cannot be chosen
    '''
    rows = await get_query(timedConnection, query, params)

    if disabled is None:
        choices = [ui.choice(name=str(row['name']), label=row['label']) for row in rows]
    else:
        # might have to add error checking here to make sure `disabled` is formatted correctly
        choices = [ui.choice(
            name = str(row['name']), 
            label = row['label'], 
            disabled = (str(row['label']) in disabled)
        ) for row in rows]

    return choices
# these functions return 

#######################################################
#######  Set Functions (for setting variables)  #######
#######################################################

async def reset_student_info_data(q):
    '''
    All the steps needed to initialize q.user.student_info and q.user.student_data
    and set multiple q.user parameters

    Will be called at startup in initialize_user and when switching to a new student 
    for admin and coaches
    '''
    q.user.student_info = initialize_student_info()
    q.user.student_info['ge'] = initialize_ge() # only if undergraduate
    q.user.student_info_populated = False # may be needed later 
    q.user.student_data = initialize_student_data() # will have required, periods, schedule

async def set_user_vars_given_role(q):
    '''
    Get role given a user id and set q.user variables
    '''
    timedConnection = q.user.conn
    query = '''
        SELECT 
		    a.role_id,
		    b.role,
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

async def get_program_title(timedConnection, program_id):
    query = '''
        SELECT b.id, b.degree || ' in ' || a.name as title
        FROM programs a, degrees b 
        WHERE a.id = ? AND a.degree_id = b.id 
    '''
    row = await get_query_one(timedConnection, query, params=(program_id,))
    if row:
        return row
    else:
        return None

######################################################################
####################  SQL-RELATED FUNCTIONS  #########################
######################################################################

import sqlite3
import time
from typing import Any, List, Dict, Optional
import pandas as pd

class TimedSQLiteConnection:
    def __init__(self, db_path: str, row_factory: bool = True, timeout: int = 1800):
        self.db_path = db_path
        self.timeout = timeout
        self.row_factory = row_factory
        self.last_activity_time = time.time()
        self.connection: Optional[sqlite3.Connection] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _check_and_close(self):
        if self.connection is not None:
            current_time = time.time()
            if current_time - self.last_activity_time >= self.timeout:
                await self.close()

    async def _update_activity_time(self):
        self.last_activity_time = time.time()

    async def _get_cursor(self):
        await self._check_and_close()
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            if self.row_factory:
                self.connection.row_factory = sqlite3.Row
        return self.connection.cursor()

    async def _execute_query(self, query: str, params: tuple = (), fetch_method: str = None):
        try:
            cursor = await self._get_cursor()
            cursor.execute(query, params)
            await self._update_activity_time()

            if fetch_method == 'one':
                result = cursor.fetchone()
                return result if result else None
            elif fetch_method == 'all':
                result = cursor.fetchall()
                return result if result else None
            elif fetch_method == 'dict':
                column_names = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(column_names, row)) for row in rows]
                return result if result else None
            elif fetch_method == 'df':
                df = pd.read_sql_query(query, self.connection, params=params)
                return df if not df.empty else None
            else:
                self.connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    async def execute(self, query: str, params: tuple = ()):
        """Execute a query without returning results."""
        await self._execute_query(query, params)

    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Any]:
        """Execute a query and fetch one result."""
        return await self._execute_query(query, params, fetch_method='one')

    async def fetchall(self, query: str, params: tuple = ()) -> Optional[List[Any]]:
        """Execute a query and fetch all results."""
        return await self._execute_query(query, params, fetch_method='all')

    async def fetchdict(self, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
        """Execute a query and fetch results as a list of dictionaries."""
        return await self._execute_query(query, params, fetch_method='dict')

    async def fetchdf(self, query: str, params: tuple = ()) -> Optional[pd.DataFrame]:
        """Execute a query and fetch results as a pandas DataFrame."""
        return await self._execute_query(query, params, fetch_method='df')

    async def close(self):
        """Close the database connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None

## remove this old version after testing the version above
class TimedSQLiteConnectionOld:
    '''
    This class creates an SQLite connection that will disconnect after 
    'timeout' amount of inactivity. This is a lightweight way to manage 
    multiple sqlite connections without using a connection pool. It prepares
    for multiple users in Wave connecting to the same SQLite database.

    Methods include 
      - execute: executing commands (like create table), nothing returned
      - fetchone and fetchall use corresponding sqlite3 methods
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

async def get_query_old(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return all rows

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    rows = await timedConnection.fetchall(query, params)
    if not rows:
        warning_message = f"Query returned no row: {query} with params {params}"
        warnings.warn(warning_message, category=Warning)
        logging.warning(warning_message)
        return None
    else:
        return rows

async def get_query_one_old(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a row

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    row = await timedConnection.fetchone(query, params)
    if not row:
        warning_message = f"Query returned no row: {query} with params {params}"
        warnings.warn(warning_message, category=Warning)
        logging.warning(warning_message)
        return None
    else:
        return row

async def get_query_dict_old(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a 
    dictionary of all rows

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    result = await timedConnection.fetchdict(query, params)
    if not result:
        warning_message = f"Query returned no row: {query} with params {params}"
        warnings.warn(warning_message, category=Warning)
        logging.warning(warning_message)
        return None
    else:
        return result

async def get_query_course_dict_old(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a 
    dictionary of all rows indexed by course

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    try:
        tmp_dict = await get_query_dict(timedConnection, query, params)
        
        if tmp_dict is None:
            warnings.warn("Query did not return a dictionary", category=Warning)
            return None
        
        try:
            result = {record['course']: record for record in tmp_dict}
        except KeyError:
            warnings.warn("'course' is not an element of the dictionary", category=Warning)
            return None
        
        if not result:
            warnings.warn("Query did not return a dictionary", category=Warning)
            return None
        
        return result
    
    except Exception as e:
        warnings.warn(f"An error occurred: {e}", category=Warning)
        return None

async def get_query_df_old(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a dataframe

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    try:
        df = await timedConnection.fetchdf(query, params)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # or return a specific value or message
    if df.empty:
        warning_message = f"Query returned no row: {query} with params {params}"
        warnings.warn(warning_message, category=Warning)
        logging.warning(warning_message)
        return None
    else:
        return df

async def _base_query(timedConnection, query_method: str, query: str, params: tuple = (), **kwargs) -> Optional[Any]:
    """
    Base function to handle queries and error logging.
    
    :param timedConnection: TimedSQLiteConnection instance
    :param query_method: String indicating which query method to use
    :param query: SQL query string
    :param params: Query parameters
    :param kwargs: Additional keyword arguments for specific query methods
    :return: Query result or None if query fails
    """
    try:
        method = getattr(timedConnection, f"fetch{query_method}")
        result = await method(query, params, **kwargs)
        
        if result is None or (isinstance(result, (list, dict)) and not result) or (isinstance(result, pd.DataFrame) and result.empty):
            warning_message = f"Query returned no results: {query} with params {params}"
            warnings.warn(warning_message, category=Warning)
            logging.warning(warning_message)
            return None
        
        return result
    except Exception as e:
        error_message = f"An error occurred during query execution: {e}"
        warnings.warn(error_message, category=Warning)
        logging.error(error_message)
        return None

async def get_query(timedConnection, query: str, params: tuple = ()) -> Optional[List[Any]]:
    """Get all rows from a query."""
    return await _base_query(timedConnection, "all", query, params)

async def get_query_one(timedConnection, query: str, params: tuple = ()) -> Optional[Any]:
    """Get a single row from a query."""
    return await _base_query(timedConnection, "one", query, params)

async def get_query_dict(timedConnection, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
    """Get all rows from a query as a list of dictionaries."""
    return await _base_query(timedConnection, "dict", query, params)

async def get_query_course_dict(timedConnection, query: str, params: tuple = ()) -> Optional[Dict[str, Dict[str, Any]]]:
    """Get all rows from a query as a dictionary indexed by course."""
    result = await get_query_dict(timedConnection, query, params)
    if result is None:
        return None
    
    try:
        return {record['course']: record for record in result}
    except KeyError:
        warnings.warn("'course' is not an element of the dictionary", category=Warning)
        return None

async def get_query_df(timedConnection, query: str, params: tuple = ()) -> Optional[pd.DataFrame]:
    """Get query results as a pandas DataFrame."""
    return await _base_query(timedConnection, "df", query, params)

######################################################################
#####################  QUERIES & FUNCTIONS  ##########################
######################################################################

######################################################################
#################  EVENT AND HANDLER FUNCTIONS  ######################
######################################################################

def example_dialog(q):
    q.page['meta'].dialog = ui.dialog(
        title='Hello!',
        name='my_dialog',
        items=[
            ui.text('Click the X button to close this dialog.'),
        ],
        # Enable a close button (displayed at the top-right of the dialog)
        closable=True,
        # Get notified when the dialog is dismissed.
        events=['dismissed'],
    )

def course_description_dialog(q, course, which='schedule'):
    '''
    Create a dialog for the course description for a table.
    This will be used for multiple tables on multiple pages.
    course: indicate what course it's for
    df: DataFrame that the table was created from

    to do: course in the schedule df is called 'name'
           course is called course in the required df
           should simplify by changing schedule df to course AFTER
           updating d3 javascript code, since it's expecting name
    '''
    if which in ['required', 'schedule']:
        #df = q.user.student_data[which]
        if which == 'schedule':
            df = q.user.student_data['schedule']
            description = df.loc[df['name'] == course, 'description'].iloc[0]
   
        elif which == 'required':
            df = q.user.student_data['required']
            description = df.loc[df['course'] == course, 'description'].iloc[0]

        #description = df.loc[df['course'] == course, 'description'].iloc[0]

        q.page['meta'].dialog = ui.dialog(
            name = which + '_description_dialog',
            title = course + ' Course Description',
            width = '480px',
            items = [ui.text(description)],
            # Enable a close button
            closable = True,
            # Get notified when the dialog is dismissed.
            events = ['dismissed']
        )
    else:
        pass

####################################################################
#################  COURSE LIST BUILDING FUNCTIONS  ################# 
####################################################################

def update_ge_ids(data):
    '''
    This function reassigns the second ARTS and BEH duplicates to the second 
    respective ge_id for those categories.
    '''
    # Create a dictionary to keep track of seen ge_id
    seen_ge_ids = {}
    
    for entry in data:
        ge_id = entry['ge_id']
        course = entry['course']
        
        # Restrict the check to ge_id 6 and 12 only
        if ge_id == 6 or ge_id == 12:
            if ge_id in seen_ge_ids:
                seen_ge_ids[ge_id] += 1
                # Check if this is the second occurrence
                if seen_ge_ids[ge_id] == 2:
                    # Increment the ge_id by 1 for the second occurrence
                    entry['ge_id'] += 1
            else:
                # Mark the ge_id as seen for the first time
                seen_ge_ids[ge_id] = 1
    
    return data

def handle_ge_duplicates(data):
    '''
    Remove possible duplicates from the ge structure, since each ge_id can have only one course.
    Return both the unique and the duplicates.
    '''
    # Create a dictionary to keep track of the first occurrence of each ge_id
    first_occurrence = {}
    
    # Initialize list to store duplicate entries
    duplicate_data = []
    
    # Remove duplicates and ensure at most one course per ge_id
    unique_data = []
    for entry in data:
        ge_id = entry['ge_id']
        course = entry['course']
        
        # If ge_id is not None, check if it's the first occurrence
        if ge_id is not None:
            if ge_id not in first_occurrence:
                # If it's the first occurrence, add it to first_occurrence
                first_occurrence[ge_id] = entry
            else:
                # If it's not the first occurrence, add it to duplicate_data
                duplicate_data.append(entry)
                # Set ge_id to None
                entry['ge_id'] = None
        
        # Add the current entry to the unique_data list if it's not None
        if entry['ge_id'] is not None:
            unique_data.append(entry)
    
    return unique_data, duplicate_data

def update_ge_list_from_student_info(ge_course_list, student_info):
    # update ge_courses with any information we have from student_info['ge']
    # Iterate over student_info['ge'] values
    for abbr, abbr_values in student_info['ge'].items():
        for part, course in abbr_values.items():
            # Ignore 'nopre'
            if part != 'nopre' and course is not None:
                # Construct course_slot key
                course_slot = f"ge_{abbr}_{part}"
                # Find the matching entry in ge_courses and update course if found
                for entry in ge_course_list:
                    if entry['course_slot'] == course_slot:
                        entry['course'] = course
                        break
    
    return ge_course_list

def update_ge_course_list_from_program(ge_course_list, updates):
    '''
    Add any required,general courses from the selected program
    '''
    # Iterate over more_updates
    for update_entry in updates:
        # Find the corresponding entry in updated_ge_courses and update course if ge_id matches
        for entry in ge_course_list:
            if entry['ge_id'] == update_entry['ge_id']:
                entry['course'] = update_entry['course']
                break
    
    return ge_course_list

def update_student_info_ge(student_info, ge_course_list):
    '''
    Update student_info['ge'] after ge_course_list is updated
    '''
    # Iterate over ge_course_list
    for course in ge_course_list:
        # Check if the course is not 'GENERAL'
        if course['course'] != 'GENERAL':
            # Update student_info['ge'] accordingly
            student_info['ge'][course['abbr']][course['part']] = course['course']
    
    return student_info

def update_bio_df(df):
    '''
    Summarize the bio GE requirements from a dataframe
    Add error checking to make sure a dataframe rather than list or dictionary 
    '''
    # Step 1: Filter df to get bio_df
    bio_df = df[(df['course'] == 'GENERAL') & (df['course_slot'].str.contains('bio_1'))]

    # Step 2: Check the length of bio_df
    if len(bio_df) == 3:
        # Take the first row and update 'part' and 'course_slot' in the original df
        first_row = bio_df.iloc[0]
        df.loc[df['ge_id'] == first_row['ge_id'], 'part'] = '1'
        df.loc[df['ge_id'] == first_row['ge_id'], 'course_slot'] = 'ge_bio_1'

        # Remove the other two rows from df
        df = df[~df['ge_id'].isin(bio_df.iloc[1:]['ge_id'])]
    elif len(bio_df) == 2:
        # Delete rows from df identified by their 'ge_id'
        df = df[~df['ge_id'].isin(bio_df['ge_id'])]

    # Step 3: Change 'part' and 'course_slot' in df
    df.loc[df['part'].str.contains('1[abc]'), 'part'] = '1'
    df.loc[df['course_slot'].str.contains('ge_bio_1[abc]'), 'course_slot'] = 'ge_bio_1'

    return df

async def build_program_course_list(program_df, timedConnection, ge_course_list):
    '''
    Fix this up for use within wave, get_required_program_courses should be updated, etc.
    program_df: the result of get_required_program_courses
    '''

    # Step 0: Convert required df to a dictionary
    #         program_course_dict contains 'Major' with possible 'Required,GE' and 'Required,Elective' entries
    program_course_dict = program_df.to_dict(orient='records')

    # Step 1: Extract the required courses if any
    #         Doing this to update GE requirements ge_course_list
    required_general_courses = [row['course'] for row in program_course_dict if row['type'] == 'Required,General']

    # check whether it returned anything
    if required_general_courses:
        required = tuple(required_general_courses)

        # Construct the SQL query
        # Using placeholders for the IN clause and excluding duplicate for ARTS and BEH
        query = f'''
            SELECT ge_id, course 
            FROM ge_view 
            WHERE ge_id NOT IN (7, 13) 
                AND course IN ({','.join(['?' for _ in required_general_courses])})
        '''

        # Step 3: Execute the query
        result = await get_query_dict(timedConnection, query, params=required)

        # Update the ge_ids for ARTS, BEH
        updated_data = update_ge_ids(result)

        # Move possible duplicates in a GE category to electives
        # (This should be rare)
        ge_data, elective_data = handle_ge_duplicates(updated_data)

        ge_course_list = update_ge_course_list_from_program(ge_course_list, ge_data)

        return ge_course_list, elective_data

# parallel the utils.get_required_program_courses code
async def get_required_program_courses_no_q(timedConnection, student_info):
    '''
    DELETE after testing. Use the get_required_program_courses code instead
    '''
    program_id = student_info['program_id']
    query = '''
        SELECT 
            id,
            course, 
            course_type as type,
            title,
            credits,
            pre,
            pre_credits,
            substitutions,
            description
        FROM program_requirements_view
        WHERE program_id = ?
    '''
    df = await get_query_df(timedConnection, query, params=(program_id,))
    return df

async def return_program_course_list_df_from_scratch(timedConnection, student_info):
    '''
    Function should be updated to work within wave (w/ q, etc.)
    Note: (timedConnection, student_info) are both accessible w/in q, would be better to pass
          program_id for clarity 
    '''
    # Build the Program course list

    # Task 1. Get the required classes from the program
    required_df = await get_required_program_courses_no_q(timedConnection, student_info)

    # Build the GE course list
    # Create a blank list of GE course requirements with all courses set to 'GENERAL'
    query = '''
        SELECT id AS ge_id, 'GENERAL' AS course, requirement, abbr, part, credits, 
            'ge_' || abbr || '_' || part AS course_slot 
        FROM general_education_requirements 
    '''
    ge_course_list = await get_query_dict(timedConnection, query)

    # update with information from student_info['ge']
    ge_course_list = update_ge_list_from_student_info(ge_course_list, student_info)

    # Update the ge_course_list 
    ge_course_list, elective_data = await build_program_course_list(required_df, timedConnection, ge_course_list)

    # check on the elective_data as well (it should be empty)

    # Process ge_course_list_df
    ge_course_list_df = pd.DataFrame(ge_course_list)
    ge_course_list_df = update_bio_df(ge_course_list_df)
    ge_course_list_df['type'] = 'General'
    ge_course_list_df = ge_course_list_df.rename(columns={'course_slot': 'ge'})

    # required_course_list_df is where we keep all of our courses for now
    required_course_list_df = required_df[['course', 'type', 'credits']].copy()

    # Merge GE information onto any 'Required,General' rows )
    merged_df = pd.merge(ge_course_list_df[['course', 'ge']], required_course_list_df, 
                         on='course', how='right')

    # remove from the GE list those already in the Program list
    remove_list = merged_df[merged_df['type']=='Required,General'][['ge']]
    if len(remove_list) > 0:
        remove_list_values = remove_list['ge'].values.tolist()
        mask = ~ge_course_list_df['ge'].isin(remove_list_values)
        ge_course_list_df = ge_course_list_df[mask][['course', 'ge', 'type', 'credits']]
    else:
        ge_course_list_df = ge_course_list_df[['course', 'ge', 'type', 'credits']]

    # concatenate lists to join all 'General' to course list
    # this will work either way
    course_list_df = pd.concat([merged_df, ge_course_list_df], ignore_index=True)
    course_list_df['credits'] = pd.to_numeric(course_list_df['credits'])

    course_list_df['ge'] = course_list_df['ge'].fillna('')
    course_list_df
    # Add Electives to our course_list_df:

    elective_credits = 120 - course_list_df['credits'].sum()

    # Calculate number of electives to add 
    # (standard pattern is one 1-credit class and the rest 3-credit classes)
    # (1-credit class is often a capstone seminar)
    # We will calculate them instead. 

    remaining_elective_credit = elective_credits % 3
    r = int(remaining_elective_credit)
    number_of_electives = (elective_credits - remaining_elective_credit)/3
    n = int(number_of_electives)

    # create a DataFrame with the desired rows
    data = {
        'course': ['ELECTIVE'] * (n+1),
        'ge': [''] * (n+1),
        'type': ['Elective'] * (n+1),
        'credits': [3] * n + [r]
    }
    elective_df = pd.DataFrame(data)

    # Add electives to final dataframe

    final_course_list = pd.concat([course_list_df, elective_df], ignore_index=True)# Build the Program course list

    # Task 1. Get the required classes from the program
    required_df = await get_required_program_courses_no_q(timedConnection, student_info)

    # Build the GE course list
    # Create a blank list of GE course requirements with all courses set to 'GENERAL'
    query = '''
        SELECT id AS ge_id, 'GENERAL' AS course, requirement, abbr, part, credits, 
            'ge_' || abbr || '_' || part AS course_slot 
        FROM general_education_requirements 
    '''
    ge_course_list = await get_query_dict(timedConnection, query)

    # update with information from student_info['ge']
    ge_course_list = update_ge_list_from_student_info(ge_course_list, student_info)

    # Update the ge_course_list 
    ge_course_list, elective_data = await build_program_course_list(required_df, timedConnection, ge_course_list)

    # check on the elective_data as well (it should be empty)

    # Process ge_course_list_df
    ge_course_list_df = pd.DataFrame(ge_course_list)
    ge_course_list_df = update_bio_df(ge_course_list_df)
    ge_course_list_df['type'] = 'General'
    ge_course_list_df = ge_course_list_df.rename(columns={'course_slot': 'ge'})

    # required_course_list_df is where we keep all of our courses for now
    required_course_list_df = required_df[['course', 'type', 'credits']].copy()

    # Merge GE information onto any 'Required,General' rows )
    merged_df = pd.merge(ge_course_list_df[['course', 'ge']], required_course_list_df, 
                         on='course', how='right')

    # remove from the GE list those already in the Program list
    remove_list = merged_df[merged_df['type']=='Required,General'][['ge']]
    if len(remove_list) > 0:
        remove_list_values = remove_list['ge'].values.tolist()
        mask = ~ge_course_list_df['ge'].isin(remove_list_values)
        ge_course_list_df = ge_course_list_df[mask][['course', 'ge', 'type', 'credits']]
    else:
        ge_course_list_df = ge_course_list_df[['course', 'ge', 'type', 'credits']]

    # concatenate lists to join all 'General' to course list
    # this will work either way
    course_list_df = pd.concat([merged_df, ge_course_list_df], ignore_index=True)
    course_list_df['credits'] = pd.to_numeric(course_list_df['credits'])

    course_list_df['ge'] = course_list_df['ge'].fillna('')
    course_list_df
    # Add Electives to our course_list_df:

    elective_credits = 120 - course_list_df['credits'].sum()

    # Calculate number of electives to add 
    # (standard pattern is one 1-credit class and the rest 3-credit classes)
    # (1-credit class is often a capstone seminar)
    # We will calculate them instead. 

    remaining_elective_credit = elective_credits % 3
    r = int(remaining_elective_credit)
    number_of_electives = (elective_credits - remaining_elective_credit)/3
    n = int(number_of_electives)

    # create a DataFrame with the desired rows
    data = {
        'course': ['ELECTIVE'] * (n+1),
        'ge': [''] * (n+1),
        'type': ['Elective'] * (n+1),
        'credits': [3] * n + [r]
    }
    elective_df = pd.DataFrame(data)

    # Add electives to final dataframe

    final_course_list = pd.concat([course_list_df, elective_df], ignore_index=True)
    return final_course_list

######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################

from utils.schedule import ScheduleEntry, generate_periods, update_periods

def create_html_template(df, start_term):
    '''
    Function that takes the q.user.student_data['schedule'] dataframe 
    and converts it to the html_template to create the Javascript D3 figure
    '''
    # accept start_term both as 'spring2024' and 'Spring 2024'. Make sure to
    # return as the latter
    if ' ' in start_term:
        term = start_term.upper()
    else:
        season = start_term[:-4]
        year = start_term[-4:]
        term = f"{season.upper()} {year}"


    # rename because the function uses 'period' rather than 'term'
    # to do: inefficient, need to rewrite
    df_input = df.copy()
    df_input.rename(columns={'term': 'period'}, inplace=True)

    df_display, headers_display = prepare_d3_data(df_input, term)
    df_json = df_display.to_json(orient='records')
    headers_json = headers_display.to_json(orient='records')

    html_template = templates.html_code_minimal.format(
        javascript=templates.javascript_draw_only,
        headers=headers_json, 
        data=df_json)
    
    return html_template


def prepare_d3_data(df, start_term='SPRING 2024'):
    '''
    Prepare data for input into D3 figure
    Note: Uses 'period' instead of 'term'
    '''
    # Use UMGC Colors
    green = '#3b8132'
    blue = '#135f96'
    red = '#a30606'
    yellow = '#fdbf38'
    def _set_colors(row):
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

    def _generate_header_data(start_semester, num_periods, data_df = df):
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
    headers = _generate_header_data(start_term, max_period)

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
    df[['color', 'textcolor']] = df.apply(_set_colors, axis=1)

    # Set text offset multiplier to 1 and text fontsize
    df['offset'] = 1
    df['fontsize'] = '12px'
    df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'
    
    df = df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 'fontsize', 'period', 'session', 'type', 'name', 'credits', 'description']]

    return df, headers

async def update_prerequisites(timedConnection, prereq_name):
    '''
    Function to update prerequisites. 
    '''
    # Placeholder implementation
    query = '''
    SELECT course AS name, 'elective' as course_type, 'elective' as type, credits, title, 
        0 as completed, 0 as term, 0 as session, 0 as locked, pre, pre_credits, 
        substitutions, description
    FROM courses
    WHERE course = ?
    ''' 
    result = await get_query_dict(timedConnection, query, params=(prereq_name, ))
    if result:
        return result
    else:
        return None

def parse_prerequisites(prereq_string):
    '''
    Parse the prerequisites string and return a list of prerequisite groups.
    Each group contains lists of courses that satisfy the 'or' and 'and' patterns.
    '''
    import re
    prereq_string = prereq_string.strip()
    prereq_string = re.sub(r'\s+', ' ', prereq_string)
    prereq_string = re.sub(r'\(', '', prereq_string)
    prereq_string = re.sub(r'\)', '', prereq_string)
    
    and_groups = prereq_string.split('&')
    prereq_groups = [group.split('|') for group in and_groups]
    
    # Strip whitespace from each course in the groups
    prereq_groups = [[course.strip() for course in group] for group in prereq_groups]
    
    return prereq_groups

### A second approach 

def insert_prerequisite(df, i, name):
    # Recursive function to insert prerequisites
    pre_dict = update_prerequisites(name)
    if pre_dict is not None:
        # Shift rows down
        df.loc[i+2:] = df.loc[i+1:-1].values
        # Insert the prerequisite row
        df.loc[i+1] = pre_dict
        # Check if the inserted prerequisite has its own prerequisites
        insert_prerequisite(df, i+1, pre_dict['name'])


### A Third Approach
### This is old but has some good code in it
def prep_course_list(df):
    '''
    This function takes a DataFrame as input and returns a modified DataFrame where the courses are 
    ordered based on their prerequisites. It handles both “or” and “and” conditions in prerequisites, 
    as well as the ‘*’ and ‘+’ notations.

    Please note that this function assumes that the update_prerequisites function returns a dictionary 
    with keys that match the columns of your DataFrame. 
    '''

    import re

    # Assuming df is the DataFrame and it has columns 'name', 'pre', 'met', and 'where'
    for i, row in df.iterrows():
        if pd.notna(row['pre']):
            pre_courses = [pre.split('&') for pre in row['pre'].split('|')]  # Split prerequisites on '|' and '&'
            met = False
            for pre_group in pre_courses:
                met_group = True
                for pre_course in pre_group:
                    pre_course = pre_course.strip()  # Remove leading/trailing whitespace
                    if '*' in pre_course:
                        pre_course = pre_course.replace('*', '')  # Remove '*' from the course name
                    if '+' in pre_course:
                        course_prefix, course_number = re.match(r'(\D+)(\d+)\+', pre_course).groups()
                        pre_rows = df[(df['name'].str.startswith(course_prefix)) & (df['name'].str.slice(start=len(course_prefix)).astype(int) >= int(course_number))]
                    else:
                        pre_rows = df[df['name'] == pre_course]
                    if not pre_rows.empty:
                        if pre_rows.index[0] > i:
                            # Move the prerequisite row to immediately precede the current row
                            cols = df.columns.tolist()
                            temp = df.loc[pre_rows.index[0], cols].tolist()
                            df.loc[i+2:] = df.loc[i+1:-1].values  # Shift rows down
                            df.loc[i+1] = temp  # Insert the prerequisite row
                    else:
                        # If the prerequisite is not found in the DataFrame, get it and insert it
                        print(f'The prerequisite {pre_course} is not found, it should be inserted!')
                        #insert_prerequisite(df, i, pre_course)
                        met_group = False
                        break  # Exit the loop as soon as one prerequisite is not met
                if met_group:
                    met = True
                    break  # Exit the loop as soon as one group of prerequisites is met
            df.at[i, 'met'] = met
            df.at[i, 'where'] = i - 1  # The prerequisite should be the previous row
    return df


async def handle_prerequisites(timedConnection, course_df):
    '''
    Expand the course list to include necessary prerequisites.

    Group_satisfied approach:

    1. For each group of prerequisites associated with a course, we iterate over each individual 
       prerequisite in the group.
    2. For each prerequisite, we check if it's already present in courses_dict. If it is, then the 
       group is considered satisfied, and we move on to the next group.
    3. If the prerequisite is not present in courses_dict, we perform wildcard (*) and optional (+) 
       matching to check if any existing courses match the pattern. If such a course is found, the 
       group is considered satisfied.
    4. If no existing courses satisfy any prerequisite in the group, we proceed to update and add the 
       missing prerequisites to courses_dict and rows_to_append.

       This approach ensures that we only update and add missing prerequisites if none of the prerequisites 
       in a group are already satisfied by existing courses in courses_dict. If any prerequisite in the 
       group is already satisfied, we skip updating and adding new prerequisites for that group.

    Features:

    1. Recursive Function: The recursive_add_prerequisites function takes a prerequisite name, checks 
       if it's already in courses_dict, and if not, it retrieves its information using update_prerequisites.
    2. Recursion: If the prerequisite has its own prerequisites, recursive_add_prerequisites is called 
       recursively for each of them.
    3. Updating courses_dict and rows_to_append: The function ensures that all necessary prerequisites are 
       added to courses_dict and rows_to_append.
    4. Processing Main Courses: The main loop processes each course with prerequisites, using the recursive 
       function to ensure all prerequisites are included.
    '''

    async def recursive_add_prerequisites(prereq_name, courses_dict, rows_to_append):
        '''
        Recursively add prerequisites to the courses_dict and rows_to_append list.
        '''
        if prereq_name in courses_dict:
            return courses_dict[prereq_name]

        prereq_info = await update_prerequisites(timedConnection, prereq_name)
        if prereq_info:
            prerequisites = parse_prerequisites(prereq_info.get('pre', ''))
            for prereq_group in prerequisites:
                group_satisfied = False
                for sub_prereq_name in prereq_group:
                    sub_prereq_name = sub_prereq_name.strip()
                    if sub_prereq_name in courses_dict:
                        group_satisfied = True
                        break
                    elif sub_prereq_name.endswith('*'):
                        base_name = sub_prereq_name.rstrip('*')
                        if any(existing_course.startswith(base_name) for existing_course in courses_dict):
                            group_satisfied = True
                            break
                    elif sub_prereq_name.endswith('+'):
                        base_name = sub_prereq_name.rstrip('+')
                        if any(existing_course.startswith(base_name) and existing_course > base_name for existing_course in courses_dict):
                            group_satisfied = True
                            break

                if not group_satisfied:
                    for sub_prereq_name in prereq_group:
                        sub_prereq_name = sub_prereq_name.strip()
                        await recursive_add_prerequisites(sub_prereq_name, courses_dict, rows_to_append)

            courses_dict[prereq_name] = prereq_info
            if prereq_info not in rows_to_append:
                rows_to_append.append(prereq_info)
        return prereq_info

    # Filter out rows where 'name' is 'ELECTIVE', 'GENERAL', or an empty string, then set index and convert to dictionary
    courses_dict = course_df[~course_df['name'].isin(['ELECTIVE', 'GENERAL', ''])].set_index('name').to_dict('index')
    rows_to_append = []
    
    # Define filter condition for prerequisites
    filter_condition = (course_df['pre'] != '') & (~course_df['pre'].isna())
    
    for idx, course in course_df[filter_condition].iterrows():
        prerequisites = parse_prerequisites(course['pre'])
        
        for prereq_group in prerequisites:
            # Check if any prerequisite in the group satisfies the condition
            group_satisfied = False
            for prereq_name in prereq_group:
                prereq_name = prereq_name.strip()
                if prereq_name in courses_dict:
                    group_satisfied = True
                    break
                elif prereq_name.endswith('*'):
                    base_name = prereq_name.rstrip('*')
                    if any(existing_course.startswith(base_name) for existing_course in courses_dict):
                        group_satisfied = True
                        break
                elif prereq_name.endswith('+'):
                    base_name = prereq_name.rstrip('+')
                    if any(existing_course.startswith(base_name) and existing_course > base_name for existing_course in courses_dict):
                        group_satisfied = True
                        break
            
            # If no prerequisite in the group is satisfied, update prerequisites
            if not group_satisfied:
                for prereq_name in prereq_group:
                    prereq_name = prereq_name.strip()
                    await recursive_add_prerequisites(prereq_name, courses_dict, rows_to_append)
    
    prereq_df = pd.DataFrame(rows_to_append)
    updated_course_df = pd.concat([prereq_df, course_df]).drop_duplicates(subset='name').reset_index(drop=True)
    return updated_course_df

async def generate_schedule(timedConnection, course_df, periods_df):
    '''
    Generate a schedule that respects prerequisites and schedules courses into available periods.
    course_df: requires columns credits, name, session, term, year  !!! 'course' column needs to be renamed 'name' !!!
    '''

    # initialize schedule    
    schedule = []

    ## Handle prerequisites and expand the course list
    ## broken, need to fix!!!
    #course_df = await handle_prerequisites(timedConnection, course_df)

    # create a dictionary to store prerequisites for each course

    
    
    # keep track of max credits by term and year
    max_credits_df = periods_df.groupby(['year', 'term', 'period'])['max_credits'].max().reset_index()


    # Convert 'locked' column to boolean
    course_df['locked'] = course_df['locked'].astype(bool)
    locked_df   = course_df[course_df['locked']]
    unlocked_df = course_df[~course_df['locked']]

    # Iterate over locked courses to update periods and max_credits_df
    for idx, course in locked_df.iterrows():
        # this is already contained in the max_credits_df dataframe
        #term_year = (course['term'], course['year'])
        #session = course['session']
        
        # debug this later
        for period_idx, period in periods_df.iterrows():
            if (period['term'], period['year'], period['session']) == (course['term'], course['year'], course['session']):
                if periods_df.at[period_idx, 'max_courses'] > 0:
                    periods_df.at[period_idx, 'max_courses'] -= 1
                    
                    if term_year not in max_credits_by_term_year:
                        max_credits_by_term_year[term_year] = period['max_credits']
                    else:
                        max_credits_by_term_year[term_year] -= course['credits']
                    
                    schedule.append({
                        'seq': len(schedule) + 1,
                        'name': course['name'],
                        'term': course['term'],
                        'year': course['year'],
                        'session': course['session'],
                        'locked': True
                    })
                else:
                    print(f"Unable to assign locked course '{course['name']}' to period {period['id']}.")
                break

    # Iterate over unlocked courses to schedule them
    for idx, course in unlocked_df.iterrows():
        assigned = False
        
        # iterate over periods to schedule the course
        for period_idx, period in periods_df.iterrows():

            # check for prerequisites

            # if no, then schedule
            # if yes and the prerequisite already is in the list, then schedule
            # if yes and the prereq is not yet in the schedule, exit loop and move to next course

            term_year = (period['term'], period['year'])
            previous_period_idx = period_idx - period['previous']
            
            if previous_period_idx >= 0:
                previous_period = periods_df.iloc[previous_period_idx]

            if periods_df.at[period_idx, 'max_courses'] > 0 and max_credits_by_term_year.get(term_year, 0) >= course['credits']:
                # Add the course to the schedule
                schedule.append({
                    'seq': len(schedule) + 1,
                    'name': course['name'],
                    'term': period['term'],
                    'year': period['year'],
                    'session': period['session'],
                    'locked': False
                })
                    
                periods_df.at[period_idx, 'max_courses'] -= 1
                max_credits_by_term_year[term_year] -= course['credits']
                
                assigned = True
                break
        
        if not assigned:
            print(f"Unable to assign unlocked course '{course['name']}' to any period.")

    return pd.DataFrame(schedule)
