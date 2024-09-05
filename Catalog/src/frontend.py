
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


######################################################################
####################  STANDARD WAVE CARDS  ###########################
######################################################################

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name: str, card) -> None:
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

#######################################################
####################  Q FUNCTIONS  ####################
#######################################################


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
