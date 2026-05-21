from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from datetime import datetime, date
import traceback
now = datetime.now()
import base64
import sys
from api.audit import log_audit

police_admin_report_bp = Blueprint('police_admin_report_bp', __name__)

# ─────────────────────────────────────────────────────────────
#   GET  /admin-reports
# ─────────────────────────────────────────────────────────────
@police_admin_report_bp.route('/admin-reports')
def admin_reports():
    if 'accounts_id' not in session or session.get('role') != 'policeAdmin':
        return redirect(url_for('login'))

    try:
        report_month = int(request.args.get('month') or date.today().month)
        report_year  = int(request.args.get('year')  or date.today().year)
    except (ValueError, TypeError):
        report_month = date.today().month
        report_year  = date.today().year

    report_precinct = request.args.get('precinct', '')

    months = [
        (1,'January'),(2,'February'),(3,'March'),(4,'April'),
        (5,'May'),(6,'June'),(7,'July'),(8,'August'),
        (9,'September'),(10,'October'),(11,'November'),(12,'December'),
    ]

    try:
        conn   = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT DISTINCT precinct FROM monthly_precinct_reports ORDER BY precinct")
        precincts = [row['precinct'] for row in cursor.fetchall()]

        report_query = """
            SELECT
                r.report_id,
                r.report_month,
                r.report_year,
                r.precinct,
                r.date_missing,
                r.date_reported,
                r.reason,
                r.found_dead,
                r.found_alive,
                r.cause_of_death,
                r.still_missing,
                r.docket_number,
                CONCAT(mpi.first_name, ' ', mpi.last_name)                AS full_name,
                mpi.gender,
                TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE())         AS age,
                mpi.address,
                CONCAT(p.rank, ' ', p.first_name, ' ', p.last_name)       AS investigator_name
            FROM monthly_precinct_reports r
            JOIN missing_person_information mpi ON r.person_id = mpi.person_id
            LEFT JOIN police p ON r.investigator_id = p.officer_id
            WHERE r.report_month = %s
            AND r.report_year  = %s
        """
        report_params = [report_month, report_year]

        if report_precinct:
            report_query += " AND r.precinct = %s"
            report_params.append(report_precinct)

        report_query += " ORDER BY r.precinct, r.date_reported"

        cursor.execute(report_query, report_params)
        reports = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            'admin/admin-base.html',
            page              = 'admin-reports',
            roles             = session.get('role'),
            reports           = reports,
            precincts         = precincts,
            months            = months,
            selected_month    = report_month,
            selected_year     = report_year,
            selected_precinct = report_precinct,
        )

    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        flash('Something went wrong loading the report.', 'danger')
        return redirect(url_for('admin_reports'))


