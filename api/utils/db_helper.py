from api.database import db
from contextlib import contextmanager

@contextmanager
def get_db_cursor(dictionary=True):
    """
    Context manager for database operations that ensures proper cleanup.
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            result = cursor.fetchall()
    """
    conn = None
    cursor = None
    try:
        conn = db.get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=dictionary)
            yield cursor
            conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass

def execute_query(query, params=None, fetch_one=False, fetch_all=False, dictionary=True):
    """
    Execute a database query with proper error handling.
    
    Args:
        query: SQL query string
        params: Query parameters tuple
        fetch_one: Return single row
        fetch_all: Return all rows
        dictionary: Return results as dictionary
    
    Returns:
        Query results or None on error
    """
    conn = None
    cursor = None
    try:
        conn = db.get_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor(dictionary=dictionary)
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
            
        conn.commit()
        return result
    except Exception as e:
        print(f"Query execution error: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return None
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass
