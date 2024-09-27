from contextlib import asynccontextmanager
from h2o_wave import main, app, Q, ui, on, run_on, data, expando_to_dict
from typing import Any, Dict, Callable, List, Optional, Union
import numpy as np
import pandas as pd
import logging
import asyncio
import sys
import time
import sqlite3
from backend.connection import TimedSQLiteConnection

###########################################################
####################  UTILITY FUNCTIONS  ##################
###########################################################

def update_dict(original: dict, update: dict, new: bool = True) -> dict:
    '''
    Update the original dictionary with values from the update dictionary.

    Parameters:
    original (dict): The original dictionary that will be updated.
    update (dict): The dictionary containing new values to update or add.
    new (bool): If True, new keys from the update dictionary will be added to the original.
                If False, only existing keys in the original dictionary will be updated.

    Returns:
    dict: The updated original dictionary.

    Note:
    This function modifies the original dictionary in place and returns it.
    '''
    for key, value in update.items():
        if value is not None:
            if new:
                # Add new keys and update existing keys
                original[key] = value
            elif key in original:
                # Only update if the key already exists in the original
                original[key] = value
    return original

##############################################################
####################  INITIALIZE FUNCTIONS  ##################
##############################################################

def initialize_ge() -> dict:
    """
    Initialize General Education tracking for undergraduate students.
    Called by initialize_student_info
    """
    ge = {
        'arts': {'1': None, '2': None, 'nopre': False},
        'beh': {'1': None, '2': None, 'nopre': False},
        'bio': {'1a': None, '1b': None, '1c': None, '2': None, 'nopre': False},
        'comm': {'1': 'WRTG 111', '2': 'WRTG 112', '3': None, '4': None, 'nopre': False},
        'math': {'1': None, 'nopre': False},
        'res': {'1': None, '2': 'LIBS 150', '3': None, '3a': None, '3b': None, '3c': None, 'nopre': False},
        'total': {},
        'summary': {}
    }
    return ge

def initialize_student_info() -> dict:
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
        'degree_id',
        'degree_program'
    ]
    student_info.update({ name: None for name in attributes })
    student_info['menu'] = {
        'degree': None,
        'area_of_study': None,
        'program': None
    }
    student_info['ge'] = initialize_ge()
    return student_info

def initialize_student_data() -> dict:
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
    student_data.update({ name: None for name in attributes })
    return student_data

def reset_student():
    '''
    Initialize both student dictionaries
    '''
    result = {
        'student_info': initialize_student_info(),
        'student_data': initialize_student_data()
    }
    return result

##############################################################
####################  POPULATE FUNCTIONS  ####################
##############################################################

## all of the menu functions other than retrieving information from the database should be in frontend
## the reverse engineer should really be in frontend instead of backend

async def reverse_engineer_dropdown_menu(conn: TimedSQLiteConnection, program_id: int) -> dict:
    """
    Recreate dropdown menus for students based on their program ID.
    This function is used when the dropdown menu status was not saved and needs to be reconstructed.

    Args:
        conn: Asynchronous database connection object
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
            row = await conn.query_one(query, params=(program_id,))
            if row:
                menu['degree'] = row['menu_degree_id']
                menu['area_of_study'] = row['menu_area_id']
        except Exception as e:
            print(f"Error retrieving menu data: {str(e)}")
            # Depending on your error handling strategy, you might want to re-raise the exception

    return menu

async def populate_student_info_dict(conn: TimedSQLiteConnection, user_id: int, 
                                     default_first_term: str = 'Spring 2024') -> dict:
    """
    Get information from student_info table and populate the student_info dictionary.

    Args:
        conn: Asynchronous database connection object
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
        result = await conn.query_dict(query, params=(user_id,))

        if not result:
            raise ValueError(f"No student found with user_id: {user_id}")
        
        student_info = result[0]
        
        if student_info.get('program_id'):
            program_id = student_info['program_id']
            program_info = await get_program_title(conn, program_id)
            if program_info:
                student_info['degree_program'] = program_info['title']
                student_info['degree_id'] = program_info['id']

            student_info['menu'] = await reverse_engineer_dropdown_menu(conn, program_id)

        # Note: first_term will also be selected on the Schedule page
        student_info.setdefault('first_term', default_first_term)

        default = initialize_student_info()
        result = update_dict(default, student_info)        
        return result
    
    except Exception as e:
        # Log the error or handle it as appropriate for your application
        print(f"Error populating student info: {str(e)}")
        raise

