from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from datetime import datetime
from api.audit import log_audit

archive_user_bp = Blueprint('archive_user_bp', __name__)

####################################
#########  A R C H I V E  ##########
####################################

@archive_user_bp.route('/admin-user-management/archive-user/<int:user_id>', methods=['POST'])
def archive_user(user_id):
    if 'accounts_id' not in session or session.get('role') != 'systemAdmin':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    try:
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Check if user exists and get current status
        cursor.execute("SELECT status, role FROM accounts WHERE accounts_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Prevent archiving system admin
        if user['role'] == 'systemAdmin':
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Cannot archive System Administrator'}), 403
        
        old_status = user['status']
        
        # Update user status to archived
        cursor.execute(
            "UPDATE accounts SET status = %s WHERE accounts_id = %s",
            ('archived', user_id)
        )
        
        # Log audit trail
        log_audit(cursor, module='users', action='archive_user',
                  target_table='accounts', target_id=user_id,
                  before={'status': old_status},
                  after={'status': 'archived'})
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'User archived successfully'
        })
        
    except Exception as e:
        print(f"Error archiving user: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


