from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from datetime import datetime
import base64
import os
from api.utils.activity_logger import log_user_activity
now = datetime.now()
from api.audit import log_audit

p_case_management_bp = Blueprint('p_case_management_bp', __name__)

###############################################################
#########  P O L I C E  C A S E  M A N A G E M E N T  #########
###############################################################

@p_case_management_bp.route('/police-case-management')
def police_case_management():
    try:
        if 'accounts_id' in session and (session['role'] == 'police' or session['role'] == 'policeChief' or session['role'].endswith('-mps') or session['role'].endswith('-ps')):
            userEmail = session.get('email')
            loggedIn = session.get('loggedIn')
            case_page = request.args.get('case_page', 1, type=int)
            case_per_page = request.args.get('case_per_page', 10, type=int)
            
            offset = (case_page - 1) * case_per_page
            
            loggedIn_email = None
            if loggedIn == True:
                loggedIn_email = userEmail
            
            
            # Get filter parameters
            status_filter = request.args.get('status', '')
            from_date = request.args.get('from_date', '')
            to_date = request.args.get('to_date', '')
            show_archived = request.args.get('show_archived', 'false').lower() == 'true'
            
            # Initialize variables
            reports = []
            locations = []
            officers = []
            notifications = []
            notification_count = 0

            # Database connection
            conn = db.get_db_connection()
            
            if conn is None:
                flash('Database connection failed')
                return render_template('police/1p-dashboard.html',
                    loggedIn_email=loggedIn_email,
                    reports=reports,
                )
            
            cursor = conn.cursor(dictionary=True, buffered=True)

            if 'accounts_id' in session and (session['role'] == 'police' or session['role'] == 'policeChief' or session['role'].endswith('-mps') or session['role'].endswith('-ps')):
                # Build WHERE clause for filters
                where_conditions = []
                params = []
                
                # Filter archived cases based on show_archived parameter
                if show_archived:
                    where_conditions.append("cf.approval_status = 'Archived'")
                else:
                    where_conditions.append("cf.approval_status != 'Archived'")
                
                # Add location-based filtering for police station accounts
                user_role = session.get('role')
                print(f"DEBUG: Current role: '{user_role}'")
                print(f"DEBUG: Role checks - police: {user_role == 'police'}, policeChief: {user_role == 'policeChief'}, policeAdmin: {user_role == 'policeAdmin'}, systemAdmin: {user_role == 'systemAdmin'}")
                if user_role and user_role != 'police' and user_role != 'policeChief' and user_role != 'policeAdmin' and user_role != 'systemAdmin':
                    # Extract city from role (e.g., 'alaminos-mps' -> 'alaminos')
                    location = user_role.split('-')[0].replace('city', '').strip()
                    print(f"DEBUG: APPLYING FILTER for role '{user_role}' with location '{location}'")
                    where_conditions.append("(LOWER(mpi.city) LIKE %s OR LOWER(mpi.barangay) LIKE %s)")
                    params.extend([f"%{location}%", f"%{location}%"])
                else:
                    print(f"DEBUG: NO FILTER APPLIED for role '{user_role}'")
                
                if status_filter:
                    where_conditions.append("cf.case_status = %s")
                    params.append(status_filter)
                
                if from_date:
                    where_conditions.append("DATE(cf.date_and_time_reported) >= %s")
                    params.append(from_date)
                
                if to_date:
                    where_conditions.append("DATE(cf.date_and_time_reported) <= %s")
                    params.append(to_date)
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                    
                count_query = f"""
                    SELECT COUNT(*) as total
                    FROM case_file cf
                    LEFT JOIN case_reporters cr ON cr.case_id = cf.case_id
                    LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
                    LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
                    {where_clause}
                """
                cursor.execute(count_query, params)
                total_records = cursor.fetchone()['total']
                    
                query = f"""
                    SELECT 
                    cf.case_id, cf.reporter_type, cf.reporter_id, cf.case_status, cf.approval_status, cf.priority, cf.date_and_time_reported, DATE(cf.date_and_time_reported) AS submission_date,
                    cf.assigned_officer_id,
                    CONCAT(p.rank, ' ', p.last_name) AS assigned_officer,
                    CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name, ' ', IFNULL(mpi.suffix, '')) as full_name,
                    mpi.person_id ,mpi.nickname, mpi.gender, mpi.date_of_birth, mpi.civil_status, mpi.citizenship, mpi.contact_number,
                    TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
                    mpi.height, mpi.weight, mpi.hair_color, mpi.eye_color, mpi.distinguishing_mark,
                    mpi.occupation, mpi.address, mpi.house_number, mpi.street, mpi.barangay, mpi.city, mpi.province, mpi.region,
                    mpls.clothing_description, mpls.circumstances, mpls.date_last_seen, mpls.time_last_seen,
                    mpm.missing_filedata, mpm.missing_filetype, mpm.uploaded_at,
                    ST_Y(mpl.location) as longitude, ST_X(mpl.location) as latitude,
                    mphc.health_type, mphc.health_condition, cr.relationship_to_missing
                    FROM case_file cf
                    LEFT JOIN case_reporters cr ON cr.case_id = cf.case_id
                    LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
                    LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
                    LEFT JOIN missing_person_health_condition mphc ON mpi.health_condition_id = mphc.missing_person_health_condition_id
                    LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
                    LEFT JOIN missing_person_location mpl ON mpls.missing_person_location_id = mpl.missing_person_location_id
                    LEFT JOIN police p ON cf.assigned_officer_id = p.officer_id
                    {where_clause}
                    ORDER BY cf.case_id ASC
                    LIMIT %s OFFSET %s
                """
                
                cursor.execute(query, params + [case_per_page, offset])
                reports = cursor.fetchall()  or []
                total_pages = (total_records + case_per_page - 1) // case_per_page
                
                # Get all police officers for dropdown
                cursor.execute("""
                    SELECT officer_id, `rank`, first_name, last_name
                    FROM police 
                    WHERE officer_id IN (SELECT officer_id FROM accounts WHERE role IN ('police', 'policeAdmin', 'systemAdmin') OR role LIKE '%-mps' OR role LIKE '%-ps')
                    ORDER BY 
                        CASE WHEN officer_id = %s THEN 0 ELSE 1 END,
                        `rank`, last_name
                """, (session.get('officer_id', 0),))
                officers = cursor.fetchall()
                
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
                
                # Process images and convert datetime/timedelta objects
                for image_data in reports:
                    if image_data['missing_filedata']:
                        image_data['missing_filedata'] = base64.b64encode(image_data['missing_filedata']).decode('utf-8')
                        image_src = f"data:{image_data['missing_filetype']};base64,{image_data['missing_filedata']}"
                        image_data['img_src'] = image_src
                    
                    # Convert datetime and timedelta objects to strings for JSON serialization
                    if image_data.get('date_and_time_reported'):
                        image_data['date_and_time_reported'] = str(image_data['date_and_time_reported'])
                    if image_data.get('time_last_seen'):
                        image_data['time_last_seen'] = str(image_data['time_last_seen'])
                        
                accounts_id = session['accounts_id']
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
                
                cursor.close()
                conn.close()
                return render_template(
                    'police/police-base.html',
                    page = 'police-case-management',
                    reports = reports,
                    case_page = case_page,
                    case_per_page = case_per_page,
                    total_pages = total_pages,
                    total_records = total_records,
                    loggedIn_email=loggedIn_email,
                    profile=profile,
                    officers=officers,
                    status_filter=status_filter,
                    from_date=from_date,
                    to_date=to_date,
                    show_archived=show_archived,
                    notifications=notifications,
                    notification_count=notification_count,
                    user_role=user_role
                )

    except Exception as e:
        print(f"Database error: {e}")

    return render_template(
            'police/police-base.html',
            page = 'police-case-management',
            reports = reports,
            case_page = case_page,
            case_per_page = case_per_page,
            total_pages = total_pages,
            total_records = total_records,
            loggedIn_email=loggedIn_email,
            profile=profile,
            officers=officers,
            status_filter=status_filter,
            from_date=from_date,
            to_date=to_date,
            show_archived=False,
            notifications=notifications,
            notification_count=notification_count,
            user_role=session.get('role', '')
        )




