from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
import base64
now = datetime.now()
current_date_time = now
from api.audit import log_audit 
from api.police.case_history import log_case_status_change

###################################################
######### U N A R C H I V E  R E P O R T  #########
###################################################


@app.route('/police-unarchive-report/<int:case_id>', methods=['POST'])
def police_unarchive_report(case_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current status for audit logging
        cursor.execute("SELECT approval_status FROM case_file WHERE case_id = %s", (case_id,))
        current_report = cursor.fetchone()
        before_status = current_report['approval_status'] if current_report else 'unknown'
        
        cursor.execute("""
            UPDATE case_file SET approval_status = 'Pending' WHERE case_id = %s
        """, (case_id,))
        
        # Log case status change
        log_case_status_change(cursor, case_id, previous_approval=before_status, new_approval='Pending')
        
        # Log audit for unarchiving report
        log_audit(cursor, module='reports', action='unarchive',
                  target_table='case_file', target_id=case_id,
                  before={'approval_status': before_status}, 
                  after={'approval_status': 'Pending'})
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Report unarchived successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})