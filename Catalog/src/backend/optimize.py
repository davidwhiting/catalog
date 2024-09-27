
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


async def populate_summarize_ge(q):
    '''
    Summarize GE to keep our dashboard updated
    '''
    ge = q.client.student_info['ge']

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

async def return_program_course_list_df_from_scratch(timedConnection, student_info):
    '''
    Function should be updated to work within wave (w/ q, etc.)
    Note: (timedConnection, student_info) are both accessible w/in q, would be better to pass
          program_id for clarity 
    '''
    # Build the Program course list

    # Task 1. Get the required classes from the program
    required_df = await get_required_program_courses(timedConnection, student_info)

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

