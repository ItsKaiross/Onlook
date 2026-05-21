from flask import Blueprint, session, render_template, redirect, url_for, flash
from api.database import db
from api.audit import log_audit

talk_to_us_bp = Blueprint('talk_to_us_bp', __name__)

@talk_to_us_bp.route('/talk-to-us')
def talk_to_us():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    return render_template('public_users/7u-talk_to_us.html', loggedIn_email = loggedIn_email)

##########################################
#########  P U B L I C  P A G E  #########
##########################################


