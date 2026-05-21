from flask import request, session
from api.database import db
from datetime import datetime

def log_user_activity(action, status='success', additional_info=None, user_id=None):
    """Log user activity to the user_logs table"""
    conn = None
    cursor = None
    try:
        if not user_id:
            user_id = session.get('accounts_id')
        
        if not user_id:
            return
            
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
        user_agent = request.headers.get('User-Agent', '')
        
        conn = db.get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_logs 
                (accounts_id, action, ip_address, user_agent, status, additional_info)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, action, ip_address, user_agent, status, additional_info))
            conn.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
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

def log_login(user_id, email, first_name, last_name, account_type):
    """Log user login"""
    log_user_activity('login', 'success', f'{{"email": "{email}", "role": "{account_type}"}}', user_id)

def log_logout(user_id=None, email=None):
    """Log user logout"""
    if not user_id:
        user_id = session.get('accounts_id')
    if not email:
        email = session.get('email')
    log_user_activity('logout', 'success', f'{{"email": "{email}"}}', user_id)
