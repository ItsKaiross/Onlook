from flask import Blueprint, session, jsonify, request
from api.database import db
from datetime import datetime
from api.audit import log_audit
import sys
import traceback

case_timeline_bp = Blueprint('case_timeline_bp', __name__)


@case_timeline_bp.route('/police/case-timeline-data/<int:case_id>')
def case_timeline_data(case_id):
    if 'accounts_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        conn   = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Status history
        cursor.execute("""
            SELECT
                history_id,
                previous_status,
                new_status,
                previous_approval,
                new_approval,
                changed_by_name,
                changed_by_role,
                notes,
                changed_at,
                'status_change' AS event_type
            FROM case_status_history
            WHERE case_id = %s
            ORDER BY changed_at ASC
        """, [case_id])
        status_history = cursor.fetchall()

        # Reporter events
        cursor.execute("""
            SELECT
                cr.date_reported        AS event_date,
                'report_filed'          AS event_type,
                cr.reporter_type        AS actor,
                cr.description          AS notes,
                cr.relationship_to_missing AS detail,
                NULL                    AS changed_by_name
            FROM case_reporters cr
            WHERE cr.case_id = %s
        """, [case_id])
        reporter_events = cursor.fetchall()

        # User logs for this case
        cursor.execute("""
            SELECT
                ul.log_timestamp        AS event_date,
                ul.action               AS event_type,
                ul.status               AS detail,
                NULL                    AS notes,
                NULL                    AS changed_by_name
            FROM user_logs ul
            WHERE ul.additional_info LIKE %s
            ORDER BY ul.log_timestamp ASC
        """, [f'%"case_id": {case_id}%'])
        log_events = cursor.fetchall()

        cursor.close()
        conn.close()

        # Combine all activity
        all_activity = []

        for e in status_history:
            all_activity.append({**e, 'changed_at': str(e['changed_at']) if e.get('changed_at') else None})

        for e in reporter_events:
            all_activity.append({**e, 'changed_at': str(e['event_date']) if e.get('event_date') else None})

        for e in log_events:
            all_activity.append({**e, 'changed_at': str(e['event_date']) if e.get('event_date') else None})

        # Sort all by date
        all_activity.sort(key=lambda x: x.get('changed_at') or '')

        # Convert status_history dates to string
        for e in status_history:
            e['changed_at'] = str(e['changed_at']) if e.get('changed_at') else None

        return jsonify({
            'success'       : True,
            'status_history': status_history,
            'all_activity'  : all_activity,
            'stages'        : ['Pending', 'Approved', 'Open', 'In Progress', 'Closed', 'Cold Case'],
        })

    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 500


