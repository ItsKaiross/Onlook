#!/usr/bin/env python3
import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="haruki1315",
            database="onlook",
            autocommit=False,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def clear_database():
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # Tables to clear (order matters due to foreign keys)
    tables = [
        'case_file',
        'missing_person_last_seen',
        'missing_person_additional_files',
        'missing_person_media',
        'missing_person_location',
        'missing_person_information',
        'missing_person_health_condition',
        'no_account_user',
        'accounts',
        'public_user',
        'police',
        'profile_pictures'
    ]
    
    try:
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Cleared table: {table}")
        
        # Reset auto-increment counters
        for table in tables:
            cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        conn.commit()
        print("\nDatabase cleared successfully!")
        
    except Exception as e:
        print(f"Error clearing database: {e}")
        conn.rollback()
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    confirm = input("Are you sure you want to clear the entire database? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_database()
    else:
        print("Operation cancelled.")