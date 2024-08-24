import sqlite3
import time
from typing import Any, List, Dict, Optional, Callable
import pandas as pd
import asyncio
import warnings
import logging
from contextlib import asynccontextmanager

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

async def get_query_old(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return all rows

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    rows = await timedConnection.fetchall(query, params)
    if not rows:
        warning_message = f"Query returned no row: {query} with params {params}"
        warnings.warn(warning_message, category=Warning)
        logging.warning(warning_message)
        return None
    else:
        return rows

async def get_query_one_old(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a row

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    row = await timedConnection.fetchone(query, params)
    if not row:
        warning_message = f"Query returned no row: {query} with params {params}"
        warnings.warn(warning_message, category=Warning)
        logging.warning(warning_message)
        return None
    else:
        return row

async def get_query_dict_old(timedConnection, query, params=()):
    '''
    This query uses the TimedSQLiteConnection class to return a 
    dictionary of all rows

    timedConnection: a TimeSQLiteConnection instance
    query: SQL query
    params: Optional parameters
    '''
    result = await timedConnection.fetchdict(query, params)
    if not result:
        warning_message = f"Query returned no row: {query} with params {params}"
        warnings.warn(warning_message, category=Warning)
        logging.warning(warning_message)
        return None
    else:
        return result

async def get_query_course_dict_old(timedConnection, query, params=()):
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

async def get_query_df_old(timedConnection, query, params=()):
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
        warning_message = f"Query returned no row: {query} with params {params}"
        warnings.warn(warning_message, category=Warning)
        logging.warning(warning_message)
        return None
    else:
        return df

async def _base_query(timedConnection, query_method: str, query: str, params: tuple = (), **kwargs) -> Optional[Any]:
    """
    Base function to handle queries and error logging.
    
    :param timedConnection: TimedSQLiteConnection instance
    :param query_method: String indicating which query method to use
    :param query: SQL query string
    :param params: Query parameters
    :param kwargs: Additional keyword arguments for specific query methods
    :return: Query result or None if query fails
    """
    try:
        method = getattr(timedConnection, f"fetch{query_method}")
        result = await method(query, params, **kwargs)
        
        if result is None or (isinstance(result, (list, dict)) and not result) or (isinstance(result, pd.DataFrame) and result.empty):
            warning_message = f"Query returned no results: {query} with params {params}"
            warnings.warn(warning_message, category=Warning)
            logging.warning(warning_message)
            return None
        
        return result
    except Exception as e:
        error_message = f"An error occurred during query execution: {e}"
        warnings.warn(error_message, category=Warning)
        logging.error(error_message)
        return None

async def get_query(timedConnection, query: str, params: tuple = ()) -> Optional[List[Any]]:
    """Get all rows from a query."""
    return await _base_query(timedConnection, "all", query, params)

async def get_query_one(timedConnection, query: str, params: tuple = ()) -> Optional[Any]:
    """Get a single row from a query."""
    return await _base_query(timedConnection, "one", query, params)

async def get_query_dict(timedConnection, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
    """Get all rows from a query as a list of dictionaries."""
    return await _base_query(timedConnection, "dict", query, params)

async def get_query_course_dict(timedConnection, query: str, params: tuple = ()) -> Optional[Dict[str, Dict[str, Any]]]:
    """Get all rows from a query as a dictionary indexed by course."""
    result = await get_query_dict(timedConnection, query, params)
    if result is None:
        return None
    
    try:
        return {record['course']: record for record in result}
    except KeyError:
        warnings.warn("'course' is not an element of the dictionary", category=Warning)
        return None

async def get_query_df(timedConnection, query: str, params: tuple = ()) -> Optional[pd.DataFrame]:
    """Get query results as a pandas DataFrame."""
    return await _base_query(timedConnection, "df", query, params)

