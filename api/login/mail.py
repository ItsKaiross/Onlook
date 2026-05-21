from flask import Blueprint, session, render_template, redirect, url_for, flash
from flask import request
from api.database import db
from flask_mail import Mail, Message
from datetime import datetime
now = datetime.now()
current_date_time = now
import math, random
from api.audit import log_audit

mail = Mail()

mail_bp = Blueprint('mail_bp', __name__)

def generateOTP():
    random_pass = '0123456789'
    length = len(random_pass)
    OneTimePass = ''
    
    for i  in range(6):
        OneTimePass += random_pass[math.floor(random.random() * length)]
        
    return OneTimePass

@mail_bp.route('/mailOTP', methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':
        otp = generateOTP()
        recipient = request.form['email']
        subject = 'RESET PASSWORD CODE'
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
        session['emailOTP'] = recipient
        session['One_Time_Password'] = otp
        conn = db.get_db_connection()
        
        if conn is None:
            return redirect(url_for('mail_bp.send_mail'))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE email =%s AND email=%s;', (recipient, recipient))
        user = cursor.fetchone()
        
        if user is None:
            flash('Account does not exist', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('public_view_bp.public_users'))
        else:
            msg = Message(subject=subject, recipients=[recipient], html=html_body)
            try:
                mail.send(msg)
                log_audit(cursor, module='auth', action='send_otp_email',
                          target_table='accounts', target_id=user['accounts_id'],
                          status='success', remarks=f'OTP email sent to: {recipient}')
                cursor.close()
                conn.close()
            except Exception as e:
                log_audit(cursor, module='auth', action='send_otp_email',
                          target_table='accounts', target_id=user['accounts_id'],
                          status='failure', remarks=f'Failed to send OTP email to: {recipient}')
                cursor.close()
                conn.close()
            return redirect(url_for('mail_bp.send_mail'))

    return render_template('login/submit_otp.html')
