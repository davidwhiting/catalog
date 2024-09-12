from h2o_wave import Q, ui
import asyncio
import logging
import sqlite3
import time
import warnings
import functools

#############################################################
####################  TESTING FUNCTIONS  ####################
#############################################################

def test_functions(func1, func2, *args, **kwargs) -> bool:
    """
    Test if two functions produce the same output given the same input.
    
    :param func1: First function to test
    :param func2: Second function to test
    :param args: Positional arguments to pass to both functions
    :param kwargs: Keyword arguments to pass to both functions
    :return: True if outputs are equal, False otherwise
    """
    result1 = func1(*args, **kwargs)
    result2 = func2(*args, **kwargs)
    
    if result1 == result2:
        print("Functions produce the same output.")
        return True
    else:
        print("Functions produce different outputs.")
        print(f"Output of func1: {result1}")
        print(f"Output of func2: {result2}")
        return False

def compare(dict1, dict2, key) -> None:
    if dict1[key] is not dict2[key]:
        print(f"'{key}' is different: {dict1[key]} is not {dict2[key]}")
    else:
        print(f"'{key}' is the same")

def compare_dictionaries(dict1, dict2) -> None:
    def _recursive_compare(d1, d2, path=""):
        if not isinstance(d1, dict) or not isinstance(d2, dict):
            compare(d1, d2, path)
            return

        all_keys = set(d1.keys()) | set(d2.keys())
        
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            
            if key not in d1:
                print(f"'{new_path}' is missing in the first dictionary")
            elif key not in d2:
                print(f"'{new_path}' is missing in the second dictionary")
            elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
                _recursive_compare(d1[key], d2[key], new_path)
            else:
                compare(d1, d2, key)

    _recursive_compare(dict1, dict2)

# Example usage:
# test_result = test_functions(initialize_ge, initialize_ge_old)

##############################################################
####################  INITIALIZE FUNCTIONS  ##################
##############################################################

def initialize_ge() -> dict:
    """
    Initialize General Education tracking for undergraduate students.
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
