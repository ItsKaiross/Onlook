from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from flask_mail import Mail, Message
from datetime import datetime
from api.audit import log_audit
from api.police.case_history import log_case_status_change
from api.login.mail import mail

##################################################
#########  A P P R O V A L  S T A T U S  #########
##################################################

@app.route('/police-update-approval-status/<int:case_id>', methods=['POST'])
def police_update_approval_status(case_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        data = request.get_json()
        approval_status = data.get('approval_status')
        rejection_note = data.get('rejection_note', '').strip()
        
        if approval_status not in ['Pending', 'Approved', 'Rejected', 'Archived']:
            return jsonify({'success': False, 'message': 'Invalid approval status'})
        
        if approval_status == 'Rejected' and not rejection_note:
            return jsonify({'success': False, 'message': 'A rejection note is required.'})
        
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current status and reporter info
        cursor.execute("""
            SELECT cf.approval_status, cf.reporter_type, cf.reporter_id,
                   CONCAT(mpi.first_name, ' ', mpi.last_name) AS missing_name
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            WHERE cf.case_id = %s
        """, (case_id,))
        current_report = cursor.fetchone()
        before_status = current_report['approval_status'] if current_report else 'unknown'
        
        cursor.execute("UPDATE case_file SET approval_status = %s WHERE case_id = %s", (approval_status, case_id))
        
        # If rejected, also update case_status to 'Rejected'
        if approval_status == 'Rejected':
            cursor.execute("UPDATE case_file SET case_status = 'Rejected' WHERE case_id = %s", (case_id,))
        
        log_case_status_change(cursor, case_id, previous_approval=before_status, new_approval=approval_status)
        log_audit(cursor, module='case_file',
                  action='approve' if approval_status == 'Approved' else 'reject' if approval_status == 'Rejected' else 'update_status',
                  target_table='case_file', target_id=case_id,
                  before={'approval_status': before_status},
                  after={'approval_status': approval_status})
        
        conn.commit()
        
        # Send rejection email
        if approval_status == 'Rejected' and current_report:
            reporter_type = current_report.get('reporter_type')
            reporter_id   = current_report.get('reporter_id')
            missing_name  = current_report.get('missing_name') or 'the missing person'
            
            reporter_email = None
            if reporter_type == 'user':
                cursor.execute("SELECT email FROM public_user WHERE user_id = %s", (reporter_id,))
            elif reporter_type == 'police':
                cursor.execute("SELECT email FROM police WHERE officer_id = %s", (reporter_id,))
            
            row = cursor.fetchone()
            if row:
                reporter_email = row['email']
            
            if reporter_email:
                try:
                    msg = Message(
                        subject=f'Report Rejected – Case #{case_id}',
                        recipients=[reporter_email],
                        body=(
                            f"Dear Reporter,\n\n"
                            f"Your missing person report for {missing_name} (Case #{case_id}) "
                            f"has been reviewed and rejected for the following reason:\n\n"
                            f"{rejection_note}\n\n"
                            f"If you believe this is an error or have additional information, "
                            f"please contact your local police station.\n\n"
                            f"Regards,\nOnlook Support Team"
                        )
                    )
                    mail.send(msg)
                except Exception as mail_err:
                    print(f'Rejection email failed: {mail_err}')
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Approval status updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})