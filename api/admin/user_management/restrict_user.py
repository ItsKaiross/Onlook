from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from datetime import datetime
now = datetime.now()
from api.audit import log_audit

restrict_user_bp = Blueprint('restrict_user_bp', __name__)

##############################################
#########  R E S T R I C T  U S E R  #########
##############################################

@restrict_user_bp.route('/admin-user-management/restrict-user/<int:accounts_id>', methods=['POST', 'GET'])
def admin_restrict_user(accounts_id):
    msg = ''
    if request.method == 'GET':
        # Database connection
        conn = db.get_db_connection()
        
        if conn is None:
            flash('Database connection failed', 'error')
            return redirect(url_for('admin_user_management'))
        
        cursor = conn.cursor(dictionary=True)
        
        # Check if the user being restricted is a systemAdmin
        cursor.execute('SELECT role FROM accounts WHERE accounts_id = %s', (accounts_id,))
        user = cursor.fetchone()
        
        if user and user['role'] == 'systemAdmin':
            flash('System Administrators cannot be restricted', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('admin_user_management'))
        
        # Log audit for restricting user
        log_audit(cursor, module='users', action='restrict_user',
                  target_table='accounts', target_id=accounts_id,
                  before={'status': 'active'}, after={'status': 'restricted'})
        
        cursor.execute('UPDATE accounts SET status=%s WHERE accounts_id = %s', ('restricted', accounts_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('User has been restricted successfully', 'success')
        
    return redirect(url_for('admin_user_management'))


