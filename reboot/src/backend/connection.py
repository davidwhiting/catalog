######################################################################
#######################  SQL-RELATED FUNCTIONS #######################
######################################################################

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import logging
import asyncio
import time
import sqlite3
import warnings

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

    '''
    def __init__(self, db_path: str, row_factory: bool = True, timeout: int = 1800):
        self.db_path = db_path
        self.timeout = timeout
        self.row_factory = row_factory
        self.last_activity_time = time.time()
        self.connection: Optional[sqlite3.Connection] = None
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def _connection(self):
        async with self._lock:
            await self._check_and_close()
            if self.connection is None:
                self.connection = sqlite3.connect(self.db_path)
                if self.row_factory:
                    self.connection.row_factory = sqlite3.Row
            try:
                yield self.connection
                await self._update_activity_time()
            finally:
                if self.connection:
                    self.connection.commit()

    async def _check_and_close(self):
        if self.connection is not None:
            current_time = time.time()
            if current_time - self.last_activity_time >= self.timeout:
                await self.close()

    async def _update_activity_time(self):
        self.last_activity_time = time.time()

    async def _base_query(self, query_method: str, query: str, params: tuple = (), **kwargs) -> Optional[Any]:
        """
        Base method to handle queries and error logging.
        
        :param query_method: String indicating which query method to use
        :param query: SQL query string
        :param params: Query parameters
        :param kwargs: Additional keyword arguments for specific query methods
        :return: Query result or None if query fails
        """
        try:
            async with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if query_method == 'one':
                    result = cursor.fetchone()
                elif query_method == 'all':
                    result = cursor.fetchall()
                elif query_method == 'dict':
                    columns = [col[0] for col in cursor.description]
                    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                elif query_method == 'df':
                    df = pd.read_sql_query(query, conn, params=params)
                    result = df if not df.empty else None
                else:
                    raise ValueError(f"Invalid query method: {query_method}")
                
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

    async def execute(self, query: str, params: tuple = ()):
        """Execute a query without returning results."""
        async with self._connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
            except sqlite3.Error as e:
                logging.error(f"SQLite error occurred: {e}")
                raise

    async def query(self, query: str, params: tuple = ()) -> Optional[List[Any]]:
        """Get all rows from a query."""
        return await self._base_query('all', query, params)

    async def query_one(self, query: str, params: tuple = ()) -> Optional[Any]:
        """Get a single row from a query."""
        return await self._base_query('one', query, params)

    async def query_dict(self, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
        """Get all rows from a query as a list of dictionaries."""
        return await self._base_query('dict', query, params)

    async def query_df(self, query: str, params: tuple = ()) -> Optional[pd.DataFrame]:
        """Get query results as a pandas DataFrame."""
        return await self._base_query('df', query, params)

    async def query_course_dict(self, query: str, params: tuple = ()) -> Optional[Dict[str, Dict[str, Any]]]:
        """Get all rows from a query as a dictionary indexed by course."""
        result = await self.query_dict(query, params)
        if result is None:
            return None
        try:
            return {record['course']: record for record in result}
        except KeyError:
            warnings.warn("'course' is not an element of the dictionary", category=Warning)
            return None

    async def _base_write(self, write_method: str, data: Any, table_name: str, column_mapping: Optional[Dict[str, str]] = None, if_exists: str = 'replace', **kwargs):
        """
        Base function to handle write operations and error logging.
        
        :param write_method: String indicating which write method to use ('dataframe' or 'dict')
        :param data: Data to be written (DataFrame or dict/list of dicts)
        :param table_name: Name of the table to write to
        :param column_mapping: Optional mapping of data columns to database fields
        :param if_exists: How to behave if the table already exists ('fail', 'replace', or 'append')
        :param kwargs: Additional keyword arguments for specific write methods
        """
        if if_exists not in ('fail', 'replace', 'append'):
            raise ValueError("if_exists must be one of 'fail', 'replace', or 'append'")

        try:
            if write_method == 'dataframe':
                if column_mapping:
                    data = data.rename(columns=column_mapping)
                async with self._connection() as conn:
                    data.to_sql(table_name, conn, if_exists=if_exists, index=False)
            elif write_method == 'dict':
                if isinstance(data, dict):
                    data = [data]
                if column_mapping:
                    data = [{column_mapping.get(k, k): v for k, v in item.items()} for item in data]
                df = pd.DataFrame(data)
                await self._base_write('dataframe', df, table_name, if_exists=if_exists)
            else:
                raise ValueError(f"Invalid write method: {write_method}")

            await self._update_activity_time()
            logging.info(f"Successfully wrote data to table {table_name}")
        except Exception as e:
            error_message = f"Error writing data to table {table_name}: {e}"
            logging.error(error_message)
            raise

    async def write_dataframe(self, df: pd.DataFrame, table_name: str, column_mapping: Optional[Dict[str, str]] = None, if_exists: str = 'replace'):
        """
        Write a pandas DataFrame to a specified table.

        Args:
            df (pd.DataFrame): The DataFrame to write to the database.
            table_name (str): The name of the table to write to.
            column_mapping (Optional[Dict[str, str]]): A dictionary mapping DataFrame column names to database field names.
            if_exists (str): How to behave if the table already exists. Options are 'fail', 'replace', or 'append'.
        """
        await self._base_write('dataframe', df, table_name, column_mapping, if_exists)

    async def write_dict(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], table_name: str, column_mapping: Optional[Dict[str, str]] = None, if_exists: str = 'append'):
        """
        Write a dictionary or list of dictionaries to a specified table.

        Args:
            data (Union[Dict[str, Any], List[Dict[str, Any]]]): The dictionary or list of dictionaries to write to the database.
            table_name (str): The name of the table to write to.
            column_mapping (Optional[Dict[str, str]]): A dictionary mapping data keys to database field names.
            if_exists (str): How to behave if the table already exists. Options are 'fail', 'replace', or 'append'.
        """
        await self._base_write('dict', data, table_name, column_mapping, if_exists)

    async def insert_or_replace(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame], columns: Optional[List[str]] = None):
        """
        Insert or replace data into the specified table, optionally specifying which columns to use.

        This method constructs and executes an "INSERT OR REPLACE INTO" SQL statement
        based on the provided data. It can handle dictionaries, lists of dictionaries, and pandas DataFrames,
        using executemany for efficient bulk operations.

        Args:
            table_name (str): The name of the table to insert/replace data into.
            data (Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]): The data to insert/replace.
                Can be a single dictionary, a list of dictionaries, or a pandas DataFrame.
            columns (Optional[List[str]]): List of column names to use for the operation.
                If None, all columns from the data will be used.

        Raises:
            ValueError: If the data is empty, not in the correct format, or if specified columns are invalid.
        """
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient='records')

        if not data:
            raise ValueError("Data cannot be empty")

        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError("Data must be a dictionary, a list of dictionaries, or a pandas DataFrame")

        if not all(isinstance(item, dict) for item in data):
            raise ValueError("All items in the list must be dictionaries")

        # If columns are not specified, use all columns from the first dictionary
        if columns is None:
            columns = list(data[0].keys())
        else:
            # Validate that all specified columns exist in the data
            if not all(col in data[0] for col in columns):
                missing_cols = set(columns) - set(data[0].keys())
                raise ValueError(f"Specified columns not found in data: {missing_cols}")

        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)

        query = f"INSERT OR REPLACE INTO {table_name} ({column_names}) VALUES ({placeholders})"

        async with self._connection() as conn:
            try:
                cursor = conn.cursor()
                values = [tuple(item.get(column) for column in columns) for item in data]
                cursor.executemany(query, values)
                await self._update_activity_time()
                logging.info(f"Successfully inserted/replaced {len(data)} row(s) into table {table_name} using columns: {columns}")
            except Exception as e:
                error_message = f"Error inserting/replacing data into table {table_name}: {e}"
                logging.error(error_message)
                raise

    async def close(self):
        """Close the database connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
