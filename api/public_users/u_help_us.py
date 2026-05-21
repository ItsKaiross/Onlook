from flask import Blueprint, session, render_template, redirect, url_for, flash
from api.database import db
from api.audit import log_audit

help_us_bp = Blueprint('help_us_bp', __name__)

@help_us_bp.route('/help-us')
def help_us():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    return render_template('public_users/5u-help_us_find.html', loggedIn_email = loggedIn_email)

##########################################
#########  P U B L I C  P A G E  #########
##########################################


