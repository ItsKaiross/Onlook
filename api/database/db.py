import mysql.connector
from mysql.connector import Error
import os



##########################################################
#########  D A T A B A S E  C O N N E C T I O N  #########
##########################################################

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.environ.get('db_password'),
            database="onlook",
            autocommit=False,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            connection_timeout=10,
            pool_reset_session=True
        )
        if conn.is_connected():
            return conn
        else:
            print("Failed to establish database connection")
            return None
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None