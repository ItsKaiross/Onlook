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

################################################
#########  A S S I G N  O F F I C E R  #########
################################################

@app.route('/police-assign-officer/<int:case_id>', methods=['POST'])
def police_assign_officer(case_id):
    print(f"DEBUG: Assign officer called for case {case_id}")
    print(f"DEBUG: Session role: {session.get('role')}")
    print(f"DEBUG: Session accounts_id: {session.get('accounts_id')}")
    
    # Only Police Chief can assign officers
    if session.get('role') != 'policeChief':
        print(f"DEBUG: Access denied for role: {session.get('role')}")
        return jsonify({'success': False, 'message': 'Only Police Chief can assign officers'})
    
    try:
        data = request.get_json()
        officer_id = data.get('officer_id')
        print(f"DEBUG: Received officer_id: {officer_id}")
        print(f"DEBUG: Request data: {data}")
        
        conn = db.get_db_connection()
        if conn is None:
            print("DEBUG: Database connection failed")
            return jsonify({'success': False, 'message': 'Database connection failed'})
            
        cursor = conn.cursor(dictionary=True)
        
        # Get current assigned officer for audit logging
        cursor.execute("SELECT assigned_officer_id FROM case_file WHERE case_id = %s", (case_id,))
        current_case = cursor.fetchone()
        before_officer_id = current_case['assigned_officer_id'] if current_case else None
        print(f"DEBUG: Current officer_id: {before_officer_id}")
        
        # Convert empty string to None
        final_officer_id = officer_id if officer_id and officer_id != '' else None
        print(f"DEBUG: Final officer_id to assign: {final_officer_id}")
        
        cursor.execute("""
            UPDATE case_file SET assigned_officer_id = %s WHERE case_id = %s
        """, (final_officer_id, case_id))
        
        rows_affected = cursor.rowcount
        print(f"DEBUG: Rows affected: {rows_affected}")
        
        # Log audit for officer assignment
        log_audit(cursor, module='case_file', action='assign_officer',
                  target_table='case_file', target_id=case_id,
                  before={'assigned_officer_id': before_officer_id},
                  after={'assigned_officer_id': final_officer_id})
        
        conn.commit()
        log_user_activity('officer_assigned', 'success', f'{{"case_id": "{case_id}", "officer_id": "{final_officer_id}"}}', session.get('accounts_id'))
        cursor.close()
        conn.close()
        
        print(f"DEBUG: Officer assignment successful")
        return jsonify({'success': True, 'message': 'Officer assigned successfully'})
        
    except Exception as e:
        print(f"DEBUG: Error in assign officer: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})