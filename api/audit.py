from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
import base64
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
now = datetime.now()
current_date_time = now
import sys
import json


def log_audit(cursor=None, module=None, action=None, target_table=None, target_id=None,
              before=None, after=None, status='success', remarks=None, override_role=None,
              accounts_id=None, performed_by=None, performed_role=None):
    """
    System-wide audit trail logger.
    Call this from any route after any significant action.

    Usage:
        from api.audit import log_audit
        log_audit(cursor, module='reports', action='generate',
                  target_table='monthly_precinct_reports', target_id=report_id,
                  after=row_data)
    """
    conn = None
    cursor_created = False
    
    try:
        # If no cursor provided, create a new connection
        if cursor is None:
            conn = db.get_db_connection()
            if conn is None:
                print("[audit_trail] Database connection failed")
                return
            cursor = conn.cursor(dictionary=True)
            cursor_created = True
        
        # Use provided values or fall back to session
        final_accounts_id = accounts_id if accounts_id is not None else session.get('accounts_id')
        final_performed_by = performed_by if performed_by else f"{session.get('firstName', '')} {session.get('lastName', '')}".strip() or 'Unknown'
        final_performed_role = performed_role if performed_role else (session.get('role', 'Unknown') if override_role is None else override_role)
        
        cursor.execute("""
            INSERT INTO audit_trail (
                accounts_id,
                performed_by,
                performed_role,
                module,
                action,
                target_table,
                target_id,
                before_change,
                after_change,
                ip_address,
                user_agent,
                action_timestamp,
                status,
                remarks
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """, [
            final_accounts_id,
            final_performed_by,
            final_performed_role,
            module,
            action,
            target_table,
            target_id,
            json.dumps(before, default=str) if before else None,
            json.dumps(after,  default=str) if after  else None,
            request.remote_addr,
            request.headers.get('User-Agent'),
            datetime.now(),
            status,
            remarks,
        ])
        
        # Commit if we created the connection
        if cursor_created and conn:
            conn.commit()
            
    except Exception as e:
        print(f"[audit_trail] Logging error: {e}", file=sys.stderr)
        if cursor_created and conn:
            conn.rollback()
    finally:
        if cursor_created:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
