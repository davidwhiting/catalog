from h2o_wave import Q, ui
import asyncio
import logging
import sqlite3
import time
import warnings
import functools




#########################################################
####################  GET FUNCTIONS  ####################
#########################################################

async def get_choices_new(timed_connection: TimedSQLiteConnection, query: str, params: tuple = (), 
                      disabled: Optional[Union[set, list, tuple]] = None, 
                      enabled: Optional[Union[set, list, tuple]] = None,
                      tooltip: bool = False):
    """
    Return choices for dropdown menus and other UI elements.

    Args:
        timed_connection: Database connection object
        query (str): SQL query to fetch choices from the database
        params (tuple): Parameters for the SQL query (default: ())
        disabled (set, list, tuple): Iterable of labels that should be disabled in the menu (default: None)
        enabled (set, list, tuple): Iterable of labels that should be enabled in the menu (default: None)
        tooltip (bool): If True, return choices with tooltips (default: False)

    Returns:
        list: List of ui.choice objects for use in H2O Wave menus

    Raises:
        ValueError: If both disabled and enabled are provided, or if they are of incorrect type

    Note:
        Either disabled or enabled should be provided, not both.
        If both disabled and enabled are None, then by default everything is enabled.
        Queries need to return 'name', 'label', and 'tooltip' as the named values.
        For tooltips, use '... AS tooltip' in your SQL query.

    Example:
        disabled = {'Social Science', 'English', 'General Studies'}
        enabled = {'Social Science', 'English', 'General Studies'}
        query = "SELECT id AS name, name AS label, explanation AS tooltip FROM Skills"
    """
    if disabled is not None and enabled is not None:
        raise ValueError("Only one of `disabled` or `enabled` should be provided, not both.")

    if disabled is not None:
        if not isinstance(disabled, (list, tuple, set)):
            raise ValueError("`disabled` should be a list, tuple, or set")
        status_set = set(disabled)
        disable_mode = True
    elif enabled is not None:
        if not isinstance(enabled, (list, tuple, set)):
            raise ValueError("`enabled` should be a list, tuple, or set")
        status_set = set(enabled)
        disable_mode = False
    else:
        status_set = set()
        disable_mode = False  # Changed to False to enable everything by default

    try:
        rows = await get_query(timed_connection, query, params)
        
        if tooltip:
            choices = [
                ui.choice(
                    name=str(row['name']),
                    label=row['label'],
                    tooltip=row['tooltip'] if row['tooltip'] else '',
                    disabled=(disable_mode if row['label'] in status_set else not disable_mode)
                )
                for row in rows
            ]
        else:
            choices = [
                ui.choice(
                    name=str(row['name']),
                    label=row['label'],
                    disabled=(disable_mode if row['label'] in status_set else not disable_mode)
                )
                for row in rows
            ]
        return choices

    except Exception as e:
        print(f"Error retrieving choices: {str(e)}")
        return []  # Return an empty list if there's an error


## quick hack: diabled={""} (need to fix the entire thing)
async def get_choices(timed_connection: TimedSQLiteConnection, query: str, params: tuple = (), 
                      disabled: Optional[Union[set, list, tuple]] = {""}, 
                      enabled: Optional[Union[set, list, tuple]] = None):
    """
    Return choices for dropdown menus and other UI elements.

    Args:
        timed_connection: Database connection object
        query (str): SQL query to fetch choices from the database
        params (tuple): Parameters for the SQL query (default: ())
        disabled (set, list, tuple): Iterable of labels that should be disabled in the menu (default: None)
        enabled (set, list, tuple): Iterable of labels that should be enabled in the menu (default: None)

    Returns:
        list: List of ui.choice objects for use in H2O Wave menus

    Raises:
        ValueError: If both disabled and enabled are provided, or if they are of incorrect type

    Note:
        Either disabled or enabled should be provided, not both.
        If both disabled and enabled are None, then by default everything is enabled.

    Example:
        disabled = {'Social Science', 'English', 'General Studies'}
        enabled = {'Social Science', 'English', 'General Studies'}
    """
    if disabled is not None and enabled is not None:
        raise ValueError("Only one of `disabled` or `enabled` should be provided, not both.")

    if disabled is not None:
        if not isinstance(disabled, (list, tuple, set)):
            raise ValueError("`disabled` should be a list, tuple, or set")
        status_set = set(disabled)
        disable_mode = True
    elif enabled is not None:
        if not isinstance(enabled, (list, tuple, set)):
            raise ValueError("`enabled` should be a list, tuple, or set")
        status_set = set(enabled)
        disable_mode = False
    else:
        status_set = set()
        disable_mode = False  # Changed to False to enable everything by default

    try:
        rows = await get_query(timed_connection, query, params)
        
        choices = [
            ui.choice(
                name=str(row['name']),
                label=row['label'],
                disabled=(disable_mode if row['label'] in status_set else not disable_mode)
            )
            for row in rows
        ]
        return choices

    except Exception as e:
        print(f"Error retrieving choices: {str(e)}")
        return []  # Return an empty list if there's an error

##############################################################
####################  POPULATE FUNCTIONS  ####################
##############################################################

async def reverse_engineer_dropdown_menu(timed_connection, program_id):
    """
    Recreate dropdown menus for students based on their program ID.
    This function is used when the dropdown menu status was not saved and needs to be reconstructed.

    Args:
        timed_connection: Asynchronous database connection object
        program_id (int): The ID of the student's program

    Returns:
        dict: A dictionary containing the menu selections for program, degree, and area of study

    Note:
        There isn't a strict 1:1 correspondence between study areas and programs,
        so we limit the query to 1 result.
    """
    menu = {
        'program': None,
        'degree': None,
        'area_of_study': None
    }

    if program_id is not None:
        menu['program'] = program_id
        query = """
            SELECT menu_degree_id, menu_area_id 
            FROM menu_all_view
            WHERE program_id = ?
            LIMIT 1
        """

        try:
            row = await get_query_one(timed_connection, query, params=(program_id,))
            if row:
                menu['degree'] = row['menu_degree_id']
                menu['area_of_study'] = row['menu_area_id']
        except Exception as e:
            print(f"Error retrieving menu data: {str(e)}")
            # Depending on your error handling strategy, you might want to re-raise the exception

    return menu

async def populate_student_info_dict(timed_connection: TimedSQLiteConnection, user_id: int, 
                                     default_first_term: str = 'Spring 2024') -> dict:
    """
    Get information from student_info table and populate the student_info dictionary.

    Args:
        timed_connection: Database connection object
        user_id: User ID to query
        default_first_term: Default term to use if not present in database (default: 'Spring 2024')

    Returns:
        dict: Student information dictionary
    """
    query = """
    SELECT user_id, fullname AS name, resident_status, app_stage_id, app_stage, student_profile,
           transfer_credits, financial_aid, program_id
    FROM student_info_view
    WHERE user_id = ?
    """
    
    try:
        result = await get_query_dict(timed_connection, query, params=(user_id,))
        if not result:
            raise ValueError(f"No student found with user_id: {user_id}")
        
        student_info = result[0]
        
        if student_info.get('program_id'):
            program_id = student_info['program_id']
            program_info = await get_program_title(timed_connection, program_id)
            if program_info:
                student_info['degree_program'] = program_info['title']
                student_info['degree_id'] = program_info['id']

            student_info['menu'] = await reverse_engineer_dropdown_menu(timed_connection, program_id)

        # Note: first_term will also be selected on the Schedule page
        student_info.setdefault('first_term', default_first_term)
        
        return student_info
    
    except Exception as e:
        # Log the error or handle it as appropriate for your application
        print(f"Error populating student info: {str(e)}")
        raise

async def populate_student_data_dict(timed_connection, student_info) -> dict:
    """
    Populate the student_data dictionary with user ID, required courses, and schedule.

    Args:
        timed_connection: Database connection object
        student_info (dict): Dictionary containing student information from populate_student_info_dict

    Returns:
        dict: Student data dictionary containing:
            - user_id: The student's user ID
            - required: List of required program courses (if program_id is available)
            - schedule: Student's course schedule (if app_stage_id is 4)

    Note:
        The function uses asyncio.gather() to run async operations concurrently.
    """
    student_data = {
        'user_id': student_info.get('user_id'),
        'required': None,
        'schedule': None
    }

    program_id = student_info.get('program_id')
    app_stage_id = student_info.get('app_stage_id')

    async def _get_required_courses():
        if program_id is not None:
            return await get_required_program_courses(timed_connection, program_id)
        return None

    async def _get_schedule():
        if app_stage_id == 4:
            return await get_student_progress_d3(timed_connection, student_data['user_id'])
        return None

    try:
        required, schedule = await asyncio.gather(
            _get_required_courses(),
            _get_schedule()
        )
        student_data['required'] = required
        student_data['schedule'] = schedule
    except Exception as e:
        print(f"Error populating student record: {str(e)}")
        # Depending on your error handling strategy, you might want to re-raise the exception

    return student_data
from contextlib import asynccontextmanager
from h2o_wave import Q, ui
from typing import Any, Dict, Callable, List, Optional, Union
import asyncio
import logging
import numpy as np
import pandas as pd
import sqlite3
import time
import warnings


from backend import initialize_ge, initialize_student_info, initialize_student_data
from backend import TimedSQLiteConnection, _base_query, get_query, get_query_one, \
    get_query_dict, get_query_course_dict, get_query_df

## _ZZ versions are newly rewritten but not all working
## will incrementally fix them and introduce the correct one


#import sys
#import traceback

import templates

############################################################
####################  POPULATE FUNCTIONS  ##################
############################################################

async def populate_student_info(q, user_id):
    '''
    Get information from student_info table and populate the q.user.student_info variables
    and q.user.student_data dataframes
    '''
    timed_connection = q.user.conn
    attributes = ['resident_status', 'app_stage_id', 'app_stage', 'student_profile', 'financial_aid', 
        'transfer_credits', 'program_id']
    query = '''
    SELECT user_id, fullname AS name, resident_status, app_stage_id, app_stage, student_profile,
        transfer_credits, financial_aid, program_id
    FROM student_info_view WHERE user_id = ?
    '''
    row = await get_query_one(timed_connection, query, params=(user_id,))
    if row:
        q.user.student_info.update({name: row[name] for name in attributes})
#                q.user.student_data['user_id'] = user_id

        q.user.student_info['user_id'] = user_id
        q.user.student_info['name'] = row['name']
        q.user.student_data['user_id'] = user_id

        if q.user.student_info['program_id'] is not None:
            row = await get_program_title(timed_connection, q.user.student_info['program_id'])
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


async def reset_student_info_data_ZZ(q):
    '''
    All the steps needed to initialize q.user.student_info and q.user.student_data
    and set multiple q.user parameters

    Will be called at startup in initialize_user and when switching to a new student 
    for admin and coaches
    '''
    q.user.student_info = initialize_student_info()
    q.user.student_info_populated = False # may be needed later 
    q.user.student_data = initialize_student_data() # will have required, periods, schedule

async def populate_q_student_info_ZZ(q, timed_connection, user_id):
    """
    Populate q.user.student_info and q.user.student_data dictionaries with student information.

    This function retrieves student information from the database and populates the relevant
    dictionaries in the q object. It's called by `app.initialize_user` and `app.select_sample_user`.

    Args:
        q: The q object containing application and user data
        timed_connection: Database connection object (also stored in q)
        user_id: The ID of the user to retrieve information for (also stored in q)

    Note:
        timed_connection and user_id are included as parameters for clarity, despite being stored in q.

    Raises:
        Exception: If there's an error during the data retrieval or population process
    """
    try:
        student_info = await populate_student_info_dict(timed_connection, user_id)
        student_data = await populate_student_data_dict(timed_connection, student_info)

        q.user.student_info = student_info
        q.user.student_data = student_data

    except Exception as e:
        error_message = f"Error populating student info for user {user_id}: {str(e)}"
        print(error_message)  # For logging purposes
        raise  # Re-raising the exception for now

    q.user.info_populated = True  


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

#########################################################
####################  GET FUNCTIONS  ####################
#########################################################

async def get_catalog_program_sequence_ZZ(timed_connection, program_id):
    """
    Retrieve the catalog program sequence for a given program.

    This function fetches all columns from the catalog_program_sequence_view
    for a specific program.

    Args:
        timed_connection: Asynchronous database connection object
        program_id (int): The ID of the program to query

    Returns:
        pandas.DataFrame: A DataFrame containing the catalog program sequence,
                          or None if no data is found or an error occurs.

    Raises:
        Exception: If there's an error during the database query or DataFrame creation.
    """
    query = """
        SELECT *
        FROM catalog_program_sequence_view
        WHERE program_id = ?
    """
    
    try:
        df = await get_query_df(timed_connection, query, params=(program_id,))
        return df if not df.empty else None
    except Exception as e:
        print(f"Error retrieving catalog program sequence: {str(e)}")
        return None

# was get_choices_ZZ

async def get_program_title_ZZ(timed_connection, program_id):
    """
    Retrieve the program title for a given program ID.

    Args:
        timed_connection: Database connection object
        program_id: ID of the program to query

    Returns:
        dict: Program information including 'id' and 'title', or None if not found
    """
    query = """
        SELECT b.id, b.name || ' in ' || a.name AS title
        FROM programs a
        JOIN degrees b ON a.degree_id = b.id
        WHERE a.id = ?
    """
    try:
        row = await get_query_one(timed_connection, query, params=(program_id,))
        return row if row else None
    except Exception as e:
        print(f"Error retrieving program title: {str(e)}")
        return None

async def get_required_program_courses_ZZ(timed_connection, program_id):
    """
    Retrieve the required courses for a given program.

    This function is called by `app.menu_program` and `populate_q_student_info`.
    It fetches course information from the program_requirements_view for a specific program.

    Args:
        timed_connection: Asynchronous database connection object
        program_id (int): The ID of the program to query

    Returns:
        pandas.DataFrame: A DataFrame containing the required courses for the program,
                          or None if no courses are found or an error occurs.

    Raises:
        Exception: If there's an error during the database query or DataFrame creation.
    """
    query = """
        SELECT 
            id,
            course, 
            course_type AS type,
            title,
            credits,
            pre,
            pre_credits,
            substitutions,
            description
        FROM program_requirements_view
        WHERE program_id = ?
    """
    
    try:
        df = await get_query_df(timed_connection, query, params=(program_id,))
        return df if not df.empty else None
    except Exception as e:
        print(f"Error retrieving required program courses: {str(e)}")
        return None

async def get_student_progress_d3_ZZ(timed_connection, user_id):
    """
    Retrieve student progress data for D3 visualization.

    This function fetches all columns from the student_progress_d3_view
    for a specific user. It's called by `populate_q_student_info`.

    Note: The 'name' column in the old version has been replaced with 'course'.
    Downstream D3 figure implementations may need to be updated accordingly.

    Args:
        timed_connection: Asynchronous database connection object
        user_id (int): The ID of the student to query

    Returns:
        pandas.DataFrame: A DataFrame containing the student's progress data,
                          or None if no data is found or an error occurs.

    Raises:
        Exception: If there's an error during the database query or DataFrame creation.
    """
    query = """
        SELECT *
        FROM student_progress_d3_view
        WHERE user_id = ?
    """
    
    try:
        df = await get_query_df(timed_connection, query, params=(user_id,))
        return df if not df.empty else None
    except Exception as e:
        print(f"Error retrieving student progress data: {str(e)}")
        return None

async def get_choices_disable_all_ZZ(timed_connection, query, params=()):
    '''
    Return choices for dropdown menus and other ui elements
    disabled: Needs to be formatted as
        disabled = {'Social Science', 'English', 'General Studies'}
        These items will be disabled in the menu so they cannot be chosen
    Should replace this with get_choices updated function !!!!
    '''
    rows = await get_query(timed_connection, query, params)

        # might have to add error checking here to make sure `disabled` is formatted correctly
    choices = [ui.choice(
        name = str(row['name']), 
        label = row['label'], 
        disabled = True 
        ) for row in rows]

    return choices

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

async def get_program_title(timed_connection: TimedSQLiteConnection, program_id: int) -> Optional[str]:
    '''
    Get the program title for a given program id
    '''
    query = '''
        SELECT b.id, b.name || ' in ' || a.name as title
        FROM programs a, degrees b 
        WHERE a.id = ? AND a.degree_id = b.id 
    '''
    # When updatign the db, change from 'name' to 'degree'
    new_query = '''
        SELECT b.id, b.degree || ' in ' || a.name as title
        FROM programs a, degrees b 
        WHERE a.id = ? AND a.degree_id = b.id 
    '''
    row = await get_query_one(timed_connection, query, params=(program_id,))
    if row:
        return row
    else:
        return None

######################################################################
####################  SQL-RELATED FUNCTIONS  #########################
######################################################################

######################################################################
#####################  QUERIES & FUNCTIONS  ##########################
######################################################################

######################################################################
#################  EVENT AND HANDLER FUNCTIONS  ######################
######################################################################

#def example_dialog(q):
#    q.page['meta'].dialog = ui.dialog(
#        title='Hello!',
#        name='my_dialog',
#        items=[
#            ui.text('Click the X button to close this dialog.'),
#        ],
#        # Enable a close button (displayed at the top-right of the dialog)
#        closable=True,
#        # Get notified when the dialog is dismissed.
#        events=['dismissed'],
#    )

#def example_dialog_ZZ(q):
#    q.page['meta'].dialog = ui.dialog(
#        title='Hello!',
#        name='my_dialog',
#        items=[
#            ui.text('Click the X button to close this dialog.'),
#        ],
#        # Enable a close button (displayed at the top-right of the dialog)
#        closable=True,
#        # Get notified when the dialog is dismissed.
#        events=['dismissed'],
#    )

async def set_user_vars_given_role_ZZ(q):
    '''
    Get role given a user id and set q.user variables
    '''
    timed_connection = q.user.conn
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
    row = await get_query_one(timed_connection, query, params=(q.user.user_id,))
    q.user.role_id = row['role_id']
    q.user.role = row['role']
    q.user.username = row['username']
    q.user.name = row['fullname']


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

async def build_program_course_list_ZZ(program_df, timed_connection, ge_course_list):
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
        result = await get_query_dict(timed_connection, query, params=required)

        # Update the ge_ids for ARTS, BEH
        updated_data = update_ge_ids(result)

        # Move possible duplicates in a GE category to electives
        # (This should be rare)
        ge_data, elective_data = handle_ge_duplicates(updated_data)

        ge_course_list = update_ge_course_list_from_program(ge_course_list, ge_data)

        return ge_course_list, elective_data

# parallel the utils.get_required_program_courses code
async def get_required_program_courses_no_q_ZZ(timed_connection, student_info):
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
    df = await get_query_df(timed_connection, query, params=(program_id,))
    return df

async def return_program_course_list_df_from_scratch_ZZ(timed_connection, student_info):
    '''
    Function should be updated to work within wave (w/ q, etc.)
    Note: (timed_connection, student_info) are both accessible w/in q, would be better to pass
          program_id for clarity 
    '''
    # Build the Program course list

    # Task 1. Get the required classes from the program
    required_df = await get_required_program_courses_no_q(timed_connection, student_info)

    # Build the GE course list
    # Create a blank list of GE course requirements with all courses set to 'GENERAL'
    query = '''
        SELECT id AS ge_id, 'GENERAL' AS course, requirement, abbr, part, credits, 
            'ge_' || abbr || '_' || part AS course_slot 
        FROM general_education_requirements 
    '''
    ge_course_list = await get_query_dict(timed_connection, query)

    # update with information from student_info['ge']
    ge_course_list = update_ge_list_from_student_info(ge_course_list, student_info)

    # Update the ge_course_list 
    ge_course_list, elective_data = await build_program_course_list(required_df, timed_connection, ge_course_list)

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
    required_df = await get_required_program_courses_no_q(timed_connection, student_info)

    # Build the GE course list
    # Create a blank list of GE course requirements with all courses set to 'GENERAL'
    query = '''
        SELECT id AS ge_id, 'GENERAL' AS course, requirement, abbr, part, credits, 
            'ge_' || abbr || '_' || part AS course_slot 
        FROM general_education_requirements 
    '''
    ge_course_list = await get_query_dict(timed_connection, query)

    # update with information from student_info['ge']
    ge_course_list = update_ge_list_from_student_info(ge_course_list, student_info)

    # Update the ge_course_list 
    ge_course_list, elective_data = await build_program_course_list(required_df, timed_connection, ge_course_list)

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

async def generate_schedule_ZZ(timed_connection, course_df, periods_df):
    '''
    Generate a schedule that respects prerequisites and schedules courses into available periods.
    course_df: requires columns credits, name, session, term, year  !!! 'course' column needs to be renamed 'name' !!!
    '''

    # initialize schedule    
    schedule = []

    ## Handle prerequisites and expand the course list
    ## broken, need to fix!!!
    #course_df = await handle_prerequisites(timed_connection, course_df)

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


######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################

# Module-level constants
DEFAULT_TERMS = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
# Sessions are UMGC-specific
DEFAULT_SESSIONS_PER_TERM = {'WINTER': 3, 'SPRING': 3, 'SUMMER': 2, 'FALL': 3}

