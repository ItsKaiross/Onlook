from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
import base64
from api.database import db
from datetime import datetime
now = datetime.now()
current_date_time = now
from api.audit import log_audit

a_dashboard_bp = Blueprint('a_dashboard_bp', __name__)

##################################################
#########  A D M I N  D A S H B O A R D  #########
##################################################

@a_dashboard_bp.route('/admin-dashboard')
def admin():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    roles = session.get('role')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail

    # Database connection
    conn = db.get_db_connection()
    if conn is None:
        flash('No database connection')
        return redirect(url_for('login_bp.home'))
    cursor = conn.cursor(dictionary=True, buffered=True)

    #Defaults
    total_police = 0
    total_users = 0

    if 'accounts_id' in session and session['role'] == 'systemAdmin':

        cursor.execute("""SELECT COUNT(*) FROM police""")
        result_police = cursor.fetchone()
        total_police = result_police['COUNT(*)'] if result_police else 0
        
        cursor.execute("""SELECT COUNT(*) FROM public_user""")
        result_users = cursor.fetchone()
        total_users = result_users['COUNT(*)'] if result_users else 0
        
        cursor.execute("""SELECT COUNT(*) FROM case_file""")
        result_cases = cursor.fetchone()
        total_cases = result_cases['COUNT(*)'] if result_cases else 0
        
        cursor.execute("""SELECT COUNT(*) FROM accounts""")
        result_accounts = cursor.fetchone()
        total_accounts = result_accounts['COUNT(*)'] if result_accounts else 0
        
        # Get monthly report cases data for current year
        cursor.execute("""
            SELECT MONTH(date_and_time_reported) as month, COUNT(*) as count
            FROM case_file 
            WHERE YEAR(date_and_time_reported) = YEAR(CURDATE())
            GROUP BY MONTH(date_and_time_reported)
            ORDER BY month
        """)
        report_monthly_results = cursor.fetchall()
        
        # Create array with all 12 months (0 count for months with no data)
        report_monthly_counts = [0] * 12
        for result in report_monthly_results:
            report_monthly_counts[result['month'] - 1] = result['count']
        
        report_cases_data = report_monthly_counts
        
        # Get monthly user registrations data for current year
        cursor.execute("""
            SELECT MONTH(created_at) as month, COUNT(*) as count
            FROM public_user 
            WHERE YEAR(created_at) = YEAR(CURDATE()) AND created_at IS NOT NULL
            GROUP BY MONTH(created_at)
            ORDER BY month
        """)
        user_monthly_results = cursor.fetchall()
        
        # Debug: Print the results
        print(f"User monthly results: {user_monthly_results}")
        
        # Create array with all 12 months (0 count for months with no data)
        user_monthly_counts = [0] * 12
        for result in user_monthly_results:
            user_monthly_counts[result['month'] - 1] = result['count']
        
        user_count_data = user_monthly_counts
        print(f"User count data: {user_count_data}")
        
        # Get monthly police registrations data for current year
        cursor.execute("""
            SELECT MONTH(a.created_at) as month, COUNT(*) as count
            FROM accounts a
            JOIN police p ON a.officer_id = p.officer_id
            WHERE YEAR(a.created_at) = YEAR(CURDATE()) AND a.role = 'police' AND a.created_at IS NOT NULL
            GROUP BY MONTH(a.created_at)
            ORDER BY month
        """)
        police_monthly_results = cursor.fetchall()
        
        # Debug: Print the results
        print(f"Police monthly results: {police_monthly_results}")
        
        # Create array with all 12 months (0 count for months with no data)
        police_monthly_counts = [0] * 12
        for result in police_monthly_results:
            police_monthly_counts[result['month'] - 1] = result['count']
        
        police_count_data = police_monthly_counts
        print(f"Police count data: {police_count_data}")
        
    elif 'accounts_id' in session and session['role'] == 'policeAdmin':
        
        # Get case statistics
        cursor.execute("SELECT COUNT(*) as count FROM case_file")
        result_cases = cursor.fetchone()
        total_cases = result_cases['count'] if result_cases else 0
        
        # Approval Status Counts
        cursor.execute("SELECT COUNT(*) as count FROM case_file WHERE approval_status = 'approved'")
        approved = cursor.fetchone()
        approved_cases = approved['count'] if approved else 0
        active_cases = approved_cases  # Keep for backward compatibility
        
        cursor.execute("SELECT COUNT(*) as count FROM case_file WHERE approval_status = 'pending' OR approval_status = 'Pending'")
        pending = cursor.fetchone()
        pending_cases = pending['count'] if pending else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM case_file WHERE approval_status = 'rejected' OR approval_status = 'Rejected'")
        rejected = cursor.fetchone()
        rejected_cases = rejected['count'] if rejected else 0
        
        # Case Status Counts
        cursor.execute("SELECT COUNT(*) as count FROM case_file WHERE case_status IN ('Open', 'Active')")
        open_result = cursor.fetchone()
        open_cases = open_result['count'] if open_result else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM case_file WHERE case_status = 'In Progress'")
        in_progress = cursor.fetchone()
        in_progress_cases = in_progress['count'] if in_progress else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM case_file WHERE case_status = 'Closed'")
        closed = cursor.fetchone()
        closed_cases = closed['count'] if closed else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM case_file WHERE case_status = 'Cold Case'")
        cold = cursor.fetchone()
        cold_cases = cold['count'] if cold else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM case_file WHERE case_status = 'Rejected'")
        rejected_status = cursor.fetchone()
        rejected_status_cases = rejected_status['count'] if rejected_status else 0
        
        # Get monthly case data for current year
        cursor.execute("""
            SELECT MONTH(date_and_time_reported) as month, COUNT(*) as count
            FROM case_file 
            WHERE YEAR(date_and_time_reported) = YEAR(CURDATE())
            GROUP BY MONTH(date_and_time_reported)
            ORDER BY month
        """)
        monthly_results = cursor.fetchall()
        
        # Create array with all 12 months (0 count for months with no data)
        monthly_counts = [0] * 12
        for result in monthly_results:
            monthly_counts[result['month'] - 1] = result['count']
        
        monthly_data = monthly_counts
        
        # Get unsolved cases (Open, Active, In Progress)
        cursor.execute("""
            SELECT cf.case_id, CONCAT(mpi.first_name, ' ', mpi.last_name) as name, cf.case_status
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            WHERE cf.case_status IN ('Open', 'Active', 'In Progress')
            ORDER BY cf.date_and_time_reported DESC
            LIMIT 10
        """)
        unsolved_cases = cursor.fetchall()
        
        # Get solved cases (Closed)
        cursor.execute("""
            SELECT cf.case_id, CONCAT(mpi.first_name, ' ', mpi.last_name) as name, cf.case_status
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            WHERE cf.case_status = 'Closed'
            ORDER BY cf.date_and_time_reported DESC
            LIMIT 10
        """)
        solved_cases = cursor.fetchall()
        
        cursor.execute(
            """SELECT COUNT(*) FROM police"""
            )
        result_police = cursor.fetchone()
        total_police = result_police['COUNT(*)'] if result_police else 0
        
        cursor.execute("""SELECT COUNT(*) FROM public_user""")
        result_users = cursor.fetchone()
        total_users = result_users['COUNT(*)'] if result_users else 0
    
    # Set default values for variables that might not be defined
    if 'total_cases' not in locals():
        total_cases = 0
    if 'total_accounts' not in locals():
        total_accounts = 0
    if 'active_cases' not in locals():
        active_cases = 0
    if 'approved_cases' not in locals():
        approved_cases = 0
    if 'pending_cases' not in locals():
        pending_cases = 0
    if 'rejected_cases' not in locals():
        rejected_cases = 0
    if 'open_cases' not in locals():
        open_cases = 0
    if 'in_progress_cases' not in locals():
        in_progress_cases = 0
    if 'closed_cases' not in locals():
        closed_cases = 0
    if 'cold_cases' not in locals():
        cold_cases = 0
    if 'rejected_status_cases' not in locals():
        rejected_status_cases = 0
    if 'monthly_data' not in locals():
        monthly_data = [0,0,0,0,0,0,0,0,0,0,0,0]
    if 'unsolved_cases' not in locals():
        unsolved_cases = []
    if 'solved_cases' not in locals():
        solved_cases = []
    if 'report_cases_data' not in locals():
        report_cases_data = [0,0,0,0,0,0,0,0,0,0,0,0]
    if 'user_count_data' not in locals():
        user_count_data = [0,0,0,0,0,0,0,0,0,0,0,0]
    if 'police_count_data' not in locals():
        police_count_data = [0,0,0,0,0,0,0,0,0,0,0,0]
    
    return render_template(
        'admin/admin-base.html',
        page = 'admin-dashboard',
        loggedIn_email = loggedIn_email,
        total_police = total_police,
        total_users= total_users,
        total_accounts = total_accounts,
        roles = roles,
        total_cases = total_cases,
        active_cases = active_cases,
        approved_cases = approved_cases,
        pending_cases = pending_cases,
        rejected_cases = rejected_cases,
        open_cases = open_cases,
        in_progress_cases = in_progress_cases,
        closed_cases = closed_cases,
        cold_cases = cold_cases,
        rejected_status_cases = rejected_status_cases,
        monthly_data = monthly_data,
        unsolved_cases = unsolved_cases,
        solved_cases = solved_cases,
        report_cases_data = report_cases_data,
        user_count_data = user_count_data,
        police_count_data = police_count_data,
        current_year = datetime.now().year
        )

