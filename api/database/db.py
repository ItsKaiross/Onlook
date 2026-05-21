import mysql.connector
from mysql.connector import Error
import os

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get('MYSQLHOST'),
            port=int(os.environ.get('MYSQLPORT', 3306)),
            user=os.environ.get('MYSQLUSER'),
            password=os.environ.get('MYSQLPASSWORD'),
            database=os.environ.get('MYSQLDATABASE'),
            autocommit=False,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            connection_timeout=10,
            pool_reset_session=True,
            ssl_disabled=False
        )
        if conn.is_connected():
            return conn
        else:
            print("Failed to establish database connection")
            return None
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None
