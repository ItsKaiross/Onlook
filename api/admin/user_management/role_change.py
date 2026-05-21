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

##########################################
#########  R O L E  C H A N G E  #########
##########################################

@app.route("/update-roles", methods=['POST'])
def update_roles():
    try:
        data = request.get_json()
        user_id = data["id"]
        new_role = data["value"]
        logout_after = data.get("logoutAfter", False)
        
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current role for audit logging
        cursor.execute("SELECT role FROM accounts WHERE accounts_id = %s", (user_id,))
        current_user = cursor.fetchone()
        old_role = current_user['role'] if current_user else 'unknown'
        
        # Prevent changing systemAdmin role
        if old_role == 'systemAdmin':
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "System Administrator role cannot be changed"}), 403
        
        if new_role == "systemAdmin" and logout_after:
            current_admin_id = session.get("accounts_id")
            
            # Log audit for current admin role change
            log_audit(cursor, module='users', action='role_change',
                      target_table='accounts', target_id=current_admin_id,
                      before={'role': 'systemAdmin'}, after={'role': 'policeAdmin'})
            
            cursor.execute(
                """
                UPDATE accounts SET role = %s WHERE accounts_id = %s
                """
                , ("policeAdmin", current_admin_id)
                )
        
        # Log audit for target user role change
        log_audit(cursor, module='users', action='role_change',
                  target_table='accounts', target_id=user_id,
                  before={'role': old_role}, after={'role': new_role})
            
        cursor.execute(
            """
            UPDATE accounts SET role = %s WHERE accounts_id = %s
            """
            , (new_role, user_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500
