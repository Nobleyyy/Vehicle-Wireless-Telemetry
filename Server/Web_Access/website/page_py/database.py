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
    # Retrieve all user-created tables sorted naturally by length and then name
    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY LENGTH(name), name
    """).fetchall()
    conn.close()
    # Return the table names as a list
    return [table["name"] for table in tables]


def get_table_data(table_name: str, limit=None, offset=0) -> dict:
    # Make sure the table exists before using it
    if table_name not in get_table_names():
        return None

    # Retrieve records from the requested table
    conn = get_db()
    
    # Get total row count for pagination
    total_count_row = conn.execute(f'SELECT COUNT(*) as count FROM "{table_name}"').fetchone()
    total_count = total_count_row["count"] if total_count_row else 0

    query = f'SELECT * FROM "{table_name}"'
    params = []
    
    # Apply limit and offset if specified and limit is not 'all'
    if limit and limit != "all":
        try:
            limit_val = int(limit)
            offset_val = int(offset) if offset is not None and str(offset).strip() != "" else 0
            query += " LIMIT ? OFFSET ?"
            params.extend([limit_val, offset_val])
        except (ValueError, TypeError):
            pass

    rows = conn.execute(query, params).fetchall()
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
     # Return the table name, column names, formatted rows, total row count, and offset
    return {
        "table": table_name,
        "columns": columns,
        "rows": formatted_rows,
        "total_count": total_count,
        "offset": offset
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

def delete_table(table_name: str) -> bool:
    # Only allow session tables to be deleted
    if not table_name.startswith("session_"):
        return False
    # Make sure the table exists
    if table_name not in get_table_names():
        return False
    conn = get_db()
    try:
        conn.execute(
            f'DROP TABLE "{table_name}"'
        )
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        conn.close()