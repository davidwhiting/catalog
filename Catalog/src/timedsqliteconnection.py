import sqlite3
import time
from typing import Any, List, Dict, Optional
import pandas as pd

class TimedSQLiteConnection:
    def __init__(self, db_path: str, row_factory: bool = True, timeout: int = 1800):
        self.db_path = db_path
        self.timeout = timeout
        self.row_factory = row_factory
        self.last_activity_time = time.time()
        self.connection: Optional[sqlite3.Connection] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _check_and_close(self):
        if self.connection is not None:
            current_time = time.time()
            if current_time - self.last_activity_time >= self.timeout:
                await self.close()

    async def _update_activity_time(self):
        self.last_activity_time = time.time()

    async def _get_cursor(self):
        await self._check_and_close()
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            if self.row_factory:
                self.connection.row_factory = sqlite3.Row
        return self.connection.cursor()

    async def _execute_query(self, query: str, params: tuple = (), fetch_method: str = None):
        try:
            cursor = await self._get_cursor()
            cursor.execute(query, params)
            await self._update_activity_time()

            if fetch_method == 'one':
                result = cursor.fetchone()
                return result if result else None
            elif fetch_method == 'all':
                result = cursor.fetchall()
                return result if result else None
            elif fetch_method == 'dict':
                column_names = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(column_names, row)) for row in rows]
                return result if result else None
            elif fetch_method == 'df':
                df = pd.read_sql_query(query, self.connection, params=params)
                return df if not df.empty else None
            else:
                self.connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    async def execute(self, query: str, params: tuple = ()):
        """Execute a query without returning results."""
        await self._execute_query(query, params)

    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Any]:
        """Execute a query and fetch one result."""
        return await self._execute_query(query, params, fetch_method='one')

    async def fetchall(self, query: str, params: tuple = ()) -> Optional[List[Any]]:
        """Execute a query and fetch all results."""
        return await self._execute_query(query, params, fetch_method='all')

    async def fetchdict(self, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
        """Execute a query and fetch results as a list of dictionaries."""
        return await self._execute_query(query, params, fetch_method='dict')

    async def fetchdf(self, query: str, params: tuple = ()) -> Optional[pd.DataFrame]:
        """Execute a query and fetch results as a pandas DataFrame."""
        return await self._execute_query(query, params, fetch_method='df')

    async def close(self):
        """Close the database connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None

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
