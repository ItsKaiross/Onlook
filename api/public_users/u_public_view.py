from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify, current_app
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime, date, timedelta
import requests
import os
now = datetime.now()
import base64
current_date_time = now
from api.utils.activity_logger import log_user_activity
import math, random
from api.audit import log_audit
from api.police.case_history import log_case_status_change

public_view_bp = Blueprint('public_view_bp', __name__)

#######################################################
#########  C O N V E R T   C M  T O  F E E T  #########
#######################################################

def cm_to_feet_inches(cm):
    if not cm:
        return 'Unknown'
    try:
        cm_float = float(cm)
        total_inches = cm_float / 2.54
        feet = int(total_inches // 12)
        inches = int(total_inches % 12)
        return f"{feet}'{inches}\""
    except:
        return 'Unknown'

#####################################################
#########  G E T  L O C A T I O N  N A M E  #########
#####################################################

def get_location_name(lat, lng):
    try:
        if not lat or not lng or lat == 0 or lng == 0:
            return 'Unknown Location'
            
        response = requests.get(os.environ.get('google_api'))
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            # Return the most detailed formatted address (first result)
            formatted_address = data['results'][0]['formatted_address']
            # Remove postal codes and country for cleaner display
            parts = formatted_address.split(', ')
            filtered_parts = [p for p in parts if not p.isdigit() and 'Philippines' not in p]
            return ', '.join(filtered_parts)
            
        return 'Unknown Location'
    except Exception as e:
        print(f"Geocoding error: {e}")
        return 'Unknown Location'

##########################################
#########  P U B L I C  P A G E  #########
##########################################

@public_view_bp.route('/', defaults={'person_id': None})
@public_view_bp.route('/public-view/<int:person_id>')
def public_users(person_id=None):
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    role = session.get('role')
    
    loggedIn_email = None
    user_contact = None
    profile = None
    if loggedIn == True:
        loggedIn_email = userEmail
        user_contact = ''
        
        # Fetch user profile data based on role
        try:
            profile_conn = db.get_db_connection()
            if profile_conn:
                profile_cursor = profile_conn.cursor(dictionary=True)
                
                if role in ['police', 'policeChief'] or (role and (role.endswith('-mps') or role.endswith('-ps'))):
                    profile_cursor.execute("""
                        SELECT pp.profile_filename, pp.profile_filetype, pp.profile_filedata
                        FROM accounts a
                        JOIN police p ON a.user_id = p.user_id
                        LEFT JOIN profile_pictures pp ON p.profile_picture_id = pp.profile_id
                        WHERE a.email = %s
                    """, (userEmail,))
                elif role in ['systemAdmin', 'policeAdmin']:
                    profile_cursor.execute("""
                        SELECT pp.profile_filename, pp.profile_filetype, pp.profile_filedata
                        FROM accounts a
                        JOIN admin ad ON a.user_id = ad.user_id
                        LEFT JOIN profile_pictures pp ON ad.profile_picture_id = pp.profile_id
                        WHERE a.email = %s
                    """, (userEmail,))
                else:
                    profile_cursor.execute("""
                        SELECT pp.profile_filename, pp.profile_filetype, pp.profile_filedata
                        FROM accounts a
                        JOIN public_user pu ON a.user_id = pu.user_id
                        LEFT JOIN profile_pictures pp ON pu.profile_picture_id = pp.profile_id
                        WHERE a.email = %s
                    """, (userEmail,))
                
                profile_data = profile_cursor.fetchone()
                profile_cursor.close()
                profile_conn.close()
                
                if profile_data and profile_data['profile_filedata']:
                    profile = {
                        'profile_filename': profile_data['profile_filename'],
                        'profile_filetype': profile_data['profile_filetype'],
                        'profile_filedata': base64.b64encode(profile_data['profile_filedata']).decode('utf-8')
                    }
        except Exception as e:
            print(f"Error fetching profile: {e}")
    
    # Fetch missing person data from database
    missing_persons = []
    user_accounts_id = None
    if loggedIn:
        # Get user accounts ID
        try:
            acc_conn = db.get_db_connection()
            if acc_conn:
                acc_cursor = acc_conn.cursor(dictionary=True)
                acc_cursor.execute("SELECT accounts_id FROM accounts WHERE email = %s", (userEmail,))
                acc_result = acc_cursor.fetchone()
                if acc_result:
                    user_accounts_id = acc_result['accounts_id']
                    print(f"Logged in user accounts ID: {user_accounts_id}")
                acc_cursor.close()
                acc_conn.close()
        except Exception as e:
            print(f"Error fetching user accounts ID: {e}")
    
    try:
        conn = db.get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT DISTINCT cf.case_id, cf.reporter_type, cf.reporter_id,
                CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name, ' ', IFNULL(mpi.suffix, '')) as full_name,
                mpi.person_id, mpi.nickname, mpi.gender, mpi.date_of_birth, mpi.civil_status, mpi.citizenship, mpi.contact_number,
                TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
                mpi.height, mpi.weight, mpi.hair_color, mpi.eye_color, mpi.distinguishing_mark,
                mpi.occupation, mpi.address, mpi.house_number, mpi.street, mpi.barangay, mpi.city, mpi.province, mpi.region,
                mpls.clothing_description, mpls.circumstances, mpls.date_last_seen, mpls.time_last_seen,
                mpm.missing_filedata, mpm.missing_filetype, mpm.uploaded_at,
                ST_Y(mpl.location) as longitude, ST_X(mpl.location) as latitude,
                mphc.health_type, mphc.health_condition, cf.case_status, cf.approval_status, cf.date_and_time_reported
                FROM case_file cf
                LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
                LEFT JOIN missing_person_information mpi ON mpls.person_id = mpi.person_id
                LEFT JOIN missing_person_health_condition mphc ON mpi.health_condition_id = mphc.missing_person_health_condition_id
                LEFT JOIN missing_person_location mpl ON mpls.missing_person_location_id = mpl.missing_person_location_id
                LEFT JOIN missing_person_media mpm ON mpi.person_id = mpm.missing_person_id
                WHERE cf.approval_status = 'approved' AND mpi.person_id IS NOT NULL
                ORDER BY cf.date_and_time_reported DESC;
            """)
            
            persons = cursor.fetchall()
            processed_persons = set()  # Track processed persons to avoid duplicates
            
            for person in persons:
                person_id = person['person_id']
                
                # Skip if already processed
                if person_id in processed_persons:
                    continue
                processed_persons.add(person_id)
                
                # Get images for this person
                cursor.execute("""
                    SELECT missing_filedata, missing_filetype
                    FROM missing_person_media 
                    WHERE missing_person_id = %s 
                    AND missing_filedata IS NOT NULL 
                    AND (is_archived IS NULL OR is_archived = 0)
                    ORDER BY uploaded_at ASC
                """, (person_id,))
                
                images_data = cursor.fetchall()
                person_images = []
                
                for img in images_data:
                    if img['missing_filedata']:
                        try:
                            img_data = base64.b64encode(img['missing_filedata']).decode('utf-8')
                            img_src = f"data:{img['missing_filetype']};base64,{img_data}"
                            person_images.append(img_src)
                        except Exception as e:
                            continue
                
                if person_images:
                    pass
                else:
                    person_images.append("../static/images/public_page/missing.jpg")
                
                # Check if this person was reported by the logged-in user
                is_reported_by_user = False
                if user_accounts_id and person['reporter_type'] == 'user' and person['reporter_id'] == user_accounts_id:
                    is_reported_by_user = True
                
                print(f"Person {person_id}: reporter_type={person['reporter_type']}, reporter_id={person['reporter_id']}, user_accounts_id={user_accounts_id}, is_reported_by_user={is_reported_by_user}")
                
                missing_persons.append({
                    'id': person_id,
                    'name': person['full_name'],
                    'age': person['age'],
                    'gender': person['gender'],
                    'birthdate': person['date_of_birth'].strftime('%B %d, %Y') if person['date_of_birth'] else 'Unknown',
                    'last_seen': person['date_last_seen'].strftime('%B %d, %Y') if person['date_last_seen'] else 'Unknown',
                    'image': person_images[0],
                    'case_id': person['case_id'],
                    'all_images': person_images,
                    'is_reported_by_user': is_reported_by_user
                })
            
            # Get selected person data if person_id is provided
            if person_id:
                cursor.execute("""
                    SELECT 
                    CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name) as full_name,
                    TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
                    mpi.gender, mpi.date_of_birth, mpls.date_last_seen, mpls.time_last_seen,
                    mpi.height, mpi.weight, mpi.hair_color, mpls.clothing_description as last_seen_clothes, 
                    mpi.eye_color, ST_Y(mpl.location) as longitude, ST_X(mpl.location) as latitude,
                    mphc.health_type, mphc.health_condition
                    FROM case_file cf
                    LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
                    LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
                    LEFT JOIN missing_person_health_condition mphc ON mpi.health_condition_id = mphc.missing_person_health_condition_id
                    LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
                    LEFT JOIN missing_person_location mpl ON mpls.missing_person_location_id = mpl.missing_person_location_id
                    WHERE mpi.person_id = %s
                """, (person_id,))
                
                person = cursor.fetchone()
                if person:
                    
                    # Get all images for this person
                    cursor.execute("""
                        SELECT missing_filedata, missing_filetype, uploaded_at
                        FROM missing_person_media 
                        WHERE missing_person_id = %s 
                        AND missing_filedata IS NOT NULL 
                        AND (is_archived IS NULL OR is_archived = 0)
                        ORDER BY uploaded_at ASC
                    """, (person_id,))
                    
                    all_images = cursor.fetchall()
                    person_images = []
                    
                    if all_images:
                        for img in all_images:
                            if img['missing_filedata'] and len(img['missing_filedata']) > 0:
                                try:
                                    image_data = base64.b64encode(img['missing_filedata']).decode('utf-8')
                                    image_src = f"data:{img['missing_filetype']};base64,{image_data}"
                                    person_images.append(image_src)
                                except Exception as e:
                                    print(f"Error encoding image for person {person_id}: {e}")
                                    continue
                    
                    # Use first image as main image or fallback
                    main_image = person_images[0] if person_images else 'static/images/public_page/missing.jpg'
                        
                    # Validate and debug location data
                    lat = person['latitude']
                    lng = person['longitude']
                    
                    # Validate and potentially swap coordinate ranges
                    if lat and lng and lat != 0 and lng != 0:
                        # Check if coordinates are swapped (latitude in longitude range)
                        if not (-90 <= lat <= 90) and (-90 <= lng <= 90):
                            # Swap coordinates
                            lat, lng = lng, lat
                        
                        # Validate final coordinates
                        if (-90 <= lat <= 90) and (-180 <= lng <= 180):
                            try:
                                location_name = get_location_name(lat, lng)
                            except Exception as e:
                                print(f"Error getting location: {e}")
                                location_name = 'Laguna, Philippines'  # Fallback on error
                        else:
                            print(f"Still invalid coordinates - Latitude: {lat}, Longitude: {lng} - using fallback")
                            location_name = 'Laguna, Philippines'  # Fallback for invalid coordinates
                    else:
                        print(f"No coordinates available - using fallback")
                        location_name = 'Laguna, Philippines'  # Fallback for missing coordinates
                        
                    # Get time last seen
                    time_last_seen = person.get('time_last_seen')
                    time_display = time_last_seen.strftime('%I:%M%p') if time_last_seen else 'Unknown'
                    
                    selected_person = {
                        'name': person['full_name'] or 'Unknown',
                        'age': person['age'] or 'Unknown',
                        'gender': person['gender'] or 'Unknown',
                        'height': cm_to_feet_inches(person['height']) if person['height'] else 'Unknown',
                        'hair_color': person['hair_color'] or 'Unknown',
                        'last_seen_attire': person['last_seen_clothes'] or 'Unknown',
                        'eye_color': person['eye_color'] or 'Unknown',
                        'location': time_display,  # Actual time from database
                        'missing_from': location_name,  # Raw Google Maps location
                        'last_seen': person['date_last_seen'].strftime('%B %d, %Y') if person['date_last_seen'] else 'Unknown',
                        'image': main_image,
                        'all_images': person_images
                    }
                    
                    cursor.close()
                    conn.close()
                    
                    return render_template(
                        'public_users/1u-public_view.html', 
                        loggedIn_email=loggedIn_email,
                        user_contact=user_contact,
                        missing_persons=missing_persons,
                        selected_person=selected_person,
                        role=role,
                        profile=profile
                    )
            cursor.close()
            conn.close()
            
            print(f"Total missing persons fetched: {len(missing_persons)}")
            for person in missing_persons:
                print(f"  - {person['name']} (ID: {person['id']}, is_reported_by_user: {person['is_reported_by_user']})")
    except Exception as e:
        print(f"Error fetching missing persons: {e}")
    
    # If we reach here, we're on the home page (no person_id) or person not found
    return render_template(
        'public_users/1u-public_view.html', 
        loggedIn_email=loggedIn_email,
        user_contact=user_contact,
        missing_persons=missing_persons,
        role=role,
        profile=profile
    )

###########################
#########  2 F A  #########
###########################

@public_view_bp.route('/is-verified')
def isVerified():
    emailVerify = session.get('email')
    if emailVerify is not None:
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({"status": "error"})
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT isVerified from accounts WHERE email=%s', (emailVerify,))
            account = cursor.fetchone()
            
            if account is not None:
                is_verified = account['isVerified'] == 1
                return jsonify({"verified": is_verified})
            return jsonify({"verified": False})
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error"})


def generateOTP():
    random_pass = '0123456789'
    length = len(random_pass)
    OneTimePass = ''
    
    for i in range(6):
        OneTimePass += random_pass[math.floor(random.random() * length)]
        
    return OneTimePass


def send_email(recipient, code):
    try:
        # FLASK MAIL CONFIGURATION
        current_app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        current_app.config['MAIL_PORT'] = 587
        current_app.config['MAIL_USE_TLS'] = True
        current_app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USER")
        current_app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASS")
        current_app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_USER")
        
        mail = Mail(current_app)
        
        subject = "Onlook One-Time Password";
        html_body = f"""
        <div style="font-family: Arial, sans-serif;">
            <p>Your One-Time Password (OTP):</p>

            <h1 style="font-size: 48px; letter-spacing: 4px; margin: 20px 0;">
                {code}
            </h1>

            <p>Please use this OTP to complete your registration.</p>
            <p>If you did not request this OTP, please ignore this email.</p>
            <p>Thank you for using Onlook!<br>Onlook Team</p>
        </div>
        """
        
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=html_body)
        
        
        mail.send(msg)
        return True
    except:
        return False
    
# Send code
@public_view_bp.route('/send_code', methods=["POST"])
def email_code():
    # Get email from session (logged-in user)
    email = session.get('email')
    
    if not email:
        print("No email in session")
        return jsonify({"status": "error", "msg": "User not logged in"})
    
    code = generateOTP()
    
    #Save code + expiration
    session["2fa_email"] = email
    session["2fa_code"] = str(code)  # Store as string
    session["2fa_expiration"] = (datetime.now() + timedelta(minutes=5)).timestamp()
    
    print(f"Generated code for {email}: {code}")
    
    # Send email
    sent = send_email(email, code)
    
    if not sent:
        print("Failed to send email")
        return jsonify({"status": "error", "msg": "Failed to send email"})
    
    print("Email sent successfully")
    return jsonify({"status": "sent", "msg": "Email sent successfully"})


# Verify code
@public_view_bp.route("/verify_2fa", methods=["POST"])
def verify_2fa():
    data = request.json
    user_code = str(data.get('code', '')).strip()  # Convert to string and trim
    
    real_code = str(session.get("2fa_code", '')).strip()  # Convert to string and trim
    expiration = session.get("2fa_expiration")
    mfa_email = session.get("2fa_email")
    
    print(f"Verifying code - User entered: '{user_code}', Expected: '{real_code}'")
    
    if not real_code:
        print("No code stored in session")
        return jsonify({"status": "error", "msg": "No code stored"})
    
    if not expiration:
        print("No expiration stored in session")
        return jsonify({"status": "error", "msg": "No expiration stored"})
    
    if datetime.now().timestamp() > expiration:
        print("Code expired")
        return jsonify({"status": "expired", "msg": "Code has expired"})
    
    if user_code == real_code:
        print("Code verified successfully")
        session.pop("2fa_code", None)
        session.pop("2fa_expiration", None)
        # Database connection
        conn = db.get_db_connection()
        if conn is None:
            flash('Database connection failed.', 'danger')
            return jsonify({"status": "error", "msg": "Database connection failed"})
        cursor = conn.cursor(dictionary=True)
        cursor.execute('UPDATE accounts set isVerified=1 WHERE email=%s', (mfa_email,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "ok"})
    
    print(f"Invalid code - codes don't match")
    return jsonify({"status": "invalid", "msg": "Invalid code"})

# Resend code
@public_view_bp.route("/resend_2fa", methods=["POST"])
def resend_code():
    email = session.get("2fa_email")
    
    if not email:
        return jsonify({"status": "error", "msg": "Email missing"})
    
    code = generateOTP()
    
    session["2fa_code"] = str(code)  # Store as string
    session["2fa_expiration"] = (datetime.now() + timedelta(minutes=5)).timestamp()
    
    print(f"Resent 2FA code to {email}: {code}")
    
    sent = send_email(email, code)
    
    if not sent:
        return jsonify({"status": "error"})
    
    return jsonify({"status": "sent"})



############################################
####  R E P O R T  S U B M I S S I O N  ####
############################################

@public_view_bp.route('/submit-report', methods=['POST', 'GET'])
def submit_report():
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = {
                'firstName': request.form.get('firstName', ''),
                'lastName': request.form.get('lastName', ''),
                'gender': request.form.get('gender', ''),
                'dob': request.form.get('dob', ''),
                'lastSeen': request.form.get('lastSeen', '')
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value.strip()]
            if missing_fields:
                flash(f'Please fill in all required fields: {", ".join(missing_fields)}', 'error')
                return redirect(url_for('public_view_bp.public_users'))
            
            # Validate image upload - support multiple files
            imageOfMissing = request.files.get('upload_last_seen', '')
            additional_images = request.files.getlist('additional_images')
            
            # Check if at least one image is uploaded
            has_main_image = imageOfMissing and imageOfMissing.filename
            has_additional_images = any(img.filename for img in additional_images)
            
            if not has_main_image and not has_additional_images:
                flash('Please upload at least one photo of the missing person.', 'error')
                return redirect(url_for('public_view_bp.public_users'))
            
            userEmail = session.get('email')
            loggedIn = session.get('loggedIn')
            
            ######################################
            ####  M I S S I N G  P E R S O N  ####
            ######################################
            
            ###################
            ####  N A M E  ####
            ###################
            
            firstName = request.form.get('firstName', '')
            middleName = request.form.get('middleName', '')
            lastName = request.form.get('lastName', '')
            suffix = request.form.get('suffix', '')
            nickname = request.form.get('nickname', '')
            
            #######################
            ####  G E N D E R  ####
            #######################
            
            gender = request.form.get('gender', '')
            
            ###########################
            ####  B I T H D A T E  ####
            ###########################
            
            birthdate_str = request.form.get('dob', '')
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date() if birthdate_str else None
            
            ##################################
            ####  C I V I L  S T A T U S  ####
            ##################################
            
            civil_status = request.form.get('civilStatus', '')
            
            #################################
            ####  C I T I Z E N S H I P  ####
            #################################
            
            citizenship = request.form.get('citizenship', '')
            
            ######################################
            ####  C O N T A C T  N U M B E R  ####
            ######################################
            
            contact_number = request.form.get('contact_number', '')
            
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
            
            
            ##########################################
            ####  A D D I T I O N A L  F I L E S  ####
            ##########################################
            
            additional_files = request.files.getlist('additional_files')
            
            #######################
            ####  H E A L T H  ####
            #######################
            
            healthType = request.form.get('health_type_dropdown', '')
            health_desc = request.form.get('health_description', '')
            
            ##################################################
            ####  P H Y S I C A L  D E S C R I P T I O N  ####
            ##################################################
            
            hair_color = request.form.get('hair_color', '')
            eye_color = request.form.get('eye_color', '')
            height = request.form.get('height', '')
            weight = float(request.form.get('weight', None)) if request.form.get('weight') else None
            distinguish_mark = request.form.get('distinguish', '')
            last_seen_attire = request.form.get('attire', '')
            occupation = request.form.get('occupation', '')
            
            ###########################################
            ####  T I M E  A N D  L O C A T I O N  ####
            ###########################################
            
            lastSeen = request.form.get('lastSeen', '')
            dateLastSeen = datetime.strptime(lastSeen, '%Y-%m-%d').date() if lastSeen else None
            timeLastSeen_str = request.form.get('timeLastSeen', '')
            timeLastSeen = datetime.strptime(timeLastSeen_str, '%H:%M').time() if timeLastSeen_str else None
            submitted_at = now
            circumstances = request.form.get('circumstances', '')
            
            #####################
            ####  I M A G E  ####
            #####################
            
            imageOfMissing = request.files.get('upload_last_seen', '')
            
            #####################################################
            ####  L O N G I T U D E  A N D  L A T I T U D E  ####
            #####################################################
            
            # Get location selection type
            location_type = request.form.get('locLastSeen', '')
            custom_location = request.form.get('customLoc', '')
            
            # Handle coordinates based on location selection
            if location_type == 'my-location':
                # Use coordinates from user's current location
                latitude = float(request.form.get('latitude', '0'))
                longitude = float(request.form.get('longitude', '0'))
            elif location_type == 'custom-location' and custom_location:
                # Use coordinates from custom location search
                latitude = float(request.form.get('latitude', '0'))
                longitude = float(request.form.get('longitude', '0'))
            else:
                # Fallback to default coordinates if no valid selection
                latitude = 0.0
                longitude = 0.0
            
            # Validate coordinate ranges
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                # Invalid coordinates, use default for Laguna, Philippines
                latitude = 14.2691
                longitude = 121.4577
            
            # Ensure coordinates are not zero
            if latitude == 0 and longitude == 0:
                # Set default coordinates for Laguna, Philippines
                latitude = 14.2691
                longitude = 121.4577
            
            locationPoint = f'POINT({latitude} {longitude})' ####  L O C A T I O N  P O I N T  ####
            
            #############################
            ####  I N F O R M A N T  ####
            #############################
            
            informant_firstName =  request.form.get('FirstName', '')
            informant_lastName = request.form.get('LastName', '')
            informant_middleName = request.form.get('MiddleName', '')
            
            #######################
            ####  G E N D E R  ####
            #######################
            
            informant_gender = request.form.get('gender', '')
            
            ###################################
            ####  R E L A T I O N S H I P  ####
            ###################################
            
            relationship = request.form.get('relation', '')
            
            #########################
            ####  C O N T A C T  ####
            #########################
            
            informant_contact_number = request.form.get('ContactNumber', '')
            
            #####################
            ####  E M A I L  ####
            #####################
            
            informant_email = request.form.get('informantEmail', '')
            
            #########################
            ####  A D D R E S S  ####
            #########################
            
            informant_house_number = request.form.get('informant_houseNo', '')
            informant_street = request.form.get('informant_street', '')
            informant_brgy = request.form.get('informant_brgy', '')
            informant_city = request.form.get('icity', '')
            informant_province = request.form.get('iprovince', '')
            informant_region = request.form.get('iregion', '')
            informant_address = f"{informant_house_number}, {informant_street}, {informant_brgy}, {informant_city}, {informant_province}, {informant_region}"
            
            
            # Database connection
            conn = db.get_db_connection()
            
            if conn is None:
                print('Database connection failed')
                flash('Database connection failed. Please try again later.', 'error')
                return redirect(url_for('public_view_bp.public_users'))
            
            cursor = conn.cursor(dictionary=True, buffered=True)
            print(f"Database connection successful. Processing report for: {firstName} {lastName}")
            
            # Additional debugging
            print(f"Form data received:")
            print(f"- Name: {firstName} {middleName} {lastName}")
            print(f"- Gender: {gender}")
            print(f"- DOB: {birthdate}")
            print(f"- Contact: {contact_number}")
            print(f"- Image uploaded: {bool(imageOfMissing and imageOfMissing.filename)}")
            print(f"- Location: {latitude}, {longitude}")# Database insert
            
            
            # Health Condition
            cursor.execute(
                """
                INSERT INTO missing_person_health_condition
                (
                    first_name,
                    middle_name,
                    last_name,
                    health_type,
                    health_condition
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    firstName,
                    middleName,
                    lastName,
                    healthType,
                    health_desc
                )
                )
            
            healthCondition_id = cursor.lastrowid
            
            # Missing Person Information
            cursor.execute(
                """
                INSERT INTO missing_person_information
                (
                    health_condition_id,
                    first_name,
                    middle_name,
                    last_name,
                    suffix,
                    nickname,
                    gender,
                    date_of_birth,
                    civil_status,
                    citizenship,
                    contact_number,
                    height,
                    weight,
                    hair_color,
                    eye_color,
                    distinguishing_mark,
                    occupation,
                    address,
                    house_number,
                    street,
                    barangay,
                    city,
                    province,
                    region
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    healthCondition_id,
                    firstName,
                    middleName,
                    lastName,
                    suffix,
                    nickname,
                    gender,
                    birthdate,
                    civil_status,
                    citizenship,
                    contact_number,
                    height,
                    weight,
                    hair_color,
                    eye_color,
                    distinguish_mark,
                    occupation,
                    address,
                    house_number,
                    street,
                    brgy,
                    city,
                    province,
                    region
                )
                )
            
            person_id = cursor.lastrowid
            # Missing person location
            cursor.execute("""
                INSERT INTO missing_person_location (location)
                VALUES (ST_GeomfromText(%s, 4326))
                """, (locationPoint, )
                )
            
            lastLocation_id = cursor.lastrowid
            
            # Process multiple image uploads
            reportMedia_id = None
            uploaded_images = []
            
            # Collect all images to upload
            images_to_process = []
            if imageOfMissing and imageOfMissing.filename:
                images_to_process.append(imageOfMissing)
            images_to_process.extend([img for img in additional_images if img.filename])
            
            # Process each image
            for idx, image_file in enumerate(images_to_process):
                try:
                    img_filename = secure_filename(image_file.filename)
                    img_filetype = image_file.content_type
                    img_filedata = image_file.read()

                    # Validate file type
                    if img_filetype not in ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']:
                        flash(f'Invalid file type for {img_filename}. Please upload JPEG, PNG, or GIF files only.', 'error')
                        cursor.close()
                        conn.close()
                        return redirect(url_for('public_view_bp.public_users'))
                    
                    # Validate file size (max 5MB)
                    if len(img_filedata) > 5 * 1024 * 1024:
                        flash(f'File {img_filename} is too large. Please upload files smaller than 5MB.', 'error')
                        cursor.close()
                        conn.close()
                        return redirect(url_for('public_view_bp.public_users'))

                    print(f"Processing image {idx+1}: {img_filename}, type: {img_filetype}, size: {len(img_filedata)} bytes")

                    # Missing Person Media
                    cursor.execute(
                        """
                        INSERT INTO missing_person_media
                        (
                            missing_person_id,
                            missing_filename,
                            missing_filetype,
                            missing_filedata,
                            uploaded_at
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """, (
                            person_id,
                            img_filename,
                            img_filetype,
                            img_filedata,
                            submitted_at
                        )
                    )   

                    media_id = cursor.lastrowid
                    uploaded_images.append(media_id)
                    
                    # Use first uploaded image as the main reportMedia_id
                    if idx == 0:
                        reportMedia_id = media_id
                    
                    print(f"Image {idx+1} uploaded successfully with ID: {media_id}")
                    
                except Exception as img_error:
                    print(f"Error processing image {idx+1}: {str(img_error)}")
                    flash(f'Error processing image {img_filename}. Please try a different image.', 'error')
                    cursor.close()
                    conn.close()
                    return redirect(url_for('public_view_bp.public_users'))
            
            print(f"Total images uploaded: {len(uploaded_images)}")
            
            # Process additional files
            additionalFiles_id = None
            for file in additional_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filetype = file.content_type
                    filedata = file.read()
                    # Missing Person Additional Files
                    cursor.execute(
                        """
                        INSERT INTO missing_person_additional_files
                        (
                            missing_person_info_id,
                            file_name,
                            file_type,
                            file_data
                            )
                        VALUES (%s, %s, %s, %s)
                        """, (
                            person_id,
                            filename,
                            filetype,
                            filedata
                            )
                    )
                    additionalFiles_id = cursor.lastrowid
            
            cursor.execute(
                """
                INSERT INTO missing_person_last_seen
                (
                    person_id,
                    missing_person_location_id,
                    date_last_seen,
                    time_last_seen,
                    clothing_description,
                    circumstances
                )
                VALUES
                (
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    person_id,
                    lastLocation_id,
                    dateLastSeen,
                    timeLastSeen,
                    last_seen_attire,
                    circumstances
                )
            )
            
            missing_person_last_seen = cursor.lastrowid
            
            approval_status = 'pending'
            case_status = 'Open'
            priority = 'medium'
            conn.commit()
            # If user is logged in
            if loggedIn == True:
                withAccounts_id = session.get('accounts_id', '')
                
                # Case File
                cursor.execute(
                    """
                    INSERT INTO case_file
                    (
                        reporter_type,
                        reporter_id,
                        approval_status,
                        case_status,
                        priority,
                        date_and_time_reported,
                        last_updated,
                        notes,
                        last_seen_id,
                        media_id,
                        additional_files_id
                    )
                    VALUES
                    ('user', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        withAccounts_id,
                        approval_status,
                        case_status,
                        priority,
                        submitted_at,
                        submitted_at,
                        '',
                        missing_person_last_seen,
                        reportMedia_id,
                        additionalFiles_id
                    )
                )
                
                case_id = cursor.lastrowid
                
                # Log case history for new case creation
                log_case_status_change(
                    cursor,
                    case_id=case_id,
                    previous_status=None,
                    new_status=case_status,
                    previous_approval=None,
                    new_approval=approval_status,
                    notes=f'Case created for missing person: {firstName} {lastName}'
                )
                
                # Log audit for case creation
                log_audit(cursor, module='case_file', action='create',
                          target_table='case_file', target_id=case_id,
                          after={'reporter_type': 'user', 'reporter_id': withAccounts_id, 
                                'person_name': f'{firstName} {lastName}', 'approval_status': approval_status})
                
                conn.commit()
                log_user_activity('report_missing_person', 'success', f'{{"person_name": "{firstName} {lastName}"}}', withAccounts_id)
                cursor.close()
                conn.close()
                flash('Report submitted successfully!')
                return redirect(url_for('public_view_bp.public_users'))
            # If user is not logged in
            else:
                
                # No Account
                cursor.execute(
                    """
                    INSERT INTO no_account_user
                    (
                        first_name,
                        middle_name,
                        last_name,
                        gender,
                        contact_number,
                        email,
                        address,
                        house_no,
                        street,
                        barangay,
                        city,
                        province,
                        region,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        informant_firstName,
                        informant_middleName,
                        informant_lastName,
                        informant_gender,
                        informant_contact_number,
                        informant_email,
                        informant_address,
                        informant_house_number,
                        informant_street,
                        informant_brgy,
                        informant_city,
                        informant_province,
                        informant_region,
                        submitted_at
                    )
                )
                
                noAccounts_id = cursor.lastrowid
                
                # Case File
                cursor.execute(
                    """
                    INSERT INTO case_file
                    (
                        reporter_type,
                        reporter_id,
                        approval_status,
                        case_status,
                        priority,
                        date_and_time_reported,
                        last_updated,
                        notes,
                        last_seen_id,
                        media_id,
                        additional_files_id
                    )
                    VALUES
                    ('no_account', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        noAccounts_id,
                        approval_status,
                        case_status,
                        priority,
                        submitted_at,
                        submitted_at,
                        '',
                        missing_person_last_seen,
                        reportMedia_id,
                        additionalFiles_id
                    )
                )
                
                case_id = cursor.lastrowid
                
                # Log case history for new case creation
                log_case_status_change(
                    cursor,
                    case_id=case_id,
                    previous_status=None,
                    new_status=case_status,
                    previous_approval=None,
                    new_approval=approval_status,
                    notes=f'Case created for missing person: {firstName} {lastName} by non-account user'
                )
                
                # Log audit for case creation by non-account user
                log_audit(cursor, module='case_file', action='create',
                          target_table='case_file', target_id=case_id,
                          after={'reporter_type': 'no_account', 'reporter_id': noAccounts_id,
                                'person_name': f'{firstName} {lastName}', 'approval_status': approval_status,
                                'informant_email': informant_email})
                
                conn.commit()
                cursor.close()
                conn.close()
                flash('Report submitted successfully!')
                return redirect(url_for('public_view_bp.public_users'))
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.rollback()
                if 'cursor' in locals() and cursor:
                    cursor.close()
                conn.close()
            print(f'Error submitting report: {str(e)}')
            import traceback
            traceback.print_exc()
            flash('Error submitting report. Please try again.', 'error')
            return redirect(url_for('public_view_bp.public_users'))
    
    return redirect(url_for('public_view_bp.public_users'))


###################################################################
#########  G E T  T H E   R E P O R T E D  P E R S O N S  #########
###################################################################

@public_view_bp.route('/get-person-data/<int:person_id>')
def get_person_data(person_id):
    try:
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'error': 'Database connection failed'})
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name, ' ', IFNULL(mpi.suffix, '')) as full_name,
            mpi.person_id, mpi.nickname, mpi.gender, mpi.date_of_birth, mpi.civil_status, mpi.citizenship, mpi.contact_number,
            TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
            mpi.height, mpi.weight, mpi.hair_color, mpi.eye_color, mpi.distinguishing_mark,
            mpi.occupation, mpi.address, mpi.house_number, mpi.street, mpi.barangay, mpi.city, mpi.province, mpi.region,
            mpls.clothing_description as last_seen_clothes, mpls.circumstances, mpls.date_last_seen, mpls.time_last_seen,
            ST_Y(mpl.location) as longitude, ST_X(mpl.location) as latitude,
            mphc.health_type, mphc.health_condition, cf.case_status, cf.approval_status, cf.date_and_time_reported
            FROM case_file cf
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            LEFT JOIN missing_person_information mpi ON mpls.person_id = mpi.person_id
            LEFT JOIN missing_person_health_condition mphc ON mpi.health_condition_id = mphc.missing_person_health_condition_id
            LEFT JOIN missing_person_location mpl ON mpls.missing_person_location_id = mpl.missing_person_location_id
            WHERE mpi.person_id = %s
        """, (person_id,))
        
        person = cursor.fetchone()
        cursor.close()
        conn.close()
        
        
        if person:
            import base64
            
            # Get all images for this person
            conn2 = db.get_db_connection()
            cursor2 = conn2.cursor(dictionary=True)
            cursor2.execute("""
                SELECT missing_filedata, missing_filetype, uploaded_at
                FROM missing_person_media 
                WHERE missing_person_id = %s 
                AND missing_filedata IS NOT NULL 
                AND (is_archived IS NULL OR is_archived = 0)
                ORDER BY uploaded_at ASC
            """, (person_id,))
            
            all_images_data = cursor2.fetchall()
            cursor2.close()
            conn2.close()
            
            person_images = []
            
            if all_images_data:
                for img in all_images_data:
                    if img['missing_filedata'] and len(img['missing_filedata']) > 0:
                        try:
                            image_data = base64.b64encode(img['missing_filedata']).decode('utf-8')
                            image_src = f"data:{img['missing_filetype']};base64,{image_data}"
                            person_images.append(image_src)
                        except Exception as e:
                            print(f"Error encoding image in get_person_data for person {person_id}: {e}")
                            continue
            
            # Use first image as main image or fallback
            main_image = person_images[0] if person_images else 'static/images/public_page/missing.jpg'
                
            # Get coordinates from database
            lat = person['latitude']
            lng = person['longitude']
            location_name = 'Main Street, Barangay Batong Malake, Los Baños, Laguna'
            
            if lat and lng and lat != 0 and lng != 0:
                if not (-90 <= lat <= 90) and (-90 <= lng <= 90):
                    lat, lng = lng, lat
                
                if (-90 <= lat <= 90) and (-180 <= lng <= 180):
                    try:
                        api_location = get_location_name(lat, lng)
                        if api_location and api_location != 'Unknown Location':
                            location_name = api_location
                    except Exception as e:
                        print(f"Error getting location: {e}")
            
            # Handle datetime objects safely
            time_display = 'Unknown'
            last_seen_date = 'Unknown'
            
            if person.get('time_last_seen') is not None:
                try:
                    time_obj = person['time_last_seen']
                    if hasattr(time_obj, 'strftime'):
                        time_display = time_obj.strftime('%I:%M%p')
                    else:
                        time_str = str(time_obj)
                        if ':' in time_str:
                            time_parts = time_str.split(':')
                            hour = int(time_parts[0])
                            minute = int(time_parts[1])
                            if hour == 0:
                                time_display = f"12:{minute:02d}AM"
                            elif hour < 12:
                                time_display = f"{hour}:{minute:02d}AM"
                            elif hour == 12:
                                time_display = f"12:{minute:02d}PM"
                            else:
                                time_display = f"{hour-12}:{minute:02d}PM"
                except Exception as e:
                    time_display = 'Unknown'
            
            if person.get('date_last_seen'):
                try:
                    last_seen_date = person['date_last_seen'].strftime('%B %d, %Y')
                except:
                    last_seen_date = 'Unknown'
            
            
            person_data = {
                'name': person['full_name'] if person['full_name'] else 'Unknown',
                'age': str(person['age']) if person['age'] is not None else 'Unknown',
                'gender': person['gender'] if person['gender'] else 'Unknown',
                'height': cm_to_feet_inches(person['height']) if person['height'] is not None and person['height'] != 0 else 'Unknown', 
                'hair_color': person['hair_color'] if person['hair_color'] else 'Unknown',
                'last_seen_attire': person['last_seen_clothes'] if person['last_seen_clothes'] else 'Unknown',
                'eye_color': person['eye_color'] if person['eye_color'] else 'Unknown',
                'location': time_display,
                'missing_from': location_name,
                'last_seen': last_seen_date,
                'image': main_image,
                'all_images': person_images
            }
            
            return jsonify({'success': True, 'person': person_data})
        else:
            return jsonify({'success': False, 'error': 'Person not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


#################################################
#########  V I E W  T H E  P E R S O N  #########
#################################################

@public_view_bp.route('/view-missing-person/<int:report_id>')
def view_missing_person(report_id):
    try:
        conn = db.get_db_connection()
        if conn is None:
            flash('Database connection failed', 'error')
            return redirect(url_for('public_view_bp.public_users'))
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name, ' ', IFNULL(mpi.suffix, '')) as full_name,
            mpi.person_id, mpi.nickname, mpi.gender, mpi.date_of_birth, mpi.civil_status, mpi.citizenship, mpi.contact_number,
            TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
            mpi.height, mpi.weight, mpi.hair_color, mpi.eye_color, mpi.distinguishing_mark,
            mpi.occupation, mpi.address, mpi.house_number, mpi.street, mpi.barangay, mpi.city, mpi.province, mpi.region,
            mpls.clothing_description as last_seen_clothes, mpls.circumstances, mpls.date_last_seen, mpls.time_last_seen,
            mpm.missing_filedata as img_filedata, mpm.missing_filetype as img_filetype, mpm.uploaded_at,
            ST_Y(mpl.location) as longitude, ST_X(mpl.location) as latitude,
            mphc.health_type, mphc.health_condition, cr.relationship_to_missing, cf.case_status, cf.approval_status, cf.date_and_time_reported
            FROM case_file cf
            LEFT JOIN case_reporters cr ON cr.case_id = cf.case_id
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_health_condition mphc ON mpi.health_condition_id = mphc.missing_person_health_condition_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            LEFT JOIN missing_person_location mpl ON mpls.missing_person_location_id = mpl.missing_person_location_id
            WHERE mpi.person_id = %s
        """, (report_id,))
        
        person = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if person:
            # Encode image if available
            image_src = 'static/images/public_page/missing.jpg'
            if person['img_filedata']:
                person['img_filedata'] = base64.b64encode(person['img_filedata']).decode('utf-8')
                image_src = f"data:{person['img_filetype']};base64,{person['img_filedata']}"
            
            # Get location name
            location_name = 'Unknown'
            if person['latitude'] and person['longitude'] and (-90 <= person['latitude'] <= 90) and (-180 <= person['longitude'] <= 180):
                location_name = get_location_name(person['latitude'], person['longitude'])
            
            # Format time
            time_display = 'Unknown'
            if person['time_last_seen']:
                try:
                    time_display = person['time_last_seen'].strftime('%I:%M%p')
                except:
                    time_display = str(person['time_last_seen'])
            
            person_data = {
                'name': person['full_name'] or 'Unknown',
                'age': str(person['age']) if person['age'] else 'Unknown',
                'gender': person['gender'] or 'Unknown',
                'height': cm_to_feet_inches(person['height']) if person['height'] else 'Unknown',
                'hair_color': person['hair_color'] or 'Unknown',
                'last_seen_attire': person['last_seen_clothes'] or 'Unknown',
                'eye_color': person['eye_color'] or 'Unknown',
                'location': time_display,
                'missing_from': location_name,
                'last_seen': person['date_last_seen'].strftime('%B %d, %Y') if person['date_last_seen'] else 'Unknown',
                'birthdate': person['date_of_birth'].strftime('%B %d, %Y') if person['date_of_birth'] else 'Unknown',
                'image': image_src
            }
            return render_template('public_users/1u-public_view.html', selected_person=person_data, missing_persons=[])
        else:
            flash('Person not found', 'error')
            return redirect(url_for('public_view_bp.public_users'))
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('public_view_bp.public_users'))
    
    

##########################################
#########  H E L P  L O C A T E  #########
##########################################

@public_view_bp.route('/help-locate-additional-report/<int:case_id>', methods=['POST', 'GET'])
def help_locate_report(case_id):
    if request.method != 'POST':
        flash('Invalid request method', 'error')
        return redirect(url_for('public_view_bp.public_users'))
    
    try:
        userEmail = session.get('email')
        loggedIn = session.get('loggedIn')
        role = session.get('role')

        ############################
        ####  P E R S O N  I D  ####
        ############################

        person_id = request.form.get('person_id', '')
        
        # Validate case_id
        if not case_id or case_id == 0:
            flash('Invalid case ID', 'error')
            return redirect(url_for('public_view_bp.public_users'))
        
        #####################
        ####  E M A I L  ####
        #####################

        email = request.form.get('helpEmail', '')
        
        ###################
        ####  N A M E  ####
        ###################
        
        first_name = request.form.get('HelpLocateFirstName','')
        middle_name = request.form.get('HelpLocateMiddleName', '')
        last_name = request.form.get('HelpLocateLastName','')

        ######################################
        ####  C O N T A C T  N U M B E R  ####
        ######################################
        
        contact_number = request.form.get('HelpLocateContact','')
        
        ###################################
        ####  T I M E  A N D  D A T E  ####
        ###################################
        
        timeLastSeen_str = request.form.get('TimeSighting', '')
        timeLastSeen = datetime.strptime(timeLastSeen_str, '%H:%M').time() if timeLastSeen_str else None
        
        lastSeen = request.form.get('DateSighting', '')
        dateLastSeen = datetime.strptime(lastSeen, '%Y-%m-%d').date() if lastSeen else None

        submitted_at = now
        
        #######################################################
        ####  R E L A T I O N S H I P  T O  M I S S I N G  ####
        #######################################################
        
        relationship_to_missing = request.form.get('HelpRelationship', '')
        
        #################################
        ####  D E S C R I P T I O N  ####
        #################################
        
        description = request.form.get('help_locate_description', '')
        
        #####################
        ####  I M A G E  ####
        #####################
        
        imageOfMissing = request.files.get('help_upload_last_seen', '')
        
        # Validate required fields
        if not all([relationship_to_missing, description, timeLastSeen, dateLastSeen]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('public_view_bp.public_users'))
        
        #####################################################
        ####  L O N G I T U D E  A N D  L A T I T U D E  ####
        #####################################################
        
        # Get location selection type - check both possible field names
        location_type = request.form.get('helpLocateLocationNoAcc', '') or request.form.get('helpLocateLocation', '')
        custom_location = request.form.get('helpCustomLoc', '')
        
        # Handle coordinates based on location selection
        if location_type == 'my-location':
            # Use coordinates from user's current location
            latitude = float(request.form.get('helpLatitude', '0'))
            longitude = float(request.form.get('helpLongitude', '0'))
        elif location_type == 'custom-location' and custom_location:
            # Use coordinates from custom location search
            latitude = float(request.form.get('helpLatitude', '0'))
            longitude = float(request.form.get('helpLongitude', '0'))
        else:
            # Fallback to default coordinates if no valid selection
            latitude = 0.0
            longitude = 0.0
        
        # Validate coordinate ranges
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            # Invalid coordinates, use default for Laguna, Philippines
            latitude = 14.2691
            longitude = 121.4577
        
        # Ensure coordinates are not zero
        if latitude == 0 and longitude == 0:
            # Set default coordinates for Laguna, Philippines
            latitude = 14.2691
            longitude = 121.4577
        
        locationPoint = f'POINT({latitude} {longitude})' ####  L O C A T I O N  P O I N T  ####
        
        # Database connection
        conn = db.get_db_connection()
        
        if conn is None:
            print('Database connection failed')
            flash('Database connection failed. Please try again.', 'error')
            return redirect(url_for('public_view_bp.public_users'))
        
        cursor = conn.cursor(dictionary=True, buffered=True)
        # Database insert

        # Missing person location
        cursor.execute("""
            INSERT INTO missing_person_location (location)
            VALUES (ST_GeomfromText(%s, 4326))
            """, (locationPoint, )
            )
        
        lastLocation_id = cursor.lastrowid
        
        # Process image upload
        reportMedia_id = None
        if imageOfMissing and imageOfMissing.filename:
            img_filename = secure_filename(imageOfMissing.filename)
            img_filetype = imageOfMissing.content_type
            img_filedata = imageOfMissing.read()

            # Optional: basic validation
            if img_filetype not in ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']:
                flash('Invalid image file type.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('public_view_bp.public_users'))

            # Missing Person Media
            cursor.execute(
                """
                INSERT INTO missing_person_media
                (
                    missing_person_id,
                    missing_filename,
                    missing_filetype,
                    missing_filedata,
                    uploaded_at
                )
                VALUES (%s, %s, %s, %s, %s)
                """, (
                    person_id,
                    img_filename,
                    img_filetype,
                    img_filedata,
                    submitted_at
                )
            )   

            reportMedia_id = cursor.lastrowid

        if loggedIn == True:
            withAccounts_id = session.get('accounts_id', '')
            reporter_type = 'user'
            insert_case_reporter(
                cursor,
                case_id,
                reporter_type,
                withAccounts_id,
                reportMedia_id,
                lastLocation_id,
                relationship_to_missing,
                submitted_at,
                description
                )
            #Commit and close
            conn.commit()
            log_user_activity('help_locate_sighting', 'success', f'{{"case_id": "{case_id}", "person_id": "{person_id}"}}', withAccounts_id)
            cursor.close()
            conn.close()

            flash('Report submitted successfully!')
            return redirect(url_for('public_view_bp.public_users'))
        
        # If user is not logged in
        else:
            # Validate required fields for non-logged in users
            if not all([email, first_name, last_name, contact_number]):
                flash('Please fill in all required fields.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('public_view_bp.public_users'))
            
            # No Account
            reporter_type = 'no_account'
            cursor.execute(
                """
                INSERT INTO no_account_user
                (
                    first_name,
                    middle_name,
                    last_name,
                    contact_number,
                    email,  
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    first_name,
                    middle_name,
                    last_name,
                    contact_number,
                    email,
                    submitted_at
                )
            )
            
            noAccounts_id = cursor.lastrowid

            insert_case_reporter(
                cursor,
                case_id,
                reporter_type,
                noAccounts_id,
                reportMedia_id,
                lastLocation_id,
                relationship_to_missing,
                submitted_at,
                description
                )
            #Commit and close
            conn.commit()
            cursor.close()
            conn.close()

            flash('Report submitted successfully!')
            return redirect(url_for('public_view_bp.public_users'))
    
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()
        print(f'Error submitting help locate report: {str(e)}')
        import traceback
        traceback.print_exc()
        flash('Error submitting report. Please try again.', 'error')
        return redirect(url_for('public_view_bp.public_users'))

    
    


#Function for inserting case reporters
def insert_case_reporter(cursor, case_id, reporter_type, reporter_id, reportMedia_id, lastLocation_id, relationship_to_missing, submitted_at, description):
    cursor.execute(
        """
        INSERT INTO case_reporters
        (
            case_id,
            reporter_type,
            reporter_id,
            follow_up_media_id,
            follow_up_location_id,
            relationship_to_missing,
            date_reported,
            description
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            case_id,
            reporter_type,
            reporter_id,
            reportMedia_id,
            lastLocation_id,
            relationship_to_missing,
            submitted_at,
            description
        )
    )





