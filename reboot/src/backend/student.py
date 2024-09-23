#from contextlib import asynccontextmanager
#from h2o_wave import main, app, Q, ui, on, run_on, data, expando_to_dict
from typing import Any, Dict, Callable, List, Optional, Union
#import numpy as np
#import pandas as pd
#import logging
#import asyncio
#import sys
#import time
#import sqlite3

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
