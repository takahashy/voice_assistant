# test with unittest

import os
import pytest
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(".env")

# Fixture to establish a database connection
@pytest.fixture
def db_connection():
    # Connect to the database
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")  # Ensure this matches your .env key
    )
    yield connection
    # Close the connection after the test
    connection.close()

# Fixture to create a cursor for executing queries
@pytest.fixture
def db_cursor(db_connection):
    cursor = db_connection.cursor()
    yield cursor
    # Close the cursor after the test
    cursor.close()

# Test if the database connection is established
def test_db_connection(db_connection):
    assert db_connection.is_connected() == True

# Test if the cursor is created successfully
def test_db_cursor(db_cursor):
    assert db_cursor is not None

# Test if the database contains specific tables
def test_db_contains_tables(db_cursor):
    # Query to list all tables in the database
    db_cursor.execute("SHOW TABLES")
    tables = [table[0] for table in db_cursor.fetchall()]

    # Define the expected tables
    expected_tables = ["users", "conversations"]  # Replace with your actual table names

    # Check if all expected tables exist in the database
    for table in expected_tables:
        assert table in tables, f"Table '{table}' is missing in the database"

# Test a simple query
def test_simple_query(db_cursor):
    db_cursor.execute("SELECT 1")
    result = db_cursor.fetchone()
    assert result[0] == 1

if __name__ == "__main__":
    pytest.main()