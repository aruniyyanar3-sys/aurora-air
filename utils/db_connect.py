import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """
    Create and return a PostgreSQL database connection.
    Uses DATABASE_URL environment variable for connection.
    Returns connection with RealDictCursor for dictionary-like row access.
    """
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        raise


def execute_query(query, params=None, fetch=False, fetchone=False):
    """
    Execute a SQL query with optional parameters.
    
    Args:
        query: SQL query string
        params: Tuple of parameters for the query
        fetch: If True, fetch all results
        fetchone: If True, fetch only one result
    
    Returns:
        Query results if fetch/fetchone is True, else None
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        
        conn.commit()
        return result
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Query execution error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def test_connection():
    """Test database connectivity and return status."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"
