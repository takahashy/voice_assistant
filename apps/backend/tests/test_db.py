'''
test_db.py

Unit tests for database connection using pytest and mysql-connector-python.
'''
import os
import pytest
import mysql.connector
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, "../../../.env")

load_dotenv(ENV_PATH)

def getPassword():
    secret_file = os.getenv("DB_PASSWORD_FILE")

    # searches in docker container
    if secret_file and os.path.exists(secret_file):
        with open(secret_file, 'r') as file:
            return file.read().strip()
        
    # if not in container fallback to .env
    else:
        return os.getenv("DB_PASSWORD")



# establish connection to the database. fixture decorator allows usage of 
# the connection when testing. yield closes the connection after tests are done
@pytest.fixture
def db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=getPassword(),
        database=os.getenv("MYSQL_DATABASE")  
    )

    yield connection
    connection.close()


@pytest.fixture
def db_cursor(db_connection):
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()


# Test 1: Check if database connection is established
def test_db_connection(db_connection):
    assert db_connection.is_connected() == True

# Test 2: Check if cursor is created successfully
def test_db_cursor(db_cursor):
    assert db_cursor is not None

# Test 3: Check if database contains specific tables
def test_db_contains_tables(db_cursor):
    #
    db_cursor.execute("SHOW TABLES")
    tables = {table[0] for table in db_cursor.fetchall()}
    
    expected_tables = ["users", "conversations"]
    for table in expected_tables:
        assert table in tables, f"Table '{table}' is not in the database"


if __name__ == "__main__":
    pytest.main()