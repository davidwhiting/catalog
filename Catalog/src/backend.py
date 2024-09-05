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
