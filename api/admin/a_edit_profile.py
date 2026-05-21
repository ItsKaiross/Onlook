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
import json
from api.audit import log_audit

a_edit_profile_bp = Blueprint('a_edit_profile_bp', __name__)

##############################################
#########  E D I T  P R O F I L E  #########
##############################################

@a_edit_profile_bp.route('/admin-edit-profile', methods=['GET', 'POST'])
def admin_edit_profile():
    print(f"DEBUG: Route accessed with method: {request.method}")
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    roles = session.get('role')

    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    if 'accounts_id' not in session:
        print("DEBUG: No accounts_id in session, redirecting to login")
        return redirect(url_for('login_bp.home'))
    
    conn = db.get_db_connection()
    if conn is None:
        flash('Database connection error')
        return redirect(url_for('a_dashboard_bp.admin'))
    
    cursor = conn.cursor(dictionary=True)
    accounts_id = session['accounts_id']
    
    print(f"DEBUG: Session accounts_id: {accounts_id}, User email: {session.get('email')}, Role: {session.get('role')}")
    
    # Test if accounts_id exists
    cursor.execute("SELECT accounts_id, email, role FROM accounts WHERE accounts_id = %s", (accounts_id,))
    account_check = cursor.fetchone()
    print(f"DEBUG: Account check result: {account_check}")
    
    if request.method == 'POST':
        try:
            loggedIn = session.get('loggedIn')
            roles = session.get('role')
            firstName = request.form.get('firstName')
            lastName = request.form.get('lastName')
            middleName = request.form.get('middleName')
            email = request.form.get('email')
            password = request.form.get('pass')
            confirmPassword = request.form.get('confirmPass')
            contactNumber = request.form.get('mobileNumber')
            badgeNumber = request.form.get('badgeNumber')
            rank = request.form.get('rank')
            gender = request.form.get('gender')
            dateOfBirth = request.form.get('dateOfBirth')
            stationAssignment = request.form.get('stationAssignment')
            positionTitle = request.form.get('positionTitle')
            dateJoined = request.form.get('dateJoined')
            barangay = request.form.get('barangay')
            city = request.form.get('city')
            province = request.form.get('province') 
            region = request.form.get('region')
            profile_picture = request.files.get('profile_picture')
            
            # Create combined address from components
            address_components = [barangay, city, province, region]
            address = ', '.join([comp for comp in address_components if comp and comp.strip()])
            
            print(f"DEBUG: Form data received - firstName: {firstName}, email: {email}, contactNumber: {contactNumber}")
            
            # Check if this is a password-only update
            password_only_update = request.form.get('password_only_update') == 'true'
            
            if password_only_update:
                print("DEBUG: Password-only update detected")
                # For password-only updates, we only need password and confirmPassword
                if not password or not confirmPassword:
                    flash('Please provide both password fields!', 'error')
                    return redirect(url_for('a_edit_profile_bp.admin_edit_profile'))
                
                if password != confirmPassword:
                    flash('Passwords do not match!', 'error')
                    return redirect(url_for('a_edit_profile_bp.admin_edit_profile'))
                
                # Update only the password
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute('UPDATE accounts SET password = %s WHERE accounts_id = %s', (hashed_password, accounts_id))
                
                # Log password change audit
                performed_by_name = f"{session.get('firstName', '')} {session.get('lastName', '')}".strip()
                if not performed_by_name or performed_by_name == ' ':
                    performed_by_name = session.get('email', 'Unknown')
                
                cursor.execute(
                    '''INSERT INTO audit_trail (accounts_id, performed_by, performed_role, module, action, 
                        target_table, target_id, before_change, after_change, ip_address, user_agent, 
                        action_timestamp, status, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (session.get('accounts_id'), performed_by_name, session.get('role', 'Unknown'), 
                     'profile', 'password_change', 'accounts', accounts_id, 
                     json.dumps({'action': 'password_change'}, default=str), json.dumps({'action': 'password_updated'}, default=str),
                     request.remote_addr, request.headers.get('User-Agent'), 
                     datetime.now(), 'success', 'Admin password changed')
                )
                
                conn.commit()
                cursor.close()
                conn.close()
                
                flash('Password updated successfully!', 'info')
                return redirect(url_for('a_edit_profile_bp.admin_edit_profile'))
            
            # Regular form validation for non-password-only updates
            if not firstName or not lastName or not email or not badgeNumber or not rank or not gender or not dateOfBirth or not stationAssignment or not positionTitle or not dateJoined:
                flash('Please fill in all required fields!', 'error')
                return redirect(url_for('a_edit_profile_bp.admin_edit_profile'))
            
            # Get current profile data for comparison
            cursor.execute(
                '''SELECT p.first_name, p.last_name, p.middle_name, p.badge_number, p.`rank`, p.gender,
                p.date_of_birth, p.station_assignment, p.position_title, p.date_joined, p.address,
                p.barangay, p.city, p.province, p.region, p.contact_number,
                a.email as account_email, p.email as police_email
                FROM accounts a
                LEFT JOIN police p ON a.officer_id = p.officer_id
                WHERE a.accounts_id = %s''',
                (accounts_id,)
            )
            current_data = cursor.fetchone()
            
            if not current_data:
                flash('Account not found!', 'error')
                return redirect(url_for('a_edit_profile_bp.admin_edit_profile'))
            
            # Create police record if it doesn't exist
            if not current_data['first_name'] and current_data['account_email']:
                cursor.execute("SELECT officer_id FROM accounts WHERE accounts_id = %s", (accounts_id,))
                account_info = cursor.fetchone()
                print(f"DEBUG: Account info for police record creation: {account_info}")
                
                if account_info and account_info['officer_id']:
                    officer_id = account_info['officer_id']
                    # Check if police record already exists
                    cursor.execute("SELECT officer_id FROM police WHERE officer_id = %s", (officer_id,))
                    existing_police = cursor.fetchone()
                    
                    if not existing_police:
                        cursor.execute(
                            """INSERT INTO police (officer_id, email, badge_number, `rank`, first_name, last_name, middle_name,
                               contact_number, barangay, city, province, region, gender, date_of_birth, station_assignment,
                               position_title, date_joined, address, profile_picture_id, status) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (officer_id, email, badgeNumber, rank, firstName, lastName, middleName,
                             contactNumber, barangay, city, province, region, gender, dateOfBirth, stationAssignment,
                             positionTitle, dateJoined, address, None, 'active')
                        )
                        conn.commit()
                        print(f"DEBUG: Created police record for officer_id: {officer_id}")
                    else:
                        print(f"DEBUG: Police record already exists for officer_id: {officer_id}")
                else:
                    # Account doesn't have officer_id, we need to create one
                    print("DEBUG: Account has no officer_id, creating new officer_id")
                    # Generate a new officer_id (you might want to use a specific format)
                    cursor.execute("SELECT MAX(officer_id) as max_id FROM accounts WHERE officer_id IS NOT NULL")
                    max_result = cursor.fetchone()
                    new_officer_id = (max_result['max_id'] or 0) + 1
                    
                    # Update account with new officer_id
                    cursor.execute("UPDATE accounts SET officer_id = %s WHERE accounts_id = %s", (new_officer_id, accounts_id))
                    
                    # Create police record
                    cursor.execute(
                        """INSERT INTO police (officer_id, email, badge_number, `rank`, first_name, last_name, middle_name,
                           contact_number, barangay, city, province, region, gender, date_of_birth, station_assignment,
                           position_title, date_joined, address, profile_picture_id, status) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (new_officer_id, email, badgeNumber, rank, firstName, lastName, middleName,
                         contactNumber, barangay, city, province, region, gender, dateOfBirth, stationAssignment,
                         positionTitle, dateJoined, address, None, 'active')
                    )
                    conn.commit()
                    print(f"DEBUG: Created new officer_id {new_officer_id} and police record")
                
                # Refresh current_data after creating police record
                cursor.execute(
                    '''SELECT p.first_name, p.last_name, p.middle_name, p.badge_number,
                    p.barangay, p.city, p.province, p.region, p.contact_number,
                    a.email as account_email, p.email as police_email
                    FROM accounts a
                    LEFT JOIN police p ON a.officer_id = p.officer_id
                    WHERE a.accounts_id = %s''',
                    (accounts_id,)
                )
                current_data = cursor.fetchone()
                print(f"DEBUG: Refreshed current_data after police record creation: {current_data}")
            
            print(f"DEBUG: Current data from DB: {current_data}")
            print(f"DEBUG: Form data - firstName: '{firstName}', lastName: '{lastName}', email: '{email}', badgeNumber: '{badgeNumber}'")
            print(f"DEBUG: Current DB data - first_name: '{current_data.get('first_name')}', last_name: '{current_data.get('last_name')}', account_email: '{current_data.get('account_email')}', badge_number: '{current_data.get('badge_number')}'")
            
            # Track what actually changed
            changes_made = False
            
            # Helper function to safely compare values (handles None vs empty string)
            def values_different(new_val, old_val):
                # Convert None to empty string for comparison
                new_val = new_val or ''
                old_val = old_val or ''
                result = str(new_val).strip() != str(old_val).strip()
                print(f"DEBUG: Comparing '{new_val}' vs '{old_val}' = {result}")
                return result
            
            # Update accounts table only if email changed
            print(f"DEBUG: Checking email change: '{email}' vs '{current_data.get('account_email')}'")
            if values_different(email, current_data.get('account_email')):
                cursor.execute('UPDATE accounts SET email = %s WHERE accounts_id = %s', (email, accounts_id))
                changes_made = True
                print(f"DEBUG: Email updated from '{current_data.get('account_email')}' to '{email}'")
            else:
                print("DEBUG: No email change detected")
            
            # Handle password update
            if password and confirmPassword:
                if password == confirmPassword:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    cursor.execute('UPDATE accounts SET password = %s WHERE accounts_id = %s', (hashed_password, accounts_id))
                    changes_made = True
                    print("DEBUG: Password updated")
                else:
                    flash('Passwords do not match!', 'error')
                    cursor.close()
                    conn.close()
                    return redirect(url_for('a_edit_profile_bp.admin_edit_profile'))
            
            # Check each field individually for debugging
            print(f"DEBUG: Individual field checks:")
            firstName_changed = values_different(firstName, current_data.get('first_name'))
            lastName_changed = values_different(lastName, current_data.get('last_name'))
            middleName_changed = values_different(middleName, current_data.get('middle_name'))
            email_police_changed = values_different(email, current_data.get('police_email'))
            badgeNumber_changed = values_different(badgeNumber, current_data.get('badge_number'))
            rank_changed = values_different(rank, current_data.get('rank'))
            gender_changed = values_different(gender, current_data.get('gender'))
            dateOfBirth_changed = values_different(dateOfBirth, current_data.get('date_of_birth'))
            stationAssignment_changed = values_different(stationAssignment, current_data.get('station_assignment'))
            positionTitle_changed = values_different(positionTitle, current_data.get('position_title'))
            dateJoined_changed = values_different(dateJoined, current_data.get('date_joined'))
            address_changed = values_different(address, current_data.get('address'))
            
            print(f"DEBUG: firstName changed: {firstName_changed}")
            print(f"DEBUG: lastName changed: {lastName_changed}")
            print(f"DEBUG: middleName changed: {middleName_changed}")
            print(f"DEBUG: email (police) changed: {email_police_changed}")
            print(f"DEBUG: badgeNumber changed: {badgeNumber_changed}")
            
            # Update police table only if basic info changed
            if (firstName_changed or lastName_changed or middleName_changed or email_police_changed or badgeNumber_changed or rank_changed or gender_changed or dateOfBirth_changed or stationAssignment_changed or positionTitle_changed or dateJoined_changed or address_changed):
                
                print(f"DEBUG: Basic info changes detected:")
                print(f"  - firstName: '{current_data.get('first_name')}' -> '{firstName}' (changed: {values_different(firstName, current_data.get('first_name'))})")
                print(f"  - lastName: '{current_data.get('last_name')}' -> '{lastName}' (changed: {values_different(lastName, current_data.get('last_name'))})")
                print(f"  - badgeNumber: '{current_data.get('badge_number')}' -> '{badgeNumber}' (changed: {values_different(badgeNumber, current_data.get('badge_number'))})")
                
                # First check if police record exists and get officer_id
                cursor.execute("SELECT officer_id FROM accounts WHERE accounts_id = %s", (accounts_id,))
                account_info = cursor.fetchone()
                print(f"DEBUG: Account info for police update: {account_info}")
                
                if account_info and account_info['officer_id']:
                    officer_id = account_info['officer_id']
                    
                    # Check if police record exists
                    cursor.execute("SELECT * FROM police WHERE officer_id = %s", (officer_id,))
                    police_record = cursor.fetchone()
                    print(f"DEBUG: Existing police record: {police_record}")
                    
                    if police_record:
                        # Update existing police record
                        update_query = '''UPDATE police SET first_name = %s, last_name = %s, middle_name = %s, 
                                         email = %s, badge_number = %s, `rank` = %s, gender = %s, date_of_birth = %s,
                                         station_assignment = %s, position_title = %s, date_joined = %s, address = %s WHERE officer_id = %s'''
                        cursor.execute(update_query, (firstName, lastName, middleName, email, badgeNumber, rank, gender, 
                                                     dateOfBirth, stationAssignment, positionTitle, dateJoined, address, officer_id))
                        print(f"DEBUG: Updated police record for officer_id {officer_id}")
                        print(f"DEBUG: Rows affected: {cursor.rowcount}")
                    else:
                        # Create new police record
                        insert_query = '''INSERT INTO police (officer_id, first_name, last_name, middle_name, 
                                         email, badge_number, `rank`, contact_number, barangay, city, province, region, gender,
                                         date_of_birth, station_assignment, position_title, date_joined, address, profile_picture_id, status) 
                                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                        cursor.execute(insert_query, (officer_id, firstName, lastName, middleName, email, badgeNumber, rank,
                                                     contactNumber, barangay, city, province, region, gender, dateOfBirth,
                                                     stationAssignment, positionTitle, dateJoined, address, None, 'active'))
                        print(f"DEBUG: Created new police record for officer_id {officer_id}")
                        print(f"DEBUG: Rows affected: {cursor.rowcount}")
                    
                    changes_made = True
                    print("DEBUG: Basic profile info updated in database")
                elif account_info:
                    # Account exists but has no officer_id, create one
                    print("DEBUG: Account has no officer_id, creating new officer_id for police update")
                    cursor.execute("SELECT MAX(officer_id) as max_id FROM accounts WHERE officer_id IS NOT NULL")
                    max_result = cursor.fetchone()
                    new_officer_id = (max_result['max_id'] or 0) + 1
                    
                    # Update account with new officer_id
                    cursor.execute("UPDATE accounts SET officer_id = %s WHERE accounts_id = %s", (new_officer_id, accounts_id))
                    
                    # Create new police record
                    insert_query = '''INSERT INTO police (officer_id, first_name, last_name, middle_name, 
                                     email, badge_number, `rank`, contact_number, barangay, city, province, region, gender,
                                     date_of_birth, station_assignment, position_title, date_joined, address, profile_picture_id, status) 
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                    cursor.execute(insert_query, (new_officer_id, firstName, lastName, middleName, email, badgeNumber, rank,
                                                 contactNumber, barangay, city, province, region, gender, dateOfBirth,
                                                 stationAssignment, positionTitle, dateJoined, address, None, 'active'))
                    print(f"DEBUG: Created new officer_id {new_officer_id} and police record")
                    print(f"DEBUG: Rows affected: {cursor.rowcount}")
                    
                    changes_made = True
                    print("DEBUG: Basic profile info updated in database")
                else:
                    print("DEBUG: No account found, cannot update police table")
            
            else:
                print("DEBUG: No basic info changes detected")
            
            # Update contact number only if changed
            print(f"DEBUG: Checking contact number change: '{contactNumber}' vs '{current_data.get('contact_number')}'")
            if values_different(contactNumber, current_data.get('contact_number')):
                # Get officer_id for contact update
                cursor.execute("SELECT officer_id FROM accounts WHERE accounts_id = %s", (accounts_id,))
                account_info = cursor.fetchone()
                
                if account_info and account_info['officer_id']:
                    cursor.execute(
                        'UPDATE police SET contact_number = %s WHERE officer_id = %s',
                        (contactNumber, account_info['officer_id'])
                    )
                    print(f"DEBUG: Contact number updated from '{current_data.get('contact_number')}' to '{contactNumber}', rows affected: {cursor.rowcount}")
                    changes_made = True
                else:
                    print("DEBUG: No officer_id found for contact update")
            else:
                print("DEBUG: No contact number change detected")
            
            # Update address fields only if changed
            print(f"DEBUG: Checking address changes:")
            barangay_changed = values_different(barangay, current_data.get('barangay'))
            city_changed = values_different(city, current_data.get('city'))
            province_changed = values_different(province, current_data.get('province'))
            region_changed = values_different(region, current_data.get('region'))
            
            if (barangay_changed or city_changed or province_changed or region_changed):
                
                # Get officer_id for address update
                cursor.execute("SELECT officer_id FROM accounts WHERE accounts_id = %s", (accounts_id,))
                account_info = cursor.fetchone()
                
                if account_info and account_info['officer_id']:
                    cursor.execute(
                        'UPDATE police SET barangay = %s, city = %s, province = %s, region = %s WHERE officer_id = %s',
                        (barangay, city, province, region, account_info['officer_id'])
                    )
                    print(f"DEBUG: Address info updated, rows affected: {cursor.rowcount}")
                    changes_made = True
                else:
                    print("DEBUG: No officer_id found for address update")
            else:
                print("DEBUG: No address changes detected")
            
            # Handle profile picture upload
            if profile_picture and profile_picture.filename:
                # Get officer_id for profile picture update
                cursor.execute("SELECT officer_id FROM accounts WHERE accounts_id = %s", (accounts_id,))
                account_info = cursor.fetchone()
                
                if account_info and account_info['officer_id']:
                    # Get current profile_picture_id
                    cursor.execute(
                        'SELECT profile_picture_id FROM police WHERE officer_id = %s',
                        (account_info['officer_id'],)
                    )
                    current_pic = cursor.fetchone()
                    print(f"DEBUG: Current profile picture info: {current_pic}")
                    
                    if current_pic and current_pic['profile_picture_id']:
                        # Update existing profile picture
                        cursor.execute(
                            'UPDATE profile_pictures SET profile_filedata = %s, profile_filename = %s, profile_filetype = %s WHERE profile_id = %s',
                            (profile_picture.read(), profile_picture.filename, profile_picture.content_type, current_pic['profile_picture_id'])
                        )
                        print(f"DEBUG: Updated existing profile picture, rows affected: {cursor.rowcount}")
                    else:
                        # Insert new profile picture
                        cursor.execute(
                            'INSERT INTO profile_pictures (profile_filedata, profile_filename, profile_filetype) VALUES (%s, %s, %s)',
                            (profile_picture.read(), profile_picture.filename, profile_picture.content_type)
                        )
                        profile_id = cursor.lastrowid
                        print(f"DEBUG: Created new profile picture with ID: {profile_id}")
                        
                        # Update police table with new profile picture ID
                        cursor.execute(
                            'UPDATE police SET profile_picture_id = %s WHERE officer_id = %s',
                            (profile_id, account_info['officer_id'])
                        )
                        print(f"DEBUG: Linked profile picture to police record, rows affected: {cursor.rowcount}")
                    
                    changes_made = True
                    print("DEBUG: Profile picture updated")
                else:
                    print("DEBUG: No officer_id found, cannot update profile picture")
            
            # Only proceed with audit and commit if changes were made
            if changes_made:
                # Log profile update audit
                after_data = {
                    'first_name': firstName,
                    'last_name': lastName, 
                    'middle_name': middleName,
                    'email': email,
                    'badge_number': badgeNumber
                }
                
                # Debug session data
                print(f"DEBUG: Session firstName: '{session.get('firstName')}', lastName: '{session.get('lastName')}'")
                print(f"DEBUG: Form firstName: '{firstName}', lastName: '{lastName}'")
                
                # Use form data for performed_by if session data is empty
                performed_by_name = f"{session.get('firstName', '')} {session.get('lastName', '')}".strip()
                if not performed_by_name or performed_by_name == ' ':
                    performed_by_name = f"{firstName} {lastName}".strip() if firstName and lastName else session.get('email', 'Unknown')
                
                print(f"DEBUG: Using performed_by_name: '{performed_by_name}'")
                
                # Insert audit trail directly with the correct name
                cursor.execute(
                    '''INSERT INTO audit_trail (accounts_id, performed_by, performed_role, module, action, 
                        target_table, target_id, before_change, after_change, ip_address, user_agent, 
                        action_timestamp, status, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (session.get('accounts_id'), performed_by_name, session.get('role', 'Unknown'), 
                     'profile', 'update', 'police', accounts_id, 
                     json.dumps(current_data, default=str), json.dumps(after_data, default=str),
                     request.remote_addr, request.headers.get('User-Agent'), 
                     datetime.now(), 'success', 'Admin profile updated')
                )
                
                conn.commit()
                print("DEBUG: Database updates committed successfully")
                
                flash('Profile updated successfully!', 'success')
            else:
                print("DEBUG: No changes detected, skipping update")
                flash('No changes were made to your profile.', 'info')
            
            cursor.close()
            conn.close()

            # Send email notification only if changes were made
            if changes_made:
                try:
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

                    if firstName:
                        updated_fields.append(f"<li><strong>First Name:</strong> {firstName}</li>")
                    if lastName:
                        updated_fields.append(f"<li><strong>Last Name:</strong> {lastName}</li>")
                    if contactNumber:
                        updated_fields.append(f"<li><strong>Contact Number:</strong> {contactNumber}</li>")
                    if email:
                        updated_fields.append(f"<li><strong>Email:</strong> {email}</li>")
                    if password:
                        updated_fields.append(f"<li><strong>Password:</strong> Updated</li>")
                    if profile_picture and profile_picture.filename:
                        updated_fields.append(f"<li><strong>Profile Picture:</strong> Updated</li>")
                    if badgeNumber:
                        updated_fields.append(f"<li><strong>Badge Number:</strong> {badgeNumber}</li>")

                    # Convert list to HTML string
                    updated_fields_html = "".join(updated_fields)

                    html_body = f"""
                    <div style="font-family: Arial, sans-serif;">
                        <p>Dear {firstName or 'Admin'},</p>

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
                    print("DEBUG: Email sent successfully")
                except Exception as e:
                    print(f"DEBUG: Email sending failed: {str(e)}")
                    # Don't fail the whole operation if email fails
                    pass
            
            return redirect(url_for('a_edit_profile_bp.admin_edit_profile'))
            
        except Exception as e:
            print(f"DEBUG: Error in profile update: {str(e)}")
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            flash(f'An error occurred while updating profile: {str(e)}')
            return redirect(url_for('a_edit_profile_bp.admin_edit_profile'))
    
    # GET request - fetch current profile data
    cursor.execute(
        '''SELECT p.first_name, p.last_name, p.middle_name, p.badge_number, p.`rank`, p.gender,
        p.date_of_birth, p.station_assignment, p.position_title, p.date_joined, p.address,
        p.barangay, p.city, p.province, p.region, p.contact_number,
        a.email,
        pp.profile_filedata, pp.profile_filetype
        FROM accounts a
        LEFT JOIN police p ON a.officer_id = p.officer_id
        LEFT JOIN profile_pictures pp ON p.profile_picture_id = pp.profile_id
        WHERE a.accounts_id = %s''',
        (accounts_id,)
    )
    
    profile = cursor.fetchone()
    
    print(f"DEBUG: Raw profile data: {profile}")
    print(f"DEBUG: Profile keys: {profile.keys() if profile else 'No profile'}")
    if profile:
        print(f"DEBUG: Email value: '{profile.get('email')}', First name: '{profile.get('first_name')}', Last name: '{profile.get('last_name')}'")
    
    # Convert profile picture to base64 if it exists
    if profile and profile.get('profile_filedata'):
        try:
            if isinstance(profile['profile_filedata'], bytes):
                profile['profile_filedata'] = base64.b64encode(profile['profile_filedata']).decode('utf-8')
                print(f"DEBUG: Profile picture encoded successfully, type: {profile.get('profile_filetype')}")
        except Exception as e:
            print(f"DEBUG: Error encoding profile picture: {e}")
            profile['profile_filedata'] = None
    
    print(f"DEBUG: Profile data loaded - Name: {profile.get('first_name') if profile else 'None'} {profile.get('last_name') if profile else ''}, Email: {profile.get('email') if profile else 'None'}, Has Picture: {bool(profile and profile.get('profile_filedata'))}")
    
    # If no profile found, just create empty profile structure for template
    if not profile:
        cursor.execute("SELECT email, officer_id FROM accounts WHERE accounts_id = %s", (accounts_id,))
        account_data = cursor.fetchone()
        print(f"DEBUG: Account data for missing profile: {account_data}")
        
        if account_data:
            # Don't create police record during GET, just prepare empty profile for template
            profile = {
                'email': account_data['email'],
                'first_name': None,
                'last_name': None,
                'middle_name': None,
                'badge_number': None,
                'rank': None,
                'contact_number': None,
                'barangay': None,
                'city': None,
                'province': None,
                'region': None,
                'profile_filedata': None,
                'profile_filetype': None
            }
            print(f"DEBUG: Created empty profile structure for template")
        else:
            # No account found at all - this shouldn't happen but handle gracefully
            profile = {
                'email': '',
                'first_name': None,
                'last_name': None,
                'middle_name': None,
                'badge_number': None,
                'rank': None,
                'contact_number': None,
                'barangay': None,
                'city': None,
                'province': None,
                'region': None,
                'profile_filedata': None,
                'profile_filetype': None
            }
            print("DEBUG: No account found, created empty profile")
    
    # Ensure profile has all required fields for template
    if profile and isinstance(profile, dict):
        # Profile is already a dictionary, ensure all fields exist
        required_fields = ['email', 'first_name', 'last_name', 'middle_name', 'badge_number', 'rank',
                          'contact_number', 'barangay', 'city', 'province', 'region', 
                          'profile_filedata', 'profile_filetype']
        for field in required_fields:
            if field not in profile:
                profile[field] = None
    elif profile:
        # Profile is a database row object, convert to dict to ensure consistency
        profile_dict = dict(profile)
        profile = profile_dict
    
    cursor.close()
    conn.close()
    
    print(f"DEBUG: Final profile data being sent to template: {profile}")
    if profile:
        print(f"DEBUG: Profile fields - email: '{profile.get('email')}', first_name: '{profile.get('first_name')}', last_name: '{profile.get('last_name')}', badge_number: '{profile.get('badge_number')}', contact_number: '{profile.get('contact_number')}'")
    
    return render_template(
        'admin/admin-base.html',
        page = 'admin-edit-profile',
        profile=profile,
        loggedIn_email = loggedIn_email,
        roles = roles
        )
    


