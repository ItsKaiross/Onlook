from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify, current_app
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime, timedelta
now = datetime.now()
current_date_time = now
import bcrypt
import math, random
import os
from api.audit import log_audit

registration_bp = Blueprint('registration_bp', __name__)

@registration_bp.route('/register')
def register():
    return render_template('registration/registration.html')

@registration_bp.route('/register-first')
def register_first():
    flash('Please register first.', 'danger')
    return render_template('registration/registration.html')

@registration_bp.route('/signUp', methods=['POST', 'GET'])
def sign_up():
    msg2 = ''
    if request.method == 'POST':
        
        ###################
        ####  N A M E  ####
        ###################
        
        fName = request.form.get('firstName', '')
        mName = request.form.get('middleName', '')
        lName = request.form.get('lastName', '')
        Suffix = request.form.get('Suffix','')
        
        #######################
        ####  G E N D E R  ####
        #######################
        
        gender = request.form.get('gender', '')
        
        ##############################
        ####  B I R T H  D A T E  ####
        ##############################
        
        dateOfBirth_str = request.form.get('dateOfBirth', '')
        dateOfBirth = datetime.strptime(dateOfBirth_str, '%Y-%m-%d').date() if dateOfBirth_str else None
        
        ###########################
        ####  C O N T A C T #  ####
        ###########################
        
        contact_number = request.form.get('contact_number', '').strip()
        
        #########################
        ####  A D D R E S S  ####
        #########################
        
        house_number = request.form.get('houseNumber', '')
        street = request.form.get('street', '')
        brgy = request.form.get('brgy', '')
        city = request.form.get('city', '')
        province = request.form.get('province', '')
        region = request.form.get('region', '')
        address = f"{house_number}, {street}, {brgy}, {city}, {province}, {region}"
        
        #########################
        ####  A C C O U N T  ####
        #########################
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        confirm_password =  request.form.get('confirm_password', '')
        
        ################################
        ####  P R O F I L E  P I C  ####
        ################################
        
        valid_id_files = request.files.getlist('valid_id')
        psa = request.files.get('psa_file')
        profile_picture = request.files.get('profile_picture', '')

        
        
        #####################
        ####  E M A I L  ####
        #####################
        
        recipient = request.form.get('email','')
        
        ######################################
        ####  A C C O U N T  S T A T U S  ####
        ######################################
        
        active = 'active'
        restricted = 'restricted'
        
        created_at = now
        
        # Database connection
        conn = db.get_db_connection()
        
        if conn is None:
            msg2 = 'No database'
            return redirect(url_for('register'))
        
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        cursor.execute('SELECT * FROM accounts WHERE email = %s;', (email,))
        user = cursor.fetchone()
        
        if user is not None:
            flash("Email already exists. Please use another email.", "error")
            return redirect(url_for('public_users'))
        
        else:
            if password == confirm_password:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())\
                    
                    uploaded_validId = []
                    
                    # Process the valid Id

                    validId_id = None
                    for valid_id in valid_id_files:
                        if valid_id and valid_id.filename:
                            validId_filename = secure_filename(valid_id.filename)
                            validId_filetype = valid_id.content_type
                            validId_filedata = valid_id.read()

                            cursor.execute(
                                """
                                INSERT INTO valid_id (valid_id_filename, valid_id_filetype, valid_id_filedata)
                                VALUES (%s, %s, %s)
                                """, (validId_filename, validId_filetype, validId_filedata)
                            )
                            validId_id = cursor.lastrowid

                    # Process PSA upload

                    psa_id = None
                    if psa and psa.filename:
                        psa_filename = secure_filename(psa.filename)
                        psa_filetype = valid_id.content_type
                        psa_filedata = psa.read()

                        cursor.execute(
                            """
                            INSERT INTO psa (psa_filename, psa_filetype, psa_filedata)
                            VALUES (%s, %s, %s)
                            """, (psa_filename, psa_filetype, psa_filedata)
                        )
                        psa_id = cursor.lastrowid
                    
                    # Process image upload
                    
                    profilePicture_id = None
                    if profile_picture and profile_picture.filename:
                        profilePic_filename = secure_filename(profile_picture.filename)
                        profilePic_filetype = profile_picture.content_type
                        profilePic_filedata = profile_picture.read()
                        
                        cursor.execute(
                            """
                            INSERT INTO profile_pictures (profile_filename, profile_filetype, profile_filedata)
                            VALUES (%s, %s, %s)
                            """, (profilePic_filename, profilePic_filetype, profilePic_filedata)
                        )
                        profilePicture_id = cursor.lastrowid
                    
                    # SQL query to insert data on users
                    cursor.execute(
                        """
                        INSERT INTO public_user (
                            first_name,
                            middle_name,
                            last_name,
                            suffix,
                            gender,
                            date_of_birth,
                            contact_number,
                            email,
                            address,
                            house_no,
                            street,
                            barangay,
                            city,
                            province,
                            region,
                            created_at,
                            profile_picture_id,
                            valid_id,
                            psa
                        ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            fName,
                            mName,
                            lName,
                            Suffix,
                            gender,
                            dateOfBirth,
                            contact_number,
                            email,
                            address,
                            house_number,
                            street,
                            brgy,
                            city,
                            province,
                            region,
                            created_at,
                            profilePicture_id,
                            validId_id,
                            psa_id
                        )
                    )
                    
                    user_id = cursor.lastrowid
                    # SQL query to insert data on accounts
                    role = 'user'
                    sqlAccounts = "INSERT INTO accounts (email, password, role, user_id, status, created_at) VALUES (%s, %s, %s, %s, %s, %s);"
                    valuesAccounts = (email, hashed_password, role, user_id, active, created_at)
                    flash("Account registered successfully!", "success")
                    cursor.execute(sqlAccounts, valuesAccounts)
                    accounts_id = cursor.lastrowid
                    
                    # Log user registration audit with proper role
                    log_audit(cursor, module='auth', action='register',
                            target_table='public_user', target_id=user_id,
                            after={'email': email, 'role': 'user', 'name': f'{fName} {lName}'},
                            status='success', remarks=f'New user registered: {fName} {lName} ({email})',
                            override_role='user')
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    sendEmail(recipient=recipient)
                    # Back to html
                    return redirect(url_for('public_users'))
            else:
                flash("Passwords do not match.", "warning")
                return redirect(url_for('public_users'))
            
            


######################################################
#########  S I G N  U P  S E N D  E M A I L  #########
######################################################

def sendEmail(recipient):
    current_app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    current_app.config['MAIL_PORT'] = 587
    current_app.config['MAIL_USE_TLS'] = True
    current_app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USER")
    current_app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASS")  
    current_app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_USER")

    mail = Mail(current_app)

    message_body = """Your registration was successful!
                    Welcome to Onlook. We're excited to have you on board. You can now log in using your credentials and start exploring our services.
                    If you have any questions, feel free to reach out to our support team.
                    Best regards,  
                    Onlook Team"""
    subject = "Registration Successful!"

    # Compose the message
    msg = Message(
        subject=subject,
        recipients=[recipient],
        body=message_body)    

    # Send the email
    try:
        mail.send(msg)
    except Exception as e:
        message = 'failed'
        



