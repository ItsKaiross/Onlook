from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from datetime import datetime
now = datetime.now()
from api.audit import log_audit

activate_user_bp = Blueprint('activate_user_bp', __name__)

##############################################
#########  A C T I V A T E  U S E R  #########
##############################################

@activate_user_bp.route('/admin-user-management/activate-user/<int:accounts_id>', methods=['POST', 'GET'])
def admin_activate_user(accounts_id):
    msg = ''
    if request.method == 'GET':
        # Database connection
        conn = db.get_db_connection()
        
        if conn is None:
            msg2 = 'No database'
            return redirect(url_for('a_dashboard_bp.admin'))
        
        cursor = conn.cursor(dictionary=True)
        
        # Log audit for activating user
        log_audit(cursor, module='users', action='activate_user',
                  target_table='accounts', target_id=accounts_id,
                  before={'status': 'restricted'}, after={'status': 'active'})
        
        cursor.execute('UPDATE accounts SET status=%s WHERE accounts_id = %s', ('active', accounts_id))
        conn.commit()
        cursor.close()
        conn.close()
        
    return redirect(url_for('a_user_management_bp.admin_user_management'))


