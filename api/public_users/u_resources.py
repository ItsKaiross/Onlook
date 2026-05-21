from flask import Blueprint, session, render_template, redirect, url_for, flash
from api.database import db
from api.audit import log_audit

resources_bp = Blueprint('resources_bp', __name__)

@resources_bp.route('/resources')
def resources():
    if 'accounts_id' in session and session['role'] == 'user':
        userEmail = session.get('email')
        loggedIn = session.get('loggedIn')
        user_id = session.get('accounts_id')
        role = session.get('role')
        
        loggedIn_email = None
        profile = None
        
        if loggedIn == True:
            loggedIn_email = userEmail
            
            # Fetch user profile picture
            try:
                conn = db.get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("""
                        SELECT pp.profile_filedata, pp.profile_filetype
                        FROM accounts a
                        LEFT JOIN public_user p ON a.user_id = p.user_id
                        LEFT JOIN profile_pictures pp ON p.profile_picture_id = pp.profile_id
                        WHERE a.accounts_id = %s
                    """, (user_id,))
                    profile_result = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    
                    if profile_result and profile_result['profile_filedata']:
                        import base64
                        profile = {
                            'profile_filedata': base64.b64encode(profile_result['profile_filedata']).decode('utf-8'),
                            'profile_filetype': profile_result['profile_filetype']
                        }
            except Exception as e:
                print(f"Error fetching profile: {e}")
        
        return render_template('public_users/11u-resources.html', 
                             loggedIn_email=loggedIn_email,
                             profile=profile,
                             role=role), 200
    return redirect(url_for('public_users'))
    
#############################################################
#########  P U B L I C  P A G E  R E S O U R C E S  #########
#############################################################


