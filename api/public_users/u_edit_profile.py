from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime, date
from api.database import db
import requests
import os
now = datetime.now()
import base64
current_date_time = now
from app import bcrypt
from api.audit import log_audit

############################################
#########  E D I T  P R O F I L E  #########
############################################

@app.route('/edit-profile', methods=['POST', 'GET'])
def public_edit_profile():
    
    user_id = session.get('accounts_id')
    firstName = request.form.get('firstName', '')
    lastName = request.form.get('lastName', '')
    phone = request.form.get('phone', '')
    current_pass = request.form.get('currentPassword', '')
    new_pass = request.form.get('newPassword', '')
    confirm_pass = request.form.get('confirmPassword', '')
    email = request.form.get('email', '')
    
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    profile_picture = request.files.get('profilePic', '')
    
    if request.method == "POST":
        try:
            # Get current profile data for audit before changes
            cursor.execute(
                'SELECT first_name, last_name, contact_number FROM public_user WHERE user_id = (SELECT user_id FROM accounts WHERE accounts_id = %s)',
                (user_id,)
            )
            before_data = cursor.fetchone()
            
            # Check passwords match
            if new_pass and new_pass != confirm_pass:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            # Check uploaded file is an image
            if profile_picture and profile_picture.filename:
                from werkzeug.utils import secure_filename
                
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in profile_picture.filename and profile_picture.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    filename = secure_filename(profile_picture.filename)
                    file_data = profile_picture.read()
                    file_type = profile_picture.content_type
                    
                    # Get user id

                    cursor.execute("SELECT user_id FROM accounts WHERE accounts_id = %s", (user_id,))
                    user = cursor.fetchone()
                    
                    if user is None:
                        raise Exception("User not found")
                    
                    real_user_id = user['user_id']

                    # Update profile picture in database
                    cursor.execute(
                        """
                        SELECT profile_picture_id from public_user WHERE user_id=%s
                        """, (real_user_id,)
                        )
                    result = cursor.fetchone()
                    
                    if result is None or result['profile_picture_id'] is None:
                        cursor.execute(
                            """
                            INSERT INTO profile_pictures (profile_filename, profile_filetype, profile_filedata)
                            VALUES (%s, %s, %s)
                            """, (filename, file_type, file_data)
                            )
                        profilePicture_id = cursor.lastrowid
                        
                        cursor.execute(
                            """
                            UPDATE public_user SET profile_picture_id=%s WHERE user_id = %s
                            """, (profilePicture_id, real_user_id)
                            )
                        conn.commit()
                    else:
                        cursor.execute("""
                            UPDATE profile_pictures SET profile_filedata = %s, profile_filetype = %s 
                            WHERE profile_id = ( SELECT profile_picture_id FROM public_user WHERE user_id = %s)
                        """, (file_data, file_type, real_user_id))
                        conn.commit()   
                else:
                    flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.')
                    return jsonify({'error': 'Invalid file type'}), 400
                
            if current_pass and new_pass:
                
                cursor.execute("SELECT password FROM accounts where accounts_id = %s", (user_id,))
                stored_password = cursor.fetchone()[0]
                
                if not bcrypt.check_password_hash(stored_password, current_pass):
                    cursor.close()
                    conn.close()
                    return jsonify({'error': 'Current password is incorrect'}), 400
                
                if new_pass != confirm_pass:
                    cursor.close()
                    conn.close()
                    return jsonify({'error': 'New passwords do not match'}), 400
                
                hashed_password = bcrypt.generate_password_hash(new_pass).decode('utf-8')
                cursor.execute("UPDATE accounts SET password = %s WHERE accounts_id = %s", (hashed_password, user_id))
                
            cursor.execute(
                """
                UPDATE public_user SET
                first_name = %s, last_name = %s, contact_number = %s
                WHERE user_id = (SELECT user_id from accounts WHERE accounts_id =%s)
                """,
                (firstName, lastName, phone, user_id)
                )
            
            # Log profile update audit
            after_data = {
                'first_name': firstName,
                'last_name': lastName,
                'contact_number': phone
            }
            log_audit(cursor, module='profile', action='update',
                      target_table='public_user', target_id=user_id,
                      before=before_data, after=after_data,
                      status='success', remarks='Public user profile updated')
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # FLASK MAIL CONFIGURATION
            app.config['MAIL_SERVER'] = 'smtp.gmail.com'
            app.config['MAIL_PORT'] = 587
            app.config['MAIL_USE_TLS'] = True
            app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USER")
            app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASS")
            app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_USER")
            
            mail = Mail(app)
            
            subject = "Onlook: Personal Information Updated"

            # Collect updated fields dynamically
            updated_fields = []

            if firstName:
                updated_fields.append(f"<li><strong>First Name:</strong> {firstName}</li>")
            if lastName:
                updated_fields.append(f"<li><strong>Last Name:</strong> {lastName}</li>")
            if phone:
                updated_fields.append(f"<li><strong>Phone Number:</strong> {phone}</li>")
            if profile_picture:
                updated_fields.append(f"<li><strong>Profile Picture:</strong> Updated</li>")
            if new_pass:
                updated_fields.append(f"<li><strong>Password:</strong> Updated</li>")

            # Convert list to HTML string
            updated_fields_html = "".join(updated_fields)

            html_body = f"""
            <div style="font-family: Arial, sans-serif;">
                <p>Dear {firstName or 'User'},</p>

                <p>Your personal information has been successfully updated:</p>

                <ul>
                    {updated_fields_html}
                </ul>

                <p>If you did not make these changes or notice any errors, please contact our support team immediately.</p>

                <p>Thank you for using Onlook!<br>Onlook Team</p>
            </div>
            """
            
            msg = Message(
                subject=subject,
                recipients=[email],
                html=html_body)
            
            
            mail.send(msg)
            
            
            return jsonify({'success': 'Profile Updated Successfully'}), 200
        except Exception as e:
            return jsonify({'error': 'Error Loading Profile'}), 500

    if request.method == "GET":

        try:
        
            cursor.execute("""
                SELECT p.first_name, p.last_name, p.email, p.contact_number,
                pp.profile_filedata, pp.profile_filetype, a.password
                FROM accounts a
                LEFT JOIN public_user p ON a.user_id = p.user_id
                LEFT JOIN profile_pictures pp ON p.profile_picture_id = pp.profile_id
                WHERE a.accounts_id = %s
            """, (user_id,))
        
            profile = cursor.fetchone()
            if profile and profile['profile_filedata']:
                profile['profile_filedata'] = base64.b64encode(profile['profile_filedata']).decode('utf-8')
            cursor.close()
            conn.close()
            
            if not profile:
                return jsonify({'error': 'Profile not found'}), 404
        
            return jsonify(profile)

        except Exception as e:
            return jsonify({'error': 'Error loading profile'}), 500