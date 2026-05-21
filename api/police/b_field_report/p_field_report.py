from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from datetime import datetime
import base64
now = datetime.now()
current_date_time = now
from api.audit import log_audit

p_field_report_bp = Blueprint('p_field_report_bp', __name__)

#########################################################
#########  P O L I C E  F I E L D  R E P O R T  #########
#########################################################

@p_field_report_bp.route('/police-field-report', methods=['GET', 'POST'])
def police_field_report():
    if 'accounts_id' not in session or not (session.get('role') == 'police' or session.get('role') == 'policeChief' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return redirect(url_for('home'))

    if request.method == 'POST':
        try:
            from werkzeug.utils import secure_filename
            from datetime import datetime
            
            # Get form data
            firstName = request.form.get('FirstName', '')
            middleName = request.form.get('MiddleName', '')
            lastName = request.form.get('LastName', '')
            suffix = request.form.get('Suffix', '') or None
            alias = request.form.get('Alias', '') or None
            gender = request.form.get('Sex', '')
            dob = request.form.get('dob', '')
            birthdate = datetime.strptime(dob, '%Y-%m-%d').date() if dob else None
            
            # Health
            healthType = request.form.get('health_type_dropdown', '')
            health_desc = request.form.get('health_description', '')
            
            # Physical
            eye_color = request.form.get('eye_color', '')
            attire = request.form.get('attire', '')
            height = float(request.form.get('height', 0)) if request.form.get('height') else None
            weight = float(request.form.get('weight', 0)) if request.form.get('weight') else None
            hair_color = request.form.get('hair_color', '')
            
            # Last seen
            lastSeen = request.form.get('lastSeen', '')
            dateLastSeen = datetime.strptime(lastSeen, '%Y-%m-%d').date() if lastSeen else None
            timeLastSeen_str = request.form.get('timeLastSeen', '')
            timeLastSeen = datetime.strptime(timeLastSeen_str, '%H:%M').time() if timeLastSeen_str else None
            
            # Image
            imageOfMissing = request.files.get('upload_last_seen', '')
            if not imageOfMissing or not imageOfMissing.filename:
                flash('Please upload a photo of the missing person.', 'error')
                return redirect(url_for('police_field_report'))
            
            # Location
            location_type = request.form.get('locLastSeen', '')
            latitude = float(request.form.get('latitude', '0'))
            longitude = float(request.form.get('longitude', '0'))
            
            if latitude == 0 and longitude == 0:
                latitude = 14.2691
                longitude = 121.4577
            
            locationPoint = f'POINT({latitude} {longitude})'
            
            conn = db.get_db_connection()
            if not conn:
                flash('Database connection failed', 'error')
                return redirect(url_for('police_field_report'))
            
            cursor = conn.cursor(dictionary=True, buffered=True)
            
            # Insert health condition
            cursor.execute(
                "INSERT INTO missing_person_health_condition (first_name, middle_name, last_name, health_type, health_condition) VALUES (%s, %s, %s, %s, %s)",
                (firstName, middleName, lastName, healthType, health_desc)
            )
            healthCondition_id = cursor.lastrowid
            
            # Insert missing person info
            cursor.execute(
                """INSERT INTO missing_person_information
                (health_condition_id, first_name, middle_name, last_name, suffix, nickname, gender, date_of_birth,
                height, weight, hair_color, eye_color)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (healthCondition_id, firstName, middleName, lastName, suffix, alias, gender, birthdate,
                height, weight, hair_color, eye_color)
            )
            person_id = cursor.lastrowid
            
            # Insert location
            cursor.execute("INSERT INTO missing_person_location (location) VALUES (ST_GeomfromText(%s, 4326))", (locationPoint,))
            lastLocation_id = cursor.lastrowid
            
            # Insert image
            img_filename = secure_filename(imageOfMissing.filename)
            img_filetype = imageOfMissing.content_type
            img_filedata = imageOfMissing.read()
            
            cursor.execute(
                "INSERT INTO missing_person_media (missing_person_id, missing_filename, missing_filetype, missing_filedata, uploaded_at) VALUES (%s, %s, %s, %s, %s)",
                (person_id, img_filename, img_filetype, img_filedata, datetime.now())
            )
            reportMedia_id = cursor.lastrowid
            
            # Insert last seen
            cursor.execute(
                "INSERT INTO missing_person_last_seen (person_id, missing_person_location_id, date_last_seen, time_last_seen, clothing_description) VALUES (%s, %s, %s, %s, %s)",
                (person_id, lastLocation_id, dateLastSeen, timeLastSeen, attire)
            )
            missing_person_last_seen = cursor.lastrowid
            
            # Insert case file
            officer_id = session.get('accounts_id')
            cursor.execute(
                """INSERT INTO case_file (reporter_type, reporter_id, approval_status, case_status, priority,
                date_and_time_reported, last_updated, last_seen_id, media_id)
                VALUES ('police', %s, 'Approved', 'Open', 'medium', %s, %s, %s, %s)""",
                (officer_id, datetime.now(), datetime.now(), missing_person_last_seen, reportMedia_id)
            )
            case_id = cursor.lastrowid
            
            log_audit(cursor, module='case_file', action='create',
                      target_table='case_file', target_id=case_id,
                      after={'reporter_type': 'police', 'person_name': f'{firstName} {lastName}'})
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Manual report submitted successfully!', 'success')
            return redirect(url_for('police_field_report'))
            
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.rollback()
            print(f'Error submitting manual report: {str(e)}')
            import traceback
            traceback.print_exc()
            flash(f'Error submitting report: {str(e)}', 'error')
            return redirect(url_for('police_field_report'))

    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    
    # Initialize variables
    reports = []
    locations = []
    notifications = []
    notification_count = 0
    profile = None
    total_pages = 0
    total_records = 0
    
    field_page = request.args.get('field_page', 1, type=int)
    field_per_page = request.args.get('field_per_page', 10, type=int)
    offset = (field_page - 1) * field_per_page
    
    try:
        if 'accounts_id' in session and (session['role'] == 'police' or session['role'] == 'policeChief' or session['role'].endswith('-mps') or session['role'].endswith('-ps')):
            # Database connection
            conn = db.get_db_connection()
            
            if conn is None:
                flash('Database connection failed')
                return render_template('police/2p-field_report.html',
                    loggedIn_email=loggedIn_email,
                    reports=reports,
                    notifications=notifications,
                    notification_count=notification_count
                )
            
            cursor = conn.cursor(dictionary=True, buffered=True)
            
            # Get filter parameters
            status_filter = request.args.get('status')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            age_range = request.args.get('age_range')
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            status_filter = request.args.get('status')
            if status_filter:
                where_conditions.append("cf.approval_status = %s")
                params.append(status_filter)
            else:
                where_conditions.append("cf.approval_status != 'Archived'")
            # Add location-based filtering for police station accounts
            user_role = session.get('role')
            if user_role and user_role != 'police' and user_role != 'policeChief' and user_role != 'policeAdmin' and user_role != 'systemAdmin':
                # Extract city from role (e.g., 'alaminos-mps' -> 'alaminos')
                location = user_role.split('-')[0].replace('city', '').strip()
                where_conditions.append("(LOWER(mpi.city) LIKE %s OR LOWER(mpi.barangay) LIKE %s)")
                params.extend([f"%{location}%", f"%{location}%"])
            
            if date_from:
                where_conditions.append("DATE(cf.date_and_time_reported) >= %s")
                params.append(date_from)
            
            if date_to:
                where_conditions.append("DATE(cf.date_and_time_reported) <= %s")
                params.append(date_to)
            
            if age_range:
                age_from, age_to = age_range.split('-')
                where_conditions.append("TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) BETWEEN %s AND %s")
                params.extend([age_from, age_to])
            
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
                CONCAT(p.rank, ' ' ,p.first_name, ' ', IFNULL(p.middle_name, ''), ' ', p.last_name, ' ', IFNULL(p.suffix, '')) as assigned_officer,
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
                LEFT JOIN police p ON cf.assigned_officer_id = p.officer_id
                LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
                LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
                LEFT JOIN missing_person_health_condition mphc ON mpi.health_condition_id = mphc.missing_person_health_condition_id
                LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
                LEFT JOIN missing_person_location mpl ON mpls.missing_person_location_id = mpl.missing_person_location_id
                {where_clause}
                ORDER BY cf.case_id ASC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, params + [field_per_page, offset])
            reports = cursor.fetchall() or []
            total_pages = (total_records + field_per_page - 1) // field_per_page
            
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
                GROUP BY cf.case_id, mpi.first_name, mpi.last_name, 
                        cf.date_and_time_reported, pn.is_read
                ORDER BY cf.date_and_time_reported DESC
                LIMIT 20
            """, (session['accounts_id'],))
            notification_results = cursor.fetchall() or []
            
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
            if reports:
                for report in reports:
                    if (report.get('latitude') and report.get('longitude') and 
                        report['latitude'] != 0 and report['longitude'] != 0):
                        locations.append({
                            'lat': float(report['latitude']),
                            'lng': float(report['longitude']),
                            'name': report.get('full_name') or 'Unknown',
                            'status': str(report.get('approval_status')) if report.get('approval_status') else 'pending'
                        })
                
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
                
                # Process images
                for image_data in reports:
                    if image_data.get('missing_filedata'):
                        image_data['missing_filedata'] = base64.b64encode(image_data['missing_filedata']).decode('utf-8')
                        image_src = f"data:{image_data['missing_filetype']};base64,{image_data['missing_filedata']}"
                        image_data['img_src'] = image_src
                
            cursor.close()
            conn.close()
            return render_template(
                'police/police-base.html',
                page = 'police-field-report',
                reports=reports,
                field_page = field_page,
                field_per_page = field_per_page,
                total_pages = total_pages,
                total_records = total_records,
                loggedIn_email=loggedIn_email,
                profile=profile,
                notifications=notifications,
                notification_count=notification_count,
                )
        else:
            return redirect(url_for('home'))

    except Exception as e:
        print(f"Database error: {e}")
        
    return render_template(
        'police/police-base.html',
        page = 'police-field-report',
        reports=reports,
        field_page = field_page,
        profile=profile,
        field_per_page = field_per_page,
        total_pages = total_pages,
        total_records = total_records,
        loggedIn_email=loggedIn_email,
        notifications=notifications,
        notification_count=notification_count,
    )





