############################################################
####################  Populate Functions  ##################
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
        student_info = await populate_student_info_dict(timed_connection, user_id, q.app.default_first_term)
        student_data = await populate_student_data_dict(timed_connection, student_info)

        q.user.student_info = student_info
        q.user.student_data = student_data

    except Exception as e:
        error_message = f"Error populating student info for user {user_id}: {str(e)}"
        print(error_message)  # For logging purposes
        raise  # Re-raising the exception for now

    q.user.info_populated = True  
