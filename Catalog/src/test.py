from backend import test_functions, initialize_student_info_ZZ, initialize_ge, initialize_student_info, initialize_student_data

test_functions(initialize_student_info_ZZ, initialize_student_info)

def compare(dict1, dict2, key):
    if dict1[key] is not dict2[key]:
        print(f"'{key}' is different: {dict1[key]} is not {dict2[key]}")
    else:
        print(f"'{key}' is the same")

def compare_dictionaries(dict1, dict2):
    def recursive_compare(d1, d2, path=""):
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
                recursive_compare(d1[key], d2[key], new_path)
            else:
                compare(d1, d2, key)

    recursive_compare(dict1, dict2)

## Example usage:
#dict1 = {
#    'a': 1,
#    'b': {
#        'c': 2,
#        'd': {
#            'e': 3
#        }
#    },
#    'f': 4
#}
#
#dict2 = {
#    'a': 1,
#    'b': {
#        'c': 2,
#        'd': {
#            'e': 5
#        }
#    },
#    'g': 6
#}
#
#compare_dictionaries(dict1, dict2)

f1 = initialize_student_info_ZZ()
f2 = initialize_student_info()

print(f1 == f2)

f1 = {
    'user_id': None, 
    'name': None, 
    'financial_aid': None, 
    'resident_status': None, 
    'student_profile': None, 
    'transfer_credits': None, 
    'app_stage': None, 
    'app_stage_id': None, 
    'first_term': None, 
    'program_id': None, 
    'degree_id': None, 
    'degree_program': None, 
    'menu': {'degree': None, 
             'area_of_study': None, 
             'program': None
    }, 
    'ge': {
        'arts': {'1': None, '2': None, 'nopre': False}, 
        'beh': {'1': None, '2': None, 'nopre': False}, 
        'bio': {'1a': None, '1b': None, '1c': None, '2': None, 'nopre': False}, 
        'comm': {'1': 'WRTG 111', '2': 'WRTG 112', '3': None, '4': None, 'nopre': False}, 
        'math': {'1': None, 'nopre': False}, 
        'res': {'1': None, '2': 'LIBS 150', '3': None, '3a': None, '3b': None, '3c': None, 'nopre': False}, 
        'total': {}, 
        'summary': {}
    }
}

f2 = {
    'user_id': None, 
    'name': None, 
    'financial_aid': None, 
    'resident_status': None, 
    'student_profile': None, 
    'transfer_credits': None, 
    'app_stage': None, 
    'app_stage_id': None, 
    'first_term': None, 
    'program_id': None, 
    'degree_program': None, 
    'menu': {'degree': None, 
             'area_of_study': None, 
             'program': None
    }, 
    'ge': {
        'arts': {'1': None, '2': None, 'nopre': False}, 
        'beh': {'1': None, '2': None, 'nopre': False}, 
        'bio': {'1a': None, '1b': None, '1c': None, '2': None, 'nopre': False}, 
        'comm': {'1': 'WRTG 111', '2': 'WRTG 112', '3': None, '4': None, 'nopre': False}, 
        'math': {'1': None, 'nopre': False}, 
        'res': {'1': None, '2': 'LIBS 150', '3': None, '3a': None, '3b': None, '3c': None, 'nopre': False}, 
        'total': {}, 'summary': {}
    }
}




compare(f1, f2, 'user_id')
compare(f1, f2, 'name')
compare(f1, f2, 'financial_aid')
compare(f1, f2, 'resident_status')
compare(f1, f2, 'student_profile')
compare(f1, f2, 'transfer_credits')
compare(f1, f2, 'app_stage')
compare(f1, f2, 'app_stage_id')
compare(f1, f2, 'first_term')
compare(f1, f2, 'program_id')
compare(f1, f2, 'degree_program')
compare(f1, f2, 'menu')
compare(f1, f2, 'ge')

    'user_id': None, 
    'name': None, 
    'financial_aid': None, 
    'resident_status': None, 
    'student_profile': None, 
    'transfer_credits': None, 
    'app_stage': None, 
    'app_stage_id': None, 
    'first_term': None, 
    'program_id': None, 
    'degree_program': None, 