from flask import Blueprint, session, render_template, redirect, url_for, flash
from flask import request
from api.database import db
from api.utils.activity_logger import log_user_activity
from datetime import datetime
now = datetime.now()
current_date_time = now
from api.audit import log_audit

a_user_logs_bp = Blueprint('a_user_logs_bp', __name__)

#################################################
#########  A D M I N  U S E R  L O G S  #########
#################################################

@a_user_logs_bp.route('/admin-user-logs')
def admin_user_logs():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    roles = session.get('role')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    
    # Get pagination parameters
    logs_page = request.args.get('logs_page', 1, type=int)
    logs_per_page = request.args.get('logs_per_page', 10, type=int)
    offset = (logs_page - 1) * logs_per_page
    
    # Get filter parameters
    role_filter = request.args.get('role', '')
    action_filter = request.args.get('action', '')
    status_filter = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Initialize users as empty list
    users = []
    total_records = 0
    total_pages = 1
    
    # Database connection
    conn = db.get_db_connection()
    if conn is None:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    try:
        if 'accounts_id' in session and session['role'] == 'systemAdmin':
            # Build WHERE clause based on filters
            where_conditions = []
            params = []
            
            if role_filter:
                where_conditions.append("a.role = %s")
                params.append(role_filter)
            
            if action_filter:
                where_conditions.append("ul.action = %s")
                params.append(action_filter)
            
            if status_filter:
                where_conditions.append("ul.status = %s")
                params.append(status_filter)
            
            if date_from:
                where_conditions.append("DATE(ul.log_timestamp) >= %s")
                params.append(date_from)
            
            if date_to:
                where_conditions.append("DATE(ul.log_timestamp) <= %s")
                params.append(date_to)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Get total count with filters
            count_query = f"""SELECT COUNT(*) as total FROM user_logs ul
                JOIN accounts a ON ul.accounts_id = a.accounts_id
                {where_clause}"""
            cursor.execute(count_query, params)
            count_result = cursor.fetchone()
            total_records = count_result['total'] if count_result else 0
            
            # Get paginated logs with filters
            query = f"""SELECT ul.log_id, a.email, a.role, ul.action, ul.log_timestamp, 
                   ul.ip_address, ul.user_agent, ul.status, ul.additional_info
                FROM user_logs ul
                JOIN accounts a ON ul.accounts_id = a.accounts_id
                {where_clause}
                ORDER BY ul.log_timestamp DESC
                LIMIT %s OFFSET %s"""
            cursor.execute(query, params + [logs_per_page, offset])
            users = cursor.fetchall()
            
            # Calculate total pages
            total_pages = (total_records + logs_per_page - 1) // logs_per_page if total_records > 0 else 1
        else:
            # User doesn't have proper admin role
            flash('Access denied. Insufficient privileges.', 'error')
            return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Error retrieving user logs: {str(e)}', 'error')
        users = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template(
        'admin/admin-base.html',
        page = 'admin-user-logs',
        loggedIn_email=loggedIn_email,
        users=users,
        roles = roles,
        logs_page=logs_page,
        logs_per_page=logs_per_page,
        total_pages=total_pages,
        total_records=total_records
        )


