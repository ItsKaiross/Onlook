from flask import Blueprint, session, jsonify
from flask import request
from api.database import db
from datetime import datetime
import base64
import os
from api.utils.activity_logger import log_user_activity
now = datetime.now()
from api.audit import log_audit
from api.police.case_history import log_case_status_change

archive_case_bp = Blueprint('archive_case_bp', __name__)

############################################
#########  A R C H I V E  C A S E  #########
############################################

@archive_case_bp.route('/police-archive-case/<int:case_id>', methods=['POST'])
def police_archive_case(case_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current status for audit logging
        cursor.execute("SELECT approval_status FROM case_file WHERE case_id = %s", (case_id,))
        current_case = cursor.fetchone()
        before_status = current_case['approval_status'] if current_case else 'unknown'
        
        cursor.execute("""
            UPDATE case_file SET approval_status = 'Archived' WHERE case_id = %s
        """, (case_id,))
        
        # Log case status change
        log_case_status_change(cursor, case_id, previous_approval=before_status, new_approval='Archived')
        
        # Log audit for case archiving
        log_audit(cursor, module='case_file', action='archive',
                  target_table='case_file', target_id=case_id,
                  before={'approval_status': before_status},
                  after={'approval_status': 'Archived'})
        
        conn.commit()
        log_user_activity('case_archived', 'success', f'{{"case_id": "{case_id}"}}', session.get('accounts_id'))
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Case archived successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


