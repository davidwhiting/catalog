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

## Would rather replace with @dataclass for cleaner code, but it is not working now.
## After debugging, replace tools.init_old with tools.init
##
## Retaining older version below

from tools.init_old import initialize_student_info, initialize_student_data, initialize_ge, reset_program
__all__ = [
    'initialize_student_info', 
    'initialize_student_data', 
    'initialize_ge', 
    'reset_program'
    ]

######################################################################
####################  SQL-RELATED FUNCTIONS  #########################

# If problems, revert to 'from tools.timedsqlite_old' and debug
from tools.timedsqlite import TimedSQLiteConnection, _base_query, get_query, get_query_one, get_query_dict, get_query_course_dict, get_query_df
to_add = [
    'TimedSQLiteConnection', 
    '_base_query', 
    'get_query', 
    'get_query_one', 
    'get_query_dict', 
    'get_query_course_dict', 
    'get_query_df'
    ]
__all__.extend(to_add)

#########################################################
####################  Get Functions  ####################
#########################################################

from tools.done import get_student_progress_d3, get_catalog_program_sequence, get_required_program_courses, get_choices
to_add = [
    'get_student_progress_d3', 
    'get_catalog_program_sequence', 
    'get_required_program_courses',
    'get_choices'
]
__all__.extend(to_add)
####################
#### DONE BELOW ####
 
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
            student_info['ge'] = await create_ge()

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

        # Update q.user.student_info with the new calculations
        student_info['ge']['total'] = total
        student_info['ge']['summary'] = summary

        return student_info

    except Exception as e:
        error_message = f"Error in summarize_ge: {str(e)}"
        print(error_message)  # For logging purposes
        # You might want to set an error flag or handle the exception in a way that fits your application
        raise  # Re-raise the exception for now

async def create_ge_stub(q):
    """
    Create and initialize the 'ge' dictionary in student_info.
    This function should be implemented to set up the initial structure of 'ge'.
    """
    # TODO: Implement this function
    # For now, return an empty dictionary with the expected structure
    return {
        'total': {},
        'summary': {},
        'arts': {'1': None, '2': None},
        'beh': {'1': None, '2': None},
        'bio': {'1a': None, '1b': None, '1c': None, '2': None},
        'comm': {'1': None, '2': None, '3': None, '4': None},
        'math': {'1': None},
        'res': {'1': None, '2': None, '3': None, '3a': None, '3b': None, '3c': None}
    }
 
#### DONE ABOVE ####
####################

async def populate_summarize_ge(q):
    '''
    Summarize GE to keep our dashboard updated
    '''
    ge = q.user.student_info['ge']
    total = ge['total']
    summary = ge['summary']

    area = 'arts'
    total[area] = 6
    summary[area] = ((ge[area]['1'] is not None) + (ge[area]['2'] is not None)) * 3

    area = 'beh'
    total[area] = 6
    summary[area] = ((ge[area]['1'] is not None) + (ge[area]['2'] is not None)) * 3

    area = 'bio'
    total[area] = 7
    summary[area] = (
        (ge[area]['1a'] is not None) or 
        (ge[area]['1b'] is not None) or 
        (ge[area]['1c'] is not None)
        ) * 4 + (ge[area]['2'] is not None) * 3

    area = 'comm'
    total[area] = 12
    summary[area] = (
        (ge[area]['1'] is not None) + 
        (ge[area]['2'] is not None) + 
        (ge[area]['3'] is not None) + 
        (ge[area]['4'] is not None)
        ) * 3

    area = 'math'
    total[area] = 3
    summary[area] = (ge[area]['1'] is not None) * 3

    area = 'res'
    total[area] = 7
    summary[area] = (
        (ge[area]['1'] is not None) * 3 + 
        (ge[area]['2'] is not None) * 1 +
        (3 if (ge[area]['3'] is not None) else (
            (ge[area]['3a'] is not None) + 
            (ge[area]['3b'] is not None) + 
            (ge[area]['3c'] is not None))
        ))
    
    # not sure if this reassignment is needed
    q.user.student_info['ge']['total'] = total
    q.user.student_info['ge']['summary'] = summary


async def populate_summarize_ge_old(q):
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

############################################################
####################  Populate Functions  ##################
############################################################

from tools.populate import reverse_engineer_dropdown_menu, populate_student_info_dict, populate_student_data_dict, populate_q_student_info TimedSQLiteConnection, _base_query, get_query, get_query_one, get_query_dict, get_query_course_dict, get_query_df
to_add = [ 
    'reverse_engineer_dropdown_menu', 
    'populate_student_info_dict', 
    'populate_student_data_dict', 
    'populate_q_student_info' 
]
__all__.extend(to_add)

#######################################################
#######  Set Functions (for setting variables)  #######
#######################################################

####################
#### DONE BELOW ####



#### DONE ABOVE ####
####################

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

####################
#### DONE BELOW ####

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

#### DONE ABOVE ####
####################

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

######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################

from tools.schedule import ScheduleEntry, generate_periods, update_periods

# debug tools.d3, not working yet, staying with tools.d3_old
from tools.d3_old import create_html_template, prepare_d3_data

to_add = ['ScheduleEntry', 
          'generate_periods', 
          'update_periods', 
          'create_html_template', 
          'prepare_d3_data'
          ]
__all__.extend(to_add)

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

########################################################################
#################  COURSE PREREQUISITE FUNCTIONS  ######################
########################################################################

from tools.prereq_old import update_prerequisites, parse_prerequisites, handle_prerequisites, insert_prerequisite
