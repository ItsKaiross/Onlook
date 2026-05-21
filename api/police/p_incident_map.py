from app import app
from flask import Flask, session, render_template, redirect, url_for, flash
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
now = datetime.now()
current_date_time = now
import json
import base64
from api.audit import log_audit

#########################################################
#########  P O L I C E  I N C I D E N T  M A P  #########
#########################################################

@app.route('/police-incident-map')
def police_incident_map():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    
    # Initialize variables
    locations = []
    notifications = []
    notification_count = 0
    profile = None
    
    # Database connection
    conn = db.get_db_connection()
    if not conn:
        print("Database connection failed for incident map")
        return render_template(
            'police/police-base.html',
            page = 'police-incident-map',
            loggedIn_email=loggedIn_email,
            profile=profile,
            locations=locations,
            notifications=notifications,
            notification_count=notification_count)
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    if 'accounts_id' in session and (session.get('role') == 'police' or session.get('role') == 'policeChief' or session.get('role') == 'policeAdmin' or (session.get('role') and (session.get('role').endswith('-mps') or session.get('role').endswith('-ps')))):
        cursor.execute(
            """
            SELECT cf.case_id,
            CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name, ' ', IFNULL(mpi.suffix, '')) as full_name,
            mpi.person_id,
            ST_Y(mpl.location) as longitude, ST_X(mpl.location) as latitude,
            cf.case_status, cf.approval_status, cf.date_and_time_reported, cf.isAlive, cf.isDead
            FROM case_file cf
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            LEFT JOIN missing_person_information mpi ON mpls.person_id = mpi.person_id
            LEFT JOIN missing_person_location mpl ON mpls.missing_person_location_id = mpl.missing_person_location_id
            WHERE LOWER(cf.approval_status) IN ('approved', 'pending') AND mpi.person_id IS NOT NULL
            GROUP BY mpi.person_id, cf.case_id, mpi.first_name, mpi.middle_name, mpi.last_name, mpi.suffix,
                     mpl.location, cf.case_status, cf.approval_status, cf.date_and_time_reported, cf.isAlive, cf.isDead
            ORDER BY cf.date_and_time_reported DESC
            """
            )
        reports = cursor.fetchall()
        
        print(f"Found {len(reports)} approved cases for incident map")
        
        # Prepare location data for map
        for report in reports:
            if (report['latitude'] and report['longitude'] and report['latitude'] != 0 and report['longitude'] != 0):
                # Determine if case is active based on case_status
                case_status = (report['case_status'] or 'Open').lower()
                is_alive = report.get('isAlive', 0)
                is_dead = report.get('isDead', 0)
                
                # Case is inactive if it's closed (either alive or dead)
                is_active = not (is_alive == 1 or is_dead == 1 or 'closed' in case_status)
                
                print(f"Case {report['case_id']}: status={case_status}, isAlive={is_alive}, isDead={is_dead}, is_active={is_active}")
                
                # Get first image for this person
                cursor.execute("""
                    SELECT missing_filedata, missing_filetype
                    FROM missing_person_media 
                    WHERE missing_person_id = %s 
                    AND missing_filedata IS NOT NULL 
                    AND (is_archived IS NULL OR is_archived = 0)
                    ORDER BY uploaded_at ASC
                    LIMIT 1
                """, (report['person_id'],))
                
                image_row = cursor.fetchone()
                image_data = None
                
                if image_row and image_row['missing_filedata']:
                    try:
                        # Ensure filetype is properly formatted
                        filetype = image_row['missing_filetype'] or 'image/jpeg'
                        if not filetype.startswith('image/'):
                            filetype = f'image/{filetype}'
                        image_data = f"data:{filetype};base64,{base64.b64encode(image_row['missing_filedata']).decode('utf-8')}"
                    except Exception as e:
                        print(f"Error encoding image for person {report['person_id']}: {e}")
                        image_data = None
                
                locations.append({
                    'lat': float(report['latitude']),
                    'lng': float(report['longitude']),
                    'name': report['full_name'] or 'Unknown',
                    'status': report['approval_status'] or 'pending',
                    'case_status': report['case_status'] or 'Unknown',
                    'is_active': is_active,
                    'image': image_data
                })
                
                print(f"Added location for {report['full_name']}: lat={report['latitude']}, lng={report['longitude']}, is_active={is_active}")
        
        print(f"Total locations added to map: {len(locations)}")
        
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
    
    print(f"Rendering incident map with {len(locations)} locations")
    print(f"Locations data: {locations}")
    
    return render_template(
        'police/police-base.html',
        page = 'police-incident-map',
        loggedIn_email=loggedIn_email,
        profile=profile,
        locations=locations,
        notifications=notifications,
        notification_count=notification_count)