def generate_periods_ZZ(
        start_term: str = 'SPRING 2024',
        years: int = 8,
        max_courses: int = 3,
        max_credits: int = 18,
        summer: bool = False,
        sessions: List[int] = [1, 3],
        as_df: bool = False,
        terms: Optional[List[str]] = None,
        sessions_per_term: Optional[Dict[str, Any]] = None
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Generate a periods structure containing information about terms and sessions.

    A periods structure is a list of dictionary objects or a DataFrame containing information about terms and sessions,
    into which we will place classes when scheduling.

    Parameters:
    - start_term (str): First term classes are to be scheduled into.
    - years (int): Number of years to create periods for (this can be larger than needed).
    - max_courses (int): Maximum number of courses per session.
    - max_credits (int): Maximum number of credits per term.
    - summer (bool): Whether attending summer (as default).
    - sessions (List[int]): Which sessions (1-3) to schedule classes in (excluding summer term, which has only sessions 1 & 2).
    - as_df (bool): Return results as Pandas DataFrame if True, otherwise return as list of dictionary objects.
    - terms (Optional[List[str]]): Custom list of terms to use instead of the default.
    - sessions_per_term (Optional[Dict[str, int]]): Custom dictionary of sessions per term to use instead of the default.

    Returns:
    Union[pd.DataFrame, List[Dict[str, Any]]]: Periods structure as specified by as_df parameter.

    Raises:
    ValueError: If input parameters are invalid.

    Note:
    We create all terms a student could potentially attend and set max_courses=0 and max_credits=0 for periods they
    are not attending.
    """
    # Input validation
    if years <= 0:
        raise ValueError('Years must be a positive integer.')
    if max_courses < 0 or max_credits < 0:
        raise ValueError('Max courses and max credits must be non-negative.')
    if not all(1 <= s <= 3 for s in sessions):
        raise ValueError('Sessions must be between 1 and 3.')

    TERMS = terms or DEFAULT_TERMS
    SESSIONS_PER_TERM = sessions_per_term or DEFAULT_SESSIONS_PER_TERM

    try:
        start_term, start_year = start_term.upper().split()
        start_year = int(start_year)
    except ValueError:
        raise ValueError('Invalid start_term format. Expected "TERM YEAR", e.g., "SPRING 2024".')

    if start_term not in TERMS:
        raise ValueError(f'Invalid start term. Must be one of {TERMS}.')

    schedule = []
    id = 1

    max_values = {
        ('SUMMER', True): (max_courses, 2 * (max_credits // 3)),
        ('WINTER', True): (max_courses, max_credits),
        ('SPRING', True): (max_courses, max_credits),
        ('FALL', True): (max_courses, max_credits)
    }

    for year in range(start_year, start_year + years):
        for term_index, term in enumerate(TERMS):
            if year == start_year and term_index < TERMS.index(start_term):
                continue
            
            for session in range(1, SESSIONS_PER_TERM[term] + 1):
                is_valid_session = session in sessions if term != 'SUMMER' else True
                max_courses_value, max_credits_value = max_values.get((term, is_valid_session and (summer or term != 'SUMMER')), (0, 0))
                
                previous = 1 if session == 1 else 2

                schedule.append({
                    'id': id,
                    'term': term,
                    'session': session,
                    'year': year,
                    'max_courses': max_courses_value,
                    'max_credits': max_credits_value,
                    'previous': previous
                })
                id += 1

    if as_df:
        return pd.DataFrame([period.to_dict() for period in schedule])
    else:
        return schedule

def update_periods_ZZ(
        periods: Union[pd.DataFrame, List[Dict[str, Any]]],
        condition: str,
        update_values: Dict[str, Any],
        as_df: bool = False
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Update the 'periods' structure based on a condition.

    Args:
    - periods (Union[pd.DataFrame, List[Dict[str, Any]]]): A DataFrame or list of dictionary objects with periods information.
    - condition (str): A string condition to be evaluated.
    - update_values (Dict[str, Any]): A dictionary of column/attribute names and values to update.
    - as_df (bool): Return results as Pandas DataFrame if True, otherwise return as list of dictionary objects.

    Returns:
    Union[pd.DataFrame, List[Dict[str, Any]]]: Updated periods structure in the format specified by as_df.

    Raises:
    ValueError: If the condition is invalid or if specified columns/attributes don't exist.

    Example:
    # Update max_courses for SPRING 2024 to 0
    update_periods(periods, "term == 'SPRING' and year == 2024", {"max_courses": 0})
    """
    input_is_df = isinstance(periods, pd.DataFrame)
    
    if input_is_df:
        periods = periods.to_dict('records')
    
    try:
        for period in periods:
            if eval(condition, period.to_dict()):
                for key, value in update_values.items():
                    if not hasattr(period, key):
                        raise ValueError(f"Attribute/Column '{key}' not found in periods.")
                    setattr(period, key, value)
    
    except NameError as e:
        raise ValueError(f"Invalid condition: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error updating periods: {str(e)}")
    
    if as_df or input_is_df:
        return pd.DataFrame([period.to_dict() for period in periods])
    else:
        return periods

## Generate periods as DataFrame
#df_periods = generate_periods(as_df=True)
#
## Update periods, input as DataFrame, output as dictionary list
#dictionary_periods = update_periods(df_periods, "term == 'SPRING' and year == 2024", {"max_courses": 0}, as_df=False)
#
## Update periods, input as dictionary list, output as DataFrame
#df_updated = update_periods(dictionary_periods, "term == 'FALL'", {"max_credits": 15}, as_df=True)


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


from typing import List, Dict, Union
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd

@dataclass
class ScheduleEntry:
    id: int
    term: str
    session: int
    year: int
    max_courses: int
    max_credits: int
    previous: int

def generate_periods(
        start_term: str = 'SPRING 2024',
        years: int = 8,
        max_courses: int = 3,
        max_credits: int = 18,
        summer: bool = False,
        sessions: List[int] = [1, 3],
        as_df: bool = True
    ) -> Union[pd.DataFrame, List[Dict]]:
    """
    Generate a periods structure containing information about terms and sessions.

    A periods structure is a list of dictionaries (or a Pandas dataframe) containing information about terms and sessions,
    into which we will place classes when scheduling.

    Parameters:

    - start_term: first term classes are to be scheduled into
    - years: number of years to create periods for (this can be larger than needed)
    - max_courses: maximum number of courses per session
    - max_credits: maximum number of credits per term
    - summer: whether attending summer (as default)
    - sessions: which sessions (1-3) to schedule classes in (excluding summer term, which has only sessions 1 & 2)
    - as_df: return results as Pandas dataframe, otherwise return as list of dictionaries

    Output includes 'previous', a value used to determine placement of prerequisites. Because Sessions 1 & 2 and 
    Sessions 2 & 3 overlap, a Session 2 class cannot have a Session 1 prerequisite, it's previous value is 2 (two
    time-slots previous). Similarly, Session 3 cannot have a Session 2 prerequisite, it's previous value is also 2.
    For all others, the 'previous' value is 1.
    
    Note: We create all terms a student could potentially attend and set max_courses=0 and max_credits=0 for periods they
    are not attending.
    """

    TERMS = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
    SESSIONS_PER_TERM = {'WINTER': 3, 'SPRING': 3, 'SUMMER': 2, 'FALL': 3}

    start_term, start_year = start_term.upper().split()
    start_year = int(start_year)

    schedule = []
    id = 1

    max_values = defaultdict(lambda: (0, 0))
    max_values.update({
        ('SUMMER', True): (max_courses, 2 * (max_credits // 3)),
        ('WINTER', True): (max_courses, max_credits),
        ('SPRING', True): (max_courses, max_credits),
        ('FALL', True): (max_courses, max_credits)
    })

    for year in range(start_year, start_year + years):
        for term_index, term in enumerate(TERMS):
            if year == start_year and term_index < TERMS.index(start_term):
                continue
            
            for session in range(1, SESSIONS_PER_TERM[term] + 1):
                is_valid_session = session in sessions if term != 'SUMMER' else True
                max_courses_value, max_credits_value = max_values[(term, is_valid_session and (summer or term != 'SUMMER'))]
                
                previous = 1 if session == 1 else 2

                schedule.append(ScheduleEntry(
                    id=id,
                    term=term,
                    session=session,
                    year=year,
                    max_courses=max_courses_value,
                    max_credits=max_credits_value,
                    previous=previous
                ))
                id += 1

    if as_df:
        return pd.DataFrame([vars(entry) for entry in schedule])
    else:
        return [vars(entry) for entry in schedule]

from typing import Union, List, Dict, Any
import pandas as pd

def update_periods(
        periods: Union[pd.DataFrame, List[Dict[str, Any]]],
        condition: str,
        update_values: Dict[str, Any]
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Update the 'periods' structure based on a condition.

    Args:
        periods (Union[pd.DataFrame, List[Dict[str, Any]]]): A DataFrame or list of dictionaries with periods information.
        condition (str): A string condition to be evaluated.
        update_values (Dict[str, Any]): A dictionary of column names and values to update.

    Returns:
        Union[pd.DataFrame, List[Dict[str, Any]]]: Updated periods structure in the same format as the input.

    Example:
        # Update max_courses for SPRING 2024 to 0
        update_periods(periods, "term == 'SPRING' and year == 2024", {"max_courses": 0})
    """
    # Check whether input periods is a DataFrame
    is_dataframe = isinstance(periods, pd.DataFrame)
    
    if not is_dataframe:
        periods = pd.DataFrame(periods)
    
    try:
        # Apply conditions
        mask = periods.eval(condition)
        
        # Update values
        for key, value in update_values.items():
            if key not in periods.columns:
                raise ValueError(f"Column '{key}' not found in periods.")
            periods.loc[mask, key] = value
    
    except Exception as e:
        raise ValueError(f"Error updating periods: {str(e)}")
    
    # Return in the original format
    if not is_dataframe:
        return periods.to_dict(orient='records')
    else:
        return periods

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


###############################################################
#####################  GE FUNCTIONS  ##########################
###############################################################

async def summarize_ge_ZZ(student_info):
    """
    Summarize General Education (GE) to keep our dashboard updated.
    If 'ge' doesn't exist in student_info, it creates it using create_ge function.

    Args:
        student_info: The student_info dictionary (most likely sourced from q.user)

    Raises:
        Exception: If there's an error during the GE summarization process
    """
    try:
        # Ensure ge exists in student_info
        if 'ge' not in student_info:
            student_info['ge'] = initialize_ge()

        ge = student_info['ge']
        
        # Initialize total and summary if they don't exist
        if 'total' not in ge:
            ge['total'] = {}
        if 'summary' not in ge:
            ge['summary'] = {}

        total = ge['total']
        summary = ge['summary']

        # Define areas and their requirements
        areas = {
            'arts': {'total': 6, 'requirements': ['1', '2']},
            'beh': {'total': 6, 'requirements': ['1', '2']},
            'bio': {'total': 7, 'requirements': ['1a', '1b', '1c', '2']},
            'comm': {'total': 12, 'requirements': ['1', '2', '3', '4']},
            'math': {'total': 3, 'requirements': ['1']},
            'res': {'total': 7, 'requirements': ['1', '2', '3', '3a', '3b', '3c']}
        }

        for area, info in areas.items():
            total[area] = info['total']
            if area == 'bio':
                summary[area] = (
                    (ge[area].get('1a') is not None or 
                     ge[area].get('1b') is not None or 
                     ge[area].get('1c') is not None)
                ) * 4 + (ge[area].get('2') is not None) * 3
            elif area == 'res':
                summary[area] = (
                    (ge[area].get('1') is not None) * 3 + 
                    (ge[area].get('2') is not None) * 1 +
                    (3 if (ge[area].get('3') is not None) else sum(
                        ge[area].get(req) is not None for req in ['3a', '3b', '3c']
                    ))
                )
            else:
                summary[area] = sum(ge[area].get(req) is not None for req in info['requirements']) * (info['total'] // len(info['requirements']))

        # Update student_info with the new calculations
        student_info['ge']['total'] = total
        student_info['ge']['summary'] = summary

        return student_info

    except Exception as e:
        error_message = f"Error in summarize_ge: {str(e)}"
        print(error_message)  # For logging purposes
        # You might want to set an error flag or handle the exception in a way that fits your application
        raise  # Re-raise the exception for now

async def update_ge_ids_ZZ(data):
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

def handle_ge_duplicates_ZZ(data):
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

def update_ge_list_from_student_info_ZZ(ge_course_list, student_info):
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

def update_ge_course_list_from_program_ZZ(ge_course_list, updates):
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

def update_student_info_ge_ZZ(student_info, ge_course_list):
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

def update_bio_df_ZZ(df):
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

########################################################################
#################  COURSE PREREQUISITE FUNCTIONS  ######################
########################################################################

async def update_prerequisites_ZZ(timed_connection, prereq_name):
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
    result = await get_query_dict(timed_connection, query, params=(prereq_name, ))
    if result:
        return result
    else:
        return None

def parse_prerequisites_ZZ(prereq_string):
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

def insert_prerequisite_ZZ(df, i, name):
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
def prep_course_list_ZZ(df):
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

async def handle_prerequisites_ZZ(timed_connection, course_df):
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

        prereq_info = await update_prerequisites(timed_connection, prereq_name)
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


#######################################################
#################  D3 FUNCTIONS  ######################
#######################################################

## debug tools.d3, not working yet, staying with tools.d3_old
##from tools.d3_old import create_html_template, prepare_d3_data
#from tools.d3 import create_html_template, prepare_d3_data
#
#__all__ = [
#    'create_html_template', 
#    'prepare_d3_data'
#]
######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################

from typing import Union, List, Dict, Any
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd

@dataclass
class ScheduleEntry:
    id: int
    term: str
    session: int
    year: int
    max_courses: int
    max_credits: int
    previous: int

def generate_periods(
        start_term: str = 'SPRING 2024',
        years: int = 8,
        max_courses: int = 3,
        max_credits: int = 18,
        summer: bool = False,
        sessions: List[int] = [1, 3],
        as_df: bool = True
    ) -> Union[pd.DataFrame, List[Dict]]:
    """
    Generate a periods structure containing information about terms and sessions.

    A periods structure is a list of dictionaries (or a Pandas dataframe) containing information about terms and sessions,
    into which we will place classes when scheduling.

    Parameters:

    - start_term: first term classes are to be scheduled into
    - years: number of years to create periods for (this can be larger than needed)
    - max_courses: maximum number of courses per session
    - max_credits: maximum number of credits per term
    - summer: whether attending summer (as default)
    - sessions: which sessions (1-3) to schedule classes in (excluding summer term, which has only sessions 1 & 2)
    - as_df: return results as Pandas dataframe, otherwise return as list of dictionaries

    Output includes 'previous', a value used to determine placement of prerequisites. Because Sessions 1 & 2 and 
    Sessions 2 & 3 overlap, a Session 2 class cannot have a Session 1 prerequisite, it's previous value is 2 (two
    time-slots previous). Similarly, Session 3 cannot have a Session 2 prerequisite, it's previous value is also 2.
    For all others, the 'previous' value is 1.
    
    Note: We create all terms a student could potentially attend and set max_courses=0 and max_credits=0 for periods they
    are not attending.
    """

    TERMS = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
    SESSIONS_PER_TERM = {'WINTER': 3, 'SPRING': 3, 'SUMMER': 2, 'FALL': 3}

    start_term, start_year = start_term.upper().split()
    start_year = int(start_year)

    schedule = []
    id = 1

    max_values = defaultdict(lambda: (0, 0))
    max_values.update({
        ('SUMMER', True): (max_courses, 2 * (max_credits // 3)),
        ('WINTER', True): (max_courses, max_credits),
        ('SPRING', True): (max_courses, max_credits),
        ('FALL', True): (max_courses, max_credits)
    })

    for year in range(start_year, start_year + years):
        for term_index, term in enumerate(TERMS):
            if year == start_year and term_index < TERMS.index(start_term):
                continue
            
            for session in range(1, SESSIONS_PER_TERM[term] + 1):
                is_valid_session = session in sessions if term != 'SUMMER' else True
                max_courses_value, max_credits_value = max_values[(term, is_valid_session and (summer or term != 'SUMMER'))]
                
                previous = 1 if session == 1 else 2

                schedule.append(ScheduleEntry(
                    id=id,
                    term=term,
                    session=session,
                    year=year,
                    max_courses=max_courses_value,
                    max_credits=max_credits_value,
                    previous=previous
                ))
                id += 1

    if as_df:
        return pd.DataFrame([vars(entry) for entry in schedule])
    else:
        return [vars(entry) for entry in schedule]

def update_periods(
        periods: Union[pd.DataFrame, List[Dict[str, Any]]],
        condition: str,
        update_values: Dict[str, Any]
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Update the 'periods' structure based on a condition.

    Args:
        periods (Union[pd.DataFrame, List[Dict[str, Any]]]): A DataFrame or list of dictionaries with periods information.
        condition (str): A string condition to be evaluated.
        update_values (Dict[str, Any]): A dictionary of column names and values to update.

    Returns:
        Union[pd.DataFrame, List[Dict[str, Any]]]: Updated periods structure in the same format as the input.

    Example:
        # Update max_courses for SPRING 2024 to 0
        update_periods(periods, "term == 'SPRING' and year == 2024", {"max_courses": 0})
    """
    # Check whether input periods is a DataFrame
    is_dataframe = isinstance(periods, pd.DataFrame)
    
    if not is_dataframe:
        periods = pd.DataFrame(periods)
    
    try:
        # Apply conditions
        mask = periods.eval(condition)
        
        # Update values
        for key, value in update_values.items():
            if key not in periods.columns:
                raise ValueError(f"Column '{key}' not found in periods.")
            periods.loc[mask, key] = value
    
    except Exception as e:
        raise ValueError(f"Error updating periods: {str(e)}")
    
    # Return in the original format
    if not is_dataframe:
        return periods.to_dict(orient='records')
    else:
        return periods

from contextlib import asynccontextmanager
from h2o_wave import Q, ui
from typing import Any, Dict, Callable, List, Optional, Union
#import asyncio
#import logging
import numpy as np
import pandas as pd
#import sqlite3
#import time
#import warnings
import backend


#######################################################
####################  Q FUNCTIONS  ####################
#######################################################

########################################################
####################  MENU QUERIES  ####################
########################################################

### These queries are used in app.py for menus and  ###
### render_dropdown_menus_horizontal                ###

degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
area_query = '''
    SELECT DISTINCT menu_area_id AS name, area_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ?
'''
program_query_old = '''
    SELECT program_id AS name, program_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''
program_query = '''
    SELECT program_id AS name, program_name AS label, disabled
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''
########################################################
####################  LAYOUT CARDS  ####################
########################################################

def return_header_card(q: Q) -> ui.header_card:
    '''
    Returns a header card with tabs for different roles: student, coach, admin
    Called in app.py.
    '''
    student_tab_items = [
        ui.tab(name='#login',     label='[Login]'),
        ui.tab(name='#home',      label='Home'),
        ui.tab(name='#skills',    label='Skills'),
        ui.tab(name='#program',   label='Program'),
        ui.tab(name='#course',    label='Courses'),
        ui.tab(name='#ge',        label='GE'), 
        ui.tab(name='#electives', label='Electives'), # 'Select Courses'
        ui.tab(name='#schedule',  label='Schedule')
    ]

    q.user.role = 'student'
    tab_items = student_tab_items
    textbox_label = 'Name'
    #textbox_value = q.user.name
    textbox_value = "John Doe"

    # Determine the current page
    current_page = q.args['#'] if '#' in q.args else 'home'

    box='header'
    card = ui.header_card(
        box=box, 
        title='UMGC', 
        subtitle='Registration Assistant',
        image=q.app.umgc_logo,
        secondary_items=[
            ui.tabs(
                name='tabs', 
                value=f'#{current_page}',
                link=True, 
                items=tab_items,
            ),
        ],
        items=[
            ui.textbox(
                name='textbox_default', 
                label=textbox_label,
                value=textbox_value, 
                disabled=True
            )
        ]
    )
    return card

def return_login_header_card(q: Q) -> ui.header_card:
    '''
    Create a header card with a login tab.
    '''

    login_tab_items = [
        ui.tab(name='#login',     label='Login'),
    ]
    tab_items = login_tab_items

    card = ui.header_card(
        box='header', 
        title='UMGC', 
        subtitle='Registration Assistant',
        image=q.app.umgc_logo,
        secondary_items=[
            ui.tabs(
                name='tabs', 
                value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, 
                items=tab_items,
            ),
        ],
    )
    return card

def return_footer_card() -> ui.footer_card:
    '''
    Footer card with caption for entire app.
    Called in app.py.
    '''
    card = ui.footer_card(
        box='footer',
        caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
        '''
    )
    return card

##########################################################
####################  HOME PAGE ##########################
##########################################################
def create_program_selection_card(location='horizontal', width='60%'):
    """
    Create the program selection card
    """
    card = ui.form_card(
        box=ui.box(location, width=width),
        #name='program_selection',
        #title='Select a UMGC Program',
        #caption='Choose an option to explore UMGC programs',
        #category='Program Selection',
        #icon='Education',
        items=[
            ui.text_xl(content='**Select a UMGC Program**'),
            ui.link(label='Option 1: Explore programs on your own', path='/#program'),
            ui.link(label='Option 2: Select a program based on your skills', path='/#skills'),
            ui.link(label='Option 3: Select a program based on your interests', disabled=True),
            ui.link(label='Option 4: Select a program that finished your degree the quickest', disabled=True)
        ]
    )
    return card


##############################################################
####################  PROGRAMS PAGE ##########################
##############################################################

async def render_dropdown_menus_horizontal(q, location='horizontal', menu_width='300px'):
    '''
    Create menus for selecting degree, area of study, and program
    '''

    timed_connection = q.user.conn    
    enabled_degree = {"Bachelor's", "Undergraduate Certificate"}
    disabled_programs = q.app.disabled_program_menu_items

    # enforcing string because I've got a bug somewhere (passing an int instead of str)
    dropdowns = ui.inline([
        ui.dropdown(
            name='menu_degree',
            label='Degree',
            value=str(q.user.student_info['menu']['degree']) if \
                (q.user.student_info['menu']['degree'] is not None) else q.args.menu_degree,
            trigger=True,
            width='230px',
            choices = await backend.get_choices(timed_connection, degree_query, disabled=None, enabled=enabled_degree)
        ),
        ui.dropdown(
            name='menu_area',
            label='Area of Study',
            value=str(q.user.student_info['menu']['area_of_study']) if \
                (str(q.user.student_info['menu']['area_of_study']) is not None) else \
                str(q.args.menu_area),
            trigger=True,
            disabled=False,
            width='250px',
            choices=None if (q.user.student_info['menu']['degree'] is None) else \
                await backend.get_choices(timed_connection, area_query, 
                                          params=(q.user.student_info['menu']['degree'],))
        ),
        ui.dropdown(
            name='menu_program',
            label='Program',
            value=str(q.user.student_info['menu']['program']) if \
                (q.user.student_info['menu']['program'] is not None) else q.args.menu_program,
            trigger=True,
            disabled=False,
            width='300px',
            choices=None if (q.user.student_info['menu']['area_of_study'] is None) else \
                await backend.get_choices(timed_connection, program_query, 
                    params=(q.user.student_info['menu']['degree'], q.user.student_info['menu']['area_of_study']),
                    disabled=disabled_programs
                )
        )
    ], justify='start', align='start')

    command_button = ui.button(
        name='command_button', 
        label='Select', 
        disabled=False,
        commands=[
            ui.command(name='select_program', label='Select Program'),
            #ui.command(name='classes_menu', label='Classes', 
            #    items=[
            #        ui.command(name='add_ge', label='Add GE'),
            #        ui.command(name='add_elective', label='Add Electives'),  
            #]),
            ui.command(name='add_ge', label='Add GE'),
            ui.command(name='add_elective', label='Add Electives')  
    ])

    card = ui.form_card(
        box = location,
        items = [
            #ui.text_xl('Browse Programs'),
            ui.inline([
                dropdowns, 
                command_button
            ],
            justify='between', 
            align='end')
        ]
    )
        
    add_card(q, 'dropdown', card)

    ########################

############################################################
####################  SKILLS PAGE ##########################
############################################################

async def return_skills_menu(timed_connection, location='vertical', width='300px', inline=False):
    '''
    Create skills choice menu
    Will send the selected skills to the database query and return a list of courses

    '''
    #timed_connection = q.user.conn
    skills_query = 'SELECT id AS name, name AS label, explanation AS tooltip FROM Skills'
    choices = await backend.get_choices_new(timed_connection, skills_query, disabled={""}, tooltip=False)

    card = ui.form_card(
        box = ui.box(location, width=width),
        items=[
            #                ui.separator(),
            ui.checklist(
                name='skills_checklist',
                label='Skills',
                inline=inline,
                choices = choices,
            ),
            #ui.number(name='result_limit', label='Number of results', min=5, max=15, step=1, value=7),
            #ui.inline(items=[
            ui.button(name='submit_skills_menu', label='Submit', primary=True),
            ui.button(name='reset_skills_menu', label='Reset', primary=False),
            #])
        ]
    )
    return card

async def return_skills_table(results, location='horizontal'):
    """
    Return the skills table given input of results from get_query_dict
    Called by submit_skills_menu
    """
    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='program', label='Program', searchable=False, min_width='250'),
        ui.table_column(name='score', label='Score', searchable=False, min_width='100'), 
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='explore_skills_program', label='Explore Program'),
                    ui.command(name='select_skills_program', label='Select Program'),
                ]
        ))
    ]
    rows = [
        ui.table_row(
            name=str(row['id']),
            #name=row['program'],
            cells=[
                #str(row['seq']),
                row['program'],
                #str(row['TotalScore']),
                f"{row['TotalScore']:.3f}"
            ]
        ) for row in results
    ]
    card = ui.form_card(
        box=location,
        items=[
            #ui.inline(justify='between', align='center', items=[
            #    ui.text(title, size=ui.TextSize.L),
            #    ui.button(name='schedule_coursework', label='Schedule', 
            #        #caption='Description', 
            #        primary=True, disabled=False)
            #]),
            ui.table(
                name='program_skills_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                columns=columns,
                rows=rows
            )
        ]
    )
    return card


######################################################################
#################  EVENT AND HANDLER FUNCTIONS  ######################
######################################################################


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


######################################################
####################  Login page  ####################
######################################################

@on('#login')
async def login(q: Q):
    clear_cards(q)
    card_height = '400px'

    #q.page['header'] = cards.return_login_header_card(q)
    #cards.render_welcome_back_card(q, width='400px', height=card_height, location='top_vertical')

    #cards.render_login_welcome_card(q, cardname='welcome_login', location='top_horizontal')
    card = cards.return_login_welcome_card(q, location='top_horizontal', width='100%')
    add_card(q, 'login/welcome', card)

    card = await cards.return_user_login_dropdown(q, location='horizontal', menu_width='300px')
    add_card(q, 'login/demo_login', card)

    if q.app.debug:
        q.page['debug'] = await cards.return_debug_card(q)

    await q.page.save()

# respond to sample user selection
@on()
async def select_sample_user(q: Q):
    '''
    Respond to sample user selection from cards.render_user_dropdown
    '''
    choice = q.args.choice_group
    logging.info('The selected user is: ' + choice)
    q.user.user_id = int(choice)
    
    # initialize all student_info stuff
    await utils.reset_student_info_data(q)
    q.user.student_info_populated = False

    # Guest has user_id = 0
    if q.user.user_id > 0:
        q.user.logged_in = True
        # get role for logged in user
        await utils.set_user_vars_given_role(q) # assigns q.user.role_id, q.user.username, q.user.name

        # Admin path:
        #   - Can add users
        #   - Can set or change user roles
        #   - Can do other administrative tasks
        #   - Can do everything a coach can do
        #
        # Coach path:
        #   - Can add students
        #   - Using pulldown menu to select student,
        #     can profile, select program, select courses, schedule courses for students
        #
        # Student path:
        #   - Can profile, select program, select courses, schedule courses for themselves
        #
        # Guest path:
        #   - Can do everything a student can do except save their info to the database 
        #
        if q.user.role in ['coach', 'admin']:
            pass
        elif q.user.role == 'student':
            await utils.populate_student_info(q, q.user.user_id)
            #await utils.populate_q_student_info(q, q.user.conn, q.user.user_id)
            q.user.student_info_populated = True

    else:
        #await utils.reset_student_info_data(q) # already done?
        pass

    # update header 
    q.page['header'] = cards.return_header_card(q)

    # update debug card
    if q.app.debug:
        q.page['debug'].content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.client value:
{q.client}

### q.user.student_info values:
{q.user.student_info}

### q.user values:
{q.user}
        '''

    # redirect to #home route
    q.page['meta'].redirect = '#home'    
        
    await q.page.save()



async def admin_skills(q: Q) -> None:
    await student_skills(q)

async def coach_skills(q: Q) -> None:
    await student_skills(q)

async def student_skills(q: Q) -> None:
    clear_cards(q)
    timed_connection = q.user.conn
    card = await return_skills_menu(timed_connection, location='vertical', width='300px')
    add_card(q, 'skill_card', card)
    await q.page.save()

    #if q.user.student_info['menu']['degree']:
    #    degree_id = int(q.user.student_info['menu']['degree'])

    #add_card(q, 'explore_programs', ui.form_card(
    #    box=ui.box('top_vertical', width='100%'),
    #    items=[
    #        ui.text('**EXPLORE PROGRAMS** using the menus below. Click **Select > Save Program** to select your program.'),
    #        #ui.text('Explore Majors. Click **Select > Save Program** to select your program.'),
    #    ]
    #))    
    #await frontend.render_dropdown_menus_horizontal(q, location='top_vertical', menu_width='300px')


    ## render program after getting the list of programs
    #if q.user.student_info['program_id']:
    #    await cards.render_program(q)

@on('#skills')
async def skills(q: Q):
    clear_cards(q) # will use in the individual functions

    timed_connection = q.user.conn
    card = await return_skills_menu(timed_connection, location='vertical', width='300px')
    add_card(q, 'skill_card', card)
#    await q.page.save()


#    if q.user.role == 'admin':
#        # admin program page
#        await admin_skills(q)
#
#    elif q.user.role == 'coach':
#        # coach program page
#        await coach_skills(q)
#        
#    elif q.user.role == 'student':
#        # student program page
#        await student_skills(q)
#        
#    else:
#        # need to raise an error here
#        pass
#    
#    if q.app.debug_program:
#        add_card(q, 'skills_debug', await cards.return_debug_card(q))

    await q.page.save()
from h2o_wave import Q, ui, copy_expando, expando_to_dict
from contextlib import asynccontextmanager
from h2o_wave import Q, ui
from typing import Any, Dict, Callable, List, Optional, Union
import asyncio
import logging
import numpy as np
import pandas as pd
import sqlite3
import time
import warnings

import backend
from backend import get_choices 


#from backend import initialize_ge, initialize_student_info, initialize_student_data
from backend import TimedSQLiteConnection, _base_query, get_query, get_query_one, \
    get_query_dict, get_query_course_dict, get_query_df

from frontend import add_card, clear_cards

import utils
#from utils import get_query, get_query_one, get_query_dict, get_query_df
#from utils import generate_periods, update_periods, generate_schedule, handle_prerequisites, \
#    schedule_courses_old, update_courses, move_courses_forward
#import sys

## Note: The functions appended with _ZZ were a new version but it broke somewhere. I will edit 
## and introduce them one-by-one in order to make sure nothing is broken.

######################################################################
##################  TEST FUNCTIONS TO BE DELETED  ####################
######################################################################

######################################################################
##################  DEFINITIONS AND QUERIES  #########################
######################################################################

UMGC_tags = [
    ui.tag(label='ELECTIVE', color='#fdbf38', label_color='$black'),
    ui.tag(label='REQUIRED', color='#a30606'),
    ui.tag(label='MAJOR', color='#135f96'),
#    ui.tag(label='GENERAL', color='#3c3c43'), # dark gray
#    ui.tag(label='GENERAL', color='#787800'), # khaki   
    ui.tag(label='GENERAL', color='#3b8132', label_color='$white'), # green   
]

### These queries are used in app.py for menus and  ###
### render_dropdown_menus_horizontal                ###

degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
area_query = '''
    SELECT DISTINCT menu_area_id AS name, area_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ?
'''
program_query_old = '''
    SELECT program_id AS name, program_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''
program_query = '''
    SELECT program_id AS name, program_name AS label, disabled
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''

######################################################################
####################  STANDARD WAVE CARDS  ###########################
######################################################################


#######################################################
####################  DEBUG CARDS  ####################
#######################################################

async def return_debug_card_ZZ(q, box='3 3 1 1', location='debug', width='100%', height='300px'):
    '''
    Show q.client information in a card for debugging
    '''
    expando_dict = expando_to_dict(q.user)
    q_user_filtered = {k: v for k, v in expando_dict.items() if k not in ['student_info', 'student_data']}

    #### q.user.student_data values:
    #{q.user.student_data}
    flex = q.app.flex

    if flex:
        box = ui.box(location, width=width, height=height)

    content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.client value:
{q.client}

### q.user.student_info values:
{q.user.student_info}

### q.user.student_data values:

#### Required:
{q.user.student_data['required']}

#### Schedule:
{q.user.student_data['schedule']}

### remaining q.user values:
{q_user_filtered}

### q.user values

### q.app values:
{q.app}

    '''
    card = ui.markdown_card(
        box,
        title='Debug Information', 
        content=content 
    )
    return card

async def return_debug_card(q, box='3 3 1 1', location='debug', width='100%', height='300px'):
    '''
    Show q.client information in a card for debugging
    '''
    expando_dict = expando_to_dict(q.user)
    q_user_filtered = {k: v for k, v in expando_dict.items() if k not in ['student_info', 'student_data']}

    #### q.user.student_data values:
    #{q.user.student_data}
    flex = q.app.flex

    if flex:
        box = ui.box(location, width=width, height=height)

    content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.client value:
{q.client}

### q.user.student_info values:
{q.user.student_info}

### q.user.student_data values:

#### Required:
{q.user.student_data['required']}

#### Schedule:
{q.user.student_data['schedule']}

### remaining q.user values:
{q_user_filtered}

### q.user values

### q.app values:
{q.app}

    '''
    card = ui.markdown_card(
        box,
        title='Debug Information', 
        content=content 
    )
    return card

###############################################################
####################  LOGIN PAGE  #############################
###############################################################

def return_login_welcome_card(location: str = 'top_vertical', width: str = '100%') -> ui.form_card:
    """
    Login welcome card
    """
    box = ui.box(location, width=width)

    card = ui.form_card(
        box=box,
        items=[
            ui.text_l('Select a user below to simulate their login.')
        ]
    )
    return card

def render_login_welcome_card(q, location='top_vertical', width='100%', box='1 2 7 1',
                              cardname='login/welcome'):
    card = return_login_welcome_card(q, location, width, box)
    add_card(q, cardname, card)

async def return_user_login_dropdown(q, box=None, location='horizontal', menu_width='300px'):
    '''
    Function to create a dropdown menu of sample users to demo the wave app
    '''
    timed_connection = q.user.conn
    flex = q.app.flex
    if flex:
        box = location

    ## Debug This
    #query = '''
    #    SELECT a.id AS name, 
    #        trim(a.firstname || ' ' || a.lastname || ' (' || b.role || ')') AS label
    #    FROM users a, roles b
    #    WHERE a.role_id = b.id
    #'''
    #choicesdict=await utils.get_choices(timed_connection, query)

    ## tmp fix for demo
    ## need to update 'populate_sample_users_and_students.py'
    choicesdict = [
        #{'name': 1, 'label': 'Admin (admin role)'},
        #{'name': 2, 'label': 'Coach (coach role)', 'disabled': True},
        {'name': 3, 'label': 'John Doe (New Student)'},
        {'name': 4, 'label': 'John Doe (After entering personal information)'},
        {'name': 5, 'label': 'John Doe (After selecting program)'},
        {'name': 6, 'label': 'John Doe (After selecting courses)'},
        {'name': 7, 'label': 'John Doe (After creating schedule)'},
        {'name': 8, 'label': 'Jane Doe (Transfer student with program selected)'},
        #{'name': 9, 'label': 'Tom Doe (military student, no program selected)'},
    ]

    choices = [ui.choice(str(row['name']), row['label']) for row in choicesdict]

    choicegroup = ui.choice_group(
        name='choice_group', 
        label='Pick one', 
        required=True, 
        choices=choices
    )
    button = ui.button(name='select_sample_user', label='Submit', primary=True)

    #dropdown = ui.dropdown(
    #    name='sample_user',
    #    label='Sample User',
    #    value=q.args.sample_user,
    #    trigger=True,
    #    placeholder='(Select)',
    #    width=menu_width,
    #    choices=choices
    #)

    card = ui.form_card(box=box,
        items=[
            ui.text_xl('Example users'),
            choicegroup,
            #dropdown, 
            ui.separator(),
            button
        ]
    ) 
    return card

async def return_user_login_dropdown_old(q, box=None, location='horizontal', menu_width='300px'):
    '''
    Function to create a dropdown menu of sample users to demo the wave app
    '''
    timedConnection = q.user.conn
    flex = q.app.flex
    if flex:
        box = location

    #query = '''
    #    SELECT a.id AS name, 
    #        trim(a.firstname || ' ' || a.lastname || ' (' || b.role || ')') AS label
    #    FROM users a, roles b
    #    WHERE a.role_id = b.id
    #'''
    #choicesdict=await utils.get_choices(timedConnection, query)

    ## tmp fix for demo
    ## need to update 'populate_sample_users_and_students.py'
    choicesdict = [
        #{'name': 1, 'label': 'Admin (admin role)'},
        #{'name': 2, 'label': 'Coach (coach role)', 'disabled': True},
        {'name': 5, 'label': 'John Doe (New Student)'},
        {'name': 6, 'label': 'John Doe (personal information entered)'},
        {'name': 7, 'label': 'John Doe (program selected)'},
        {'name': 3, 'label': 'John Doe (schedule created)'},
        {'name': 4, 'label': 'John Doe (transfer student with program selected)'},
        #{'name': 6, 'label': 'Tom Doe (military student, no program selected)'},
    ]

    choices = [ui.choice(str(row['name']), row['label']) for row in choicesdict]

    choicegroup = ui.choice_group(
        name='choice_group', 
        label='Pick one', 
        required=True, 
        choices=choices
    )
    button = ui.button(name='select_sample_user', label='Submit', primary=True)

    #dropdown = ui.dropdown(
    #    name='sample_user',
    #    label='Sample User',
    #    value=q.args.sample_user,
    #    trigger=True,
    #    placeholder='(Select)',
    #    width=menu_width,
    #    choices=choices
    #)

    card = ui.form_card(box=box,
        items=[
            ui.text_xl('Example users'),
            choicegroup,
            #dropdown, 
            ui.separator(),
            button
        ]
    ) 
    return card

async def render_user_login_dropdown(q, box=None, location='horizontal', menu_width='300px',
                                     cardname='login/demo_login'):
    '''
    Function to create a dropdown menu of sample users to demo the wave app
    '''
    card = await return_user_login_dropdown(q, box, location, menu_width)
    add_card(q, cardname, card)

def return_login_welcome_card_ZZ(q, location='top_vertical', width='100%', box='1 2 7 1'):
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)

    card = ui.form_card(
        box=box,
        items=[
            ui.text_l('Select a user below to simulate their login.')
            #ui.text('(The Home page will collect student information)')
        ]
    )
    return card

def render_login_welcome_card_ZZ(q, location='top_vertical', width='100%', box='1 2 7 1',
                              cardname='login/welcome'):
    card = return_login_welcome_card(q, location, width, box)
    add_card(q, cardname, card)


async def render_user_login_dropdown_ZZ(q, box=None, location='horizontal', menu_width='300px',
                                     cardname='login/demo_login'):
    '''
    Function to create a dropdown menu of sample users to demo the wave app
    '''
    card = await return_user_login_dropdown(q, box, location, menu_width)
    add_card(q, cardname, card)

##############################################################
####################  HOME PAGE  #############################
##############################################################

def return_task1_card_ZZ(location='top_horizontal', width='350px'):
    '''
    Task 1 Card repeated on home page and home/1, home/2, etc.
    '''
    task_1_caption = f'''
### Enter selected information 
- Residency status
- Attendance type
- Financial aid
- Transfer credits
'''
    card = ui.wide_info_card(
        box=ui.box(location, width=width),
        name='task1',
        icon='AccountActivity',
        title='Task 1',
        caption=task_1_caption
    )
    return card

def render_task1_card_ZZ(q, location='top_horizontal', width='350px'):
    '''
    Task 1 Card repeated on home page and home/1, home/2, etc.
    '''
    card = return_task1_card(location=location, width=width)
    add_card(q, 'home/task1', card=card)

def return_demographics_card1_ZZ(card_height = '400px', location='top_horizontal', width='400px'):
    '''
    Demographics card for home page
    '''
    resident_choices = [
        ui.choice('A', 'In-State'),
        ui.choice('B', 'Out-of-State'),
        ui.choice('C', 'Military'),
    ]
    attendance_choices = [
        ui.choice('A', 'Full Time'),
        ui.choice('B', 'Part Time'),
        ui.choice('C', 'Evening only'),
    ]
    card = ui.form_card(
        box=ui.box(location, width=width),
        items=[
            ui.text_xl('Tell us about yourself'),
            ui.text('This information will help us build a course schedule'),
            ui.inline(items=[
                #ui.choice_group(name='resident_status', label='My Resident status is', choices=resident_choices, required=True),
                #ui.text_xl(''),
                ui.choice_group(name='attendance', label='I will be attending', choices=attendance_choices, required=True),
            ]),
            ui.separator(name='my_separator', width='100%', visible=True),
            ui.checkbox(name='financial_aid', label='I will be using Financial Aid'),
            ui.checkbox(name='transfer_credits', label='I have credits to transfer'),
            #ui.separator(),
            #ui.text('(Other appropriate questions here...)'),
            #ui.separator(),
            ui.button(name='next_demographic_1', label='Next', primary=True),
        ]
    )
    return card

def render_demographics_card1_ZZ(q, card_height = '400px', location='top_horizontal', width='400px'):
    '''
    Demographics card for home page
    '''
    card = return_demographics_card1(location=location, width=width)
    add_card(q, 'home/demographics1', card)

def return_demographics_card2_ZZ(location='top_horizontal', width='400px'):
    '''

    '''
    resident_choices = [
        ui.choice('A', 'In-State'),
        ui.choice('B', 'Out-of-State'),
        ui.choice('C', 'Military'),
    ]
    card = ui.form_card(
        box=ui.box(location, width=width),
        items=[
            ui.text_xl('Tell us more about yourself:'),
            ui.text('This information will help us estimate your tuition costs'),
            ui.choice_group(name='resident_status', label='My Resident status is', choices=resident_choices, required=True),
            ui.separator(label='', name='my_separator2', width='100%', visible=True),
            ui.button(name='next_demographic_2', label='Next', primary=True),
        ]
    )
    return card

def demographics2_ZZ(q):
    '''

    '''
    resident_choices = [
        ui.choice('A', 'In-State'),
        ui.choice('B', 'Out-of-State'),
        ui.choice('C', 'Military'),
    ]
    add_card(q, 'demographics2', 
        ui.form_card(
            box=ui.box('top_horizontal', width='400px'),
            items=[
                ui.text_xl('Tell us more about yourself:'),
                ui.text('This information will help us estimate your tuition costs'),
                ui.choice_group(name='resident_status', label='My Resident status is', choices=resident_choices, required=True),
                ui.separator(label='', name='my_separator2', width='100%', visible=True),
                ui.button(name='next_demographic_2', label='Next', primary=True),
            ]
        )
    )

def return_tasks_card_ZZ(checked=0, location='top_horizontal', width='350px', height='400px'):
    '''
    Return tasks optionally checked off
    '''
    icons = ['Checkbox', 'Checkbox', 'Checkbox', 'Checkbox']
    checked_icon = 'CheckboxComposite'
    # checked needs to be a value between 0 and 4
    if checked > 0:
        for i in range(checked):
            icons[i] = checked_icon

    card = ui.form_card(
        box=ui.box(location, width=width, height=height),
        items=[
            #ui.text(title + ': Credits', size=ui.TextSize.L),
            ui.text('Task Tracker', size=ui.TextSize.L),
            ui.stats(items=[ui.stat(
                label=' ',
                value='1. Information',
                caption='Tell us about yourself',
                icon=icons[0],
                icon_color='#135f96'
            )]),
            ui.stats(items=[ui.stat(
                label=' ',
                value='2. Select Program',
                caption='Decide what you want to study',
                icon=icons[1],
                icon_color='#a30606'
            )]),
            ui.stats(items=[ui.stat(
                label=' ',
                value='3. Add Courses',
                caption='Add GE and Electives',
                icon=icons[2],
                #icon_color='#787800'
                icon_color='#3c3c43'
            )]),
            ui.stats(items=[ui.stat(
                label=' ',
                value='4. Create Schedule',
                caption='Optimize your schedule',
                icon=icons[3],
                icon_color='#da1a32'
            )]),
        ])
    return card

def tasks_unchecked_ZZ(q):
    '''
    All tasks unchecked
    '''

    add_card(q, 'unchecked_tasks', 
        ui.form_card(
            box=ui.box('top_horizontal', width='350px', height='400px'),
            items=[
        #ui.text(title + ': Credits', size=ui.TextSize.L),
        ui.text('Task Tracker', size=ui.TextSize.L),
        ui.stats(items=[ui.stat(
            label=' ',
            value='1. Information',
            caption='Tell us about yourself',
            icon='Checkbox',
            icon_color='#135f96'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='2. Select Program',
            caption='Decide what you want to study',
            icon='Checkbox',
            icon_color='#a30606'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='3. Add Courses',
            caption='Add GE and Electives',
            icon='Checkbox',
            #icon_color='#787800'
            icon_color='#3c3c43'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='4. Create Schedule',
            caption='Optimize your schedule',
            icon='Checkbox',
            icon_color='#da1a32'
        )]),
    ]))

def tasks_checked1_ZZ(q):
    '''
    First task checked
    '''

    add_card(q, 'checked1_tasks', 
        ui.form_card(
            box=ui.box('top_horizontal', width='350px', height='400px'),
            items=[
        #ui.text(title + ': Credits', size=ui.TextSize.L),
        ui.text('Task Tracker', size=ui.TextSize.L),
        ui.stats(items=[ui.stat(
            label=' ',
            value='1. Information',
            caption='Tell us about yourself',
            icon='CheckboxComposite',
            icon_color='#135f96'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='2. Select Program',
            caption='Decide what you want to study',
            icon='Checkbox',
            icon_color='#a30606'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='3. Add Courses',
            caption='Add GE and Electives',
            icon='Checkbox',
            #icon_color='#787800'
            icon_color='#3c3c43'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='4. Create Schedule',
            caption='Optimize your schedule',
            icon='Checkbox',
            icon_color='#da1a32'
        )]),
    ]))

def task2_ZZ(q):
    '''
    '''
    task_2b_caption = f'''
### Option 2: With the help of AI:

- Take a **Skills Assessment** and find programs that best fit your Skills
- Take an **Interests Assessment** and find programs that best fit your Interests
- Take a **Personality Assessment** and find programs that best fit your Personality
- If you have transfer credits, find programs that let you graduate the soonest
'''
    task_2a_caption = f'''
### Option 1: Explore Programs on your own. 
The **Program** tab above will take you to the program exploration page
'''
    add_card(q, 'task2a', 
        card = ui.wide_info_card(
            box=ui.box('top_horizontal', width='400px'),
            name='task2a',
            icon='AccountActivity',
            title='Select a UMGC Program',
            caption=task_2a_caption
        )
    )

#    add_card(q, 'task2b', 
#        card = ui.wide_info_card(
#            box=ui.box('top_horizontal', width='400px'),
#            name='task2b',
#            icon='AccountActivity',
#            title='Task 2b',
#            caption=task_2b_caption
#        )
#    )

def render_registration_card_ZZ(q, location='top_horizontal', width='40%', 
                             height='400px', cardname='registration'):
    '''
    This is the registration form for an new student
    '''
    card = ui.form_card(
        box=ui.box(location, width=width, height=height),
        items=[
            ui.text_xl('Welcome to the UMGC Registration Assistant'),
            ui.separator(),
            ui.text_xl('Please register:'),
            ui.textbox(name='firstname', label='First Name', required=True),
            ui.textbox(name='lastname', label='Last Name', required=True),
            ui.separator(),
            ui.button(name='register_submit', label='Submit', primary=True),
        ]
    )
    add_card(q, cardname, card)

def return_welcome_back_card_ZZ(q, location='vertical', height='400px', width='100%', 
                             box='1 3 3 3', title=''):
    student_info = q.user.student_info
    flex = q.app.flex

    if flex:
        box = ui.box(location, height=height, width=width)

    content2 = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

#### You need to select a degree program.

'''

    content3 = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

- **Selected program**: {student_info['degree_program']}

#### You need to create a schedule.

'''

    content4 = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

- **Selected program**: {student_info['degree_program']}

#### Congratulations, you have a saved schedule.

- Select the **Program** tab to review or change your program.
- Select the **Courses** tab to add or change courses.
- Select the **Schedule** tab to update your schedule.
'''
    app_stage_id = int(q.user.student_info['app_stage_id'])
    if app_stage_id == 2:
        content = content2
    elif app_stage_id == 3:
        content = content3
    elif app_stage_id == 4:
        content = content4

    if content:
        card = ui.markdown_card(
            box=box,
            title=title,
            content=content
        )
    else:
        card = None
    return card

def render_welcome_back_card_ZZ(q, location='vertical', height='400px', width='100%', cardname='user_info',
                             box='1 3 3 3', title=''):
    student_info = q.user.student_info
    flex = q.app.flex

    if flex:
        box = ui.box(location, height=height, width=width)
    content1 = f'''## Welcome back, {student_info['name']}.

### We need to gather some information from you

'''

    content4 = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

- **Selected program**: {student_info['degree_program']}

'''
    card = ui.markdown_card(
        box=box,
        title=title,
        content=content1 if int(q.user.student_info['app_stage_id']) else content4
    )

    add_card(q, cardname, card)

def render_welcome_back_card_stage1_ZZ(q, location='vertical', height='400px', width='100%', cardname='user_info',
                             box='1 3 3 3', title=''):
    student_info = q.user.student_info
    flex = q.app.flex

    if flex:
        box = ui.box(location, height=height, width=width)
    content = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

- **Selected program**: {student_info['degree_program']}

'''
    card = ui.markdown_card(
        box=box,
        title=title,
        content=content
    )

    add_card(q, cardname, card)

    #add_card(q, 'user_info', 
    #    ui.form_card(
    #        box=box,
    #        items=[
    #            content,
    #            ui.inline(
    #                items=[
    #                    ui.button(name='show_recommendations', label='Submit', primary=True),
    #                    ui.button(name='clear_recommendations', label='Clear', primary=False),  # enable this
    #                ]
    #)]))

def return_ai_enablement_card_ZZ(box='1 1 2 2', location='grid', width='400px', flex=True):
    if flex:
        box=ui.box(location, width=width)
    card = ui.wide_info_card(
        box=box,
        name='ai',
        icon='LightningBolt',
        title='AI Enablement',
        caption='*Interest*, *Skills*, or **Personality** assessments critical for AI recommendations.'
    )
    return card

async def render_career_assessment_card_ZZ(q, box='1 1 2 2', location='horizontal', 
                                        width='400px', cardname='assessments'):
    '''
    Create career assessment card
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, width=width)
    yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'
    caption=f'Access career assessment tools like **UMGC CareerQuest** or add a page like <a href="{yale_url}" target="_blank">Yale\'s</a> with _Interest_, _Personality_, and _Skills_ assessments.'
    card = ui.wide_info_card(
        box=box,
        name='Assessments',
        icon='AccountActivity',
        title='Career Assessments',
        caption=caption
    )
    add_card(q, cardname, card)

async def render_skills_assessment_card_ZZ(q, box='1 1 2 2', location='horizontal', 
                                        width='400px', cardname='assessments'):
    '''
    Create career assessment card
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, width=width)
    old_caption = f'Take a **Skills Assessment** to find programs that best fit your **skills**. *UMGC CareerQuest* '
    new_caption = f'''
### Option 2: Let AI suggest programs

- Take a **Skills Assessment** and find programs that best fit your Skills
- Take an **Interests Assessment** and find programs that best fit your Interests
- If you have transfer credits, find programs that let you graduate the soonest
'''
    card = ui.wide_info_card(
        box=box,
        name='SkillsAssessment',
        icon='AccountActivity',
        title='Select a UMGC Program',
        caption=new_caption
    )
    add_card(q, cardname, card)

async def render_interest_assessment_card_ZZ(q, box='1 1 2 2', location='horizontal', 
                                        width='400px', cardname='interest_assessments'):
    '''
    Create career assessment card
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, width=width)
    yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'
    caption=f'Take an **Interests Assessment** to find programs that best fit your **interests**. *UMGC CareerQuest* '
    card = ui.wide_info_card(
        box=box,
        name='InterestsAssessment',
        icon='AccountActivity',
        title='Let AI suggest Programs based on your Interests',
        caption=caption
    )
    add_card(q, cardname, card)

async def render_personality_assessment_card_ZZ(q, box='1 1 2 2', location='horizontal', 
                                        width='400px', cardname='personality_assessments'):
    '''
    Create career assessment card
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, width=width)
    yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'
    caption=f'Take a **Personality Assessment** to find programs that best fit your **personality**. *UMGC CareerQuest* '
    card = ui.wide_info_card(
        box=box,
        name='InterestsAssessment',
        icon='AccountActivity',
        title='Let AI suggest Programs based on your Personality',
        caption=caption
    )
    add_card(q, cardname, card)

def render_student_information_stub_card_ZZ(box='1 1 2 2', location='horizontal', width='400px', flex=True):
    if flex:
        box=ui.box(location, width=width)
    caption=f'Gather incomplete student information. Walk students through transfer credits. Access allowable data from UMGC servers.'
    card = ui.wide_info_card(
        box=box,
        name='StudentAssessments',
        icon='AccountActivity',
        title='Guided Student Updates',
        caption=caption
    )
    return card

def return_task1_card(location='top_horizontal', width='350px'):
    '''
    Task 1 Card repeated on home page and home/1, home/2, etc.
    '''
    task_1_caption = f'''
### Enter selected information 
- Residency status
- Attendance type
- Financial aid
- Transfer credits
'''
    card = ui.wide_info_card(
        box=ui.box(location, width=width),
        name='task1',
        icon='AccountActivity',
        title='Task 1',
        caption=task_1_caption
    )
    return card

def render_task1_card(q, location='top_horizontal', width='350px'):
    '''
    Task 1 Card repeated on home page and home/1, home/2, etc.
    '''
    card = return_task1_card(location=location, width=width)
    add_card(q, 'home/task1', card=card)

def return_demographics_card1(card_height = '400px', location='top_horizontal', width='400px'):
    '''
    Demographics card for home page
    '''
    resident_choices = [
        ui.choice('A', 'In-State'),
        ui.choice('B', 'Out-of-State'),
        ui.choice('C', 'Military'),
    ]
    attendance_choices = [
        ui.choice('A', 'Full Time'),
        ui.choice('B', 'Part Time'),
        ui.choice('C', 'Evening only'),
    ]
    card = ui.form_card(
        box=ui.box(location, width=width),
        items=[
            ui.text_xl('Tell us about yourself'),
            ui.text('This information will help us build a course schedule'),
            ui.inline(items=[
                #ui.choice_group(name='resident_status', label='My Resident status is', choices=resident_choices, required=True),
                #ui.text_xl(''),
                ui.choice_group(name='attendance', label='I will be attending', choices=attendance_choices, required=True),
            ]),
            ui.separator(name='my_separator', width='100%', visible=True),
            ui.checkbox(name='financial_aid', label='I will be using Financial Aid'),
            ui.checkbox(name='transfer_credits', label='I have credits to transfer'),
            #ui.separator(),
            #ui.text('(Other appropriate questions here...)'),
            #ui.separator(),
            ui.button(name='next_demographic_1', label='Next', primary=True),
        ]
    )
    return card

def render_demographics_card1(q, card_height = '400px', location='top_horizontal', width='400px'):
    '''
    Demographics card for home page
    '''
    card = return_demographics_card1(location=location, width=width)
    add_card(q, 'home/demographics1', card)

def return_demographics_card2(location='top_horizontal', width='400px'):
    '''

    '''
    resident_choices = [
        ui.choice('A', 'In-State'),
        ui.choice('B', 'Out-of-State'),
        ui.choice('C', 'Military'),
    ]
    card = ui.form_card(
        box=ui.box(location, width=width),
        items=[
            ui.text_xl('Tell us more about yourself:'),
            ui.text('This information will help us estimate your tuition costs'),
            ui.choice_group(name='resident_status', label='My Resident status is', choices=resident_choices, required=True),
            ui.separator(label='', name='my_separator2', width='100%', visible=True),
            ui.button(name='next_demographic_2', label='Next', primary=True),
        ]
    )
    return card


def demographics2(q):
    '''

    '''
    resident_choices = [
        ui.choice('A', 'In-State'),
        ui.choice('B', 'Out-of-State'),
        ui.choice('C', 'Military'),
    ]
    add_card(q, 'demographics2', 
        ui.form_card(
            box=ui.box('top_horizontal', width='400px'),
            items=[
                ui.text_xl('Tell us more about yourself:'),
                ui.text('This information will help us estimate your tuition costs'),
                ui.choice_group(name='resident_status', label='My Resident status is', choices=resident_choices, required=True),
                ui.separator(label='', name='my_separator2', width='100%', visible=True),
                ui.button(name='next_demographic_2', label='Next', primary=True),
            ]
        )
    )

def return_tasks_card(checked=0, location='top_horizontal', width='350px', height='400px'):
    '''
    Return tasks optionally checked off
    '''
    icons = ['Checkbox', 'Checkbox', 'Checkbox', 'Checkbox']
    checked_icon = 'CheckboxComposite'
    # checked needs to be a value between 0 and 4
    if checked > 0:
        for i in range(checked):
            icons[i] = checked_icon

    card = ui.form_card(
        box=ui.box(location, width=width, height=height),
        items=[
            #ui.text(title + ': Credits', size=ui.TextSize.L),
            ui.text('Task Tracker', size=ui.TextSize.L),
            ui.stats(items=[ui.stat(
                label=' ',
                value='1. Information',
                caption='Tell us about yourself',
                icon=icons[0],
                icon_color='#135f96'
            )]),
            ui.stats(items=[ui.stat(
                label=' ',
                value='2. Select Program',
                caption='Decide what you want to study',
                icon=icons[1],
                icon_color='#a30606'
            )]),
            ui.stats(items=[ui.stat(
                label=' ',
                value='3. Add Courses',
                caption='Add GE and Electives',
                icon=icons[2],
                #icon_color='#787800'
                icon_color='#3c3c43'
            )]),
            ui.stats(items=[ui.stat(
                label=' ',
                value='4. Create Schedule',
                caption='Optimize your schedule',
                icon=icons[3],
                icon_color='#da1a32'
            )]),
        ])
    return card

def tasks_unchecked(q):
    '''
    All tasks unchecked
    '''

    add_card(q, 'unchecked_tasks', 
        ui.form_card(
            box=ui.box('top_horizontal', width='350px', height='400px'),
            items=[
        #ui.text(title + ': Credits', size=ui.TextSize.L),
        ui.text('Task Tracker', size=ui.TextSize.L),
        ui.stats(items=[ui.stat(
            label=' ',
            value='1. Information',
            caption='Tell us about yourself',
            icon='Checkbox',
            icon_color='#135f96'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='2. Select Program',
            caption='Decide what you want to study',
            icon='Checkbox',
            icon_color='#a30606'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='3. Add Courses',
            caption='Add GE and Electives',
            icon='Checkbox',
            #icon_color='#787800'
            icon_color='#3c3c43'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='4. Create Schedule',
            caption='Optimize your schedule',
            icon='Checkbox',
            icon_color='#da1a32'
        )]),
    ]))


def tasks_checked1(q):
    '''
    First task checked
    '''

    add_card(q, 'checked1_tasks', 
        ui.form_card(
            box=ui.box('top_horizontal', width='350px', height='400px'),
            items=[
        #ui.text(title + ': Credits', size=ui.TextSize.L),
        ui.text('Task Tracker', size=ui.TextSize.L),
        ui.stats(items=[ui.stat(
            label=' ',
            value='1. Information',
            caption='Tell us about yourself',
            icon='CheckboxComposite',
            icon_color='#135f96'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='2. Select Program',
            caption='Decide what you want to study',
            icon='Checkbox',
            icon_color='#a30606'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='3. Add Courses',
            caption='Add GE and Electives',
            icon='Checkbox',
            #icon_color='#787800'
            icon_color='#3c3c43'
        )]),
        ui.stats(items=[ui.stat(
            label=' ',
            value='4. Create Schedule',
            caption='Optimize your schedule',
            icon='Checkbox',
            icon_color='#da1a32'
        )]),
    ]))




def task2(q):
    '''
    '''
    task_2b_caption = f'''
### Option 2: With the help of AI:

- Take a **Skills Assessment** and find programs that best fit your Skills
- Take an **Interests Assessment** and find programs that best fit your Interests
- Take a **Personality Assessment** and find programs that best fit your Personality
- If you have transfer credits, find programs that let you graduate the soonest
'''
    task_2a_caption = f'''
### Option 1: Explore Programs on your own. 
The **Program** tab above will take you to the program exploration page
'''
    add_card(q, 'task2a', 
        card = ui.wide_info_card(
            box=ui.box('top_horizontal', width='400px'),
            name='task2a',
            icon='AccountActivity',
            title='Select a UMGC Program',
            caption=task_2a_caption
        )
    )

#    add_card(q, 'task2b', 
#        card = ui.wide_info_card(
#            box=ui.box('top_horizontal', width='400px'),
#            name='task2b',
#            icon='AccountActivity',
#            title='Task 2b',
#            caption=task_2b_caption
#        )
#    )

def render_registration_card(q, location='top_horizontal', width='40%', 
                             height='400px', cardname='registration'):
    '''
    This is the registration form for an new student
    '''
    card = ui.form_card(
        box=ui.box(location, width=width, height=height),
        items=[
            ui.text_xl('Welcome to the UMGC Registration Assistant'),
            ui.separator(),
            ui.text_xl('Please register:'),
            ui.textbox(name='firstname', label='First Name', required=True),
            ui.textbox(name='lastname', label='Last Name', required=True),
            ui.separator(),
            ui.button(name='register_submit', label='Submit', primary=True),
        ]
    )
    add_card(q, cardname, card)

def return_welcome_back_card(q, location='vertical', height='400px', width='100%', 
                             title=''):
    student_info = q.user.student_info
    box = ui.box(location, height=height, width=width)

    content2 = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

#### You need to select a degree program.

'''

    content3 = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

- **Selected program**: {student_info['degree_program']}

#### You need to create a schedule.

'''

    content4 = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

- **Selected program**: {student_info['degree_program']}

#### Congratulations, you have a saved schedule.

- Select the **Program** tab to review or change your program.
- Select the **Courses** tab to add or change courses.
- Select the **Schedule** tab to update your schedule.
'''
    app_stage_id = int(q.user.student_info['app_stage_id'])

    if app_stage_id == 2:
        content = content2
    elif app_stage_id == 3:
        content = content3
    else:
        content = content4

    if content:
        card = ui.markdown_card(
            box=box,
            title=title,
            content=content
        )
    else:
        card = None
    return card

def render_welcome_back_card(q, location='vertical', height='400px', width='100%', cardname='user_info',
                             box='1 3 3 3', title=''):
    student_info = q.user.student_info
    flex = q.app.flex

    if flex:
        box = ui.box(location, height=height, width=width)
    content1 = f'''## Welcome back, {student_info['name']}.

### We need to gather some information from you

'''

    content4 = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

- **Selected program**: {student_info['degree_program']}

'''
    card = ui.markdown_card(
        box=box,
        title=title,
        content=content1 if int(q.user.student_info['app_stage_id']) else content4
    )

    add_card(q, cardname, card)

def render_welcome_back_card_stage1(q, location='vertical', height='400px', width='100%', cardname='user_info',
                             box='1 3 3 3', title=''):
    student_info = q.user.student_info
    flex = q.app.flex

    if flex:
        box = ui.box(location, height=height, width=width)
    content = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Attendance type**: {student_info['student_profile']}

- **Transfer credits**: {'Yes' if student_info['transfer_credits']==1 else 'No'}

- **Financial aid**: {student_info['financial_aid']==1}

- **Selected program**: {student_info['degree_program']}

'''
    card = ui.markdown_card(
        box=box,
        title=title,
        content=content
    )

    add_card(q, cardname, card)

    #add_card(q, 'user_info', 
    #    ui.form_card(
    #        box=box,
    #        items=[
    #            content,
    #            ui.inline(
    #                items=[
    #                    ui.button(name='show_recommendations', label='Submit', primary=True),
    #                    ui.button(name='clear_recommendations', label='Clear', primary=False),  # enable this
    #                ]
    #)]))

def return_ai_enablement_card(box='1 1 2 2', location='grid', width='400px', flex=True):
    if flex:
        box=ui.box(location, width=width)
    card = ui.wide_info_card(
        box=box,
        name='ai',
        icon='LightningBolt',
        title='AI Enablement',
        caption='*Interest*, *Skills*, or **Personality** assessments critical for AI recommendations.'
    )
    return card

async def render_career_assessment_card(q, box='1 1 2 2', location='horizontal', 
                                        width='400px', cardname='assessments'):
    '''
    Create career assessment card
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, width=width)
    yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'
    caption=f'Access career assessment tools like **UMGC CareerQuest** or add a page like <a href="{yale_url}" target="_blank">Yale\'s</a> with _Interest_, _Personality_, and _Skills_ assessments.'
    card = ui.wide_info_card(
        box=box,
        name='Assessments',
        icon='AccountActivity',
        title='Career Assessments',
        caption=caption
    )
    add_card(q, cardname, card)

async def render_skills_assessment_card(q, box='1 1 2 2', location='horizontal', 
                                        width='400px', cardname='assessments'):
    '''
    Create career assessment card
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, width=width)
    old_caption = f'Take a **Skills Assessment** to find programs that best fit your **skills**. *UMGC CareerQuest* '
    new_caption = f'''
### Option 2: Let AI suggest programs

- Take a **Skills Assessment** and find programs that best fit your Skills
- Take an **Interests Assessment** and find programs that best fit your Interests
- If you have transfer credits, find programs that let you graduate the soonest
'''
    card = ui.wide_info_card(
        box=box,
        name='SkillsAssessment',
        icon='AccountActivity',
        title='Select a UMGC Program',
        caption=new_caption
    )
    add_card(q, cardname, card)


