from flask import Blueprint, session, render_template, redirect, url_for, flash
from flask import request
from api.database import db
from datetime import datetime
now = datetime.now()
current_date_time = now
import math, random
import bcrypt
from api.audit import log_audit

reset_password_bp = Blueprint('reset_password_bp', __name__)

########################################
#########  R E S E T  P A S S  #########
########################################

@reset_password_bp.route('/reset_pass', methods=['GET', 'POST'])
def reset_pass():
    if request.method == 'POST':
        emailOTP = session.get('emailOTP', None)
        new_password = request.form['new_pass']
        confirm_new_password = request.form['confirm_new_pass']
        
        import re
        if new_password != confirm_new_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('reset_password_bp.reset_pass'))
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return redirect(url_for('reset_password_bp.reset_pass'))
        if not re.search(r'[A-Z]', new_password):
            flash('Password must contain at least one uppercase letter', 'error')
            return redirect(url_for('reset_password_bp.reset_pass'))
        if not re.search(r'[a-z]', new_password):
            flash('Password must contain at least one lowercase letter', 'error')
            return redirect(url_for('reset_password_bp.reset_pass'))
        if not re.search(r'[0-9]', new_password):
            flash('Password must contain at least one number', 'error')
            return redirect(url_for('reset_password_bp.reset_pass'))
        if not re.search(r'[^A-Za-z0-9]', new_password):
            flash('Password must contain at least one special character', 'error')
            return redirect(url_for('reset_password_bp.reset_pass'))
        
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        conn = db.get_db_connection()
        if conn is None:
            return redirect(url_for('reset_password_bp.reset_pass'))
        
        if new_password == confirm_new_password:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT accounts_id, email, role FROM accounts WHERE email=%s;', (emailOTP,))
            account = cursor.fetchone()
            cursor.execute('UPDATE accounts SET password = %s WHERE email=%s;', (hashed_password, emailOTP))
            
            if account:
                session['accounts_id'] = account['accounts_id']
                session['role'] = account['role']
                log_audit(cursor, module='auth', action='password_reset',
                          target_table='accounts', target_id=account['accounts_id'],
                          status='success', remarks=f'Password reset for: {emailOTP}')
            
            conn.commit()
            cursor.close()
            conn.close()
            flash('Password changed successfully', 'success')
            return redirect(url_for('public_view_bp.public_users'))

    return render_template('login/reset_password.html')
