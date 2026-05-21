from flask import Blueprint, session, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from datetime import datetime
import base64
now = datetime.now()
from api.audit import log_audit

follow_up_report_bp = Blueprint('follow_up_report_bp', __name__)

###################################################
#########  F O L L O W  U P  R E P O R T  #########
###################################################

@follow_up_report_bp.route('/police-add-follow-report', methods=['POST'])
def police_add_follow_report():
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        case_id = request.form.get('case_id')
        reporter_name = request.form.get('reporter_name')
        relationship = request.form.get('relationship')
        follow_date = request.form.get('follow_date')
        follow_time = request.form.get('follow_time')
        description = request.form.get('description')
        officer_id = session.get('officer_id')
        submitted_at = now
        
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # Handle file uploads if any
        reportMedia_id = None
        if 'evidence_files' in request.files:
            files = request.files.getlist('evidence_files')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_data = file.read()
                    file_type = file.content_type
                    
                    # Get person_id from case
                    cursor.execute("""
                        SELECT mpm.missing_person_id 
                        FROM case_file cf
                        LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
                        WHERE cf.case_id = %s
                    """, (case_id,))
                    person_result = cursor.fetchone()
                    person_id = person_result['missing_person_id'] if person_result else None
                    
                    cursor.execute("""
                        INSERT INTO missing_person_media
                        (missing_person_id, missing_filename, missing_filetype, missing_filedata, uploaded_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (person_id, filename, file_type, file_data, submitted_at))
                    
                    reportMedia_id = cursor.lastrowid
                    break  # Only handle first file for now
        
        # Create location entry (default coordinates)
        cursor.execute("""
            INSERT INTO missing_person_location (location)
            VALUES (ST_GeomfromText('POINT(14.2691 121.4577)', 4326))
        """)
        lastLocation_id = cursor.lastrowid
        
        # Use same structure as help locate - insert into case_reporters table
        cursor.execute("""
            INSERT INTO case_reporters
            (case_id, reporter_type, reporter_id, follow_up_media_id, follow_up_location_id, 
            relationship_to_missing, date_reported, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            case_id,
            'police',
            officer_id,
            reportMedia_id,
            lastLocation_id,
            relationship,
            submitted_at,
            description
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Follow report added successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