# ─────────────────────────────────────────────────────────────
#   POST /police/reports/generate
# ─────────────────────────────────────────────────────────────
@police_admin_report_bp.route('/police/reports/generate', methods=['POST'])
def generate_monthly_report():
    if 'accounts_id' not in session or session.get('role') != 'policeAdmin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        data  = request.get_json(silent=True) or {}
        try:
            month = int(data.get('month') or date.today().month)
            year  = int(data.get('year')  or date.today().year)
        except (ValueError, TypeError):
            month = date.today().month
            year  = date.today().year

        conn   = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                cf.case_id,
                cf.date_and_time_reported,
                cf.case_status,
                cf.assigned_officer_id,
                cf.notes,
                cf.isAlive,
                cf.isDead,
                mpls.person_id,
                mpls.date_last_seen,
                mpls.circumstances
            FROM case_file cf
            JOIN missing_person_last_seen mpls
                ON cf.last_seen_id = mpls.missing_person_last_seen_id
            WHERE MONTH(cf.date_and_time_reported) = %s
                AND YEAR(cf.date_and_time_reported)  = %s
                AND cf.approval_status = 'Approved'
        """, [month, year])

        cases         = cursor.fetchall()
        created_count = 0
        skipped_count = 0

        for case in cases:

            cursor.execute("""
                SELECT COUNT(*) AS cnt FROM monthly_precinct_reports
                WHERE case_id = %s AND report_month = %s AND report_year = %s
            """, [case['case_id'], month, year])

            if cursor.fetchone()['cnt'] > 0:
                skipped_count += 1
                continue

            station         = 'Unassigned'
            investigator_id = None

            if case['assigned_officer_id']:
                cursor.execute("""
                    SELECT officer_id, station_assignment
                    FROM police WHERE officer_id = %s
                """, [case['assigned_officer_id']])
                officer = cursor.fetchone()
                if officer:
                    investigator_id = officer['officer_id']
                    station         = officer['station_assignment']

            status         = (case['case_status'] or '').lower()
            is_alive       = case.get('isAlive', 0)
            is_dead        = case.get('isDead', 0)
            
            found_dead     = 1 if (is_dead == 1 or status == 'found_dead' or 'closed - dead' in status) else 0
            found_alive    = 1 if (is_alive == 1 or status == 'found_alive' or 'closed - alive' in status) else 0
            still_missing  = 1 if (status == 'missing' or status == 'ongoing') else 0
            cause_of_death = case['notes'] if found_dead  else None
            docket_number  = f"DC-{str(case['case_id']).zfill(5)}"

            cursor.execute("""
                INSERT INTO monthly_precinct_reports (
                    report_month, report_year, precinct,
                    person_id, case_id, investigator_id,
                    date_missing, date_reported,
                    reason, found_dead, found_alive,
                    cause_of_death, still_missing, docket_number
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
            """, [
                month, year, station,
                case['person_id'], case['case_id'], investigator_id,
                case['date_last_seen'], case['date_and_time_reported'],
                case['circumstances'], found_dead, found_alive,
                cause_of_death, still_missing, docket_number
            ])
            
            # Get the new report ID for audit logging
            new_report_id = cursor.lastrowid
            
            # Log audit for generating report
            log_audit(cursor, module='reports', action='generate',
                      target_table='monthly_precinct_reports', target_id=new_report_id,
                      after={'month': month, 'year': year, 'station': station, 'case_id': case['case_id']})

            created_count += 1

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'created': created_count,
            'skipped': skipped_count,
            'message': f"{created_count} rows generated, {skipped_count} already existed."
        })

    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
#   GET /admin-reports/print
# ─────────────────────────────────────────────────────────────
@police_admin_report_bp.route('/admin-reports/print')
def admin_reports_print():
    if 'accounts_id' not in session or session.get('role') != 'policeAdmin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        report_month = int(request.args.get('month') or date.today().month)
        report_year  = int(request.args.get('year')  or date.today().year)
    except (ValueError, TypeError):
        report_month = date.today().month
        report_year  = date.today().year

    report_precinct = request.args.get('precinct', '')

    try:
        conn   = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        report_query = """
            SELECT
                r.report_id,
                r.report_month,
                r.report_year,
                r.precinct,
                r.date_missing,
                r.date_reported,
                r.reason,
                r.found_dead,
                r.found_alive,
                r.cause_of_death,
                r.still_missing,
                r.docket_number,
                CONCAT(mpi.first_name, ' ', mpi.last_name)                AS full_name,
                mpi.gender,
                TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE())         AS age,
                mpi.address,
                CONCAT(p.rank, ' ', p.first_name, ' ', p.last_name)       AS investigator_name
            FROM monthly_precinct_reports r
            JOIN missing_person_information mpi ON r.person_id = mpi.person_id
            LEFT JOIN police p ON r.investigator_id = p.officer_id
            WHERE r.report_month = %s
            AND r.report_year  = %s
        """
        report_params = [report_month, report_year]

        if report_precinct:
            report_query += " AND r.precinct = %s"
            report_params.append(report_precinct)

        report_query += " ORDER BY r.precinct, r.date_reported"

        cursor.execute(report_query, report_params)
        reports = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'reports': reports
        })

    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
#   GET /admin-reports/get-officers
# ─────────────────────────────────────────────────────────────
@police_admin_report_bp.route('/admin-reports/get-officers')
def get_officers_for_report():
    if 'accounts_id' not in session or session.get('role') != 'policeAdmin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        conn   = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get all police officers and police admins from accounts with police role
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

        return jsonify({
            'success': True,
            'officers': officers
        })

    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 500


