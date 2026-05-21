from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
now = datetime.now()
current_date_time = now
import base64
import bcrypt
import logging
import os
from api.audit import log_audit

##############################################
#########  A C T I V A T E  U S E R  #########
##############################################

@app.route('/admin-user-management/activate-user/<int:accounts_id>', methods=['POST', 'GET'])
def admin_activate_user(accounts_id):
    msg = ''
    if request.method == 'GET':
        # Database connection
        conn = db.get_db_connection()
        
        if conn is None:
            msg2 = 'No database'
            return redirect(url_for('admin'))
        
        cursor = conn.cursor(dictionary=True)
        
        # Log audit for activating user
        log_audit(cursor, module='users', action='activate_user',
                  target_table='accounts', target_id=accounts_id,
                  before={'status': 'restricted'}, after={'status': 'active'})
        
        cursor.execute('UPDATE accounts SET status=%s WHERE accounts_id = %s', ('active', accounts_id))
        conn.commit()
        cursor.close()
        conn.close()
        
    return redirect(url_for('admin_user_management'))