async def render_interest_assessment_card(q, box='1 1 2 2', location='horizontal', 
                                        width='400px', cardname='interest_assessments'):
    '''
    Create career assessment card
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, width=width)
    yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'
    caption=f'Take an **Interests Assessment** to find programs that best fit your **interests**. *UMGC CareerQuest* '
    card = ui.wide_info_card(
        box=box,
        name='InterestsAssessment',
        icon='AccountActivity',
        title='Let AI suggest Programs based on your Interests',
        caption=caption
    )
    add_card(q, cardname, card)

async def render_personality_assessment_card(q, box='1 1 2 2', location='horizontal', 
                                        width='400px', cardname='personality_assessments'):
    '''
    Create career assessment card
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, width=width)
    yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'
    caption=f'Take a **Personality Assessment** to find programs that best fit your **personality**. *UMGC CareerQuest* '
    card = ui.wide_info_card(
        box=box,
        name='InterestsAssessment',
        icon='AccountActivity',
        title='Let AI suggest Programs based on your Personality',
        caption=caption
    )
    add_card(q, cardname, card)

def render_student_information_stub_card(box='1 1 2 2', location='horizontal', width='400px', flex=True):
    if flex:
        box=ui.box(location, width=width)
    caption=f'Gather incomplete student information. Walk students through transfer credits. Access allowable data from UMGC servers.'
    card = ui.wide_info_card(
        box=box,
        name='StudentAssessments',
        icon='AccountActivity',
        title='Guided Student Updates',
        caption=caption
    )
    return card

