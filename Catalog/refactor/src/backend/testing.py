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
