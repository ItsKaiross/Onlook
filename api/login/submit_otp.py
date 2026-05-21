from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify, current_app
from flask import request
from api.database import db
from flask_mail import Mail, Message
from datetime import datetime
now = datetime.now()
current_date_time = now
import math, random
from api.audit import log_audit

submit_otp_bp = Blueprint('submit_otp_bp', __name__)

########################################
#########  S U B M I T  O T P  #########
########################################

@submit_otp_bp.route('/submit_otp', methods=['GET', 'POST'])
def submit_otp():
    if request.method == 'POST':
        otp_input = request.form['otp_code']
        OneTimePass = session.get('One_Time_Password', None)
        email = session.get('emailOTP', None)
        
        # Get database connection for audit logging
        conn = db.get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get user info for audit
            cursor.execute('SELECT accounts_id FROM accounts WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            if OneTimePass == otp_input:
                # Log successful OTP verification
                if user:
                    log_audit(cursor, module='auth', action='verify_otp',
                              target_table='accounts', target_id=user['accounts_id'],
                              status='success', remarks=f'OTP verified for: {email}')
                
                cursor.close()
                conn.close()
                return redirect(url_for('reset_password_bp.reset_pass'))
            else:
                # Log failed OTP verification
                if user:
                    log_audit(cursor, module='auth', action='verify_otp',
                              target_table='accounts', target_id=user['accounts_id'],
                              status='failure', remarks=f'Invalid OTP attempt for: {email}')
                
                cursor.close()
                conn.close()
                message = "Invalid OTP code"
                return render_template('login/submit_otp.html', msg = message)
        

    return render_template('login/submit_otp.html')


########################################
#########  R E S E N D  O T P  #########
########################################

def generateOTP():
    random_pass = '0123456789'
    length = len(random_pass)
    OneTimePass = ''
    
    for i in range(6):
        OneTimePass += random_pass[math.floor(random.random() * length)]
        
    return OneTimePass

@submit_otp_bp.route('/resend_otp', methods=['POST'])
def resend_otp():
    try:
        email = session.get('emailOTP', None)
        
        if not email:
            return jsonify({'success': False, 'message': 'No email found in session'}), 400
        
        # Generate new OTP
        otp = generateOTP()
        session['One_Time_Password'] = otp
        
        # Get database connection
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get user info
        cursor.execute('SELECT accounts_id FROM accounts WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Send email
        from flask_mail import Mail, Message
        mail = Mail(current_app)
        
        subject = 'RESET PASSWORD CODE - RESENT'
        html_body = f"""
        <div style="font-family: Arial, sans-serif;">
            <p>Your One-Time Password (OTP):</p>

            <h1 style="font-size: 48px; letter-spacing: 4px; margin: 20px 0;">
                {otp}
            </h1>

            <p>Please use this OTP to reset your password.</p>
            <p>If you did not request this OTP, please ignore this email.</p>
            <p>Thank you for using Onlook!<br>Onlook Team</p>
        </div>
        """
        
        msg = Message(
            subject=subject,
            recipients=[email],
            html=html_body)
        
        mail.send(msg)
        
        # Log audit
        log_audit(cursor, module='auth', action='resend_otp_email',
                  target_table='accounts', target_id=user['accounts_id'],
                  status='success', remarks=f'OTP resent to: {email}')
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'OTP resent successfully'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


