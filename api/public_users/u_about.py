from flask import Flask, session, render_template, redirect, url_for, flash
from api.database import db
from api.audit import log_audit

##########################################
#########  P U B L I C  P A G E  #########
##########################################

@app.route('/about')
def about():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    return render_template('public_users/4u-about_onlook.html', loggedIn_email = loggedIn_email)

##########################################
#########  P U B L I C  P A G E  #########
##########################################


