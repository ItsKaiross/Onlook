from flask import render_template, redirect, url_for, flash, Blueprint
from api.database import db
from api.audit import log_audit

post_response_bp = Blueprint('post_api', __name__)

@post_response_bp.route('/post-report-response/<token>/<response>')
def handle_post_response(token, response):
    """Handle informant's response to post their report publicly"""
    try:
        conn = db.get_db_connection()
        if not conn:
            flash('Database connection failed')
            return redirect(url_for('public_view_bp.public_users'))
            
        cursor = conn.cursor(dictionary=True)
        
        # Find the case by token
        cursor.execute("""
            SELECT case_id, approval_status 
            FROM case_file 
            WHERE post_token = %s
        """, (token,))
        
        case = cursor.fetchone()
        
        if not case:
            flash('Invalid or expired link')
            return redirect(url_for('public_view_bp.public_users'))
        
        if response == 'yes':
            # Update approval status to approved for public posting
            cursor.execute("""
                UPDATE case_file 
                SET approval_status = 'approved', post_response = 'yes', post_response_date = NOW()
                WHERE case_id = %s
            """, (case['case_id'],))
            
            # Log audit for case approval via public response
            log_audit(cursor, module='case_file', action='approve',
                      target_table='case_file', target_id=case['case_id'],
                      before={'approval_status': case['approval_status']},
                      after={'approval_status': 'approved', 'post_response': 'yes'})
            
            flash('Thank you! Your report has been posted publicly to help with the search.')
            
        elif response == 'no':
            # Keep as pending/private
            cursor.execute("""
                UPDATE case_file 
                SET post_response = 'no', post_response_date = NOW()
                WHERE case_id = %s
            """, (case['case_id'],))
            
            # Log audit for case response (declined public posting)
            log_audit(cursor, module='case_file', action='decline_public_post',
                      target_table='case_file', target_id=case['case_id'],
                      before={'post_response': None},
                      after={'post_response': 'no'})
            
            flash('Your report will remain private as requested.')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('public_view_bp.public_users'))
        
    except Exception as e:
        flash(f'Error processing response: {str(e)}')
        return redirect(url_for('public_view_bp.public_users'))