##############################################################
####################  PROGRAMS PAGE ##########################
##############################################################


async def render_dropdown_menus_horizontal_ZZ(q, box='1 2 7 1', location='horizontal', 
                                           menu_width='300px'):
    '''
    Create menus for selecting degree, area of study, and program
    '''
    flex = q.app.flex
    timed_connection = q.user.conn

    #degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
    #area_query = '''
    #    SELECT DISTINCT menu_area_id AS name, area_name AS label
    #    FROM menu_all_view 
    #    WHERE menu_degree_id = ?
    #'''
    #program_query_old = '''
    #    SELECT program_id AS name, program_name AS label
    #    FROM menu_all_view 
    #    WHERE menu_degree_id = ? AND menu_area_id = ?
    #'''
    #program_query = '''
    #    SELECT program_id AS name, program_name AS label, disabled
    #    FROM menu_all_view 
    #    WHERE menu_degree_id = ? AND menu_area_id = ?
    #'''

    current_disabled = q.app.disabled_program_menu_items
    
    # enforcing string because I've got a bug somewhere (passing an int instead of str)
    dropdowns = ui.inline([
        ui.dropdown(
            name='menu_degree',
            label='Degree',
            value=str(q.user.student_info['menu']['degree']) if \
                (q.user.student_info['menu']['degree'] is not None) else q.args.menu_degree,
            trigger=True,
            width='230px',
            choices=await utils.get_choices(timed_connection, degree_query)
        ),
        ui.dropdown(
            name='menu_area',
            label='Area of Study',
            value=str(q.user.student_info['menu']['area_of_study']) if \
                (str(q.user.student_info['menu']['area_of_study']) is not None) else \
                str(q.args.menu_area),
            trigger=True,
            disabled=False,
            width='250px',
            choices=None if (q.user.student_info['menu']['degree'] is None) else \
                await utils.get_choices(timed_connection, area_query, (q.user.student_info['menu']['degree'],))
        ),
        ui.dropdown(
            name='menu_program',
            label='Program',
            value=str(q.user.student_info['menu']['program']) if \
                (q.user.student_info['menu']['program'] is not None) else q.args.menu_program,
            trigger=True,
            disabled=False,
            width='300px',
            choices=None if (q.user.student_info['menu']['area_of_study'] is None) else \
                await utils.get_choices(
                    timed_connection, 
                    program_query, 
                    (q.user.student_info['menu']['degree'], q.user.student_info['menu']['area_of_study'])
                )
        )
    ], justify='start', align='start')

    command_button = ui.button(
        name='command_button', 
        label='Select', 
        disabled=False,
        commands=[
            ui.command(name='program', label='Save Program'),
            #ui.command(name='classes_menu', label='Classes', 
            #    items=[
            #        ui.command(name='add_ge', label='Add GE'),
            #        ui.command(name='add_elective', label='Add Electives'),  
            #]),
            ui.command(name='add_ge', label='Add GE'),
            ui.command(name='add_elective', label='Add Electives')  
    ])
    if flex:
        box = location
    card = ui.form_card(box=box,
        items=[
            #ui.text_xl('Browse Programs'),
            ui.inline([
                dropdowns, 
                command_button
            ],
            justify='between', 
            align='end')
        ]
    )
        
    add_card(q, 'dropdown', card)

    ########################

