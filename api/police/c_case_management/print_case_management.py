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


@app.route('/police-case-report/filtered')
def print_case_management_filtered():
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        status = request.args.get('status', '')
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        show_archived = request.args.get('show_archived', '')

        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                cf.case_id,
                CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name) AS full_name,
                TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
                mpls.date_last_seen,
                cf.approval_status,
                cf.case_status,
                cf.priority,
                cf.assigned_officer_id,
                CONCAT(p.rank, ' ', p.last_name) AS assigned_officer
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            LEFT JOIN police p ON cf.assigned_officer_id = p.officer_id
            WHERE 1=1
        """
        params = []

        if show_archived == 'true':
            query += " AND cf.approval_status = 'Archived'"
        else:
            query += " AND cf.approval_status != 'Archived'"

        if status:
            query += " AND cf.case_status = %s"
            params.append(status)

        if from_date:
            query += " AND mpls.date_last_seen >= %s"
            params.append(from_date)

        if to_date:
            query += " AND mpls.date_last_seen <= %s"
            params.append(to_date)

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
        print(f"Error fetching filtered case reports: {e}")
        return jsonify({'success': False, 'error': str(e)})


#######################################################
#########  P R I N T  C A S E  R E P O R T  #########
#######################################################

@app.route('/police-case-report/all')
def print_case_management():
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
                cf.approval_status,
                cf.case_status,
                cf.priority,
                cf.assigned_officer_id,
                CONCAT(p.rank, ' ', p.last_name) AS assigned_officer
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            LEFT JOIN police p ON cf.assigned_officer_id = p.officer_id
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


@app.route('/police-case-report/get-officers')
def get_case_officers():
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