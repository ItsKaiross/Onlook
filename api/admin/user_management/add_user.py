from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify, current_app
from flask import request
from api.database import db
from flask_mail import Mail, Message
from datetime import datetime
now = datetime.now()
current_date_time = now
import base64
import bcrypt
import logging
import os
from api.audit import log_audit

add_user_bp = Blueprint('add_user_bp', __name__)

####################################
#########  A D D  U S E R  #########
####################################

@add_user_bp.route('/admin-user-management/add-user', methods=['POST', 'GET'])
def admin_add_user():
    if request.method == 'POST':
        # Get form data
        badge_number = request.form.get('badgeNumber', '')
        rank = request.form.get('rank', '')
        first_name = request.form.get('firstName', '')
        middle_name = request.form.get('middleName', '')
        last_name = request.form.get('lastName', '')
        gender = request.form.get('gender', '')
        dateOfBirth_str = request.form.get('dateOfBirth', '')
        date_of_birth = datetime.strptime(dateOfBirth_str, '%Y-%m-%d').date() if dateOfBirth_str else None
        contact_number = request.form.get('contact_number', '')
        email = request.form.get('email', '')
        station = request.form.get('station', '')
        
        submitted_at = now
        
        # Database connection
        conn = db.get_db_connection()
        if conn is None:
            flash('Database connection failed', 'error')
            return redirect(url_for('admin_user_management'))
        
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        try:
            # Insert police officer data with minimal fields
            cursor.execute(
                """
                INSERT INTO police (badge_number, `rank`, first_name, middle_name, last_name, 
                gender, date_of_birth, contact_number, email, station_assignment, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (badge_number, rank, first_name, middle_name, last_name, gender, 
                date_of_birth, contact_number, email, station, 'active')
            )
            
            officer_id = cursor.lastrowid
            
            hashed_password = bcrypt.hashpw(badge_number.encode('utf-8'), bcrypt.gensalt())
            # Create account
            cursor.execute(
                """
                INSERT INTO accounts (email, password, role, status, officer_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (email, hashed_password,'police', 'active', officer_id, submitted_at)
            )
            
            conn.commit()
            
            # Get the new account ID for audit logging
            new_account_id = cursor.lastrowid
            
            # Log audit for adding user
            log_audit(cursor, module='users', action='add_user',
                      target_table='accounts', target_id=new_account_id,
                      after={'email': email, 'role': 'police', 'officer_id': officer_id})
            
            sendEmail(recipient=email, badge_number=badge_number, first_name=first_name, 
                     last_name=last_name, rank=rank, station=station)
            flash(f'User added successfully and the password is {badge_number}', 'success')
            
        except Exception as e:
            conn.rollback()
            flash(f'Error adding user: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
        
    return redirect(url_for('admin_user_management'))

########################################################
#########  A D D  U S E R  S E N D  E M A I L  #########
########################################################

def sendEmail(recipient, badge_number='', first_name='', last_name='', rank='', station=''):
    #FLASK MAIL CONFIGURATION
    current_app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    current_app.config['MAIL_PORT'] = 587
    current_app.config['MAIL_USE_TLS'] = os.environ.get('TLS')
    current_app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USER')
    current_app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASS')
    current_app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USER')

    mail = Mail(current_app)

    # Plain text version
    text_body = f"""Dear {rank} {first_name} {last_name},

Welcome to the Onlook System!

Your police officer account has been successfully created.

Account Details:
Badge Number: {badge_number}
Email: {recipient}
Password: {badge_number}
Rank: {rank}
Station: {station}

Please change your password after your first login.

Best regards,
Onlook System Administration Team"""

    # HTML version
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7fa;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
        }}
        .header {{
            background: linear-gradient(135deg, #1A1B41 0%, #2a2b51 100%);
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header p {{
            color: #e0e0e0;
            margin: 10px 0 0 0;
            font-size: 16px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333333;
            margin-bottom: 20px;
            line-height: 1.6;
        }}
        .welcome-text {{
            font-size: 16px;
            color: #555555;
            line-height: 1.8;
            margin-bottom: 30px;
        }}
        .info-box {{
            background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
            border-left: 4px solid #1A1B41;
            border-radius: 8px;
            padding: 25px;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .info-box h2 {{
            color: #1A1B41;
            font-size: 18px;
            margin: 0 0 20px 0;
            font-weight: 600;
        }}
        .info-row {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #e8e8e8;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            color: #1A1B41;
            min-width: 140px;
            font-size: 14px;
        }}
        .info-value {{
            color: #555555;
            font-size: 14px;
            word-break: break-word;
        }}
        .password-highlight {{
            background-color: #fff3cd;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-weight: 600;
            color: #856404;
        }}
        .alert-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 25px 0;
            border-radius: 8px;
        }}
        .alert-box h3 {{
            color: #856404;
            margin: 0 0 10px 0;
            font-size: 16px;
            font-weight: 600;
        }}
        .alert-box p {{
            color: #856404;
            margin: 0;
            font-size: 14px;
            line-height: 1.6;
        }}
        .steps-box {{
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 25px;
            margin: 25px 0;
        }}
        .steps-box h3 {{
            color: #1A1B41;
            margin: 0 0 15px 0;
            font-size: 16px;
            font-weight: 600;
        }}
        .step {{
            display: flex;
            align-items: flex-start;
            margin: 12px 0;
        }}
        .step-number {{
            background-color: #1A1B41;
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
            flex-shrink: 0;
            margin-right: 12px;
        }}
        .step-text {{
            color: #555555;
            font-size: 14px;
            line-height: 1.6;
            padding-top: 4px;
        }}
        .support-box {{
            background-color: #e8f4f8;
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
            text-align: center;
        }}
        .support-box h3 {{
            color: #1A1B41;
            margin: 0 0 15px 0;
            font-size: 16px;
            font-weight: 600;
        }}
        .support-box p {{
            color: #555555;
            margin: 8px 0;
            font-size: 14px;
        }}
        .support-box a {{
            color: #1A1B41;
            text-decoration: none;
            font-weight: 600;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
        }}
        .footer p {{
            color: #888888;
            font-size: 13px;
            margin: 5px 0;
            line-height: 1.6;
        }}
        .footer-note {{
            color: #999999;
            font-size: 12px;
            margin-top: 15px;
            font-style: italic;
        }}
        @media only screen and (max-width: 600px) {{
            .content {{
                padding: 30px 20px;
            }}
            .info-row {{
                flex-direction: column;
            }}
            .info-label {{
                margin-bottom: 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <h1>🚔 Welcome to Onlook</h1>
            <p>Police Officer Account Created</p>
        </div>
        
        <!-- Content -->
        <div class="content">
            <div class="greeting">
                Dear <strong>{rank} {first_name} {last_name}</strong>,
            </div>
            
            <div class="welcome-text">
                Welcome to the <strong>Onlook System</strong>! Your police officer account has been successfully created. 
                You now have access to our collaborative platform for monitoring and locating missing and cognitively impaired individuals.
            </div>
            
            <!-- Account Details -->
            <div class="info-box">
                <h2>📋 Account Details</h2>
                <div class="info-row">
                    <div class="info-label">Badge Number:</div>
                    <div class="info-value"><strong>{badge_number}</strong></div>
                </div>
                <div class="info-row">
                    <div class="info-label">Email:</div>
                    <div class="info-value">{recipient}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Temporary Password:</div>
                    <div class="info-value"><span class="password-highlight">{badge_number}</span></div>
                </div>
                <div class="info-row">
                    <div class="info-label">Rank:</div>
                    <div class="info-value">{rank}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Station:</div>
                    <div class="info-value">{station}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Role:</div>
                    <div class="info-value">Police Officer</div>
                </div>
            </div>
            
            <!-- Security Alert -->
            <div class="alert-box">
                <h3>⚠️ Important Security Notice</h3>
                <p>
                    For security purposes, please <strong>change your password immediately</strong> after your first login. 
                    Your temporary password is your badge number: <span class="password-highlight">{badge_number}</span>
                </p>
            </div>
            
            <!-- Getting Started -->
            <div class="steps-box">
                <h3>🚀 Getting Started</h3>
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-text">Log in to the Onlook system using your email and temporary password</div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-text">Change your password in your profile settings</div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-text">Complete your profile information</div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-text">Familiarize yourself with the system features</div>
                </div>
            </div>
            
            <!-- Support -->
            <div class="support-box">
                <h3>💬 Need Help?</h3>
                <p>If you have any questions or need assistance, please contact:</p>
                <p><strong>Onlook Support Team</strong></p>
                <p>Email: <a href="mailto:support@onlook.ph">support@onlook.ph</a></p>
                <p>Phone: <a href="tel:+63491234567">+63 (049) 123-4567</a></p>
            </div>
            
            <div class="welcome-text" style="margin-top: 30px;">
                Thank you for your service and dedication to helping locate missing individuals.
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>Best regards,</strong></p>
            <p>Onlook System Administration Team</p>
            <p class="footer-note">This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
    """
    
    subject = "Welcome to Onlook - Police Officer Account Created"

    # Compose the message with both HTML and plain text
    msg = Message(
        subject=subject,
        recipients=[recipient],
        body=text_body,
        html=html_body)    

    # Send the email
    try:
        mail.send(msg)
    except Exception as e:
        message = 'failed'


