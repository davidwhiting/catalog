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

#import sys
#import traceback
###########################################################################
###########################################################################

################################################################
####################  INITIALIZE FUNCTIONS  ####################
################################################################

def initialize_ge():
    """
    Initialize General Education tracking for undergraduate students.
    """
    return {
        'arts': {'1': None, '2': None, 'nopre': False},
        'beh': {'1': None, '2': None, 'nopre': False},
        'bio': {'1a': None, '1b': None, '1c': None, '2': None, 'nopre': False},
        'comm': {'1': 'WRTG 111', '2': 'WRTG 112', '3': None, '4': None, 'nopre': False},
        'math': {'1': None, 'nopre': False},
        'res': {'1': None, '2': 'LIBS 150', '3': None, '3a': None, '3b': None, '3c': None, 'nopre': False}
    }

def initialize_student_info():
    """
    Initialize new student information within Wave.
    (This is not the same as populating a student from the database)
    """
    result = {
        'user_id': None,
        'name': None,
        'financial_aid': None,
        'resident_status': None,
        'student_profile': None,
        'transfer_credits': None,
        'app_stage': None,
        'app_stage_id': None,
        'first_term': None,
        'program_id': None,
        'degree_id': None,
        'degree_program': None,
        'menu': {'degree': None, 'area_of_study': None, 'program': None},
        'ge': {
            'arts': {'1': None, '2': None, 'nopre': False},
            'beh': {'1': None, '2': None, 'nopre': False},
            'bio': {'1a': None, '1b': None, '1c': None, '2': None, 'nopre': False},
            'comm': {'1': 'WRTG 111', '2': 'WRTG 112', '3': None, '4': None, 'nopre': False},
            'math': {'1': None, 'nopre': False},
            'res': {'1': None, '2': 'LIBS 150', '3': None, '3a': None, '3b': None, '3c': None, 'nopre': False},
            'total': {},
            'summary': {}
        }
    }
    return result

def initialize_student_data():
    """
    Initialize new student data
    (This is not the same as populating from the database)
    """
    return {
        'user_id': None,
        'periods': {},
        'required': {},
        'schedule': {}
    }

def reset_program(q: Q) -> None:
    """
    When program is changed, multiple variables need to be reset
    """
    q.user.student_info['menu']['program'] = None
    q.user.student_info['program_id'] = None
    q.user.student_info['degree_program'] = None

    q.user.student_data['required'] = None
    q.user.student_data['schedule'] = None

    q.page['dropdown'].menu_program.value = None
    q.page['dropdown'].menu_program.choices = None


async def reset_student_info_data(q):
    '''
    All the steps needed to initialize q.user.student_info and q.user.student_data
    and set multiple q.user parameters

    Will be called at startup in initialize_user and when switching to a new student 
    for admin and coaches
    '''
    q.user.student_info = initialize_student_info()
    q.user.student_info_populated = False # may be needed later 
    q.user.student_data = initialize_student_data() # will have required, periods, schedule

#########################################################
####################  GET FUNCTIONS  ####################
#########################################################

async def get_catalog_program_sequence(timed_connection, program_id):
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

async def get_choices(timed_connection, query, params=(), disabled=None, enabled=None):
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

async def get_program_title(timed_connection, program_id):
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

async def get_required_program_courses(timed_connection, program_id):
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

async def get_student_progress_d3(timed_connection, user_id):
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

async def get_choices_disable_all(timed_connection, query, params=()):
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

############################################################
####################  POPULATE FUNCTIONS  ##################
############################################################

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

async def populate_student_info_dict(timed_connection, user_id, default_first_term='Spring 2024'):
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

async def populate_student_data_dict(timed_connection, student_info):
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

async def populate_q_student_info(q, timed_connection, user_id):
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

######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################

# Module-level constants
DEFAULT_TERMS = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
# Sessions are UMGC-specific
DEFAULT_SESSIONS_PER_TERM = {'WINTER': 3, 'SPRING': 3, 'SUMMER': 2, 'FALL': 3}

