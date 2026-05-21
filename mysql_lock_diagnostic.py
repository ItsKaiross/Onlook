"""
MySQL Lock Diagnostic and Fix Utility

This script helps diagnose and resolve MySQL lock wait timeout issues.
Run this when you encounter "Lock wait timeout exceeded" errors.
"""

import mysql.connector
import os
from datetime import datetime

def get_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.environ.get('db_password'),
            database="onlook"
        )
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def show_processlist():
    """Show all MySQL processes"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SHOW FULL PROCESSLIST")
        processes = cursor.fetchall()
        
        print("\n" + "="*100)
        print("MYSQL PROCESS LIST")
        print("="*100)
        print(f"{'ID':<8} {'USER':<15} {'HOST':<20} {'DB':<15} {'COMMAND':<10} {'TIME':<8} {'STATE':<30}")
        print("-"*100)
        
        for proc in processes:
            print(f"{proc['Id']:<8} {proc['User']:<15} {proc['Host']:<20} "
                  f"{str(proc['db']):<15} {proc['Command']:<10} {proc['Time']:<8} "
                  f"{str(proc['State']):<30}")
        
        cursor.close()
        conn.close()
        
        return processes
    except Exception as e:
        print(f"Error showing processlist: {e}")
        if conn:
            conn.close()
        return None

def show_innodb_status():
    """Show InnoDB status including locks"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW ENGINE INNODB STATUS")
        status = cursor.fetchone()
        
        print("\n" + "="*100)
        print("INNODB STATUS (TRANSACTIONS SECTION)")
        print("="*100)
        
        if status:
            # Parse the status output to find TRANSACTIONS section
            full_status = status[2]
            if "TRANSACTIONS" in full_status:
                trans_section = full_status.split("TRANSACTIONS")[1].split("FILE I/O")[0]
                print(trans_section[:2000])  # Print first 2000 chars
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error showing InnoDB status: {e}")
        if conn:
            conn.close()

def show_locks():
    """Show current locks"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Check for locked tables
        cursor.execute("""
            SELECT 
                r.trx_id waiting_trx_id,
                r.trx_mysql_thread_id waiting_thread,
                r.trx_query waiting_query,
                b.trx_id blocking_trx_id,
                b.trx_mysql_thread_id blocking_thread,
                b.trx_query blocking_query
            FROM information_schema.innodb_lock_waits w
            INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
            INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id
        """)
        
        locks = cursor.fetchall()
        
        if locks:
            print("\n" + "="*100)
            print("BLOCKING LOCKS DETECTED")
            print("="*100)
            for lock in locks:
                print(f"\nBlocking Thread: {lock['blocking_thread']}")
                print(f"Blocking Query: {lock['blocking_query']}")
                print(f"Waiting Thread: {lock['waiting_thread']}")
                print(f"Waiting Query: {lock['waiting_query']}")
                print("-"*100)
        else:
            print("\nNo blocking locks detected.")
        
        cursor.close()
        conn.close()
        
        return locks
    except Exception as e:
        print(f"Error showing locks: {e}")
        if conn:
            conn.close()
        return None

def kill_long_running_queries(max_time=60):
    """Kill queries running longer than max_time seconds"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SHOW FULL PROCESSLIST")
        processes = cursor.fetchall()
        
        killed = []
        for proc in processes:
            # Skip system processes and current connection
            if proc['User'] == 'root' and proc['Command'] != 'Sleep' and proc['Time'] > max_time:
                try:
                    kill_cursor = conn.cursor()
                    kill_cursor.execute(f"KILL {proc['Id']}")
                    kill_cursor.close()
                    killed.append(proc['Id'])
                    print(f"Killed process {proc['Id']} (running for {proc['Time']}s)")
                except Exception as e:
                    print(f"Failed to kill process {proc['Id']}: {e}")
        
        cursor.close()
        conn.close()
        
        if killed:
            print(f"\nKilled {len(killed)} long-running processes")
        else:
            print("\nNo long-running processes to kill")
            
        return killed
    except Exception as e:
        print(f"Error killing processes: {e}")
        if conn:
            conn.close()
        return None

def optimize_tables():
    """Optimize frequently used tables"""
    conn = get_connection()
    if not conn:
        return
    
    tables = ['user_logs', 'audit_trail', 'case_file', 'accounts']
    
    try:
        cursor = conn.cursor()
        print("\n" + "="*100)
        print("OPTIMIZING TABLES")
        print("="*100)
        
        for table in tables:
            try:
                print(f"Optimizing {table}...", end=" ")
                cursor.execute(f"OPTIMIZE TABLE {table}")
                print("Done")
            except Exception as e:
                print(f"Failed: {e}")
        
        cursor.close()
        conn.close()
        print("\nTable optimization complete")
    except Exception as e:
        print(f"Error optimizing tables: {e}")
        if conn:
            conn.close()

def check_table_locks():
    """Check for table-level locks"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SHOW OPEN TABLES WHERE In_use > 0")
        locked_tables = cursor.fetchall()
        
        if locked_tables:
            print("\n" + "="*100)
            print("LOCKED TABLES")
            print("="*100)
            for table in locked_tables:
                print(f"Database: {table['Database']}, Table: {table['Table']}, In_use: {table['In_use']}")
        else:
            print("\nNo locked tables detected")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking table locks: {e}")
        if conn:
            conn.close()

def main():
    """Main diagnostic function"""
    print("\n" + "="*100)
    print(f"MySQL LOCK DIAGNOSTIC TOOL - {datetime.now()}")
    print("="*100)
    
    # Show current processes
    processes = show_processlist()
    
    # Show locks
    locks = show_locks()
    
    # Check table locks
    check_table_locks()
    
    # Show InnoDB status
    show_innodb_status()
    
    # Ask if user wants to kill long-running queries
    if processes:
        print("\n" + "="*100)
        response = input("\nDo you want to kill queries running longer than 60 seconds? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            kill_long_running_queries(60)
    
    # Ask if user wants to optimize tables
    print("\n" + "="*100)
    response = input("\nDo you want to optimize tables? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        optimize_tables()
    
    print("\n" + "="*100)
    print("Diagnostic complete!")
    print("="*100)

if __name__ == "__main__":
    main()
