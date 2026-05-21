from flask import Blueprint, session, render_template, redirect, url_for, flash
from api.database import db
from api.audit import log_audit

report_missing_bp = Blueprint('report_missing_bp', __name__)

@report_missing_bp.route('/report-missing')
def report_missing():
    if 'accounts_id' in session and session['role'] == 'user':
        userEmail = session.get('email')
        loggedIn = session.get('loggedIn')
        
        loggedIn_email = None
        if loggedIn == True:
            loggedIn_email = userEmail
        return render_template('public_users/8u-report_missing.html', loggedIn_email = loggedIn_email), 200
    return redirect(url_for('public_users'))

######################################################################
#########  P U B L I C  P A G E  R E P O R T  M I S S I N G  #########
######################################################################


