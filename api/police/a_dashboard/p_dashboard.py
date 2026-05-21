from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
now = datetime.now()
current_date_time = now
import base64
import json
from api.audit import log_audit

####################################################
#########  P O L I C E  D A S H B O A R D  #########
####################################################

@app.route('/police-dashboard')
def police_dashboard():
    # Get year filter from request
    selected_year = request.args.get('year', datetime.now().year, type=int)
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    user_id = session.get('accounts_id')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    
    # Initialize variables
    total_cases = 0
    active_cases = 0
    closed_cases = 0
    pending_cases = 0
    approved_cases = 0
    rejected_cases = 0
    open_cases = 0
    in_progress_cases = 0
    cold_cases = 0
    rejected_status_cases = 0
    reports = []
    locations = []
    monthly_data = []
    unsolved_cases = []
    solved_cases = []
    notifications = []
    notification_count = 0
    
    try:
        # Database connection
        conn = db.get_db_connection()
        
        if conn is None:
            flash('Database connection failed')
            return render_template('police/1p-dashboard.html',
                loggedIn_email=loggedIn_email,
                total_cases=total_cases,
                active_cases=active_cases,
                closed_cases=closed_cases,
                reports=reports,
                locations=json.dumps(locations)
            )
            
        cursor = conn.cursor(dictionary=True, buffered=True)
        accounts_id = session['accounts_id']
        if 'accounts_id' in session and (session['role'] == 'police' or session['role'] == 'policeChief' or session['role'].endswith('-mps') or session['role'].endswith('-ps')):
        
            cursor.execute("SELECT COUNT(*) as count FROM case_file")
            result_cases = cursor.fetchone()
            total_cases = result_cases['count'] if result_cases else 0
            
            # Approval Status Counts
            cursor.execute("SELECT COUNT(*) as count FROM case_file WHERE approval_status = 'approved'")
            approved = cursor.fetchone()
            approved_cases = approved['count'] if approved else 0
            
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
            
            # Keep active_cases for backward compatibility (approved cases)
            active_cases = approved_cases
            
            # Get monthly case data for selected year
            cursor.execute("""
                SELECT MONTH(date_and_time_reported) as month, COUNT(*) as count
                FROM case_file 
                WHERE YEAR(date_and_time_reported) = %s
                GROUP BY MONTH(date_and_time_reported)
                ORDER BY month
            """, (selected_year,))
            monthly_results = cursor.fetchall()
            
            # Create array with all 12 months (0 count for months with no data)
            monthly_counts = [0] * 12
            for result in monthly_results:
                monthly_counts[result['month'] - 1] = result['count']
            
            monthly_data = {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'data': monthly_counts
            }
            
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
            
            # Get recent notifications (new reports submitted in last 7 days)
            cursor.execute("""
                SELECT 
                    cf.case_id,
                    CONCAT(mpi.first_name, ' ', mpi.last_name) as reporter_name,
                    cf.date_and_time_reported,
                    TIMESTAMPDIFF(HOUR, cf.date_and_time_reported, NOW()) as hours_ago,
                    COALESCE(pn.is_read, FALSE) as is_read
                FROM case_file cf
                LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
                LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
                LEFT JOIN police_notifications pn ON cf.case_id = pn.case_id AND pn.police_id = %s
                WHERE cf.date_and_time_reported >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ORDER BY cf.date_and_time_reported DESC
                LIMIT 20
            """, (session['accounts_id'],))
            notification_results = cursor.fetchall()
            
            # Format notifications and count unread ones
            unread_count = 0
            for notif in notification_results:
                hours_ago = notif['hours_ago']
                if hours_ago < 1:
                    time_ago = "Just now"
                elif hours_ago < 24:
                    time_ago = f"{hours_ago} hours ago"
                else:
                    days_ago = hours_ago // 24
                    time_ago = f"{days_ago} day{'s' if days_ago > 1 else ''} ago"
                
                is_read = bool(notif['is_read'])
                if not is_read:
                    unread_count += 1
                
                notifications.append({
                    'case_id': notif['case_id'],
                    'message': f"New missing person report for {notif['reporter_name'] or 'Unknown'}",
                    'time_ago': time_ago,
                    'is_read': is_read
                })
            
            notification_count = unread_count
        
        
        cursor.execute(
            """
            SELECT CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name, ' ', IFNULL(mpi.suffix, '')) as full_name,
            mpi.person_id ,mpi.nickname, mpi.gender, mpi.date_of_birth, mpi.civil_status, mpi.citizenship, mpi.contact_number,
            TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
            mpi.height, mpi.weight, mpi.hair_color, mpi.eye_color, mpi.distinguishing_mark,
            mpi.occupation, mpi.address, mpi.house_number, mpi.street, mpi.barangay, mpi.city, mpi.province, mpi.region,
            mpls.clothing_description, mpls.circumstances, mpls.date_last_seen, mpls.time_last_seen,
            mpm.missing_filedata, mpm.missing_filetype, mpm.uploaded_at,
            ST_Y(mpl.location) as longitude, ST_X(mpl.location) as latitude,
            mphc.health_type, mphc.health_condition, cr.relationship_to_missing, cf.case_status, cf.approval_status, cf.date_and_time_reported, DATE(cf.date_and_time_reported) AS submission_date
            FROM case_file cf
            LEFT JOIN case_reporters cr ON cr.case_id = cf.case_id
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_health_condition mphc ON mpi.health_condition_id = mphc.missing_person_health_condition_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            LEFT JOIN missing_person_location mpl ON mpls.missing_person_location_id = mpl.missing_person_location_id
            ORDER BY date_and_time_reported DESC
            """
            )
        reports = cursor.fetchall()
        
        # Prepare location data for map
        for report in reports:
            if (report['latitude'] and report['longitude'] and 
                report['latitude'] != 0 and report['longitude'] != 0):
                locations.append({
                    'lat': float(report['latitude']),
                    'lng': float(report['longitude']),
                    'name': report['full_name'] or 'Unknown',
                    'status': str(report['approval_status']) if report['approval_status'] else 'pending'
                })
        
        
        cursor.execute(
            '''
            SELECT p.first_name, p.last_name, p.middle_name, p.email, p.badge_number,
            p.barangay, p.city, p.province, p.region, p.rank, p.station_assignment, p.street, p.house_no, p.contact_number,
            pp.profile_filedata, pp.profile_filetype
            FROM police p
            JOIN accounts acc ON p.officer_id = acc.accounts_id
            LEFT JOIN profile_pictures pp ON p.profile_picture_id = pp.profile_id
            WHERE acc.accounts_id = %s
            ''',
            (accounts_id,)
        )
        profile = cursor.fetchone()
        if profile and profile['profile_filedata']:
            profile['profile_filedata'] = base64.b64encode(profile['profile_filedata']).decode('utf-8')

            
            # Process images
        for image_data in reports:
            if image_data['missing_filedata']:
                image_data['missing_filedata'] = base64.b64encode(image_data['missing_filedata']).decode('utf-8')
                image_src = f"data:{image_data['missing_filetype']};base64,{image_data['missing_filedata']}"
                image_data['img_src'] = image_src
                    
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")
        
    return render_template(
        'police/police-base.html',
        page = 'police-dashboard',
        loggedIn_email=loggedIn_email,
        total_cases=total_cases,
        active_cases=active_cases,
        closed_cases=closed_cases,
        pending_cases=pending_cases,
        approved_cases=approved_cases,
        rejected_cases=rejected_cases,
        open_cases=open_cases,
        in_progress_cases=in_progress_cases,
        cold_cases=cold_cases,
        rejected_status_cases=rejected_status_cases,
        reports=reports,
        profile=profile,
        locations=json.dumps(locations),
        monthly_data=json.dumps(monthly_data),
        unsolved_cases=unsolved_cases,
        solved_cases=solved_cases,
        notifications=notifications,
        notification_count=notification_count,
        selected_year=selected_year
    )

