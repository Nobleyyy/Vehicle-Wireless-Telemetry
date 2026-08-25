### Database Page Python ###

# Package Imports
from pathlib import Path
import sqlite3
import time
import csv
from io import StringIO

DATABASE_FILE = (
    Path(__file__).resolve().parents[3]
    / "Data_Archive"
    / "car_data.db"
)

## Functions ##
def get_db():
    # Open a connection to the SQLite database
    conn = sqlite3.connect(DATABASE_FILE)
    # Return query results as dictionary-like rows
    conn.row_factory = sqlite3.Row
    return conn


def get_table_names() -> list:
    # Open a database connection
    conn = get_db()
    # Retrieve all user-created tables
    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()
    conn.close()
    # Return the table names as a list
    return [table["name"] for table in tables]

def get_table_data(table_name:str) -> dict:
    # Make sure the table exists before using it
    if table_name not in get_table_names():
        return None

    # Retrieve all records from the requested table
    conn = get_db()
    rows = conn.execute(
        f'SELECT * FROM "{table_name}"'
    ).fetchall()
    conn.close()
    # Get the column names from the first row
    columns = list(rows[0].keys()) if rows else []
    formatted_rows = []

    for row in rows:
        record = dict(row)
         # Convert Unix timestamps into a human-readable date and time
        if record.get("timestamp"):
            try:
                record["timestamp"] = time.strftime(
                    "%d/%m/%y %H:%M:%S",
                    time.localtime(float(record["timestamp"]))
                )
            except (ValueError, TypeError, OverflowError):
                pass
        # Store the row values in the same order as the column names
        formatted_rows.append([
            record[column]
            for column in columns
        ])
     # Return the table name, column names, and formatted rows
    return {
        "table": table_name,
        "columns": columns,
        "rows": formatted_rows
    }

def get_table_csv(table_name:str):
    # Retrieve table data in a format suitable for CSV output
    data = get_table_data(table_name)
    # Table does not exist
    if data is None:
        return None

    output = StringIO()
    writer = csv.writer(output)
    # Write the column names followed by the table data
    writer.writerow(data["columns"])
    writer.writerows(data["rows"])
    return output.getvalue()