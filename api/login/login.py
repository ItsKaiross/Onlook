from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from flask_bcrypt import check_password_hash
from datetime import datetime
import json
from api.utils.activity_logger import log_login, log_logout
from api.audit import log_audit

login_bp = Blueprint('login_bp', __name__)


############################################
#########  S E S S I O N  T I M E  #########
############################################


@login_bp.before_app_request
def check_session_timeout():
    session.permanent = True
    allowed_endpoints = {
        'login_bp.home',
        'submit_otp_bp.submit_otp',
        'reset_password_bp.reset_pass',
        'mail_bp.send_mail',
        'public_view_bp.email_code',
        'public_view_bp.verify_2fa',
        'public_view_bp.resend_code',
        'login_bp.signIn',
        'about_bp.about',
        'community_bp.community',
        'get_help_bp.get_help',
        'professional_bp.professional',
        'help_us_bp.help_us',
        'talk_to_us_bp.talk_to_us',
        'registration_bp.register',
        'login_bp.logout',
        'login_bp.keepalive',
        'login_bp.check_session',
        'public_view_bp.submit_report',
        'public_view_bp.public_users',
        'static',
        'public_view_bp.help_locate_report',
        'public_view_bp.get_person_data',
        'registration_bp.register_first'
        }
    
    if request.endpoint and request.endpoint not in allowed_endpoints:
        if 'email' not in session:
            return redirect(url_for('login_bp.logout'))


@login_bp.route('/keepalive', methods=['POST'])
def keepalive():
    
    if 'email' in session:
        return jsonify({'status': 'active'})
    else:
        return jsonify({'status': 'expired'}), 401

@login_bp.route('/check-session', methods=['GET'])
def check_session():
    if 'email' in session and session.get('loggedIn') == True:
        return jsonify({'valid': True})
    else:
        manual_logout = session.get('manual_logout', False)
        return jsonify({'valid': False, 'manual_logout': manual_logout})



########################################
#########  L O G I N  P A G E  #########
########################################

@login_bp.route('/login')
def home():
    return render_template('login/login.html')

###############################
#########  L O G I N  #########
###############################

