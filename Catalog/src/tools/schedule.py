######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################

from typing import Union, List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd

# Module-level constants
DEFAULT_TERMS = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
# Sessions are UMGC-specific
DEFAULT_SESSIONS_PER_TERM = {'WINTER': 3, 'SPRING': 3, 'SUMMER': 2, 'FALL': 3}

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
        as_df: bool = True,
        terms: Optional[List[str]] = None,
        sessions_per_term: Optional[Dict[str, int]] = None
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Generate a periods structure containing information about terms and sessions.

    A periods structure is a list of dictionaries (or a Pandas dataframe) containing information about terms and sessions,
    into which we will place classes when scheduling.

    Parameters:
    - start_term (str): First term classes are to be scheduled into.
    - years (int): Number of years to create periods for (this can be larger than needed).
    - max_courses (int): Maximum number of courses per session.
    - max_credits (int): Maximum number of credits per term.
    - summer (bool): Whether attending summer (as default).
    - sessions (List[int]): Which sessions (1-3) to schedule classes in (excluding summer term, which has only sessions 1 & 2).
    - as_df (bool): Return results as Pandas dataframe, otherwise return as list of dictionaries.
    - terms (Optional[List[str]]): Custom list of terms to use instead of the default.
    - sessions_per_term (Optional[Dict[str, int]]): Custom dictionary of sessions per term to use instead of the default.

    Returns:
    Union[pd.DataFrame, List[Dict[str, Any]]]: Periods structure as specified by as_df parameter.

    Raises:
    ValueError: If input parameters are invalid.

    Note:
    We create all terms a student could potentially attend and set max_courses=0 and max_credits=0 for periods they
    are not attending.
    """
    # Input validation
    if years <= 0:
        raise ValueError('Years must be a positive integer.')
    if max_courses < 0 or max_credits < 0:
        raise ValueError('Max courses and max credits must be non-negative.')
    if not all(1 <= s <= 3 for s in sessions):
        raise ValueError('Sessions must be between 1 and 3.')

    TERMS = terms or DEFAULT_TERMS
    SESSIONS_PER_TERM = sessions_per_term or DEFAULT_SESSIONS_PER_TERM

    try:
        start_term, start_year = start_term.upper().split()
        start_year = int(start_year)
    except ValueError:
        raise ValueError('Invalid start_term format. Expected "TERM YEAR", e.g., "SPRING 2024".')

    if start_term not in TERMS:
        raise ValueError(f'Invalid start term. Must be one of {TERMS}.')

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
    - periods (Union[pd.DataFrame, List[Dict[str, Any]]]): A DataFrame or list of dictionaries with periods information.
    - condition (str): A string condition to be evaluated.
    - update_values (Dict[str, Any]): A dictionary of column names and values to update.

    Returns:
    Union[pd.DataFrame, List[Dict[str, Any]]]: Updated periods structure in the same format as the input.

    Raises:
    ValueError: If the condition is invalid or if specified columns don't exist.

    Example:
    # Update max_courses for SPRING 2024 to 0
    update_periods(periods, "term == 'SPRING' and year == 2024", {"max_courses": 0})
    """
    is_dataframe = isinstance(periods, pd.DataFrame)
    
    if not is_dataframe:
        periods = pd.DataFrame(periods)
    
    try:
        mask = periods.eval(condition)
        
        for key, value in update_values.items():
            if key not in periods.columns:
                raise ValueError(f"Column '{key}' not found in periods.")
            periods.loc[mask, key] = value
    
    except pd.errors.UndefinedVariableError as e:
        raise ValueError(f"Invalid condition: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error updating periods: {str(e)}")
    
    return periods if is_dataframe else periods.to_dict(orient='records')
