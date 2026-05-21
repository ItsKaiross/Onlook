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
from api.audit import log_audit


def log_audit(cursor, module, action, target_table=None, target_id=None,
                before=None, after=None, status='success', remarks=None):
    """
    System-wide audit trail logger.
    Call this from any route after any significant action.

    Usage:
        from api.audit import log_audit
        log_audit(cursor, module='reports', action='generate',
                target_table='monthly_precinct_reports', target_id=report_id,
                after=row_data)
    """
    try:
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
            session.get('accounts_id'),
            session.get('full_name', 'Unknown'),
            session.get('role', 'Unknown'),
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
    except Exception as e:
        print(f"[audit_trail] Logging error: {e}", file=sys.stderr)