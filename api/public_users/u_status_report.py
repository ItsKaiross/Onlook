from flask import Flask, session, render_template, redirect, url_for, flash, request, jsonify
from api.database import db
from api.audit import log_audit

####################################################################
#########  P U B L I C  P A G E  S T A T U S  R E P O R T  #########
####################################################################

@app.route('/status-report')
def status_report():
    if 'accounts_id' in session and session['role'] == 'user':
        userEmail = session.get('email')
        loggedIn = session.get('loggedIn')
        user_id = session.get('accounts_id')
        
        loggedIn_email = None
        user_reports = []
        profile = None
        
        if loggedIn == True:
            loggedIn_email = userEmail
            
            # Fetch reports made by this user
            try:
                conn = db.get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    # Fetch user profile picture
                    cursor.execute("""
                        SELECT pp.profile_filedata, pp.profile_filetype
                        FROM accounts a
                        LEFT JOIN public_user p ON a.user_id = p.user_id
                        LEFT JOIN profile_pictures pp ON p.profile_picture_id = pp.profile_id
                        WHERE a.accounts_id = %s
                    """, (user_id,))
                    profile_result = cursor.fetchone()
                    
                    if profile_result and profile_result['profile_filedata']:
                        import base64
                        profile = {
                            'profile_filedata': base64.b64encode(profile_result['profile_filedata']).decode('utf-8'),
                            'profile_filetype': profile_result['profile_filetype']
                        }
                    
                    print(f"DEBUG: Fetching reports for user_id: {user_id}")
                    
                    query = """
                        SELECT 
                            cf.case_id,
                            cf.case_status,
                            cf.approval_status,
                            cf.priority,
                            cf.date_and_time_reported,
                            cf.media_id,
                            CONCAT(IFNULL(mpi.first_name, ''), ' ', IFNULL(mpi.middle_name, ''), ' ', IFNULL(mpi.last_name, '')) as full_name,
                            mpi.gender,
                            mpi.date_of_birth,
                            TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
                            mpls.date_last_seen,
                            mpls.circumstances,
                            CONCAT(IFNULL(p.rank, ''), ' ', IFNULL(p.last_name, '')) AS assigned_officer
                        FROM case_file cf
                        LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
                        LEFT JOIN missing_person_information mpi ON mpls.person_id = mpi.person_id
                        LEFT JOIN police p ON cf.assigned_officer_id = p.officer_id
                        WHERE cf.reporter_type = 'user' AND cf.reporter_id = %s
                        ORDER BY cf.date_and_time_reported DESC
                    """
                    
                    cursor.execute(query, (user_id,))
                    results = cursor.fetchall()
                    
                    print(f"DEBUG: Found {len(results)} reports")
                    
                    for result in results:
                        print(f"DEBUG: Processing case_id {result['case_id']}, media_id: {result['media_id']}")
                        
                        # Fetch image separately if media_id exists
                        image_data = None
                        if result['media_id']:
                            try:
                                image_query = "SELECT missing_filedata, missing_filetype FROM missing_person_media WHERE missing_person_media_id = %s"
                                cursor.execute(image_query, (result['media_id'],))
                                image_result = cursor.fetchone()
                                
                                print(f"DEBUG: Image query executed for media_id {result['media_id']}")
                                print(f"DEBUG: Image result: {image_result is not None}")
                                
                                if image_result:
                                    print(f"DEBUG: missing_filedata exists: {image_result['missing_filedata'] is not None}")
                                    print(f"DEBUG: missing_filetype: {image_result['missing_filetype']}")
                                    
                                    if image_result['missing_filedata'] and image_result['missing_filetype']:
                                        import base64
                                        image_base64 = base64.b64encode(image_result['missing_filedata']).decode('utf-8')
                                        image_data = f"data:{image_result['missing_filetype']};base64,{image_base64}"
                                        print(f"DEBUG: Image successfully encoded for case_id {result['case_id']}, length: {len(image_base64)}")
                                    else:
                                        print(f"DEBUG: Image data or type is None for media_id {result['media_id']}")
                                else:
                                    print(f"DEBUG: No record found in missing_person_media for media_id {result['media_id']}")
                            except Exception as img_error:
                                print(f"DEBUG: Error fetching image for media_id {result['media_id']}: {img_error}")
                                import traceback
                                traceback.print_exc()
                        else:
                            print(f"DEBUG: No media_id for case_id {result['case_id']}")
                        
                        print(f"DEBUG: Adding report - case_id: {result['case_id']}, has_image: {image_data is not None}")
                        
                        user_reports.append({
                            'case_id': result['case_id'],
                            'full_name': result['full_name'].strip() if result['full_name'] else 'Unknown',
                            'case_status': result['case_status'] if result['case_status'] else 'Active',
                            'approval_status': result['approval_status'] if result['approval_status'] else 'Pending',
                            'priority': result['priority'] if result['priority'] else 'Medium',
                            'date_reported': result['date_and_time_reported'].strftime('%B %d, %Y %I:%M %p') if result['date_and_time_reported'] else 'Unknown',
                            'age': result['age'] if result['age'] else 'Unknown',
                            'gender': result['gender'] if result['gender'] else 'Unknown',
                            'date_last_seen': result['date_last_seen'].strftime('%B %d, %Y') if result['date_last_seen'] else 'Unknown',
                            'circumstances': result['circumstances'] if result['circumstances'] else 'No details provided',
                            'assigned_officer': result['assigned_officer'].strip() if result['assigned_officer'] and result['assigned_officer'].strip() else 'Not assigned',
                            'image': image_data
                        })
                    
                    print(f"DEBUG: Total reports added: {len(user_reports)}")
                    
                    cursor.close()
                    conn.close()
            except Exception as e:
                print(f"Error fetching user reports: {e}")
                import traceback
                traceback.print_exc()
        
        return render_template('public_users/10u-status_report.html', 
                             loggedIn_email=loggedIn_email, 
                             user_reports=user_reports,
                             profile=profile,
                             role=session.get('role')), 200
    return redirect(url_for('public_users'))

