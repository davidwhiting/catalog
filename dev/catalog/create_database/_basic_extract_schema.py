import sqlite3
import re

dbname = 'UMGC.db'
outputfile = '_tmp_dbinfo.txt'
print_schema = False
print_table = True
print_vis = False
print_view = True

# translate_sql doesn't work correctly yet
# for sake of time, will just edit output of print_table

def translate_sql(sql):
    # Extract table name
    table_name = re.search(r'CREATE TABLE (\w+)', sql).group(1)

    # Extract column definitions and foreign key constraints
    columns = re.findall(r'(\w+ \w+)(?:,| PRIMARY KEY|,| FOREIGN KEY|\))', sql)
    foreign_keys = re.findall(r'FOREIGN KEY\((\w+)\) REFERENCES (\w+)\(\w+\)', sql)

    # Initialize result string with table name
    result = f'Table {table_name} {{\n'

    # Add column definitions to result
    for column in columns:
        if 'PRIMARY KEY' in column:
            column = column.replace(' PRIMARY KEY', ' [primary key]')
        result += f'  {column}\n'

    # Add foreign key constraints to result
    for fk in foreign_keys:
        result += f'  {fk[0]} integer [ref: > {fk[1]}.id]\n'

    # Close the table definition
    result += '}'

    return result

#print(translate_sql(sql))

# Connect to your database
conn = sqlite3.connect(dbname)

# Create a cursor object
c = conn.cursor()

# Retrieve all table names
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()

# Retrieve all view names
c.execute("SELECT name FROM sqlite_master WHERE type='view';")
views = c.fetchall()

# Open the output file
with open(outputfile, 'w') as f:
    # Loop over each table name and write its schema to the file
    for table in tables:
        table = table[0]
        if print_schema:
            c.execute(f"PRAGMA table_info({table})")
            schema = c.fetchall()
            f.write(f"Schema for {table}:\n")
            for column in schema:
                f.write(str(column) + '\n')
            f.write('\n\n')

        # Loop over each table name and write its creation SQL to the file
        c.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
        creation_sql = c.fetchone()[0]
        if print_table:
            f.write(f"Creation SQL for {table}:\n")
            f.write(creation_sql + '\n')
            f.write('\n\n')

        vis_code = translate_sql(creation_sql)
        if print_vis:
            f.write(vis_code + '\n')
            f.write('\n\n')

    # Loop over each view name and write its creation SQL to the file
    for view in views:
        view = view[0]
        c.execute(f"SELECT sql FROM sqlite_master WHERE type='view' AND name='{view}';")
        creation_sql = c.fetchone()[0]

        if print_view:
            f.write(f"Creation SQL for {view}:\n")
            f.write(creation_sql + '\n')
            f.write('\n\n')

# Close the connection
conn.close()