async def render_program_description_ZZ(q, box='1 3 7 2', location='top_vertical', width='100%', height='100px'):
    '''
    Renders the program description in an article card
    :param q: instance of Q for wave query
    :param location: page location to display
    '''
    flex = q.app.flex
    timed_connection = q.user.conn
    title = q.user.student_info['degree_program'] # program name

    if flex:
        box = ui.box(location, width=width, height=height)

    query = '''
        SELECT description, info, learn, certification
        FROM program_descriptions WHERE program_id = ?
    '''
    row = await backend.get_query_one(timed_connection, query, params=(q.user.student_info['program_id'],))
    if row:
        # major = '\n##' + title + '\n\n'
        frontstuff = "\n\n#### What You'll Learn\nThrough your coursework, you will learn how to\n"
        if int(q.user.student_info['program_id']) in (4, 24, 29):
            content = row['info'] + '\n\n' + row['description']
        else:
            content = row['description'] + frontstuff + row['learn'] #+ '\n\n' + row['certification']

        card = add_card(q, 'program_description', ui.markdown_card(
            box=box, 
            title=title,
            content=content
        ))
        #card = add_card(q, 'program_description', ui.article_card(
        #    box=box, 
        #    title=title,
        ##    content=row['description'] + row['']
        #    content=content
        #))
        return card

async def render_program_dashboard_ZZ(q, box=None, location='horizontal', width='100px'):
    '''
    Renders the dashboard with explored majors
    :param q: instance of Q for wave query
    :param location: page location to display
    flex=True: location is required
    flex=False: box is required
    '''
    flex = q.app.flex
    timed_connection = q.user.conn
    title = q.user.student_info['degree_program'] # program name

    if flex:
        box = ui.box(location, width=width)
    #if q.user.student_info['menu_degree'] == '2':

    # get program summary for bachelor's degrees
    query = 'SELECT * FROM program_requirements WHERE program_id = ?'
    row = await backend.get_query_one(timed_connection, query, params=(q.user.student_info['program_id'],))
    if row:
        card = add_card(q, 'major_dashboard', ui.form_card(
            box=box,
            items=[
                #ui.text(title + ': Credits', size=ui.TextSize.L),
                ui.text('Credits', size=ui.TextSize.L),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Major',
                            value=str(row['major']),
                            #caption='Credits',
                            icon='Trackers',
                            icon_color='#135f96'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Required Related',
                            value=str(row['related_ge'] + row['related_elective']),
                            #caption='Credits',
                            icon='News',
                            icon_color='#a30606'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='General Education',
                            value=str(row['remaining_ge']),
                            #caption='Remaining GE',
                            icon='TestBeaker',
                            #icon_color='#787800'
                            icon_color='#3c3c43'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Elective',
                            value=str(row['remaining_elective']),
                            #caption='Remaining Elective',
                            icon='Media',
                            icon_color='#fdbf38'
                    )]
                ),
                ui.separator(),
                ui.stats(
                    items=[
                        ui.stat(
                            label='TOTAL',
                            value=str(row['total']),
                            #caption='Remaining Elective',
                            icon='Education',
                            icon_color='#da1a32 '
                    )]
                ),
            ])
        )
        return card
        #else: '#3c3c43' 
        #    pass
        #    # send a warning

UMGC_tags_ZZ = [
    ui.tag(label='ELECTIVE', color='#fdbf38', label_color='$black'),
    ui.tag(label='REQUIRED', color='#a30606'),
    ui.tag(label='MAJOR', color='#135f96'),
#    ui.tag(label='GENERAL', color='#3c3c43'), # dark gray
#    ui.tag(label='GENERAL', color='#787800'), # khaki   
    ui.tag(label='GENERAL', color='#3b8132', label_color='$white'), # green   
]

async def render_program_table_ZZ(q, box='1 5 6 5', location='horizontal', width='90%', 
                               height='500px', check=True, ge=False, elective=False):
    '''
    q:
    df:
    location:
    cardname:
    width:
    height:
    ge: Include GE classes
    elective: Include Elective classes
    '''
    flex = q.app.flex
    df = q.user.student_data['required']

    async def _render_program_group(group_name, record_type, df, collapsed, check=True):
        '''
        group_name: 
        record_type: 
        df: course (Pandas) dataframe
        collapsed:
        check: If True, only return card if # rows > 0
            e.g., we will always return 'MAJOR' but not necessarily 'REQUIRED'
        '''
        # card will be returned if 
        # (1) check == False
        # (2) check == True and sum(rows) > 0
        no_rows = ((df['type'].str.upper() == record_type).sum() == 0)

        if check and no_rows: #(check and not_blank) or (not check):
            return ''
        else:
            return ui.table_group(group_name, [
                ui.table_row(
                    #name=str(row['id']),
                    name=row['course'],
                    cells=[
                        row['course'],
                        row['title'],
                        str(row['credits']),
                        row['type'].upper(),
                    ]
                ) for _, row in df.iterrows() if row['type'].upper() == record_type
            ], collapsed=collapsed)

    # Create groups with logic
    groups = []
    result = await _render_program_group(
        'Required Major Core Courses',
        'MAJOR',
        df, collapsed=False, check=False
    )
    if result != '':
        groups.append(result)
        
    result = await _render_program_group(
        'Required Related Courses/General Education',
        'REQUIRED,GENERAL',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)
    
    result = await _render_program_group(
        'Required Related Courses/Electives',
        'REQUIRED,ELECTIVE',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)

    if ge:
        result = await _render_program_group(
            'General Education',
            'GENERAL',
            df, collapsed=True, check=False
        )
        if result != '':
            groups.append(result)
        
    if elective:
        result = await _render_program_group(
            'Electives',
            'ELECTIVE',
            df, collapsed=True, check=False
        )
        if result != '':
            groups.append(result)

    columns = [
        # ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300',
                        cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_program_description', label='Course Description'),
                    #ui.command(name='prerequisites', label='Show Prerequisites'),
                ]
        ))
    ]

    if flex:
        box = ui.box(location, height=height, width=width)

    #title = q.user.student_info['degree_program'] + ': Explore Required Courses'
    title = 'Explore Required Courses'
    card = add_card(q, 'program_table_card', ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='describe_program', label='About', 
                    #caption='Description', 
                    primary=True, disabled=True)
            ]),
            ui.table(
                name='program_table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height=height,
                columns=columns,
                groups=groups
            )
        ]
    ))
    return card

async def render_program_ZZ(q):
    await render_program_description(q, location='top_vertical', height='250px', width='100%')
    await render_program_table(q, location='horizontal', width='90%')
    await render_program_dashboard(q, location='horizontal', width='150px')


async def render_program_description(q, box='1 3 7 2', location='top_vertical', width='100%', height='100px'):
    '''
    Renders the program description in an article card
    :param q: instance of Q for wave query
    :param location: page location to display
    '''
    flex = q.app.flex
    timedConnection = q.user.conn
    title = q.user.student_info['degree_program'] # program name

    if flex:
        box = ui.box(location, width=width, height=height)

    query = '''
        SELECT description, info, learn, certification
        FROM program_descriptions WHERE program_id = ?
    '''
    row = await backend.get_query_one(timedConnection, query, params=(q.user.student_info['program_id'],))
    if row:
        # major = '\n##' + title + '\n\n'
        frontstuff = "\n\n#### What You'll Learn\nThrough your coursework, you will learn how to\n"
        if int(q.user.student_info['program_id']) in (4, 24, 29):
            content = row['info'] + '\n\n' + row['description']
        else:
            content = row['description'] + frontstuff + row['learn'] #+ '\n\n' + row['certification']

        card = add_card(q, 'program_description', ui.markdown_card(
            box=box, 
            title=title,
            content=content
        ))
        #card = add_card(q, 'program_description', ui.article_card(
        #    box=box, 
        #    title=title,
        ##    content=row['description'] + row['']
        #    content=content
        #))
        return card

async def render_program_dashboard(q, box=None, location='horizontal', width='100px'):
    '''
    Renders the dashboard with explored majors
    :param q: instance of Q for wave query
    :param location: page location to display
    flex=True: location is required
    flex=False: box is required
    '''
    flex = q.app.flex
    timedConnection = q.user.conn
    title = q.user.student_info['degree_program'] # program name

    if flex:
        box = ui.box(location, width=width)
    #if q.user.student_info['menu_degree'] == '2':

    # get program summary for bachelor's degrees
    query = 'SELECT * FROM program_requirements WHERE program_id = ?'
    row = await backend.get_query_one(timedConnection, query, params=(q.user.student_info['program_id'],))
    if row:
        card = add_card(q, 'major_dashboard', ui.form_card(
            box=box,
            items=[
                #ui.text(title + ': Credits', size=ui.TextSize.L),
                ui.text('Credits', size=ui.TextSize.L),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Major',
                            value=str(row['major']),
                            #caption='Credits',
                            icon='Trackers',
                            icon_color='#135f96'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Required Related',
                            value=str(row['related_ge'] + row['related_elective']),
                            #caption='Credits',
                            icon='News',
                            icon_color='#a30606'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='General Education',
                            value=str(row['remaining_ge']),
                            #caption='Remaining GE',
                            icon='TestBeaker',
                            #icon_color='#787800'
                            icon_color='#3c3c43'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Elective',
                            value=str(row['remaining_elective']),
                            #caption='Remaining Elective',
                            icon='Media',
                            icon_color='#fdbf38'
                    )]
                ),
                ui.separator(),
                ui.stats(
                    items=[
                        ui.stat(
                            label='TOTAL',
                            value=str(row['total']),
                            #caption='Remaining Elective',
                            icon='Education',
                            icon_color='#da1a32 '
                    )]
                ),
            ])
        )
        return card
        #else: '#3c3c43' 
        #    pass
        #    # send a warning

UMGC_tags = [
    ui.tag(label='ELECTIVE', color='#fdbf38', label_color='$black'),
    ui.tag(label='REQUIRED', color='#a30606'),
    ui.tag(label='MAJOR', color='#135f96'),
#    ui.tag(label='GENERAL', color='#3c3c43'), # dark gray
#    ui.tag(label='GENERAL', color='#787800'), # khaki   
    ui.tag(label='GENERAL', color='#3b8132', label_color='$white'), # green   
]

async def render_program_table(q, box='1 5 6 5', location='horizontal', width='90%', 
                               height='500px', check=True, ge=False, elective=False):
    '''
    q:
    df:
    location:
    cardname:
    width:
    height:
    ge: Include GE classes
    elective: Include Elective classes
    '''
    flex = q.app.flex
    df = q.user.student_data['required']

    async def _render_program_group(group_name, record_type, df, collapsed, check=True):
        '''
        group_name: 
        record_type: 
        df: course (Pandas) dataframe
        collapsed:
        check: If True, only return card if # rows > 0
            e.g., we will always return 'MAJOR' but not necessarily 'REQUIRED'
        '''
        # card will be returned if 
        # (1) check == False
        # (2) check == True and sum(rows) > 0
        no_rows = ((df['type'].str.upper() == record_type).sum() == 0)

        if check and no_rows: #(check and not_blank) or (not check):
            return ''
        else:
            return ui.table_group(group_name, [
                ui.table_row(
                    #name=str(row['id']),
                    name=row['course'],
                    cells=[
                        row['course'],
                        row['title'],
                        str(row['credits']),
                        row['type'].upper(),
                    ]
                ) for _, row in df.iterrows() if row['type'].upper() == record_type
            ], collapsed=collapsed)

    # Create groups with logic
    groups = []
    result = await _render_program_group(
        'Required Major Core Courses',
        'MAJOR',
        df, collapsed=False, check=False
    )
    if result != '':
        groups.append(result)
        
    result = await _render_program_group(
        'Required Related Courses/General Education',
        'REQUIRED,GENERAL',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)
    
    result = await _render_program_group(
        'Required Related Courses/Electives',
        'REQUIRED,ELECTIVE',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)

    if ge:
        result = await _render_program_group(
            'General Education',
            'GENERAL',
            df, collapsed=True, check=False
        )
        if result != '':
            groups.append(result)
        
    if elective:
        result = await _render_program_group(
            'Electives',
            'ELECTIVE',
            df, collapsed=True, check=False
        )
        if result != '':
            groups.append(result)

    columns = [
        # ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300',
                        cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_program_description', label='Course Description'),
                    #ui.command(name='prerequisites', label='Show Prerequisites'),
                ]
        ))
    ]

    if flex:
        box = ui.box(location, height=height, width=width)

    #title = q.user.student_info['degree_program'] + ': Explore Required Courses'
    title = 'Explore Required Courses'
    card = add_card(q, 'program_table_card', ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='describe_program', label='About', 
                    #caption='Description', 
                    primary=True, disabled=True)
            ]),
            ui.table(
                name='program_table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height=height,
                columns=columns,
                groups=groups
            )
        ]
    ))
    return card

