from flask import Blueprint, session, jsonify
from flask import request
from api.database import db
from datetime import datetime
import base64
now = datetime.now()
from api.audit import log_audit

report_details_bp = Blueprint('report_details_bp', __name__)


################################################
#########  R E P O R T  D E T A I L S  #########
################################################


@report_details_bp.route('/police-report-details/<int:case_id>')
def police_report_details(case_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'error': 'Database connection failed'})
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT cf.case_id, cf.case_status, cf.approval_status, cf.date_and_time_reported,
            CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name, ' ', IFNULL(mpi.suffix, '')) as full_name,
            mpi.gender, TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
            mpi.height, mpi.weight, mpi.hair_color, mpi.eye_color,
            mpls.clothing_description, mpls.date_last_seen, mpls.time_last_seen,
            mpm.missing_filedata, mpm.missing_filetype
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            WHERE cf.case_id = %s
        """, (case_id,))
        
        report = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if report:
            # ← serialize all date/time/timedelta fields
            for key, value in report.items():
                if isinstance(value, datetime):
                    report[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif hasattr(value, 'days') and hasattr(value, 'seconds'):  # timedelta
                    total_seconds = int(value.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    report[key] = f"{hours:02}:{minutes:02}:{seconds:02}"
                elif hasattr(value, 'strftime'):  # date object
                    report[key] = value.strftime("%Y-%m-%d")
                    
            # Process image if exists
            if report.get('missing_filedata'):
                try:
                    report['missing_filedata'] = base64.b64encode(report['missing_filedata']).decode('utf-8')
                    report['img_src'] = f"data:{report['missing_filetype']};base64,{report['missing_filedata']}"
                except:
                    report['img_src'] = None
            
            # Convert timedelta to string
            if report.get('time_last_seen'):
                report['time_last_seen'] = str(report['time_last_seen'])
            
            # Keep height in cm for editing (don't convert to feet)
            if report.get('height'):
                try:
                    report['height'] = float(report['height'])
                except:
                    report['height'] = report['height']
            
            return jsonify({'success': True, 'report': report})
        else:
            return jsonify({'success': False, 'error': 'Report not found'})
            
    except Exception as e:
        print(f"Error in police_report_details: {e}")
        return jsonify({'success': False, 'error': str(e)})


