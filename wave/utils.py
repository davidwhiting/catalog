from h2o_wave import Q, ui
from typing import Optional, List

import logging
import warnings
import sqlite3
import asyncio
import time
import pandas as pd
import numpy as np

#import sys
#import traceback
#from h2o_wave import Q, ui, graphics as g
#import templates

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
    # 'required' used to be 'q.client.program_df'
    # 
    student_info['df'] = {
        'required': None,
        'periods': None,
        'schedule': None
    }
    
    return student_info


############################################################
####################  Populate Functions  ##################
############################################################

async def populate_student_info(q, user_id):
    '''
    Get information from student_info table and populate the q.user.student_info parameters
    '''
    timedConnection = q.user.conn
    attributes = ['resident_status', 'app_stage_id', 'app_stage', 'student_profile', 'financial_aid', 
        'transfer_credits', 'program_id']
    query = 'SELECT * FROM student_info_view WHERE user_id = ?'
    row = await get_query_one(timedConnection, query, params=(user_id,))
    if row:
        q.user.student_info.update({name: row[name] for name in attributes})
        if q.user.student_info['program_id'] is not None:
            row = await get_program_title(timedConnection, q.user.student_info['program_id'])
            if row:
                q.user.student_info['degree_program'] = row['title']
                q.user.student_info['degree_id'] = row['id']
    
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
# these functions return 

async def get_role(q):
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
        SELECT b.id, b.name || ' in ' || a.name as title
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

async def get_query(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return all rows

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    rows = await timedConnection.fetchall(query, params)
    if not rows:
        warnings.warn("Query returned no rows", category=Warning)
        return None
    else:
        return rows

async def get_query_one(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a row

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    row = await timedConnection.fetchone(query, params)
    if not row:
        warnings.warn("Query returned no row", category=Warning)
        return None
    else:
        return row

async def get_query_dict(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a 
    dictionary of all rows

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    result = await timedConnection.fetchdict(query, params)
    if not result:
        warnings.warn("Query did not return a dictionary", category=Warning)
        return None
    else:
        return result

async def get_query_course_dict(timedConnection, query, params=()):
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

async def get_query_df(timedConnection, query, params=()):
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
        warnings.warn("Query returned zero rows", category=Warning)
        return None
    else:
        return df

######################################################################
#####################  QUERIES & FUNCTIONS  ##########################
######################################################################

######################################################################
#################  EVENT AND HANDLER FUNCTIONS  ######################
######################################################################

######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################
