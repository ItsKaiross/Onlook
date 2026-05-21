from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
import base64
import os
from werkzeug.utils import secure_filename
from api.utils.activity_logger import log_user_activity
now = datetime.now()
current_date_time = now
from api.audit import log_audit

############################################
#########  C A S E  D E T A I L S  #########
############################################

@app.route('/police-case-details/<int:case_id>')
def police_case_details(case_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'error': 'Database connection failed'})
            
        cursor = conn.cursor(dictionary=True)
        
        # Get case details with all related information
        cursor.execute("""
            SELECT cf.case_id, cf.case_status, cf.approval_status, cf.priority, cf.date_and_time_reported,
            CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name, ' ', IFNULL(mpi.suffix, '')) as full_name,
            mpi.gender, mpi.date_of_birth,
            CASE 
                WHEN mpi.date_of_birth IS NOT NULL THEN TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE())
                ELSE NULL
            END AS age,
            mpi.height, mpi.weight, mpi.hair_color, mpi.eye_color,
            mpls.clothing_description, mpls.date_last_seen, mpls.time_last_seen,
            CONCAT(p.rank, ' ', p.first_name, ' ', p.last_name) as assigned_officer
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            LEFT JOIN police p ON cf.assigned_officer_id = p.officer_id
            WHERE cf.case_id = %s
        """, (case_id,))
        
        case_data = cursor.fetchone()
        
        if not case_data:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Case not found'})
        
        # Check if archived columns exist first
        cursor.execute("SHOW COLUMNS FROM missing_person_media LIKE 'is_archived'")
        has_archived_column = cursor.fetchone() is not None
        
        # Get all non-archived images for this missing person
        if has_archived_column:
            cursor.execute("""
                SELECT mpm2.missing_person_media_id, mpm2.missing_filedata, mpm2.missing_filetype, mpm2.uploaded_at
                FROM missing_person_media mpm2
                JOIN missing_person_information mpi ON mpm2.missing_person_id = mpi.person_id
                JOIN missing_person_media mpm ON mpi.person_id = mpm.missing_person_id
                JOIN case_file cf ON mpm.missing_person_media_id = cf.media_id
                WHERE cf.case_id = %s AND mpm2.missing_filedata IS NOT NULL AND LENGTH(mpm2.missing_filedata) > 10
                AND (mpm2.is_archived IS NULL OR mpm2.is_archived = 0)
            """, (case_id,))
        else:
            cursor.execute("""
                SELECT mpm2.missing_person_media_id, mpm2.missing_filedata, mpm2.missing_filetype, mpm2.uploaded_at
                FROM missing_person_media mpm2
                JOIN missing_person_information mpi ON mpm2.missing_person_id = mpi.person_id
                JOIN missing_person_media mpm ON mpi.person_id = mpm.missing_person_id
                JOIN case_file cf ON mpm.missing_person_media_id = cf.media_id
                WHERE cf.case_id = %s AND mpm2.missing_filedata IS NOT NULL AND LENGTH(mpm2.missing_filedata) > 10
            """, (case_id,))
        
        all_images = cursor.fetchall()
        case_images = []
        
        for i, img in enumerate(all_images):
            if img.get('missing_filedata'):
                try:
                    img_data = base64.b64encode(img['missing_filedata']).decode('utf-8')
                    case_images.append({
                        'id': img['missing_person_media_id'],
                        'src': f"data:{img['missing_filetype']};base64,{img_data}",
                        'title': f"Evidence Photo {i + 1}",
                        'timestamp': str(img.get('uploaded_at', 'Unknown date'))
                    })
                except Exception as img_error:
                    print(f"Image processing error: {img_error}")
                    continue
        
        # Get detailed case reporters information
        cursor.execute("""
            SELECT cr.relationship_to_missing, cr.date_reported, cr.reporter_type, cr.description,
            CASE 
                WHEN cr.reporter_type = 'user' THEN CONCAT(u.first_name, ' ', u.last_name)
                WHEN cr.reporter_type = 'no_account' THEN CONCAT(nu.first_name, ' ', nu.last_name)
                WHEN cr.reporter_type = 'police' THEN CONCAT(p.rank, ' ', p.first_name, ' ', p.last_name)
                ELSE 'Unknown Reporter'
            END as reporter_name,
            CASE 
                WHEN cr.reporter_type = 'no_account' THEN nu.contact_number
                WHEN cr.reporter_type = 'police' THEN 'Police Officer'
                WHEN cr.reporter_type = 'user' THEN u.contact_number
                ELSE 'N/A'
            END as contact_number,
            CASE 
                WHEN cr.reporter_type = 'no_account' THEN nu.email
                WHEN cr.reporter_type = 'police' THEN 'Official Report'
                WHEN cr.reporter_type = 'user' THEN a.email
                ELSE 'N/A'
            END as email
            FROM case_reporters cr
            LEFT JOIN accounts a ON cr.reporter_id = a.accounts_id AND cr.reporter_type = 'user'
            LEFT JOIN public_user u ON a.user_id = u.user_id AND cr.reporter_type = 'user'
            LEFT JOIN no_account_user nu ON cr.reporter_id = nu.no_account_id AND cr.reporter_type = 'no_account'
            LEFT JOIN police p ON cr.reporter_id = p.officer_id AND cr.reporter_type = 'police'
            WHERE cr.case_id = %s
            ORDER BY cr.date_reported DESC
        """, (case_id,))
        
        reporters = cursor.fetchall()
        case_reporters = []
        
        for reporter in reporters:
            case_reporters.append({
                'name': reporter.get('reporter_name', 'Unknown'),
                'relationship': reporter.get('relationship_to_missing', 'N/A'),
                'contact': reporter.get('contact_number', 'N/A'),
                'email': reporter.get('email', 'N/A'),
                'reporter_type': reporter.get('reporter_type', 'N/A'),
                'report_date': str(reporter.get('date_reported', 'N/A')),
                'description': reporter.get('description', 'N/A')
            })
        
        # Convert datetime and timedelta to string
        if case_data.get('time_last_seen'):
            case_data['time_last_seen'] = str(case_data['time_last_seen'])
        if case_data.get('date_and_time_reported'):
            case_data['date_and_time_reported'] = str(case_data['date_and_time_reported'])
        if case_data.get('date_last_seen'):
            case_data['date_last_seen'] = str(case_data['date_last_seen'])
        
        # Case data is now clean without binary data
        
        case_data['images'] = case_images
        case_data['reporters'] = case_reporters
        case_data['has_archived_column'] = has_archived_column
        
        cursor.close()
        conn.close()
        
        print(f'Retrieved case details for case {case_id}: {len(case_images)} images, {len(case_reporters)} reporters')
        return jsonify({'success': True, 'case': case_data})
        
    except Exception as e:
        print(f"Error in police_case_details: {e}")
        return jsonify({'success': False, 'error': str(e)})