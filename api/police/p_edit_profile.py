from flask import Blueprint, session, render_template, redirect, url_for, flash, request, jsonify, current_app
from api.database import db
from datetime import datetime
import base64
from flask_mail import Mail, Message
import os
from flask_bcrypt import Bcrypt
from api.audit import log_audit

bcrypt = Bcrypt()

p_edit_profile_bp = Blueprint('p_edit_profile_bp', __name__)

@p_edit_profile_bp.route('/police-edit-profile', methods=['GET', 'POST'])
def police_edit_profile():
    # Check if user is logged in and is police
    if not session.get('loggedIn') or session.get('role') not in ['police', 'policeAdmin', 'alaminos-mps', 'bay-mps', 'binancity-ps', 'cabuyaocity-ps',
                'calambacity-ps', 'calauan-mps', 'cavinti-mps', 'famy-mps',
                'kalayaan-mps', 'liliw-mps', 'sanpablocity-ps', 'santacruz-mps',
                'santarosacity-ps', 'siniloan-mps', 'victoria-mps']:
        flash('Access denied', 'error')
        return redirect(url_for('login_bp.home'))
    
    user_id = session.get('accounts_id')
    conn = db.get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return redirect(url_for('p_edit_profile_bp.police_edit_profile'))
    cursor = conn.cursor(dictionary=True)
    accounts_id = session['accounts_id']
    if not user_id:
        flash('Session expired', 'error')
        return redirect(url_for('login_bp.home'))
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        contact_number = request.form.get('contact_number')
        badge_number = request.form.get('badge_number')
        rank = request.form.get('rank')
        station = request.form.get('station')
        address = request.form.get('address')
        house_number = request.form.get('house_number')
        street = request.form.get('street')
        barangay = request.form.get('barangay')
        city = request.form.get('city')
        province = request.form.get('province')
        region = request.form.get('region')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        profile_picture = request.files.get('profile_picture')
        
        
        # Check uploaded file is an image
        if profile_picture and profile_picture.filename:
            from werkzeug.utils import secure_filename
            
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in profile_picture.filename and profile_picture.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                filename = secure_filename(profile_picture.filename)
                file_data = profile_picture.read()
                file_type = profile_picture.content_type
                
                # Update profile picture in database
                cursor.execute(
                    """
                    SELECT profile_picture_id FROM police WHERE officer_id = %s
                    """, (user_id,)
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
                        UPDATE police SET profile_picture_id = %s WHERE officer_id = %s
                        """, (profilePicture_id, user_id)
                        )
                    conn.commit()
                else:
                    cursor.execute("""
                        UPDATE profile_pictures SET profile_filedata = %s, profile_filetype = %s 
                        WHERE profile_id = (SELECT profile_picture_id FROM police WHERE officer_id = %s)
                    """, (file_data, file_type, user_id))
                    conn.commit()   
            else:
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.')
                return jsonify({'error': 'Invalid file type'}), 400
        
        # Handle password change if provided
        if current_password and new_password:
                        
            # Verify current password
            cursor.execute("SELECT password FROM accounts WHERE accounts_id = %s", (user_id,))
            row = cursor.fetchone()
            if not row:
                flash('Account not found', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('p_edit_profile_bp.police_edit_profile'))
            stored_password = row['password']
            
            if not bcrypt.check_password_hash(stored_password, current_password):
                flash('Current password is incorrect', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('p_edit_profile_bp.police_edit_profile'))
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('p_edit_profile_bp.police_edit_profile'))
            
            # Update password
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            cursor.execute("UPDATE accounts SET password = %s WHERE accounts_id = %s", (hashed_password, user_id))
            flash('Password updated successfully!', 'success')
        
        # Check if police record exists
        cursor.execute("SELECT officer_id FROM police WHERE officer_id = %s", (user_id,))
        police_exists = cursor.fetchone()
        
        if not police_exists:
            flash('Police record not found', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('p_edit_profile_bp.police_edit_profile'))
        
        # Get current profile data for audit before changes
        cursor.execute(
            'SELECT first_name, last_name, middle_name, email, badge_number FROM police WHERE officer_id = %s',
            (user_id,)
        )
        before_data = cursor.fetchone()
        
        # Update police profile directly using accounts_id
        cursor.execute("""
            UPDATE police SET 
            first_name = %s, middle_name = %s, last_name = %s, 
            email = %s, contact_number = %s, address = %s, house_no = %s,
            street = %s, barangay = %s, city = %s, province = %s, region = %s, 
            badge_number = %s, `rank` = %s, station_assignment = %s
            WHERE officer_id = %s
        """, (first_name, middle_name, last_name, email, contact_number, address, house_number, street, barangay, city, province, region, badge_number, rank, station, user_id))
        print(f"DEBUG: Police update affected {cursor.rowcount} rows")
        
        # Update email on accounts
        cursor.execute("""
            UPDATE accounts SET 
            email = %s
            WHERE accounts_id = %s
        """, (email, user_id))
        
        # Log profile update audit
        after_data = {
            'first_name': first_name,
            'last_name': last_name, 
            'middle_name': middle_name,
            'email': email,
            'badge_number': badge_number
        }
        log_audit(cursor, module='profile', action='update',
                  target_table='police', target_id=user_id,
                  before=before_data, after=after_data,
                  status='success', remarks='Police profile updated')
        
        conn.commit()
        
        # FLASK MAIL CONFIGURATION
        current_app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        current_app.config['MAIL_PORT'] = 587
        current_app.config['MAIL_USE_TLS'] = os.environ.get("TLS")
        current_app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USER")
        current_app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASS")
        current_app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_USER")
        
        mail = Mail(current_app)
        
        subject = "Onlook: Personal Information Updated"

        # Collect updated fields dynamically
        updated_fields = []

        if first_name:
            updated_fields.append(f"<li><strong>First Name:</strong> {first_name}</li>")
        if last_name:
            updated_fields.append(f"<li><strong>Last Name:</strong> {last_name}</li>")
        if contact_number:
            updated_fields.append(f"<li><strong>Email:</strong> {contact_number}</li>")
        if email:
            updated_fields.append(f"<li><strong>Email:</strong> {email}</li>")
        if new_password:
            updated_fields.append(f"<li><strong>Password:</strong>Updated</li>")
        if region:
            updated_fields.append(f"<li><strong>Phone Number:</strong> {region}</li>")
        if profile_picture:
            updated_fields.append(f"<li><strong>Profile Picture:</strong> Updated</li>")
        if province:
            updated_fields.append(f"<li><strong>Station:</strong> {province}</li>")
        if city:
            updated_fields.append(f"<li><strong>Rank:</strong> {city}</li>")
        if badge_number:
            updated_fields.append(f"<li><strong>Badge Number:</strong> {badge_number}</li>")

        # Convert list to HTML string
        updated_fields_html = "".join(updated_fields)

        html_body = f"""
        <div style="font-family: Arial, sans-serif;">
            <p>Dear {first_name  or 'Admin'},</p>

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
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('p_edit_profile_bp.police_edit_profile'))
    
    if request.method == 'GET':
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            '''
            SELECT p.first_name, p.last_name, p.middle_name, p.email, p.badge_number,
            p.barangay, p.city, p.province, p.region, p.rank, p.station_assignment, p.street, p.house_no, p.contact_number,
            pp.profile_filedata, pp.profile_filetype
            FROM police p
            LEFT JOIN accounts acc ON p.officer_id = acc.accounts_id
            LEFT JOIN profile_pictures pp ON p.profile_picture_id = pp.profile_id
            WHERE acc.accounts_id = %s
            ''',
            (user_id,)
        )
        profile = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*) as unread FROM case_file cf
            LEFT JOIN police_notifications pn ON cf.case_id = pn.case_id AND pn.police_id = %s
            WHERE cf.date_and_time_reported >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            AND COALESCE(pn.is_read, FALSE) = FALSE
        """, (user_id,))
        notification_count = cursor.fetchone()['unread']

        cursor.close()
        conn.close()

        if profile and profile['profile_filedata']:
            profile['profile_filedata'] = base64.b64encode(profile['profile_filedata']).decode('utf-8')

        return render_template(
            'police/police-base.html',
            page='police-edit-profile',
            profile=profile,
            notification_count=notification_count,
            loggedIn_email=session.get('email')
        )


