from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
import base64
now = datetime.now()
current_date_time = now
from api.audit import log_audit


@app.route('/police-field-report/filtered')
def police_field_report_filtered():
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        status = request.args.get('status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        age_range = request.args.get('age_range', '')

        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                cf.case_id,
                CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name) AS full_name,
                TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
                mpls.date_last_seen,
                cf.approval_status
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND cf.approval_status = %s"
            params.append(status)
        else:
            query += " AND cf.approval_status != 'Archived'"

        if date_from:
            query += " AND mpls.date_last_seen >= %s"
            params.append(date_from)

        if date_to:
            query += " AND mpls.date_last_seen <= %s"
            params.append(date_to)

        if age_range:
            age_parts = age_range.split('-')
            if len(age_parts) == 2:
                min_age, max_age = age_parts
                query += " AND TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) BETWEEN %s AND %s"
                params.extend([int(min_age), int(max_age)])

        query += " ORDER BY cf.case_id ASC"

        cursor.execute(query, params)
        reports = cursor.fetchall()
        cursor.close()
        conn.close()

        for report in reports:
            for key, value in report.items():
                if hasattr(value, 'strftime'):
                    report[key] = value.strftime("%Y-%m-%d")
                elif hasattr(value, 'total_seconds'):
                    total_seconds = int(value.total_seconds())
                    h = total_seconds // 3600
                    m = (total_seconds % 3600) // 60
                    s = total_seconds % 60
                    report[key] = f"{h:02}:{m:02}:{s:02}"

        return jsonify({'success': True, 'reports': reports})

    except Exception as e:
        print(f"Error fetching filtered reports: {e}")
        return jsonify({'success': False, 'error': str(e)})


#######################################################
#########  P R I N T  F I E L D  R E P O R T  #########
#######################################################

@app.route('/police-field-report/all')
def police_field_report_all():
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                cf.case_id,
                CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name) AS full_name,
                TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
                mpls.date_last_seen,
                cf.approval_status
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            WHERE cf.approval_status != 'Archived'
            ORDER BY cf.case_id ASC
        """)

        reports = cursor.fetchall()
        cursor.close()
        conn.close()

        # serialize date fields
        for report in reports:
            for key, value in report.items():
                if hasattr(value, 'strftime'):
                    report[key] = value.strftime("%Y-%m-%d")
                elif hasattr(value, 'total_seconds'):
                    total_seconds = int(value.total_seconds())
                    h = total_seconds // 3600
                    m = (total_seconds % 3600) // 60
                    s = total_seconds % 60
                    report[key] = f"{h:02}:{m:02}:{s:02}"

        return jsonify({'success': True, 'reports': reports})

    except Exception as e:
        print(f"Error fetching all reports: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/police-field-report/get-officers')
def get_field_report_officers():
    if 'accounts_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                p.officer_id,
                CONCAT(p.rank, ' ', p.first_name, ' ', p.last_name) AS name
            FROM police p
            JOIN accounts a ON p.officer_id = a.accounts_id
            WHERE a.status = 'active'
            AND (a.role = 'police' OR a.role = 'policeAdmin' OR a.role = 'policeChief' 
                 OR a.role LIKE '%-mps' OR a.role LIKE '%-ps')
            ORDER BY p.rank, p.last_name, p.first_name
        """)
        
        officers = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'officers': officers})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500