def generate_periods(
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

def update_periods(
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

###############################################################
#####################  GE FUNCTIONS  ##########################
###############################################################

async def summarize_ge(student_info):
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

async def update_ge_ids(data):
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

#######################################################
#################  D3 FUNCTIONS  ######################
#######################################################

# debug tools.d3, not working yet, staying with tools.d3_old
#from tools.d3_old import create_html_template, prepare_d3_data
from tools.d3 import create_html_template, prepare_d3_data

__all__ = [
    'create_html_template', 
    'prepare_d3_data'
]

########################################################################
#################  COURSE PREREQUISITE FUNCTIONS  ######################
########################################################################

async def update_prerequisites(timed_connection, prereq_name):
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

async def handle_prerequisites(timed_connection, course_df):
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
      - fetchone and fetchall use corresponding sqlite3 methods
      - fetchdict returns query results as a dictionary
      - fetchdf returns a Pandas DataFrame

    '''
    def __init__(self, db_path: str, row_factory: bool = True, timeout: int = 1800):
        self.db_path = db_path
        self.timeout = timeout
        self.row_factory = row_factory
        self.last_activity_time = time.time()
        self.connection: Optional[sqlite3.Connection] = None
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def _connection(self):
        async with self._lock:
            await self._check_and_close()
            if self.connection is None:
                self.connection = sqlite3.connect(self.db_path)
                if self.row_factory:
                    self.connection.row_factory = sqlite3.Row
            try:
                yield self.connection
                await self._update_activity_time()
            finally:
                if self.connection:
                    self.connection.commit()

    async def _check_and_close(self):
        if self.connection is not None:
            current_time = time.time()
            if current_time - self.last_activity_time >= self.timeout:
                await self.close()

    async def _update_activity_time(self):
        self.last_activity_time = time.time()

    async def _execute_query(self, query: str, params: tuple = (), fetch_method: Optional[Callable] = None):
        async with self._connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch_method:
                    result = fetch_method(cursor)
                    return result if result else None
            except sqlite3.Error as e:
                logging.error(f"SQLite error occurred: {e}")
                raise

    async def execute(self, query: str, params: tuple = ()):
        """Execute a query without returning results."""
        await self._execute_query(query, params)

    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Any]:
        """Execute a query and fetch one result."""
        return await self._execute_query(query, params, lambda cursor: cursor.fetchone())

    async def fetchall(self, query: str, params: tuple = ()) -> Optional[List[Any]]:
        """Execute a query and fetch all results."""
        return await self._execute_query(query, params, lambda cursor: cursor.fetchall())

    async def fetchdict(self, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
        """Execute a query and fetch results as a list of dictionaries."""
        def fetch_dict(cursor):
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return await self._execute_query(query, params, fetch_dict)

    async def fetchdf(self, query: str, params: tuple = ()) -> Optional[pd.DataFrame]:
        """Execute a query and fetch results as a pandas DataFrame."""
        async with self._connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df if not df.empty else None

    async def close(self):
        """Close the database connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None

async def _base_query(timed_connection: TimedSQLiteConnection, query_method: str, query: str, params: tuple = (), **kwargs) -> Optional[Any]:
    """
    Base function to handle queries and error logging.
    
    :param timed_connection: TimedSQLiteConnection instance
    :param query_method: String indicating which query method to use
    :param query: SQL query string
    :param params: Query parameters
    :param kwargs: Additional keyword arguments for specific query methods
    :return: Query result or None if query fails
    """
    try:
        method = getattr(timed_connection, f"fetch{query_method}")
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

async def get_query(timed_connection: TimedSQLiteConnection, query: str, params: tuple = ()) -> Optional[List[Any]]:
    """Get all rows from a query."""
    return await _base_query(timed_connection, "all", query, params)

async def get_query_one(timed_connection: TimedSQLiteConnection, query: str, params: tuple = ()) -> Optional[Any]:
    """Get a single row from a query."""
    return await _base_query(timed_connection, "one", query, params)

async def get_query_dict(timed_connection: TimedSQLiteConnection, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
    """Get all rows from a query as a list of dictionaries."""
    return await _base_query(timed_connection, "dict", query, params)

async def get_query_course_dict(timed_connection: TimedSQLiteConnection, query: str, params: tuple = ()) -> Optional[Dict[str, Dict[str, Any]]]:
    """Get all rows from a query as a dictionary indexed by course."""
    result = await get_query_dict(timed_connection, query, params)
    if result is None:
        return None
    try:
        return {record['course']: record for record in result}
    except KeyError:
        warnings.warn("'course' is not an element of the dictionary", category=Warning)
        return None

async def get_query_df(timed_connection: TimedSQLiteConnection, query: str, params: tuple = ()) -> Optional[pd.DataFrame]:
    """Get query results as a pandas DataFrame."""
    return await _base_query(timed_connection, "df", query, params)

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

####################################################################
#################  COURSE LIST BUILDING FUNCTIONS  ################# 
####################################################################

async def build_program_course_list(program_df, timed_connection, ge_course_list):
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
async def get_required_program_courses_no_q(timed_connection, student_info):
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

async def return_program_course_list_df_from_scratch(timed_connection, student_info):
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

async def generate_schedule(timed_connection, course_df, periods_df):
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

    to do: course in the schedule df is called 'name' (changing this now)
           course is called course in the required df
           should simplify by changing schedule df to course AFTER
           updating d3 javascript code, since it's expecting name
    '''
    if which in ['required', 'schedule']:
        #df = q.user.student_data[which]
        if which == 'schedule':
            df = q.user.student_data['schedule']
            description = df.loc[df['course'] == course, 'description'].iloc[0]
   
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

async def set_user_vars_given_role(q):
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