async def render_program(q):
    await render_program_description(q, location='top_vertical', height='250px', width='100%')
    await render_program_table(q, location='horizontal', width='90%')
    await render_program_dashboard(q, location='horizontal', width='150px')

##############################################################
####################  COURSES PAGE  ##########################
##############################################################


def render_courses_header_ZZ(q, box='1 2 7 1', location='horizontal'):
    flex = q.app.flex
    degree_program = q.user.student_info['degree_program']
    if flex:
        box = ui.box(location)
    content=f'**Program Selected**: {degree_program}'
    add_card(q, 'courses_header', ui.form_card(
        box=box,
        items=[
            ui.text_l(content),
            #ui.text('We will guide you through this experience.')
        ]
    ))

async def render_course_page_table_use_ZZ(q, box=None, location=None, width=None, height=None, check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    data: a list of dictionaries, each element corresponding to a row of the table 
    location:
    cardname:
    width:
    height:
    '''
    flex = q.app.flex
    df = q.user.student_data['schedule']

    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300', cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='select_elective', label='Select Elective'),
                ]
        ))
        #ui.table_column(name='menu', label='Menu', max_width='150',
        #    cell_type=ui.menu_table_cell_type(name='commands', 
        #        commands=[
        #            ui.command(name='view_description', label='Course Description'),
        #            ui.command(name='show_prereq', label='Show Prerequisites'),
        #            ui.command(name='select_elective', label='Select Elective'),
        #        ]
        #))
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['course'],
            cells=[
                #str(row['seq']),
                row['course'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        box = ui.box(location, height=height, width=width)
    degree_program = q.user.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'course_table', ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='schedule_coursework', label='Schedule', 
                    #caption='Description', 
                    primary=True, disabled=False)
            ]),
            ui.table(
                name='course_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card

async def render_course_page_table_ZZ(q, df, box=None, location=None, width=None, height=None, 
                                   check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    df: a Pandas df containing the table
    location:
    cardname:
    width:
    height:
    '''
    flex = q.app.flex
    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300', cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='select_elective', label='Select Elective'),
                ]
        ))
        #ui.table_column(name='menu', label='Menu', max_width='150',
        #    cell_type=ui.menu_table_cell_type(name='commands', 
        #        commands=[
        #            ui.command(name='view_description', label='Course Description'),
        #            ui.command(name='show_prereq', label='Show Prerequisites'),
        #            ui.command(name='select_elective', label='Select Elective'),
        #        ]
        #))
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['name'],
            cells=[
                #str(row['seq']),
                row['name'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        box = ui.box(location, height=height, width=width)
    degree_program = q.user.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'course_table', ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='schedule_coursework', label='Schedule', 
                    #caption='Description', 
                    primary=True, disabled=False)
            ]),
            ui.table(
                name='course_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card


def render_courses_header(q, box='1 2 7 1', location='horizontal'):
    flex = q.app.flex
    degree_program = q.user.student_info['degree_program']
    if flex:
        box = ui.box(location)
    content=f'**Program Selected**: {degree_program}'
    add_card(q, 'courses_header', ui.form_card(
        box=box,
        items=[
            ui.text_l(content),
            #ui.text('We will guide you through this experience.')
        ]
    ))

async def render_course_page_table_use(q, box=None, location=None, width=None, height=None, check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    data: a list of dictionaries, each element corresponding to a row of the table 
    location:
    cardname:
    width:
    height:
    '''
    flex = q.app.flex
    df = q.user.student_data['schedule']

    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300', cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='select_elective', label='Select Elective'),
                ]
        ))
        #ui.table_column(name='menu', label='Menu', max_width='150',
        #    cell_type=ui.menu_table_cell_type(name='commands', 
        #        commands=[
        #            ui.command(name='view_description', label='Course Description'),
        #            ui.command(name='show_prereq', label='Show Prerequisites'),
        #            ui.command(name='select_elective', label='Select Elective'),
        #        ]
        #))
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['name'],
            cells=[
                #str(row['seq']),
                row['name'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        box = ui.box(location, height=height, width=width)
    degree_program = q.user.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'course_table', ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='schedule_coursework', label='Schedule', 
                    #caption='Description', 
                    primary=True, disabled=False)
            ]),
            ui.table(
                name='course_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card

async def render_course_page_table(q, df, box=None, location=None, width=None, height=None, 
                                   check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    df: a Pandas df containing the table
    location:
    cardname:
    width:
    height:
    '''
    flex = q.app.flex
    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300', cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='select_elective', label='Select Elective'),
                ]
        ))
        #ui.table_column(name='menu', label='Menu', max_width='150',
        #    cell_type=ui.menu_table_cell_type(name='commands', 
        #        commands=[
        #            ui.command(name='view_description', label='Course Description'),
        #            ui.command(name='show_prereq', label='Show Prerequisites'),
        #            ui.command(name='select_elective', label='Select Elective'),
        #        ]
        #))
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['name'],
            cells=[
                #str(row['seq']),
                row['name'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        box = ui.box(location, height=height, width=width)
    degree_program = q.user.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'course_table', ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='schedule_coursework', label='Schedule', 
                    #caption='Description', 
                    primary=True, disabled=False)
            ]),
            ui.table(
                name='course_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card

#######################################################
####################  GE PAGE  ########################
#######################################################


ge_query_ZZ = '''
    SELECT course AS name, course || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? 
    ORDER BY course
'''
ge_query_nopre_ZZ = '''
    SELECT course AS name, course || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? 
        AND pre='' 
        AND pre_credits=''
    ORDER BY course
'''
ge_credits_query_ZZ = '''
    SELECT course AS name, course || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? AND credits=? 
    ORDER BY course
'''
ge_pairs_query_ZZ = '''
    SELECT 
        course AS name, 
        course || ' & ' || substr(note, 27, 3) || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=10 AND credits=3
    ORDER BY course
'''
ge_query = '''
    SELECT course AS name, course || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? 
    ORDER BY course
'''
ge_query_nopre = '''
    SELECT course AS name, course || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? 
        AND pre='' 
        AND pre_credits=''
    ORDER BY course
'''
ge_credits_query = '''
    SELECT course AS name, course || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? AND credits=? 
    ORDER BY course
'''
ge_pairs_query = '''
    SELECT 
        course AS name, 
        course || ' & ' || substr(note, 27, 3) || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=10 AND credits=3
    ORDER BY course
'''

async def render_ge_arts_card_ZZ(q, menu_width='300px', box='1 11 3 3', location='grid', 
                              cardname='ge_arts', width='300px'):
    '''
    Create the General Education - Arts card
    '''
    ge = q.user.student_info['ge']['arts']
    nopre = ge['nopre']
    timed_connection = q.user.conn
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Arts and Humanities', size=ui.TextSize.L),
                ui.checkbox(name='ge_arts_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_arts_1',
                label='1. Course (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_arts_1,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (6,))
            ),
            ui.dropdown(
                name='ge_arts_2',
                label='2. Course (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_arts_2,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                # figure out how to omit choice selected in Course 1
                choices=await get_choices(timed_connection, ge_query, (7,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_beh_card_ZZ(q, menu_width='300px', box='4 11 3 3', location='grid', 
                             cardname='ge_beh', width='300px'):
    '''
    Create the General Education - Behavioral and Social Sciences card
    '''
    ge = q.user.student_info['ge']['beh']
    nopre = ge['nopre']
    timed_connection = q.user.conn
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            #ui.separator(label=''),
            ui.inline([
                ui.text('Behavioral and Social Sciences', size=ui.TextSize.L),
                ui.checkbox(name='ge_beh_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_beh_1',
                label='1. Course (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_beh_1,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (12,))
                #choices=await get_choices(timed_connection, ge_query_nopre if nopre else ge_query, (11,))
            ),
            ui.dropdown(
                name='ge_beh_2',
                label='2. Course (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_beh_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (13,))
#                choices=await get_choices(timed_connection, ge_query_nopre if nopre else ge_query, (11,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_bio_card_ZZ(q, menu_width='300px', box='1 7 3 4', location='grid', 
                             cardname='ge_bio', width='300px'):
    '''
    Create the General Education - Science card
    '''
    timed_connection = q.user.conn
    ge = q.user.student_info['ge']['bio']
    nopre = ge['nopre']
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Biological and Physical Sciences', size=ui.TextSize.L),
                ui.checkbox(name='ge_bio_check', label='')
            ], justify='between', align='start'),
            #ui.text('Select one of the following:', size=ui.TextSize.L),
            #ui.separator(label='1. Select one of the following three choices:'),
            ui.dropdown(
                name='ge_bio_1a',
                label='1. Lecture & Lab (4 credits): Select one',
                value = ge['1a'] if (ge['1a'] is not None) else q.args.ge_bio_1a,
                trigger=True,
                placeholder='(Combined Lecture & Lab)',
                required=True,
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (8,))
            ),
            ui.dropdown(
                name='ge_bio_1c',
                #label='Separate Lecture and Laboratory',
                value=ge['1c'] if (ge['1c'] is not None) else q.args.ge_bio_1c,
                trigger=True,
                placeholder='or (Separate Lecture & Lab)',
                width=menu_width,
                choices=await utils.get_choices_disable_all(timed_connection, ge_pairs_query, ())
            ),
            ui.dropdown(
                name='ge_bio_1b',
                #label='For Science Majors and Minors only:',
                value=ge['1b'] if (ge['1b'] is not None) else q.args.ge_bio_1b,
                trigger=True,
                placeholder='or (Science Majors and Minors)',
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (9,))
            ),
            #ui.separator(label='Select an additional science course:'),
            #nopre=True # check for easy classes by selecting those w/o prerequisites
            ui.dropdown(
                name='ge_bio_2',
                label='2. An additional course (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_bio_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
#                choices=await get_choices(timed_connection, ge_query_nopre if nopre else ge_query, (10,))
                choices=await get_choices(timed_connection, ge_query, (11,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_comm_card_ZZ(q, menu_width='300px', box='1 3 3 4', location='grid', 
                             cardname='ge_comm', width='300px'):
    '''
    Create the General Education - Communications card
    '''
    timed_connection = q.user.conn
    ge = q.user.student_info['ge']['comm']
    nopre = ge['nopre']
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Communications', size=ui.TextSize.L),
                ui.checkbox(name='ge_comm_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_comm_1',
                label='1. WRTG 111 or equivalent (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_comm_1,
                trigger=True,
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (1,))
            ),
            ui.dropdown(
                name='ge_comm_2',
                label='2. WRTG 112 (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_comm_2,
                disabled=False,
                trigger=True,
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (2,))
            ),
            ui.dropdown(
                name='ge_comm_3',
                label='3. Another course (3 credits)',
                placeholder='(Select One)',
                value=ge['3'] if (ge['3'] is not None) else q.args.ge_comm_3,
                trigger=True,
                popup='always',
                required=True,
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (3,))
            ),
            ui.dropdown(
                name='ge_comm_4',
                label='4. Advanced writing course (3 credits)',
                placeholder='(Select One)',
                value=ge['4'] if (ge['4'] is not None) else q.args.ge_comm_4,
                trigger=True,
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (4,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_math_card_ZZ(q, menu_width='300px', box='4 9 3 2', location='grid', 
                             cardname='ge_math', width='300px'):
    '''
    Create the General Education - Mathematics card
    '''
    ge = q.user.student_info['ge']['math']
    timed_connection = q.user.conn
    nopre = ge['nopre']
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Mathematics', size=ui.TextSize.L),
                ui.checkbox(name='ge_math_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_math_1',
                label='One Course (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_math,
                placeholder='(Select One)',
                trigger=True,
                required=True,
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (5,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_res_card_ZZ(q, menu_width='300px', box='1 3 3 4', location='grid', 
                             cardname='ge_res', width='300px'):
    '''
    Create the General Education - Research and Computing Literacy card
    '''
    timed_connection = q.user.conn
    ge = q.user.student_info['ge']['res']
    nopre = ge['nopre']
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    # make some defaults based on area of program chosen:
    if q.user.student_info['menu']['area_of_study'] == '1':
        ge['1'] = 'PACE 111B'
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Research and Computing Literacy', size=ui.TextSize.L),
                ui.checkbox(name='ge_res_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_res_1',
                label='1. Professional Exploration (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_res_1,
                # default value will depend on the major chosen
                trigger=True,
                placeholder='(Select One)',
                popup='always',
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (14,))
            ),
            ui.dropdown(
                name='ge_res_2',
                label='2. Research Skills / Professional Development (1 credit)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_res_2,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(timed_connection, ge_query, (15,))
            ),
            ui.dropdown(
                name='ge_res_3',
                label='3. Computing or IT (3 credits)',
                value=ge['3'] if (ge['3'] is not None) else q.args.ge_res_3,
                trigger=True,
                required=True,
                placeholder='(Select 3-credit Course)',
                width=menu_width,
                choices=await get_choices(timed_connection, ge_credits_query, (16,3))
            ),
           ui.dropdown(
                name='ge_res_3a',
                label='[or three 1-credit courses]:',
                required=True,
                value=ge['3a'] if (ge['3a'] is not None) else q.args.ge_res_3a,
                trigger=True,
                placeholder='(Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(timed_connection, ge_credits_query, (16,1))
            ),
            ui.dropdown(
                name='ge_res_3b',
                #label='Computing or Information Technology (1 credit)',
                value=ge['3b'] if (ge['3b'] is not None) else q.args.ge_res_3b,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(timed_connection, ge_credits_query, (16,1))
            ),
            ui.dropdown(
                name='ge_res_3c',
                #label='Computing or Information Technology (1 credit each)',
                value=ge['3c'] if (ge['3c'] is not None) else q.args.ge_res_3c,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(timed_connection, ge_credits_query, (16,1))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_arts_card(q, menu_width='300px', box='1 11 3 3', location='grid', 
                              cardname='ge_arts', width='300px'):
    '''
    Create the General Education - Arts card
    '''
    ge = q.user.student_info['ge']['arts']
    nopre = ge['nopre']
    timedConnection = q.user.conn
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Arts and Humanities', size=ui.TextSize.L),
                ui.checkbox(name='ge_arts_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_arts_1',
                label='1. Course (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_arts_1,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (6,))
            ),
            ui.dropdown(
                name='ge_arts_2',
                label='2. Course (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_arts_2,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                # figure out how to omit choice selected in Course 1
                choices=await get_choices(timedConnection, ge_query, (7,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_beh_card(q, menu_width='300px', box='4 11 3 3', location='grid', 
                             cardname='ge_beh', width='300px'):
    '''
    Create the General Education - Behavioral and Social Sciences card
    '''
    ge = q.user.student_info['ge']['beh']
    nopre = ge['nopre']
    timedConnection = q.user.conn
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            #ui.separator(label=''),
            ui.inline([
                ui.text('Behavioral and Social Sciences', size=ui.TextSize.L),
                ui.checkbox(name='ge_beh_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_beh_1',
                label='1. Course (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_beh_1,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (12,))
                #choices=await get_choices(timedConnection, ge_query_nopre if nopre else ge_query, (11,))
            ),
            ui.dropdown(
                name='ge_beh_2',
                label='2. Course (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_beh_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (13,))
#                choices=await get_choices(timedConnection, ge_query_nopre if nopre else ge_query, (11,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_bio_card(q, menu_width='300px', box='1 7 3 4', location='grid', 
                             cardname='ge_bio', width='300px'):
    '''
    Create the General Education - Science card
    '''
    timedConnection = q.user.conn
    ge = q.user.student_info['ge']['bio']
    nopre = ge['nopre']
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Biological and Physical Sciences', size=ui.TextSize.L),
                ui.checkbox(name='ge_bio_check', label='')
            ], justify='between', align='start'),
            #ui.text('Select one of the following:', size=ui.TextSize.L),
            #ui.separator(label='1. Select one of the following three choices:'),
            ui.dropdown(
                name='ge_bio_1a',
                label='1. Lecture & Lab (4 credits): Select one',
                value = ge['1a'] if (ge['1a'] is not None) else q.args.ge_bio_1a,
                trigger=True,
                placeholder='(Combined Lecture & Lab)',
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (8,))
            ),
            ui.dropdown(
                name='ge_bio_1c',
                #label='Separate Lecture and Laboratory',
                value=ge['1c'] if (ge['1c'] is not None) else q.args.ge_bio_1c,
                trigger=True,
                placeholder='or (Separate Lecture & Lab)',
                width=menu_width,
                choices=await utils.get_choices_disable_all(timedConnection, ge_pairs_query, ())
            ),
            ui.dropdown(
                name='ge_bio_1b',
                #label='For Science Majors and Minors only:',
                value=ge['1b'] if (ge['1b'] is not None) else q.args.ge_bio_1b,
                trigger=True,
                placeholder='or (Science Majors and Minors)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (9,))
            ),
            #ui.separator(label='Select an additional science course:'),
            #nopre=True # check for easy classes by selecting those w/o prerequisites
            ui.dropdown(
                name='ge_bio_2',
                label='2. An additional course (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_bio_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
#                choices=await get_choices(timedConnection, ge_query_nopre if nopre else ge_query, (10,))
                choices=await get_choices(timedConnection, ge_query, (11,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_comm_card(q, menu_width='300px', box='1 3 3 4', location='grid', 
                             cardname='ge_comm', width='300px'):
    '''
    Create the General Education - Communications card
    '''
    timedConnection = q.user.conn
    ge = q.user.student_info['ge']['comm']
    nopre = ge['nopre']
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Communications', size=ui.TextSize.L),
                ui.checkbox(name='ge_comm_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_comm_1',
                label='1. WRTG 111 or equivalent (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_comm_1,
                trigger=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (1,))
            ),
            ui.dropdown(
                name='ge_comm_2',
                label='2. WRTG 112 (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_comm_2,
                disabled=False,
                trigger=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (2,))
            ),
            ui.dropdown(
                name='ge_comm_3',
                label='3. Another course (3 credits)',
                placeholder='(Select One)',
                value=ge['3'] if (ge['3'] is not None) else q.args.ge_comm_3,
                trigger=True,
                popup='always',
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (3,))
            ),
            ui.dropdown(
                name='ge_comm_4',
                label='4. Advanced writing course (3 credits)',
                placeholder='(Select One)',
                value=ge['4'] if (ge['4'] is not None) else q.args.ge_comm_4,
                trigger=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (4,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_math_card(q, menu_width='300px', box='4 9 3 2', location='grid', 
                             cardname='ge_math', width='300px'):
    '''
    Create the General Education - Mathematics card
    '''
    ge = q.user.student_info['ge']['math']
    timedConnection = q.user.conn
    nopre = ge['nopre']
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Mathematics', size=ui.TextSize.L),
                ui.checkbox(name='ge_math_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_math_1',
                label='One Course (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_math,
                placeholder='(Select One)',
                trigger=True,
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (5,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_res_card(q, menu_width='300px', box='1 3 3 4', location='grid', 
                             cardname='ge_res', width='300px'):
    '''
    Create the General Education - Research and Computing Literacy card
    '''
    timedConnection = q.user.conn
    ge = q.user.student_info['ge']['res']
    nopre = ge['nopre']
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)
    # make some defaults based on area of program chosen:
    if q.user.student_info['menu']['area_of_study'] == '1':
        ge['1'] = 'PACE 111B'
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Research and Computing Literacy', size=ui.TextSize.L),
                ui.checkbox(name='ge_res_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_res_1',
                label='1. Professional Exploration (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_res_1,
                # default value will depend on the major chosen
                trigger=True,
                placeholder='(Select One)',
                popup='always',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (14,))
            ),
            ui.dropdown(
                name='ge_res_2',
                label='2. Research Skills / Professional Development (1 credit)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_res_2,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (15,))
            ),
            ui.dropdown(
                name='ge_res_3',
                label='3. Computing or IT (3 credits)',
                value=ge['3'] if (ge['3'] is not None) else q.args.ge_res_3,
                trigger=True,
                required=True,
                placeholder='(Select 3-credit Course)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_credits_query, (16,3))
            ),
           ui.dropdown(
                name='ge_res_3a',
                label='[or three 1-credit courses]:',
                required=True,
                value=ge['3a'] if (ge['3a'] is not None) else q.args.ge_res_3a,
                trigger=True,
                placeholder='(Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_credits_query, (16,1))
            ),
            ui.dropdown(
                name='ge_res_3b',
                #label='Computing or Information Technology (1 credit)',
                value=ge['3b'] if (ge['3b'] is not None) else q.args.ge_res_3b,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_credits_query, (16,1))
            ),
            ui.dropdown(
                name='ge_res_3c',
                #label='Computing or Information Technology (1 credit each)',
                value=ge['3c'] if (ge['3c'] is not None) else q.args.ge_res_3c,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_credits_query, (16,1))
            ),
        ]
    )
    add_card(q, cardname, card)

########################################################
####################  SCHEDULE PAGE  ###################
########################################################

async def return_d3plot(q, html, box='1 2 5 6', location='horizontal', 
                        height='500px', width='100%', add_title=False):
    '''
    Create the D3 display from html input
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, height=height, width=width)
    title = 'Course Schedule' if add_title else ''

    card = ui.frame_card(
        box=box,
        title=title,
        content=html
    )
    return card

async def return_schedule_menu(q, location='vertical', width='300px'):
    '''
    Create menu for schedule page
    (retrieve defaults from DB or from q.user.student_info fields)
    '''

    Sessions = ['Session 1', 'Session 2', 'Session 3']
    default_attend_summer = True
    student_profile = q.user.student_info['student_profile']
    if student_profile == 'Full-time':
        ## full-time: 
        ##   - 14 week and 17 week terms: (min 12, max 18)
        ##   - 4 week term: (min 3, max 6)
        ## half-time:
        ##   - 14 week and 17 week terms: (min 6)

        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 18
        default_courses_per_session = 3
    elif student_profile == 'Part-time':
        # todo: get courses_per_session and max_credits from university rules
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 7
        default_courses_per_session = 1
    else:
        # todo: enumerate the rest of the profile cases
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 13
        default_courses_per_session = 2

    card = ui.form_card(
        box = ui.box(location, width=width),
        items=[
            ui.dropdown(
                name='first_term',
                label='First Term',
                value=q.user.student_info['first_term'] if (q.user.student_info['first_term'] is not None) \
                    else q.args.first_term,
                trigger=False,
                width='150px',
                # todo: create these choices via same function call as used in scheduling slots
                choices=[
                    ui.choice(name='Spring 2024', label="Spring 2024"),
                    ui.choice(name='Summer 2024', label="Summer 2024"),
                    ui.choice(name='Fall 2024', label="Fall 2024"),
                    ui.choice(name='Winter 2025', label="Winter 2025"),
                ]),
            #                ui.separator(),
            ui.checklist(
                name='sessions_checklist',
                label='Sessions Attending',
                choices=[ui.choice(name=x, label=x) for x in Sessions],
                values=default_sessions,  # set default
            ),
            ui.spinbox(
                name='courses_per_session',
                label='Courses per Session',
                width='150px',
                min=1, max=5, step=1, value=default_courses_per_session),
            #                ui.separator(label=''),
            ui.slider(name='max_credits', label='Max Credits per Term', min=1, max=18, 
                step=1, value=default_max_credits),
            ui.checkbox(name='attend_summer', label='Attending Summer', 
                value=default_attend_summer),
            ui.inline(items=[
                ui.button(name='submit_schedule_menu', label='Submit', primary=True),
                ui.button(name='reset_schedule_menu', label='Reset', primary=False),
            ])
            #ui.button(name='submit_schedule_menu', label='Submit', primary=True),
        ]
    )
    return card

async def render_schedule_page_table(q, box=None, location='horizontal', width='90%', height=None):
    '''
    Input comes from 
    q:
    location:
    cardname:
    width:
    height:
    '''
    flex = q.app.flex
    df = q.user.student_data['schedule']

    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_schedule_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', 
                        max_width='300', cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='term', label='Term', max_width='50', data_type='number'),        
        ui.table_column(name='session', label='Session', max_width='80', data_type='number'),
        ui.table_column(name='locked', label='Locked', max_width='50', data_type='number'),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_schedule_description', label='Course Description'),
                    ui.command(name='move_class', label='Move Class'),
                    ui.command(name='lock_class', label='Lock/Unlock Class'),
                ]
        ))
        #            ui.command(name='select_elective', label='Select Elective'),
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['name'],
            cells=[
                #str(row['seq']),
                row['name'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
                str(row['term']),
                str(row['session']),
                str(row['locked']),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        #box = ui.box(location, height=height, width=width)
        box = ui.box(location, width=width)

    degree_program = q.user.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'schedule_table', ui.form_card(
        box=box,
        items=[
            #ui.inline(justify='between', align='center', items=[
            #    ui.text(title, size=ui.TextSize.L),
            #    ui.button(name='schedule_coursework', label='Schedule', 
            #        #caption='Description', 
            #        primary=True, disabled=False)
            #]),
            ui.table(
                name='schedule_table',
                downloadable=True,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card

async def render_d3plot(q, html, box='1 2 5 6', location='horizontal', height='500px', 
                        width='100%', cardname='schedule/d3_display', add_title=False):
    '''
    Create the D3 display from html input
    '''
    card = await return_d3plot(q, html, box, location, height, width, add_title)
    add_card(q, cardname, card)
async def render_schedule_menu(q, box='6 2 2 5', location='horizontal', width='300px',
                               cardname='schedule/menu'):
    '''
    Create menu for schedule page
    (retrieve defaults from DB or from q.user.student_info fields)
    '''
    card = await return_schedule_menu(q, box='6 2 2 5', location=location, width=width )
    add_card(q, cardname, card)

async def return_d3plot_ZZ(q, html, box='1 2 5 6', location='horizontal', 
                        height='500px', width='100%', add_title=False):
    '''
    Create the D3 display from html input
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, height=height, width=width)
    title = 'Course Schedule' if add_title else ''

    card = ui.frame_card(
        box=box,
        title=title,
        content=html
    )
    return card

async def return_schedule_menu_ZZ(q, box='6 2 2 5', location='vertical', width='300px'):
    '''
    Create menu for schedule page
    (retrieve defaults from DB or from q.user.student_info fields)
    '''
    flex = q.app.flex

    Sessions = ['Session 1', 'Session 2', 'Session 3']
    default_attend_summer = True
    student_profile = q.user.student_info['student_profile']
    if student_profile == 'Full-time':
        ## full-time: 
        ##   - 14 week and 17 week terms: (min 12, max 18)
        ##   - 4 week term: (min 3, max 6)
        ## half-time:
        ##   - 14 week and 17 week terms: (min 6)

        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 18
        default_courses_per_session = 3
    elif student_profile == 'Part-time':
        # todo: get courses_per_session and max_credits from university rules
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 7
        default_courses_per_session = 1
    else:
        # todo: enumerate the rest of the profile cases
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 13
        default_courses_per_session = 2

    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.dropdown(
                name='first_term',
                label='First Term',
                value=q.user.student_info['first_term'] if (q.user.student_info['first_term'] is not None) \
                    else q.args.first_term,
                trigger=False,
                width='150px',
                # todo: create these choices via same function call as used in scheduling slots
                choices=[
                    ui.choice(name='Spring 2024', label="Spring 2024"),
                    ui.choice(name='Summer 2024', label="Summer 2024"),
                    ui.choice(name='Fall 2024', label="Fall 2024"),
                    ui.choice(name='Winter 2025', label="Winter 2025"),
                ]),
            #                ui.separator(),
            ui.checklist(
                name='sessions_checklist',
                label='Sessions Attending',
                choices=[ui.choice(name=x, label=x) for x in Sessions],
                values=default_sessions,  # set default
            ),
            ui.spinbox(
                name='courses_per_session',
                label='Courses per Session',
                width='150px',
                min=1, max=5, step=1, value=default_courses_per_session),
            #                ui.separator(label=''),
            ui.slider(name='max_credits', label='Max Credits per Term', min=1, max=18, 
                step=1, value=default_max_credits),
            ui.checkbox(name='attend_summer', label='Attending Summer', 
                value=default_attend_summer),
            ui.inline(items=[
                ui.button(name='submit_schedule_menu', label='Submit', primary=True),
                ui.button(name='reset_schedule_menu', label='Reset', primary=False),
            ])
            #ui.button(name='submit_schedule_menu', label='Submit', primary=True),
        ]
    )
    return card

async def render_schedule_page_table_ZZ(q, box=None, location='horizontal', width='90%', height=None):
    '''
    Input comes from 
    q:
    location:
    cardname:
    width:
    height:
    '''
    flex = q.app.flex
    df = q.user.student_data['schedule']

    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_schedule_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', 
                        max_width='300', cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='term', label='Term', max_width='50', data_type='number'),        
        ui.table_column(name='session', label='Session', max_width='80', data_type='number'),
        ui.table_column(name='locked', label='Locked', max_width='50', data_type='number'),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_schedule_description', label='Course Description'),
                    ui.command(name='move_class', label='Move Class'),
                    ui.command(name='lock_class', label='Lock/Unlock Class'),
                ]
        ))
        #            ui.command(name='select_elective', label='Select Elective'),
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['name'],
            cells=[
                #str(row['seq']),
                row['name'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
                str(row['term']),
                str(row['session']),
                str(row['locked']),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        #box = ui.box(location, height=height, width=width)
        box = ui.box(location, width=width)

    degree_program = q.user.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'schedule_table', ui.form_card(
        box=box,
        items=[
            #ui.inline(justify='between', align='center', items=[
            #    ui.text(title, size=ui.TextSize.L),
            #    ui.button(name='schedule_coursework', label='Schedule', 
            #        #caption='Description', 
            #        primary=True, disabled=False)
            #]),
            ui.table(
                name='schedule_table',
                downloadable=True,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card
async def render_d3plot_ZZ(q, html, box='1 2 5 6', location='horizontal', height='500px', 
                        width='100%', cardname='schedule/d3_display', add_title=False):
    '''
    Create the D3 display from html input
    '''
    card = await return_d3plot(q, html, box, location, height, width, add_title)
    add_card(q, cardname, card)
async def render_schedule_menu_ZZ(q, box='6 2 2 5', location='horizontal', width='300px',
                               cardname='schedule/menu'):
    '''
    Create menu for schedule page
    (retrieve defaults from DB or from q.user.student_info fields)
    '''
    card = await return_schedule_menu(q, box='6 2 2 5', location=location, width=width )
    add_card(q, cardname, card)

######################################################
####################  PROJECT PAGE  ##################
######################################################

def render_home_cards_ZZ(q, location='top_horizontal', width='25%'):
    add_card(q, 'student_guest', ui.wide_info_card(
        box=ui.box(location, width=width),
        name='',
        icon='Contact',
        title='Guests',
        caption='Login not required to use this app.'
    ))
    add_card(q, 'login',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='login',
            title='Login',
            caption='User roles: *admin*, *coach*, *student*, *prospect*.',
            icon='Signin')
    )
    add_card(q, 'import',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='import',
            title='Import',
            caption='Future state: Import UMGC student info.',
            icon='Import')
    )
    add_card(q, 'personalize',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='person',
            title='Personalize',
            caption='User adds new info or confirms imported info.',
            icon='UserFollowed')
    )


def render_home_cards(q, location='top_horizontal', width='25%'):
    add_card(q, 'student_guest', ui.wide_info_card(
        box=ui.box(location, width=width),
        name='',
        icon='Contact',
        title='Guests',
        caption='Login not required to use this app.'
    ))
    add_card(q, 'login',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='login',
            title='Login',
            caption='User roles: *admin*, *coach*, *student*, *prospect*.',
            icon='Signin')
    )
    add_card(q, 'import',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='import',
            title='Import',
            caption='Future state: Import UMGC student info.',
            icon='Import')
    )
    add_card(q, 'personalize',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='person',
            title='Personalize',
            caption='User adds new info or confirms imported info.',
            icon='UserFollowed')
    )


