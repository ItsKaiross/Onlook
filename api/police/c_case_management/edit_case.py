from flask import Blueprint, session, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from datetime import datetime
import base64
import os
from api.utils.activity_logger import log_user_activity
now = datetime.now()
from api.audit import log_audit
from api.police.case_history import log_case_status_change

edit_case_bp = Blueprint('edit_case_bp', __name__)

######################################
#########  E D I T  C A S E  #########
######################################


@edit_case_bp.route('/police-edit-case/<int:case_id>', methods=['POST']) 
def police_edit_case(case_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current case data for audit logging
        cursor.execute("""
            SELECT case_status, priority, isAlive, isDead FROM case_file WHERE case_id = %s
        """, (case_id,))
        current_case = cursor.fetchone()
        before_data = {
            'case_status': current_case['case_status'] if current_case else None,
            'priority': current_case['priority'] if current_case else None,
            'isAlive': current_case['isAlive'] if current_case else None,
            'isDead': current_case['isDead'] if current_case else None
        }
        
        new_case_status = request.form.get('case_status')
        new_priority = request.form.get('priority')
        
        # Determine isAlive and isDead based on case status
        isAlive = 0
        isDead = 0
        if new_case_status == 'Closed - Alive':
            isAlive = 1
            isDead = 0
        elif new_case_status == 'Closed - Dead':
            isAlive = 0
            isDead = 1
        
        # Update case file
        cursor.execute("""
            UPDATE case_file SET case_status = %s, priority = %s, isAlive = %s, isDead = %s WHERE case_id = %s
        """, (new_case_status, new_priority, isAlive, isDead, case_id))
        
        # Log case status change if status changed
        if before_data['case_status'] != new_case_status:
            log_case_status_change(cursor, case_id, previous_status=before_data['case_status'], new_status=new_case_status)
            conn.commit()  # Commit the status history insert
        
        # Update missing person information
        cursor.execute("""
            UPDATE missing_person_information mpi
            JOIN missing_person_media mpm ON mpi.person_id = mpm.missing_person_id
            JOIN case_file cf ON mpm.missing_person_media_id = cf.media_id
            SET mpi.first_name = %s, mpi.gender = %s, mpi.height = %s, mpi.weight = %s,
                mpi.hair_color = %s, mpi.eye_color = %s
            WHERE cf.case_id = %s
        """, (
            request.form.get('full_name', '').split()[0] if request.form.get('full_name') else '',
            request.form.get('gender'), request.form.get('height'), request.form.get('weight'),
            request.form.get('hair_color'), request.form.get('eye_color'), case_id
        ))
        
        # Update last seen information
        cursor.execute("""
            UPDATE missing_person_last_seen mpls
            JOIN case_file cf ON mpls.missing_person_last_seen_id = cf.last_seen_id
            SET mpls.date_last_seen = %s, mpls.clothing_description = %s
            WHERE cf.case_id = %s
        """, (request.form.get('date_last_seen'), request.form.get('clothing_description'), case_id))
        
        # Handle additional images
        if 'additional_images' in request.files:
            files = request.files.getlist('additional_images')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_data = file.read()
                    file_type = file.content_type
                    
                    # Insert new image
                    cursor.execute("""
                        INSERT INTO missing_person_media (missing_person_id, missing_filedata, missing_filetype, uploaded_at)
                        SELECT mpi.person_id, %s, %s, NOW()
                        FROM missing_person_information mpi
                        JOIN missing_person_media mpm ON mpi.person_id = mpm.missing_person_id
                        JOIN case_file cf ON mpm.missing_person_media_id = cf.media_id
                        WHERE cf.case_id = %s
                        LIMIT 1
                    """, (file_data, file_type, case_id))
        
        conn.commit()
        
        # Log audit for case update
        after_data = {
            'case_status': new_case_status,
            'priority': new_priority,
            'isAlive': isAlive,
            'isDead': isDead,
            'full_name': request.form.get('full_name'),
            'gender': request.form.get('gender')
        }
        log_audit(cursor, module='case_file', action='update',
                  target_table='case_file', target_id=case_id,
                  before=before_data, after=after_data)
        
        log_user_activity('case_updated', 'success', f'{{"case_id": "{case_id}"}}', session.get('accounts_id'))
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Case updated successfully'})
        
    except Exception as e:
        print(f"Error in police_edit_case: {e}")
        return jsonify({'success': False, 'message': str(e)})


