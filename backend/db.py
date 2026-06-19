import os
import mysql.connector

# Load credentials from a local .env file if python-dotenv is available.
# .env is gitignored so secrets never get committed.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "medicines_db"),
    )