import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g

project_data = [
    {
        "id": "1",
        "rank": "1",
        "category": "Catalog",
        "description": "Enter all undergraduate courses into DB",
        "status": "1.00",
        "tags": "Database",
        "group": "Database"
    },
    {
        "id": "2",
        "rank": "2",
        "category": "Catalog",
        "description": "Enter all graduate courses into DB",
        "status": "0.00",
        "tags": "Database"
    },
    {
        "id": "3",
        "rank": "3",
        "category": "Catalog",
        "description": "Enter all Associate's programs",
        "status": str(2 / 50),
        "tags": "Database"
    },
    {
        "id": "4",
        "rank": "4",
        "category": "Catalog",
        "description": "Enter all Bachelor's Major programs",
        "status": str(2 / 50),
        "tags": "Database"
    },
    {
        "id": "5",
        "rank": "5",
        "category": "Catalog",
        "description": "Enter all Bachelor's Minor programs",
        "status": str(2 / 50),
        "tags": "Database"
    },
    {
        "id": "6",
        "rank": "6",
        "category": "Catalog",
        "description": "Enter all Undergraduate Certificates",
        "status": str(2 / 50),
        "tags": "Database"
    },
    {
        "id": "6",
        "rank": "6",
        "category": "Catalog",
        "description": "Enter all Master's programs",
        "status": str(2 / 50),
        "tags": "Database"
    },

    {
        "id": "3",
        "rank": "3",
        "category": "Wave",
        "description": "Make table menus active",
        "status": "0.00",
        "tags": "Wave"
    },
    {
        "id": "3",
        "rank": "3",
        "category": "Wave",
        "description": "Example Text",
        "status": "0.90",
        "tags": "Data,UI"
    },
    {
        "id": "5",
        "rank": "5",
        "category": "Example",
        "description": "Example Text",
        "status": "0.90",
        "tags": "Data,UI"
    },
    {
        "id": "4",
        "rank": "4",
        "category": "Example",
        "description": "Example Text",
        "status": "0.50",
        "tags": "Code"
    },
]

# used to be on app, not used now?
complete_records_query = '''
    SELECT 
        a.seq,
        a.name,
        a.program_id,
        a.class_id,
        a.course_type_id,
        b.title,
        b.description,
        b.prerequisites
    FROM 
        program_sequence a
    JOIN 
        courses b
    ON 
        a.class_id = b.id
    WHERE 
        a.program_id = ?
'''

# query moved to view
ge_query_j_old_delete_me = '''
    SELECT 
        b.id,
        b.name,
        b.title,
        b.credits,
        b.description,
        b.pre,
        b.pre_credits
    FROM 
        general_education a
    LEFT JOIN 
        courses b
    ON 
        a.course_id = b.id
    WHERE 
        b.general_education_requirements_id = ?
'''

ge_query_j = 'SELECT * FROM ge_view WHERE ge_id = ?'

complete_records_query = 'SELECT * FROM complete_records_view WHERE program_id = ?'

complete_student_records_query = 'SELECT * FROM student_records_view WHERE student_info_id = ?'


home_markdown = '''
# Notes

We need to allow for a view with exploration before someone logs in (suppose this is used by somebody not yet enrolled). We will add additional views for those that are logged in. E.g., completed courses, transfer credits, etc.

_**We assume someone is logged in at this point.**_

Once logged in, the home page will show important dashboard.


## Tab Steps Above (Currently Disabled)
### Login

### Import information

### Update Information

### Personalization

'''

home_markdown2 = '''
## Philosophy

- For this prototype, we will assume we have access to appropriate student information.
  -  What information that entails we will fill in as we go.

- For this prototype, we will save the student information in a sqlite3 db to be retrieved in course
- We will keep track of the steps, and show different "Home" pages depending on what has already been filled in by the student. 
- We will also allow the student to navigate to previous steps to update or fix information.
- The most important information is included as tabs in the top of the webpage.

'''

home_markdown1 = '''
# Notes

We need to allow for a view with exploration before someone logs in (suppose this is used by somebody not yet enrolled). We will add additional views for those that are logged in. E.g., completed courses, transfer credits, etc.

_**We assume someone is logged in at this point.**_

_**Need to add a few example students to our DB to demo the web tool.**_

Once logged in, the home page will show important dashboard.


## Tab Steps Above (Currently Disabled)
### Login

1. This is where the notes will go.
1. This is where the notes will go.

### Import information

1. This is where the notes will go.

### Update Information

1. This is where  the notes will go.

### Personalization

1. This is where the notes will go.
'''

sample_markdown = '''
## Notes and To Do's:

To Do:

- Find icons and change them.
- Add dropdown or tab menus for personalization
- Add menus for elective exploration and selection
- Add menus for minor exploration and selection
- Add checkbox or toggle switch for adding completed credits
'''

## Escape curly brackets {} with {{}} so that substitution within Python works properly
html_code_works = '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      text-align: center;
    }}
    
    svg {{
      margin-top: 12px;
      border: 1px solid #aaa;
    }}
  </style>

  <!-- Load d3.js -->
  <script src='https://d3js.org/d3.v5.js'></script>
</head>

<body>

  <script type="module">
    const screenWidth = 800;
    const boxWidth = 110;
    const boxHeight = 40;
    const textOffsetX = 10; 
    const textOffsetY = 25;
    const sessionOffset = 60;
    const headerRow = 20;

    // Define x coordinates for rectangles
    var bin = [10];
    // if sessions, then 2.25*boxWidth else boxWidth
    for (let k=0; k <=30; k++) {{
        bin.push(bin[k] + 20 + 2.25*boxWidth);
    }}
    
    // Define y coordinates for rectangles
    const yGap = 4;
    const boxSpace = boxHeight + yGap;
    var row = [80];
    for (let k=0; k <=10; k++) {{
        row.push(row[k] + boxSpace);
    }}

    var semesterData = [];
    const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
    for (let year = 2024; year <= 2040; year++) {{
      for (let season of seasons) {{
        semesterData.push(`${{season}} ${{year}}`);
      }}
    }}
    
    function render(data) {{
      // Start Nested Functions
      function drawColumn(period, data) {{
        var filteredData = data.filter(item => item.period === period);
        var anyItem = false;
        for (let j = 0; j < data.length; j++) {{
          let offset = (j % 3 - 1) * sessionOffset;
          let item = filteredData[j];
          if (item !== undefined) {{
            anyItem = true;
            let fullname = `${{item.name}} (${{item.credits}})`;
            drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
          }}
        }}
        if (anyItem) {{
          drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
        }}
      }}
      function drawRectangle(x, y, name, color, textcolor, description='') {{
        var g = zoomable.append("g");
        g.append("rect")
          .attr("x", x)
          .attr("y", y)
          .attr("width", boxWidth)
          .attr("height", boxHeight)
          .style("fill", color)
          .classed("movable", true); // Add the "movable" class
        g.append("text")
          .attr("x", x + textOffsetX)
          .attr("y", y + textOffsetY)
          .text(name)
          .attr("fill", textcolor)
          .style("font-size", "12px")
          .style("font-family", "Arial")
          .style("font-weight", "bold")
          .classed("movable", true); // Add the "movable" class
        // Add a tooltip
        g.append("description")
          .text(description);
      }}
      function drawHeader(x, y, name, color, textcolor, description='') {{
        var g = zoomable.append("g");
        g.append("rect")
          .attr("x", x - sessionOffset)
          .attr("y", y)
          .attr("width", boxWidth + 2 * sessionOffset)
          .attr("height", boxHeight)
          .style("fill", color)
          .classed("movable", true); // Add the "movable" class
        g.append("text")
          .attr("x", x - sessionOffset + 2*textOffsetX)
          .attr("y", y + textOffsetY)
          .text(name)
          .attr("fill", textcolor)
          .style("font-size", "14px")
          .style("font-family", "Arial")
          .style("font-weight", "bold")
          .classed("movable", true); // Add the "movable" class
        // Add a tooltip
        g.append("description")
          .text(description);
      }}
      // End of Nested Functions
      zoomable.selectAll(".movable").remove();
      var maxPeriod = Math.max(...data.map(item => item.period));
      for (let j = 0; j <= maxPeriod; j++) {{
        drawColumn(j, data);
      }}
    }}

    // Select the body
    var body = d3.select("body");

    // Zoom behavior
    var svg = body.append('svg')
      .attr('id', 'datavizArea')
      .attr('height', 300)
      .attr('width', 900);
    var zoomable = svg.append("g");
    var zoom = d3.zoom()
      .on("zoom", function() {{
        zoomable.attr("transform", d3.event.transform);
      }});
    svg.call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(0.80).translate(-160, 0));

    render({data});
  
  </script>

</body>
</html>
'''

## Escape curly brackets {} with {{}} so that substitution within Python works properly
html_code = '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      text-align: center;
    }}   
    svg {{
      margin-top: 12px;
      border: 1px solid #aaa;
    }}
  </style>
  <script src='https://d3js.org/d3.v5.js'></script>
</head>
<body>
  <script type="module">
    {javascript}
    render({data});
  </script>
</body>
</html>
'''

## Escape curly brackets {} with {{}} so that substitution within Python works properly
html_code_minimal = '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      text-align: center;
    }}   
    svg {{
      margin-top: 12px;
      border: 1px solid #aaa;
    }}
  </style>
  <script src='https://d3js.org/d3.v5.js'></script>
</head>
<body>
  <script type="module">
    {javascript}
    render({headers});
    render({data});
  </script>
