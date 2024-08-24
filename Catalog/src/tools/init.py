from typing import Dict, Any
from dataclasses import dataclass, field, asdict
from h2o_wave import Q

## Create a dataclass where we can access via dictionary-like or attribute-like syntax

@dataclass
class DictLikeDataclass:
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

@dataclass
class StudentInfo(DictLikeDataclass):
    user_id: str = None
    name: str = None
    financial_aid: bool = None
    resident_status: str = None
    student_profile: Dict[str, Any] = field(default_factory=dict)
    transfer_credits: int = None
    app_stage: str = None
    app_stage_id: int = None
    first_term: str = None
    program_id: int = None
    degree_program: str = None
    menu: Dict[str, str] = field(default_factory=lambda: {
        'degree': None,
        'area_of_study': None,
        'program': None
    })

@dataclass
class StudentData(DictLikeDataclass):
    user_id: str = None
    required: Dict[str, Any] = field(default_factory=dict)
    periods: Dict[str, Any] = field(default_factory=dict)
    schedule: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeneralEducation(DictLikeDataclass):
    arts: Dict[str, Any] = field(default_factory=lambda: {'1': None, '2': None, 'nopre': False})
    beh: Dict[str, Any] = field(default_factory=lambda: {'1': None, '2': None, 'nopre': False})
    bio: Dict[str, Any] = field(default_factory=lambda: {'1a': None, '1b': None, '1c': None, '2': None, 'nopre': False})
    comm: Dict[str, Any] = field(default_factory=lambda: {'1': 'WRTG 111', '2': 'WRTG 112', '3': None, '4': None, 'nopre': False})
    math: Dict[str, Any] = field(default_factory=lambda: {'1': None, 'nopre': False})
    res: Dict[str, Any] = field(default_factory=lambda: {'1': None, '2': 'LIBS 150', '3': None, '3a': None, '3b': None, '3c': None, 'nopre': False})

def initialize_student_info() -> StudentInfo:
    """
    Initialize new student information within Wave.
    (This is not the same as populating a student from the database)
    """
    return StudentInfo()

def initialize_student_data() -> StudentData:
    """
    Initialize new student data
    (This is not the same as populating from the database)
    """
    return StudentData()

def initialize_ge() -> GeneralEducation:
    """
    Initialize General Education tracking for undergraduate students.
    """
    return GeneralEducation()

def reset_program(q: Q) -> None:
    """
    When program is changed, multiple variables need to be reset
    
    :param q: The h2o Wave query context
    """
    q.user.student_info['menu']['program'] = None
    q.user.student_info['program_id'] = None
    q.user.student_info['degree_program'] = None

    q.user.student_data['required'] = None
    q.user.student_data['schedule'] = None

    if hasattr(q.page, 'dropdown'):
        q.page.dropdown.menu_program.value = None
        q.page.dropdown.menu_program.choices = None

## Example usage:
#def example_usage(q: Q):
#    # Initializing
#    q.user.student_info = initialize_student_info()
#    q.user.student_data = initialize_student_data()
#    q.user.ge = initialize_ge()
#
#    # Dictionary-style access (now supported)
#    if int(q.user.student_info['app_stage_id']) == 1:
#        # Do something
#        pass
#
#    # Attribute-style access (still supported)
#    q.user.student_info.name = "John Doe"
#
#    # Dictionary-style updates
#    q.user.student_data['user_id'] = "12345"
#    q.user.ge['math']['1'] = "MATH 101"
#
#    # Accessing nested dictionaries (unchanged)
#    area_of_study = q.user.student_info.menu['area_of_study']
#
#    # Converting to dictionary if needed
#    student_info_dict = asdict(q.user.student_info)