@a_dashboard_bp.route('/admin-case-details/<int:case_id>')
def admin_case_details(case_id):
    if session.get('role') not in ['policeAdmin', 'systemAdmin']:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'error': 'Database connection failed'})
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT cf.case_id, cf.case_status, cf.approval_status, cf.priority, cf.date_and_time_reported,
            CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name, ' ', IFNULL(mpi.suffix, '')) as full_name,
            mpi.gender, TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
            mpi.height, mpi.weight, mpi.hair_color, mpi.eye_color,
            mpls.clothing_description, mpls.date_last_seen, mpls.time_last_seen,
            mpm.missing_filedata, mpm.missing_filetype
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            WHERE cf.case_id = %s
        """, (case_id,))
        
        case_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if case_data:
            # Process image if exists
            if case_data.get('missing_filedata'):
                try:
                    case_data['missing_filedata'] = base64.b64encode(case_data['missing_filedata']).decode('utf-8')
                    case_data['img_src'] = f"data:{case_data['missing_filetype']};base64,{case_data['missing_filedata']}"
                except:
                    case_data['img_src'] = None
            
            # Convert timedelta to string
            if case_data.get('time_last_seen'):
                case_data['time_last_seen'] = str(case_data['time_last_seen'])
            
            # Convert height to feet
            if case_data.get('height'):
                try:
                    cm_float = float(case_data['height'])
                    total_inches = cm_float / 2.54
                    feet = int(total_inches // 12)
                    inches = int(total_inches % 12)
                    case_data['height'] = f"{feet}'{inches}\""
                except:
                    case_data['height'] = str(case_data['height'])
            
            return jsonify({'success': True, 'case': case_data})
        else:
            return jsonify({'success': False, 'error': 'Case not found'})
            
    except Exception as e:
        print(f"Error in admin_case_details: {e}")
        return jsonify({'success': False, 'error': str(e)})

@a_dashboard_bp.route('/admin-dashboard/report-cases-data/<int:year>')
def get_report_cases_data(year):
    if session.get('role') != 'systemAdmin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT MONTH(date_and_time_reported) as month, COUNT(*) as count
            FROM case_file 
            WHERE YEAR(date_and_time_reported) = %s
            GROUP BY MONTH(date_and_time_reported)
            ORDER BY month
        """, (year,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create array with all 12 months
        monthly_counts = [0] * 12
        for result in results:
            monthly_counts[result['month'] - 1] = result['count']
        
        return jsonify({'success': True, 'data': monthly_counts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@a_dashboard_bp.route('/admin-dashboard/registrations-data/<int:year>')
def get_registrations_data(year):
    if session.get('role') != 'systemAdmin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user registrations
        cursor.execute("""
            SELECT MONTH(created_at) as month, COUNT(*) as count
            FROM public_user 
            WHERE YEAR(created_at) = %s AND created_at IS NOT NULL
            GROUP BY MONTH(created_at)
            ORDER BY month
        """, (year,))
        user_results = cursor.fetchall()
        
        # Get police registrations
        cursor.execute("""
            SELECT MONTH(a.created_at) as month, COUNT(*) as count
            FROM accounts a
            JOIN police p ON a.officer_id = p.officer_id
            WHERE YEAR(a.created_at) = %s AND a.role = 'police' AND a.created_at IS NOT NULL
            GROUP BY MONTH(a.created_at)
            ORDER BY month
        """, (year,))
        police_results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Create arrays with all 12 months
        user_monthly_counts = [0] * 12
        for result in user_results:
            user_monthly_counts[result['month'] - 1] = result['count']
        
        police_monthly_counts = [0] * 12
        for result in police_results:
            police_monthly_counts[result['month'] - 1] = result['count']
        
        return jsonify({
            'success': True, 
            'user_data': user_monthly_counts,
            'police_data': police_monthly_counts
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


