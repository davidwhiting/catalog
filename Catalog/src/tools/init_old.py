from typing import Dict, Any
from h2o_wave import Q


def initialize_student_info():
    '''
    Initialize new student information within Wave.
    (This is not the same as populating a student from the database)
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

    return student_info

def initialize_student_data():
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
    student_data.update({name: None for name in attributes})    
    return student_data

def initialize_ge():
    '''
    Initialize General Education tracking for undergraduate students.
    '''
    ge = {
        'arts': {
            '1': None,
            '2': None,
            'nopre': False
        },
        'beh': {
            '1': None,
            '2': None,
            'nopre': False
        },
        'bio': {
            '1a': None,
            '1b': None,
            '1c': None,
            '2': None,
            'nopre': False
        },
        'comm': {
            '1': 'WRTG 111',
            '2': 'WRTG 112',
            '3': None,
            '4': None,
            'nopre': False
        },
        'math': {
            '1': None,
            'nopre': False
        },
        'res': {
            '1': None,
            '2': 'LIBS 150',
            '3': None,
            '3a': None,
            '3b': None,
            '3c': None,
            'nopre': False
        }
    }
    return ge

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