@app.route('/police-notification-count')
def police_notification_count():
    if 'accounts_id' not in session or not (session.get('role') == 'police' or session.get('role') == 'policeChief' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'count': 0})
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as unread FROM case_file cf
            LEFT JOIN police_notifications pn ON cf.case_id = pn.case_id AND pn.police_id = %s
            WHERE cf.date_and_time_reported >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            AND COALESCE(pn.is_read, FALSE) = FALSE
        """, (session['accounts_id'],))
        count = cursor.fetchone()['unread']
        cursor.close()
        conn.close()
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'count': 0})


@app.route('/police-mark-notifications-read', methods=['POST'])
def mark_notifications_read():
    try:
        if 'accounts_id' not in session or not (session['role'] == 'police' or session['role'] == 'policeChief' or session['role'].endswith('-mps') or session['role'].endswith('-ps')):
            return {'success': False, 'message': 'Unauthorized'}, 401
            
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        # Create notifications table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS police_notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                police_id INT,
                case_id INT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_police_case (police_id, case_id)
            )
        """)
        
        # Mark all notifications as read for this police officer
        cursor.execute("""
            INSERT INTO police_notifications (police_id, case_id, is_read)
            SELECT %s, cf.case_id, TRUE
            FROM case_file cf
            WHERE cf.date_and_time_reported >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ON DUPLICATE KEY UPDATE is_read = TRUE
        """, (session['accounts_id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True}
        
    except Exception as e:
        print(f"Error marking notifications as read: {e}")
        return {'success': False, 'message': str(e)}, 500