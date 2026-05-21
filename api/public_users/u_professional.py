from flask import Blueprint, session, render_template, redirect, url_for, flash
from api.database import db
from api.audit import log_audit

professional_bp = Blueprint('professional_bp', __name__)

@professional_bp.route('/professional')
def professional():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    return render_template('public_users/6u-professional.html', loggedIn_email = loggedIn_email)

##########################################
#########  P U B L I C  P A G E  #########
##########################################


