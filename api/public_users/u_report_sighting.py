from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, request, jsonify
from api.database import db
from werkzeug.utils import secure_filename
from datetime import datetime
from api.audit import log_audit

######################################################################
#########  P U B L I C  P A G E  R E P O R T  S I G H T I N G  #######
######################################################################

@app.route('/report-sighting')
def report_sighting():
    if 'accounts_id' in session and session['role'] == 'user':
        userEmail = session.get('email')
        loggedIn = session.get('loggedIn')
        
        loggedIn_email = None
        if loggedIn == True:
            loggedIn_email = userEmail
            
        # Get approved missing person cases for dropdown and user info
        conn = db.get_db_connection()
        approved_cases = []
        user_email = userEmail
        user_contact = None
        
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get user contact info
            cursor.execute("""
                SELECT contact_number FROM public_user WHERE email = %s
            """, (userEmail,))
            user_result = cursor.fetchone()
            if user_result:
                user_contact = user_result['contact_number']
            
            # Get approved cases
            cursor.execute("""
                SELECT 
                    cf.case_id,
                    CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name) as full_name,
                    mpi.gender,
                    TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
                    cf.approval_status
                FROM case_file cf
                LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
                LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
                WHERE cf.approval_status = 'Approved' AND (cf.case_status = 'Open' OR cf.case_status = 'Active')
                ORDER BY mpi.first_name, mpi.last_name
            """)
            approved_cases = cursor.fetchall()
            cursor.close()
            conn.close()
            
        return render_template('public_users/9u-report_sighting.html', 
                             loggedIn_email=loggedIn_email, 
                             approved_cases=approved_cases,
                             user_email=user_email,
                             user_contact=user_contact), 200
    return redirect(url_for('public_users'))

@app.route('/submit-sighting', methods=['POST'])
def submit_sighting():
    if 'accounts_id' not in session or session['role'] != 'user':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        case_id = request.form.get('case_id')
        sighting_date = request.form.get('sighting_date')
        sighting_time = request.form.get('sighting_time')
        description = request.form.get('description')
        relationship = request.form.get('relationship')
        email = request.form.get('email')
        contact = request.form.get('contact')
        sighting_image = request.files.get('sighting_image')
        
        if not all([case_id, sighting_date, sighting_time, description, relationship, email, contact]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Database connection failed'})
        
        cursor = conn.cursor(dictionary=True)
        submitted_at = datetime.now()
        
        # Get person_id from case_id
        cursor.execute("""
            SELECT mpm.missing_person_id 
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            WHERE cf.case_id = %s
        """, (case_id,))
        result = cursor.fetchone()
        person_id = result['missing_person_id'] if result else None
        
        # Create location point (default coordinates)
        latitude = 14.2691
        longitude = 121.4577
        locationPoint = f'POINT({latitude} {longitude})'
        
        cursor.execute("""
            INSERT INTO missing_person_location (location)
            VALUES (ST_GeomfromText(%s, 4326))
        """, (locationPoint,))
        lastLocation_id = cursor.lastrowid
        
        # Handle image upload
        reportMedia_id = None
        if sighting_image and sighting_image.filename:
            img_filename = secure_filename(sighting_image.filename)
            img_filetype = sighting_image.content_type
            img_filedata = sighting_image.read()
            
            cursor.execute("""
                INSERT INTO missing_person_media
                (missing_person_id, missing_filename, missing_filetype, missing_filedata, uploaded_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (person_id, img_filename, img_filetype, img_filedata, submitted_at))
            reportMedia_id = cursor.lastrowid
        
        # Insert case reporter (sighting report)
        withAccounts_id = session.get('accounts_id')
        cursor.execute("""
            INSERT INTO case_reporters
            (case_id, reporter_type, reporter_id, follow_up_media_id, follow_up_location_id, 
             relationship_to_missing, date_reported, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (case_id, 'user', withAccounts_id, reportMedia_id, lastLocation_id, 
              relationship, submitted_at, description))
        
        reporter_id = cursor.lastrowid
        
        # Log sighting report audit
        log_audit(cursor, module='reports', action='submit_sighting',
                  target_table='case_reporters', target_id=reporter_id,
                  after={'case_id': case_id, 'reporter_type': 'user', 'relationship': relationship},
                  status='success', remarks=f'Sighting report submitted for case {case_id}')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sighting report submitted successfully'})
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn.close()
        print(f"Error in submit_sighting: {e}")
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
