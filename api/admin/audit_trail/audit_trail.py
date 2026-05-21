from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
import base64
from api.database import db
from datetime import datetime
now = datetime.now()
current_date_time = now
import sys
import json
import traceback
from api.audit import log_audit

audit_trail_bp = Blueprint('audit_trail_bp', __name__)

@audit_trail_bp.route('/admin/audit-trail')
def admin_audit_trail():
    if 'accounts_id' not in session or session.get('role') not in ['systemAdmin', 'policeAdmin']:
        return redirect(url_for('login'))

    try:
        module    = request.args.get('module', '')
        action    = request.args.get('action', '')
        date_from = request.args.get('date_from', '')
        date_to   = request.args.get('date_to', '')

        try:
            page     = int(request.args.get('page') or 1)
            per_page = int(request.args.get('per_page') or 20)
        except (ValueError, TypeError):
            page     = 1
            per_page = 20

        offset = (page - 1) * per_page

        conn   = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        base_query = "FROM audit_trail WHERE 1=1"
        params     = []

        if module:
            base_query += " AND module = %s"
            params.append(module)

        if action:
            base_query += " AND action = %s"
            params.append(action)

        if date_from:
            base_query += " AND DATE(action_timestamp) >= %s"
            params.append(date_from)

        if date_to:
            base_query += " AND DATE(action_timestamp) <= %s"
            params.append(date_to)

        # Count
        cursor.execute(f"SELECT COUNT(*) AS total {base_query}", params)
        total_records = cursor.fetchone()['total']
        total_pages   = (total_records + per_page - 1) // per_page if total_records > 0 else 1

        # Fetch
        cursor.execute(f"""
            SELECT
                audit_id,
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
                action_timestamp,
                status,
                remarks
            {base_query}
            ORDER BY action_timestamp DESC
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])

        logs = cursor.fetchall()

        # Get distinct modules and actions for filter dropdowns
        cursor.execute("SELECT DISTINCT module FROM audit_trail ORDER BY module")
        modules = [row['module'] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT action FROM audit_trail ORDER BY action")
        actions = [row['action'] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return render_template(
            'admin/admin-base.html',
            page           = 'admin-audit-trail',
            roles          = session.get('role'),
            logs           = logs,
            modules        = modules,
            actions        = actions,
            total_records  = total_records,
            total_pages    = total_pages,
            current_page   = page,
            per_page       = per_page,
            selected_module   = module,
            selected_action   = action,
            selected_date_from= date_from,
            selected_date_to  = date_to,
        )

    except Exception as e:
        print(f"Database error in audit trail: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        
        # Try to close connections if they exist
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass
            
        flash('Something went wrong loading the audit trail.', 'error')
        return redirect(url_for('admin'))


