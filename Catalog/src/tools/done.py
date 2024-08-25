#########################################################
####################  Get Functions  ####################
#########################################################


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