@login_bp.route('/signIn', methods=['GET' ,'POST'])
def signIn():
    msg = ''
    if request.method == 'POST':
        session.permanent = True
        data = request.json
        email = (data.get('email') or "").lower()
        password = data.get('password')
        # Database connection
        conn = db.get_db_connection()
        if conn is None:
            flash('Database connection failed.', 'danger')
            return jsonify({"status": "error"})
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM accounts WHERE email = %s;', (email,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        
        if user is not None:

            session['email_check'] = user['email']
            email_database = session.get('email_check')
            session['pass_check'] = user['password']
            stored_hash = session.get('pass_check')
            isValid = check_password_hash(stored_hash, password)

            session.pop('email_check')
            session.pop('pass_check')
            
            if isValid == True and email_database == email:
                session['loggedIn'] = True
                session['accounts_id'] = user['accounts_id']
                session['role'] = user["role"]
                session['email'] = user["email"]

                if user['officer_id'] is not None:
                    session['officer_id'] = user['officer_id']
                    
                elif user['user_id'] is not None:
                    session['user_id'] = user['user_id']
                    

                if session['loggedIn'] == True:
                    session['active_status'] = 'active'
                    session['logged_in_time'] = datetime.now()
                    session['status'] = user['status']
                    session['isVerified'] = user.get('isVerified', 0) == 1
                    
                    # Get user's name from police or public_user table
                    conn_name = db.get_db_connection()
                    if conn_name:
                        try:
                            cursor_name = conn_name.cursor(dictionary=True)
                            if user['officer_id']:
                                cursor_name.execute('SELECT first_name, last_name FROM police WHERE officer_id = %s', (user['officer_id'],))
                                police_data = cursor_name.fetchone()
                                if police_data:
                                    session['firstName'] = police_data.get('first_name', '')
                                    session['lastName'] = police_data.get('last_name', '')
                            elif user['user_id']:
                                cursor_name.execute('SELECT first_name, last_name FROM public_user WHERE user_id = %s', (user['user_id'],))
                                user_data = cursor_name.fetchone()
                                if user_data:
                                    session['firstName'] = user_data.get('first_name', '')
                                    session['lastName'] = user_data.get('last_name', '')
                        finally:
                            cursor_name.close()
                            conn_name.close()
                    
                    # Fallback if names not found
                    if 'firstName' not in session:
                        session['firstName'] = user.get('firstName', '')
                        session['lastName'] = user.get('lastName', '')
                    
                    # Log the login activity
                    try:
                        log_login(
                            user['accounts_id'], user['email'], 
                            user.get('firstName', ''), user.get('lastName', ''), 
                            user['role'])
                    except Exception as e:
                        print(f"Error logging login: {e}")
                    
                    # Log successful login audit
                    try:
                        performed_by_name = f"{session.get('firstName', '')} {session.get('lastName', '')}".strip()
                        if not performed_by_name or performed_by_name == ' ':
                            performed_by_name = session.get('email', 'Unknown')
                        
                        log_audit(
                            accounts_id=user['accounts_id'],
                            performed_by=performed_by_name,
                            performed_role=user['role'],
                            module='auth',
                            action='login',
                            target_table='accounts',
                            target_id=user['accounts_id'],
                            status='success'
                        )
                    except Exception as e:
                        print(f"Error logging audit: {e}")
                

                if user['status'].lower() == 'active':

                    if user['role'] == 'police' or user['role'] == 'policeChief' or user['role'].endswith('-mps') or user['role'].endswith('-ps'):
                        flash("Welcome Police!", "success")
                        return jsonify({"status": "police-login"})
                    elif user['role'] == 'user':
                        flash(f"Welcome {email}!", "success")
                        return jsonify({"status": "user-login"})
                    elif user['role'] in ['systemAdmin', 'policeAdmin']:
                        flash("Welcome Admin!", "success")
                        return jsonify({"status": "admin-login"})
                    else:
                        pass
                elif user['status'].lower() == 'restricted':
                    flash("Account restricted", "error")
                    return jsonify({"status": "restricted"})
                else:
                    pass
            else:
                # Log failed login audit
                try:
                    log_audit(
                        accounts_id=None,
                        performed_by=email,
                        performed_role='Unknown',
                        module='auth',
                        action='login',
                        target_table='accounts',
                        target_id=None,
                        status='failure',
                        remarks=f"Failed login attempt for {email}"
                    )
                except Exception as e:
                    print(f"Error logging audit: {e}")
                    
                flash("Password or email is incorrect", "error")   
                return jsonify({"status": "login-failed"})
        else:
            # Log failed login audit for unregistered email
            try:
                log_audit(
                    accounts_id=None,
                    performed_by=email,
                    performed_role='Unknown',
                    module='auth',
                    action='login',
                    target_table='accounts',
                    target_id=None,
                    status='failure',
                    remarks=f"Login attempt with unregistered email: {email}"
                )
            except Exception as e:
                print(f"Error logging audit: {e}")
                
            flash("Email is not registered", "error")
            return jsonify({"status": "not-registered"})
            
    return jsonify({"status": "success"})


#################################
#########  L O G O U T  #########
#################################


@login_bp.route('/logout')
def logout():
    if 'email' not in session:
        return redirect(url_for('public_view_bp.public_users'))
    
    # Get account_id before clearing session for audit logging
    account_id = session.get('accounts_id')
    
    session['logged_out_time'] = datetime.now()
    
    # Log the logout activity
    log_logout()
    
    # Log logout audit
    if account_id:
        try:
            performed_by_name = f"{session.get('firstName', '')} {session.get('lastName', '')}".strip()
            if not performed_by_name or performed_by_name == ' ':
                performed_by_name = session.get('email', 'Unknown')
            
            log_audit(
                accounts_id=account_id,
                performed_by=performed_by_name,
                performed_role=session.get('role', 'Unknown'),
                module='auth',
                action='logout',
                target_table='accounts',
                target_id=account_id,
                status='success'
            )
        except Exception as e:
            print(f"Error logging audit: {e}")
    
    logged_users()
    
    # Clear session completely
    session.clear()
    
    return redirect(url_for('public_view_bp.public_users'))



############################################
#########  L O G G E D  U S E R S  #########
############################################

def logged_users():
    try:
        logged_in_time = session.get('logged_in_time', None)
        logged_out_time = session.get('logged_out_time', None)
        account_type = session.get('role', None)
        
        
    except Exception as e:
        print(f'Error in logged_users: {e}')


