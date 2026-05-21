from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from datetime import datetime
import base64
now = datetime.now()
from api.audit import log_audit
from api.police.case_history import log_case_status_change

edit_report_bp = Blueprint('edit_report_bp', __name__)


##########################################
#########  E D I T  R E P O R T  #########
##########################################



@edit_report_bp.route('/police-edit-report/<int:case_id>', methods=['GET', 'POST'])
def police_edit_report(case_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Access denied'})
        flash('Access denied')
        return redirect(url_for('police_field_report'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Received edit data: {data}")
            
            if not data:
                return jsonify({'success': False, 'message': 'No data received'})
            
            conn = db.get_db_connection()
            if conn is None:
                return jsonify({'success': False, 'message': 'Database connection failed'})
            
            cursor = conn.cursor(dictionary=True)
            
            # Parse full name
            full_name = data.get('full_name') or ''
            full_name = full_name.strip() if full_name else ''
            
            name_parts = full_name.split() if full_name else []
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            if len(name_parts) >= 3:
                middle_name = ' '.join(name_parts[1:-1])
                last_name = name_parts[-1]
            elif len(name_parts) == 2:
                middle_name = ''
                last_name = name_parts[1]
            else:
                middle_name = ''
                last_name = name_parts[0] if name_parts else ''
            
            # Calculate date of birth
            date_of_birth = None
            age = data.get('age')
            if age and age != '':
                try:
                    age = int(age)
                    current_year = datetime.now().year
                    birth_year = current_year - age
                    date_of_birth = f"{birth_year}-01-01"
                except (ValueError, TypeError):
                    pass
            
            # Get other fields
            gender = data.get('gender') or ''
            
            # For VARCHAR columns - convert None to empty string
            height = data.get('height')
            weight = data.get('weight')
            
            # CRITICAL FIX: Convert None to empty string for VARCHAR columns
            if height is None or height == '':
                height = ''  # Empty string instead of NULL
            else:
                height = str(height)
            
            if weight is None or weight == '':
                weight = ''  # Empty string instead of NULL
            else:
                weight = str(weight)
            
            hair_color = data.get('hair_color') or ''
            eye_color = data.get('eye_color') or ''
            clothing_description = data.get('clothing_description') or ''
            date_last_seen = data.get('date_last_seen') or None
            approval_status = data.get('approval_status') or 'Pending'
            case_status = data.get('case_status') or 'Open'
            
            print(f"Height value being saved: '{height}'")
            print(f"Weight value being saved: '{weight}'")
            
            # Get current approval status for logging
            cursor.execute("SELECT approval_status, case_status FROM case_file WHERE case_id = %s", (case_id,))
            current_case = cursor.fetchone()
            before_approval = current_case['approval_status'] if current_case else 'unknown'
            before_case_status = current_case['case_status'] if current_case else 'unknown'
            
            # Get person_id
            cursor.execute("""
                SELECT cf.media_id, mpm.missing_person_id
                FROM case_file cf
                LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
                WHERE cf.case_id = %s
            """, (case_id,))
            
            result = cursor.fetchone()
            if not result:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Case not found'})
            
            person_id = result['missing_person_id']
            
            if not person_id:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Person not found for this case'})
            
            # Update missing person information
            if date_of_birth:
                cursor.execute("""
                    UPDATE missing_person_information 
                    SET first_name = %s, 
                        middle_name = %s, 
                        last_name = %s, 
                        date_of_birth = %s, 
                        gender = %s, 
                        height = %s, 
                        weight = %s,
                        hair_color = %s, 
                        eye_color = %s
                    WHERE person_id = %s
                """, (
                    first_name, middle_name, last_name, date_of_birth,
                    gender, height, weight,
                    hair_color, eye_color, person_id
                ))
            else:
                cursor.execute("""
                    UPDATE missing_person_information 
                    SET first_name = %s, 
                        middle_name = %s, 
                        last_name = %s, 
                        gender = %s, 
                        height = %s, 
                        weight = %s,
                        hair_color = %s, 
                        eye_color = %s
                    WHERE person_id = %s
                """, (
                    first_name, middle_name, last_name,
                    gender, height, weight,
                    hair_color, eye_color, person_id
                ))
            
            # Update case status and approval status
            cursor.execute("""
                UPDATE case_file SET approval_status = %s, case_status = %s WHERE case_id = %s
            """, (approval_status, case_status, case_id))
            
            # Log case status change if approval status changed
            if before_approval != approval_status:
                print(f"DEBUG: Logging approval status change - User: {session.get('full_name', 'Unknown')}, Role: {session.get('role', 'Unknown')}")
                log_case_status_change(cursor, case_id, previous_approval=before_approval, new_approval=approval_status)
            
            # Log case status change if case status changed
            if before_case_status != case_status:
                print(f"DEBUG: Logging case status change - User: {session.get('full_name', 'Unknown')}, Role: {session.get('role', 'Unknown')}")
                log_case_status_change(cursor, case_id, previous_status=before_case_status, new_status=case_status)
            
            # Update last seen information
            cursor.execute("""
                SELECT last_seen_id FROM case_file WHERE case_id = %s
            """, (case_id,))
            case_result = cursor.fetchone()
            
            if case_result and case_result['last_seen_id']:
                cursor.execute("""
                    UPDATE missing_person_last_seen
                    SET date_last_seen = %s, 
                        clothing_description = %s
                    WHERE missing_person_last_seen_id = %s
                """, (date_last_seen, clothing_description, case_result['last_seen_id']))
            
            conn.commit()
            
            # Log audit for editing report
            before_data = {'case_id': case_id, 'approval_status': 'previous_status'}
            after_data = {
                'full_name': full_name,
                'gender': gender,
                'height': height,
                'weight': weight,
                'approval_status': approval_status
            }
            log_audit(cursor, module='reports', action='edit',
                      target_table='case_file', target_id=case_id,
                      before=before_data, after=after_data)
            
            print(f"Successfully updated report {case_id}")
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Report updated successfully'})
            
        except Exception as e:
            print(f"Error in police_edit_report: {e}")
            import traceback
            traceback.print_exc()
            if conn:
                conn.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    return render_template('police/edit_report.html', case_id=case_id)