async def populate_student_data_dict(conn: TimedSQLiteConnection, student_info: dict) -> dict:
    """
    Populate the student_data dictionary with user ID, required courses, and schedule.

    Args:
        conn: Asynchronous database connection object
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
        'periods': None,
        'schedule': None
    }

    program_id = student_info.get('program_id')
    app_stage_id = student_info.get('app_stage_id')

    async def _get_required_courses():
        if program_id is not None:
            return await get_required_program_courses(conn, program_id)
        else:
            return None

    async def _get_schedule():
        if app_stage_id == 5:
            return await get_student_progress_d3(conn, student_data['user_id'])
        else:
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

async def populate_student_info_data(q: Q, user_id: int) -> None:
    """
    Populate q.client.student_info and q.client.student_data dictionaries with student information.

    This function retrieves student information from the database and populates the relevant
    dictionaries in the q object. It's called by `app.initialize_user` and `app.select_sample_user`.

    Args:
        q: The q object containing application and user data
        user_id: The ID of the user to retrieve information for (also stored in q)

    Note:
        timed_connection and user_id are included as parameters for clarity, despite being stored in q.

    Raises:
        Exception: If there's an error during the data retrieval or population process
    """
    try:
        conn = q.client.conn

        student_info = await populate_student_info_dict(conn, user_id)
        student_data = await populate_student_data_dict(conn, student_info)

        q.client.student_info = student_info
        q.client.student_data = student_data

    except Exception as e:
        error_message = f"Error populating student info for user {user_id}: {str(e)}"
        print(error_message)  # For logging purposes
        raise  # Re-raising the exception for now

    q.client.info_populated = True  


#########################################################
####################  GET FUNCTIONS  ####################
#########################################################

async def get_choices(conn: TimedSQLiteConnection, query: str, params: tuple = (), 
                      disabled: Optional[Union[set, list, tuple]] = {""}, 
                      enabled: Optional[Union[set, list, tuple]] = None):
    """
    Return choices for dropdown menus and other UI elements.
    # quick hack: diabled={""} to make this work when both are none (need to fix the entire thing)
    
    Args:
        conn: Asynchronous database connection object
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
        rows = await conn.query(query, params)
        
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

async def get_program_title(conn: TimedSQLiteConnection, program_id: int):
    """
    Retrieve the program title for a given program ID.

    Args:
        conn: Asynchronous database connection object
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
        row = await conn.query_one(query, params=(program_id,))
        return row if row else None
    except Exception as e:
        print(f"Error retrieving program title: {str(e)}")
        return None

async def get_required_program_courses(conn: TimedSQLiteConnection, program_id: int) -> pd.DataFrame:
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
        df = await conn.query_df(query, params=(program_id,))
        return df if not df.empty else None
    except Exception as e:
        print(f"Error retrieving required program courses: {str(e)}")
        return None

async def get_student_progress_d3(conn: TimedSQLiteConnection, user_id: int) -> pd.DataFrame:
    """
    Retrieve student progress data for D3 visualization.

    This function fetches all columns from the student_progress_d3_view
    for a specific user. It's called by `populate_q_student_info`.

    Note: The 'name' column in the old version has been replaced with 'course'.
    Downstream D3 figure implementations may need to be updated accordingly.

    Args:
        conn: Asynchronous database connection object
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
        df = await conn.query_df(query, params=(user_id,))
        return df if not df.empty else None
    except Exception as e:
        print(f"Error retrieving student progress data: {str(e)}")
        return None