</body>
</html>
'''

javascript_insert_double = '''
    const screenWidth = 800;
    const boxWidth = 110;
    const boxHeight = 40;
    const textOffsetX = 10; 
    const textOffsetY = 25;
    const sessionOffset = 60;
    const headerRow = 20;

    // Define x coordinates for rectangles
    var bin = [10];
    // if sessions, then 2.25*boxWidth else boxWidth
    for (let k=0; k <=30; k++) {{
        bin.push(bin[k] + 20 + 2.25*boxWidth);
    }}
    
    // Define y coordinates for rectangles
    const yGap = 4;
    const boxSpace = boxHeight + yGap;
    var row = [80];
    for (let k=0; k <=10; k++) {{
        row.push(row[k] + boxSpace);
    }}

    var semesterData = [];
    const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
    for (let year = 2024; year <= 2040; year++) {{
      for (let season of seasons) {{
        semesterData.push(`${{season}} ${{year}}`);
      }}
    }}
    
    function render(data) {{
      // Start Nested Functions
      function drawColumn(period, data) {{
        var filteredData = data.filter(item => item.period === period);
        var anyItem = false;
        for (let j = 0; j < data.length; j++) {{
          let offset = (j % 3 - 1) * sessionOffset;
          let item = filteredData[j];
          if (item !== undefined) {{
            anyItem = true;
            let fullname = `${{item.name}} (${{item.credits}})`;
            drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
          }}
        }}
        if (anyItem) {{
          drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
        }}
      }}
      function drawRectangle(x, y, name, color, textcolor, description='') {{
        var g = zoomable.append("g");
        g.append("rect")
          .attr("x", x)
          .attr("y", y)
          .attr("width", boxWidth)
          .attr("height", boxHeight)
          .style("fill", color)
          .classed("movable", true); // Add the "movable" class
        g.append("text")
          .attr("x", x + textOffsetX)
          .attr("y", y + textOffsetY)
          .text(name)
          .attr("fill", textcolor)
          .style("font-size", "12px")
          .style("font-family", "Arial")
          .style("font-weight", "bold")
          .classed("movable", true); // Add the "movable" class
        // Add a tooltip
        g.append("description")
          .text(description);
      }}
      function drawHeader(x, y, name, color, textcolor, description='') {{
        var g = zoomable.append("g");
        g.append("rect")
          .attr("x", x - sessionOffset)
          .attr("y", y)
          .attr("width", boxWidth + 2 * sessionOffset)
          .attr("height", boxHeight)
          .style("fill", color)
          .classed("movable", true); // Add the "movable" class
        g.append("text")
          .attr("x", x - sessionOffset + 2*textOffsetX)
          .attr("y", y + textOffsetY)
          .text(name)
          .attr("fill", textcolor)
          .style("font-size", "14px")
          .style("font-family", "Arial")
          .style("font-weight", "bold")
          .classed("movable", true); // Add the "movable" class
        // Add a tooltip
        g.append("description")
          .text(description);
      }}
      // End of Nested Functions
      zoomable.selectAll(".movable").remove();
      var maxPeriod = Math.max(...data.map(item => item.period));
      for (let j = 0; j <= maxPeriod; j++) {{
        drawColumn(j, data);
      }}
    }}

    // Select the body
    var body = d3.select("body");

    // Zoom behavior
    var svg = body.append('svg')
      .attr('id', 'datavizArea')
      .attr('height', 300)
      .attr('width', 900);
    var zoomable = svg.append("g");
    var zoom = d3.zoom()
      .on("zoom", function() {{
        zoomable.attr("transform", d3.event.transform);
      }});
    svg.call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(0.80).translate(-160, 0));
'''

## javascript_minimal is currently the one being used !!!!
javascript_insert = '''
    const screenWidth = 800;
    const boxWidth = 110;
    const boxHeight = 40;
    const textOffsetX = 10; 
    const textOffsetY = 25;
    const sessionOffset = 60;
    const headerRow = 20;

    // Define x coordinates for rectangles
    var bin = [10];
    // if sessions, then 2.25*boxWidth else boxWidth
    for (let k=0; k <=30; k++) {
        bin.push(bin[k] + 20 + 2.3*boxWidth);
    }
    
    // Define y coordinates for rectangles
    const yGap = 4;
    const boxSpace = boxHeight + yGap;
    var row = [80];
    for (let k=0; k <=10; k++) {
        row.push(row[k] + boxSpace);
    }

    var semesterData = [];
    const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
    for (let year = 2024; year <= 2040; year++) {
      for (let season of seasons) {
        semesterData.push(`${season} ${year}`);
      }
    }
    
    function render(data) {
      // Start Nested Functions
      function drawColumn(period, data) {
        var filteredData = data.filter(item => item.period === period);
        var anyItem = false;
        for (let j = 0; j < data.length; j++) {
          let offset = (j % 3 - 1) * sessionOffset;
          let item = filteredData[j];
          if (item !== undefined) {
            anyItem = true;
            let fullname = `${item.name} (${item.credits})`;
            drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
          }
        }
        if (anyItem) {
          drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
        }
      }
      function drawRectangle(x, y, name, color, textcolor, description='') {
        var g = zoomable.append("g");
        g.append("rect")
          .attr("x", x)
          .attr("y", y)
          .attr("width", boxWidth)
          .attr("height", boxHeight)
          .style("fill", color)
          .classed("movable", true); // Add the "movable" class
        g.append("text")
          .attr("x", x + textOffsetX)
          .attr("y", y + textOffsetY)
          .text(name)
          .attr("fill", textcolor)
          .style("font-size", "12px")
          .style("font-family", "Arial")
          .style("font-weight", "bold")
          .classed("movable", true); // Add the "movable" class
        // Add a tooltip
        g.append("description")
          .text(description);
      }
      function drawHeader(x, y, name, color, textcolor, description='') {
        var g = zoomable.append("g");
        g.append("rect")
          .attr("x", x - sessionOffset)
          .attr("y", y)
          .attr("width", boxWidth + 2 * sessionOffset)
          .attr("height", boxHeight)
          .style("fill", color)
          .classed("movable", true); // Add the "movable" class
        g.append("text")
          .attr("x", x - sessionOffset + 2*textOffsetX)
          .attr("y", y + textOffsetY)
          .text(name)
          .attr("fill", textcolor)
          .style("font-size", "14px")
          .style("font-family", "Arial")
          .style("font-weight", "bold")
          .classed("movable", true); // Add the "movable" class
        // Add a tooltip
        g.append("description")
          .text(description);
      }
      // End of Nested Functions
      zoomable.selectAll(".movable").remove();
      var maxPeriod = Math.max(...data.map(item => item.period));
      for (let j = 0; j <= maxPeriod; j++) {
        drawColumn(j, data);
      }
    }

    // Select the body
    var body = d3.select("body");

    // Zoom behavior
    var svg = body.append('svg')
      .attr('id', 'datavizArea')
      .attr('height', 300)
      .attr('width', 900);
    var zoomable = svg.append("g");
    var zoom = d3.zoom()
      .on("zoom", function() {
        zoomable.attr("transform", d3.event.transform);
      });
    svg.call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(0.80).translate(-160, 0));
'''

# javascript_draw_only takes coordinates from python rather than computing itself in d3
# it is the current implementation

javascript_draw_only = '''
    //const screenWidth = 1200;
    const screenWidth = 800;
    const boxHeight = 40;
    const textOffsetX = 20;
    const textOffsetY = 25;

    function drawRect(x, y, width, printname, color, textcolor, offset, fontsize, description) {
        var g = zoomable.append("g");
        g.append("rect")
            .attr("x", x)
            .attr("y", y)
            .attr("width", width)
            .attr("height", boxHeight)
            .style("fill", color)
            .classed("movable", true); 
        g.append("text")
            .attr("x", x + offset*textOffsetX)
            .attr("y", y + textOffsetY)
            .text(printname)
            .attr("fill", textcolor)
            .style("font-size", fontsize)
            .style("font-family", "Arial")
            .style("font-weight", "bold")
            .classed("movable", true); 
        // Add a tooltip
        g.append("description")
            .text(description);
    }
    function render(data) {
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            if (item.x === undefined || 
                item.y === undefined ||
                item.width === undefined || 
                item.printname === undefined || 
                item.color === undefined || 
                item.textcolor === undefined ||
                item.offset === undefined ||
                item.fontsize === undefined ||
                item.description === undefined) {
                    console.error('Error: Missing property in item ' + i);
                    continue;
            }
            drawRect(item.x, item.y, item.width, item.printname, item.color, 
                item.textcolor, item.offset, item.fontsize, item.description);
        }
    }

    // Select the body
    var body = d3.select("body");
    // Zoom behavior
    var svg = body.append('svg')
        .attr('id', 'datavizArea')
        .attr('height', 290)
        .attr('width', 690);
    var zoomable = svg.append("g");
    var zoom = d3.zoom()
        .on("zoom", function() {
            zoomable.attr("transform", d3.event.transform);
        });
    svg.call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(0.75).translate(0, 0));
'''

## Escape curly brackets {} with {{}} so that substitution within Python works properly
javascript_code = '''
const screenWidth = 800;
const boxWidth = 110;
const boxHeight = 40;
const textOffsetX = 10; 
const textOffsetY = 25;
const sessionOffset = 35;
const headerRow = 20;

// Define x coordinates for rectangles
var bin = [10];
// if sessions, then 1.75*boxWidth else boxWidth
for (let k=0; k <=30; k++) {{
    bin.push(bin[k] + 20 + 1.75*boxWidth);
}}
    
// Define y coordinates for rectangles
const yGap = 4;
const boxSpace = boxHeight + yGap;
var row = [80];
for (let k=0; k <=10; k++) {{
    row.push(row[k] + boxSpace);
}}

var semesterData = [];
const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
for (let year = 2024; year <= 2040; year++) {{
  for (let season of seasons) {{
    semesterData.push(`${{season}} ${{year}}`);
  }}
}}
    
function render(data) {{
  // Start Nested Functions
  function drawColumn(period, data) {{
    var filteredData = data.filter(item => item.period === period);
    var anyItem = false;
    for (let j = 0; j < data.length; j++) {{
      let offset = (j % 3 - 1) * sessionOffset;
      let item = filteredData[j];
      if (item !== undefined) {{
        anyItem = true;
        let fullname = `${{item.name}} (${{item.credits}})`;
        drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
      }}
    }}
    if (anyItem) {{
      drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
    }}
  }}
  function drawRectangle(x, y, name, color, textcolor, description='') {{
    var g = zoomable.append("g");
    g.append("rect")
      .attr("x", x)
      .attr("y", y)
      .attr("width", boxWidth)
      .attr("height", boxHeight)
      .style("fill", color)
      .classed("movable", true); // Add the "movable" class
    g.append("text")
      .attr("x", x + textOffsetX)
      .attr("y", y + textOffsetY)
      .text(name)
      .attr("fill", textcolor)
      .style("font-size", "12px")
      .style("font-family", "Arial")
      .style("font-weight", "bold")
      .classed("movable", true); // Add the "movable" class
    // Add a tooltip
    g.append("description")
      .text(description);
  }}
  function drawHeader(x, y, name, color, textcolor, description='') {{
    var g = zoomable.append("g");
    g.append("rect")
      .attr("x", x - sessionOffset)
      .attr("y", y)
      .attr("width", boxWidth + 2 * sessionOffset)
      .attr("height", boxHeight)
      .style("fill", color)
      .classed("movable", true); // Add the "movable" class
    g.append("text")
      .attr("x", x - sessionOffset + 2*textOffsetX)
      .attr("y", y + textOffsetY)
      .text(name)
      .attr("fill", textcolor)
      .style("font-size", "14px")
      .style("font-family", "Arial")
      .style("font-weight", "bold")
      .classed("movable", true); // Add the "movable" class
    // Add a tooltip
    g.append("description")
      .text(description);
  }}
  // End of Nested Functions
  zoomable.selectAll(".movable").remove();
  var maxPeriod = Math.max(...data.map(item => item.period));
  for (let j = 0; j <= maxPeriod; j++) {{
    drawColumn(j, data);
  }}
}}

// Select the body
var body = d3.select("body");

// Zoom behavior
var svg = body.append('svg')
  .attr('id', 'datavizArea')
  .attr('height', 400)
  .attr('width', 800);
var zoomable = svg.append("g");
var zoom = d3.zoom()
  .on("zoom", function() {{
    zoomable.attr("transform", d3.event.transform);
  }});
svg.call(zoom);
'''

d3_template = '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      text-align: center;
    }
    svg {
      margin-top: 12px;
      border: 1px solid #aaa;
    }
  </style>
  <!-- Load d3.js -->
  <script src='https://d3js.org/d3.v5.js'></script>
</head>

<body style="margin:0; padding:0">
  <script src="{script}"></script>
  <script>render({data})</script>
</body>
</html>
'''

data_json = [
    {
        "seq": 1,
        "name": "PACE 111B",
        "credits": 3,
        "color": "purple",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1,
    },
    {
        "seq": 2,
        "name": "LIBS 150",
        "credits": 1,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1,
    },
    {
        "seq": 3,
        "name": "WRTG 111",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1,
    },
    {
        "seq": 4,
        "name": "WRTG 112",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 2
    },
    {
        "seq": 5,
        "name": "NUTR 100",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 2
    },
    {
        "seq": 6,
        "name": "BMGT 110",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 2
    },
    {
        "seq": 7,
        "name": "SPCH 100",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 3
    },
    {
        "seq": 8,
        "name": "STAT 200",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 3
    },
    {
        "seq": 9,
        "name": "IFSM 300",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 3
    },
    {
        "seq": 10,
        "name": "ACCT 220",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 4
    },
    {
        "seq": 11,
        "name": "HUMN 100",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 4
    },
    {
        "seq": 12,
        "name": "BIOL 103",
        "credits": 4,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 5
    },
    {
        "seq": 13,
        "name": "ECON 201",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 4
    },
    {
        "seq": 14,
        "name": "ARTH 334",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 5
    },
    {
        "seq": 15,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 6
    },
    {
        "seq": 16,
        "name": "ECON 203",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 6
    },
    {
        "seq": 17,
        "name": "ACCT 221",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "ACCT 220",
        "period": 6
    },
    {
        "seq": 18,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 7
    },
    {
        "seq": 19,
        "name": "BMGT 364",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 7
    },
    {
        "seq": 20,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 7
    },
    {
        "seq": 21,
        "name": "BMGT 365",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "BMGT 364",
        "period": 8
    },
    {
        "seq": 22,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 8
    },
    {
        "seq": 23,
        "name": "MRKT 310",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 8
    },
    {
        "seq": 24,
        "name": "WRTG 394",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "WRTG 112",
        "period": 9
    },
    {
        "seq": 25,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 9
    },
    {
        "seq": 26,
        "name": "BMGT 380",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 9
    },
    {
        "seq": 27,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 10
    },
    {
        "seq": 28,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 10
    },
    {
        "seq": 29,
        "name": "HRMN 300",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 10
    },
    {
        "seq": 30,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 11
    },
    {
        "seq": 31,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 11
    },
    {
        "seq": 32,
        "name": "FINC 330",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "ACCT 221 & STAT 200",
        "period": 11
    },
    {
        "seq": 33,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 12
    },
    {
        "seq": 34,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 12
    },
    {
        "seq": 35,
        "name": "BMGT 496",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 12
    },
    {
        "seq": 36,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 13
    },
    {
        "seq": 37,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 13
    },
    {
        "seq": 38,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 13
    },
    {
        "seq": 39,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 14
    },
    {
        "seq": 40,
        "name": "BMGT 495",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "BMGT 365 & MRKT 310 & FINC 330",
        "period": 14
    },
    {
        "seq": 41,
        "name": "CAPSTONE",
        "credits": 1,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "FINC 330",
        "period": 14
    }
]

## map "term" to "period" using start_term
## allow someone to X out of a term directly

## will make it possible to move from one session to another
## check whether prerequisites in session 1 fulfill session 3 follow up
## also, have warnings for courses that should be taken closely together if we are doing,
##  e.g., period 1 session 1 to period 2 session 3 is a pretty long time
## allow people to x out a session
## 

data_json_new = [
    { "seq":  1, "name": "PACE 111", "credits": 3, "type": "general",  "period":  1, "session": 1, "prerequisite": ""                                },
    { "seq":  2, "name": "LIBS 150", "credits": 1, "type": "general",  "period":  1, "session": 2, "prerequisite": ""                                },
    { "seq":  3, "name": "WRTG 111", "credits": 3, "type": "general",  "period":  1, "session": 3, "prerequisite": ""                                },
    { "seq":  4, "name": "WRTG 112", "credits": 3, "type": "general",  "period":  2, "session": 1, "prerequisite": ""                                },
    { "seq":  5, "name": "NUTR 100", "credits": 3, "type": "general",  "period":  2, "session": 2, "prerequisite": ""                                },
    { "seq":  6, "name": "BMGT 110", "credits": 3, "type": "major",    "period":  3, "session": 3, "prerequisite": ""                                },
    { "seq":  7, "name": "SPCH 100", "credits": 3, "type": "general",  "period":  3, "session": 1, "prerequisite": ""                                },
    { "seq":  8, "name": "STAT 200", "credits": 3, "type": "required", "period":  3, "session": 2, "prerequisite": ""                                },
    { "seq":  9, "name": "IFSM 300", "credits": 3, "type": "required", "period":  4, "session": 1, "prerequisite": ""                                },
    { "seq": 10, "name": "ACCT 220", "credits": 3, "type": "major",    "period":  4, "session": 2, "prerequisite": ""                                }, 
    { "seq": 11, "name": "HUMN 100", "credits": 3, "type": "general",  "period":  4, "session": 3, "prerequisite": ""                                }, 
    { "seq": 12, "name": "BIOL 103", "credits": 4, "type": "general",  "period":  5, "session": 1, "prerequisite": ""                                }, 
    { "seq": 13, "name": "ECON 201", "credits": 3, "type": "required", "period":  5, "session": 3, "prerequisite": ""                                }, 
    { "seq": 14, "name": "ARTH 334", "credits": 3, "type": "general",  "period":  5, "session": 2, "prerequisite": ""                                },
    { "seq": 15, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  6, "session": 1, "prerequisite": ""                                }, 
    { "seq": 16, "name": "ECON 203", "credits": 3, "type": "required", "period":  6, "session": 2, "prerequisite": ""                                }, 
    { "seq": 17, "name": "ACCT 221", "credits": 3, "type": "major",    "period":  7, "session": 1, "prerequisite": "ACCT 220"                        }, 
    { "seq": 18, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  7, "session": 2, "prerequisite": ""                                }, 
    { "seq": 19, "name": "BMGT 364", "credits": 3, "type": "major",    "period":  7, "session": 3, "prerequisite": ""                                }, 
    { "seq": 20, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  8, "session": 2, "prerequisite": ""                                }, 
    { "seq": 21, "name": "BMGT 365", "credits": 3, "type": "major",    "period":  8, "session": 1, "prerequisite": "BMGT 364"                        }, 
    { "seq": 22, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  9, "session": 1, "prerequisite": ""                                }, 
    { "seq": 23, "name": "MRKT 310", "credits": 3, "type": "major",    "period":  8, "session": 3, "prerequisite": ""                                }, 
    { "seq": 24, "name": "WRTG 394", "credits": 3, "type": "general",  "period":  9, "session": 2, "prerequisite": "WRTG 112"                        }, 
    { "seq": 25, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  9, "session": 3, "prerequisite": ""                                }, 
    { "seq": 26, "name": "BMGT 380", "credits": 3, "type": "major",    "period": 10, "session": 1, "prerequisite": ""                                }, 
    { "seq": 27, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 10, "session": 2, "prerequisite": ""                                }, 
    { "seq": 28, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 11, "session": 1, "prerequisite": ""                                }, 
    { "seq": 29, "name": "HRMN 300", "credits": 3, "type": "major",    "period": 11, "session": 2, "prerequisite": ""                                },
    { "seq": 30, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 11, "session": 3, "prerequisite": ""                                }, 
    { "seq": 31, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 12, "session": 2, "prerequisite": ""                                }, 
    { "seq": 32, "name": "FINC 330", "credits": 3, "type": "major",    "period": 12, "session": 1, "prerequisite": "ACCT 221 & STAT 200"             }, 
    { "seq": 33, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 12, "session": 3, "prerequisite": ""                                }, 
    { "seq": 34, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 13, "session": 1, "prerequisite": ""                                }, 
    { "seq": 35, "name": "BMGT 496", "credits": 3, "type": "major",    "period": 13, "session": 2, "prerequisite": ""                                }, 
    { "seq": 36, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 13, "session": 3, "prerequisite": ""                                }, 
    { "seq": 37, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 14, "session": 1, "prerequisite": ""                                }, 
    { "seq": 38, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 14, "session": 2, "prerequisite": ""                                }, 
    { "seq": 39, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 15, "session": 1, "prerequisite": ""                                }, 
    { "seq": 40, "name": "BMGT 495", "credits": 3, "type": "major",    "period": 15, "session": 2, "prerequisite": "BMGT 365 & MRKT 310 & FINC 330"  }, 
    { "seq": 41, "name": "CAPSTONE", "credits": 1, "type": "elective", "period": 15, "session": 3, "prerequisite": "FINC 330"                        }, 
]