@app.route('/check-status', methods=['POST'])
def check_status():
    if 'accounts_id' not in session or session['role'] != 'user':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        data = request.get_json()
        first_name = data.get('first_name', '').strip()
        middle_name = data.get('middle_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        if not first_name or not last_name:
            return jsonify({'success': False, 'message': 'First name and last name are required'})
        
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Database connection failed'})
        
        cursor = conn.cursor(dictionary=True)
        
        # Search for missing person reports matching the name
        query = """
            SELECT 
                cf.case_id,
                cf.case_status,
                cf.approval_status,
                cf.priority,
                cf.date_and_time_reported,
                CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name) as full_name,
                mpi.first_name,
                mpi.middle_name,
                mpi.last_name,
                mpi.gender,
                mpi.date_of_birth,
                TIMESTAMPDIFF(YEAR, mpi.date_of_birth, CURDATE()) AS age,
                mpls.date_last_seen,
                mpls.circumstances,
                CONCAT(p.rank, ' ', p.last_name) AS assigned_officer
            FROM case_file cf
            LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
            LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
            LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
            LEFT JOIN police p ON cf.assigned_officer_id = p.officer_id
            WHERE mpi.first_name LIKE %s 
                AND mpi.last_name LIKE %s
        """
        
        params = [f"%{first_name}%", f"%{last_name}%"]
        
        # Add middle name condition if provided
        if middle_name:
            query += " AND mpi.middle_name LIKE %s"
            params.append(f"%{middle_name}%")
        
        query += " ORDER BY cf.date_and_time_reported DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not results:
            return jsonify({
                'success': True, 
                'message': 'No missing person reports found matching the provided name.',
                'results': []
            })
        
        # Format results for response
        formatted_results = []
        for result in results:
            formatted_results.append({
                'case_id': result['case_id'],
                'full_name': result['full_name'],
                'case_status': result['case_status'],
                'approval_status': result['approval_status'],
                'priority': result['priority'],
                'date_reported': str(result['date_and_time_reported']),
                'age': result['age'],
                'gender': result['gender'],
                'date_last_seen': str(result['date_last_seen']) if result['date_last_seen'] else None,
                'circumstances': result['circumstances'],
                'assigned_officer': result['assigned_officer']
            })
        
        return jsonify({
            'success': True,
            'message': f'Found {len(results)} matching report(s)',
            'results': formatted_results
        })
        
    except Exception as e:
        print(f"Error in check_status: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while searching'})

####################################################################
#########  P U B L I C  P A G E  S T A T U S  R E P O R T  #########
####################################################################


