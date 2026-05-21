from flask import Flask, session, render_template, redirect, url_for, flash, Blueprint
from api.database import db
from api.audit import log_audit

#############################################################
#########  P U B L I C  P A G E  C O M M U N I T Y  #########
#############################################################

community_bp = Blueprint('community_api', __name__)

@community_bp.route('/community')
def community():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    return render_template('public_users/3u-community.html', loggedIn_email = loggedIn_email)

##########################################
#########  P U B L I C  P A G E  #########
##########################################


