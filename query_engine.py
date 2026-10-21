
"""
VerityDB AI — Secure Query Engine

Validates and executes read-only SQL queries
against the local SQLite database.
"""

import sqlite3
import time
from pathlib import Path

# Find the database in the same folder as this Python file.
DATABASE_PATH = Path(__file__).resolve().parent / "verity.db"

# Only these two tables can be accessed by AI-generated SQL.
ALLOWED_TABLES = {"applications", "departments"}


def run_query(sql):
    # Make sure the AI provided a SQL query.
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("The SQL query cannot be empty.")

    sql = sql.strip()

    # Reject anything that doesn't start with SELECT or WITH.
    # WITH allows queries that use common table expressions.
    if sql.split(maxsplit=1)[0].upper() not in {"SELECT", "WITH"}:
        raise ValueError("Only SELECT queries are allowed.")

    # Make sure the database already exists.
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError("VerityDB database was not found.")

    # Open the existing database in read-only mode.
    connection = sqlite3.connect(
        DATABASE_PATH.as_uri() + "?mode=ro",
        uri=True
    )

    try:
        # Add another layer of protection against changes.
        connection.execute("PRAGMA query_only = ON")

        # SQLite checks each operation before executing it.
        def authorize(action, arg1, arg2, db_name, source):
            if action == sqlite3.SQLITE_READ:
                if arg1 not in ALLOWED_TABLES:
                    return sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK

            if action in {
                sqlite3.SQLITE_SELECT,
                sqlite3.SQLITE_FUNCTION,
            }:
                return sqlite3.SQLITE_OK

            return sqlite3.SQLITE_DENY

        connection.set_authorizer(authorize)

        # Stop queries that consume too much processing time.
        deadline = time.monotonic() + 5

        def check_timeout():
            return 1 if time.monotonic() > deadline else 0

        connection.set_progress_handler(check_timeout, 1000)

        # Execute the query.
        cursor = connection.execute(sql)

        # Retrieve column names and up to 100 records.
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchmany(101)

        if len(rows) > 100:
            raise ValueError("Query returned more than 100 rows.")

        return columns, rows

    except sqlite3.Error as error:
        raise ValueError(f"Query rejected: {error}") from error

    finally:
        connection.close()
