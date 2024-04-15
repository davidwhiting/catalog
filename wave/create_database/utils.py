# connect to UMGC database
import sqlite3
conn = sqlite3.connect('UMGC.db')
c = conn.cursor()

# Utilities for interacting with Sqlite3 database

def drop_table(table, db=c):
    db.execute('DROP TABLE IF EXISTS ' + table)

def drop_view(table, db=c):
    db.execute('DROP VIEW IF EXISTS ' + table)

def column_exists(table_name, column_name, db=c):
    # Get the info of all columns of the table
    db.execute(f"PRAGMA table_info({table_name})")
    columns = db.fetchall()

    # Check if the column exists in the table
    for column in columns:
        if column[1] == column_name:
            return True

    return False
