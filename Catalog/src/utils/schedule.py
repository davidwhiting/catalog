######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################

from typing import Union, List, Dict, Any
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
