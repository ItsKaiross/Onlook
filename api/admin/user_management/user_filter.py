from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
now = datetime.now()
current_date_time = now
import base64
import bcrypt
import logging
import os
from api.audit import log_audit

##########################################
#########  U S E R  F I L T E R  #########
##########################################

@app.route('/users/filter', methods=['POST'])
def filter_users():
    import traceback
    import sys
    
    try:
        print("=" * 60, file=sys.stderr)
        print("FILTER START", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        
        # Check auth
        print(f"Session keys: {list(session.keys())}", file=sys.stderr)
        print(f"Role: {session.get('role')}", file=sys.stderr)
        
        if 'accounts_id' not in session or session.get('role') != 'systemAdmin':
            print("AUTH FAILED", file=sys.stderr)
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get data
        data = request.get_json(silent=True)
        print(f"Received data: {data}", file=sys.stderr)
        
        if not data:
            data = {}
        
        search = str(data.get('search', '')).strip()
        role_filter = str(data.get('role', '')).strip()
        status_filter = str(data.get('status', '')).strip()
        
        try:
            user_page = int(data.get('user_page', 1))
            user_per_page = int(data.get('user_per_page', 10))
        except:
            user_page = 1
            user_per_page = 10
        
        
        if user_page < 1:
            user_page = 1
        if user_per_page < 1 or user_per_page > 100:
            user_per_page = 10
            
        offset = (user_page - 1) * user_per_page
        
        # Database
        print("Connecting to database...", file=sys.stderr)
        conn = db.get_db_connection()
        print(f"Connection: {conn}", file=sys.stderr)
        
        cursor = conn.cursor(dictionary=True)
        print("Cursor created", file=sys.stderr)
        
        if session['role'] == 'systemAdmin':
            base_query = """
            FROM accounts a
            LEFT JOIN public_user u ON a.user_id = u.user_id
            LEFT JOIN police p ON a.officer_id = p.officer_id
            LEFT JOIN profile_pictures ppu ON u.profile_picture_id = ppu.profile_id
            LEFT JOIN profile_pictures ppp ON p.profile_picture_id = ppp.profile_id
            WHERE a.status != 'restricted'
            """
            
            params = []

            # Search Filter
            if search:
                print("Adding search filter", file=sys.stderr)
                base_query += """ AND (
                    COALESCE(u.first_name, p.first_name) LIKE %s OR
                    COALESCE(u.last_name, p.last_name) LIKE %s OR
                    a.email LIKE %s OR
                    CONCAT(COALESCE(u.first_name, p.first_name), ' ', COALESCE(u.last_name, p.last_name)) LIKE %s
                )"""
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param, search_param])
                
            # Role Filter
            if role_filter:
                print("Adding role filter", file=sys.stderr)
                base_query += " AND a.role = %s"
                params.append(role_filter)
            
            # Status Filter
            if status_filter:
                print("Adding status filter", file=sys.stderr)
                base_query += " AND a.status = %s"
                params.append(status_filter)
            
            print(f"Base query: {base_query}", file=sys.stderr)
            print(f"Params: {params}", file=sys.stderr)
            
            # Count query
            print("Running count query...", file=sys.stderr)
            count_query = f"SELECT COUNT(*) as total {base_query}"
            print(f"Count SQL: {count_query}", file=sys.stderr)
            
            cursor.execute(count_query, params)
            result = cursor.fetchone()
            total_records = result['total'] if result else 0
            print(f"Total records: {total_records}", file=sys.stderr)
            
            # Select query
            print("Running select query...", file=sys.stderr)
            select_query = f"""
            SELECT
                a.accounts_id,
                a.email,
                a.role,
                a.status,
                COALESCE(u.contact_number, p.contact_number) AS contact_number,
                COALESCE(u.first_name, p.first_name) AS firstName,
                COALESCE(u.last_name, p.last_name) AS lastName,
                COALESCE(u.middle_name, p.middle_name) AS middleName,
                COALESCE(CONCAT(u.first_name, ' ', u.last_name), 
                        CONCAT(p.first_name, ' ', p.last_name)) AS full_name,
                COALESCE(ppu.profile_filedata, ppp.profile_filedata) AS profilePic,
                (SELECT psa_filedata FROM psa WHERE psa.psa_id = u.psa LIMIT 1) AS psa,
                (SELECT psa_filetype FROM psa WHERE psa.psa_id = u.psa LIMIT 1) AS psa_type,
                (SELECT valid_id_filedata FROM valid_id WHERE valid_id.valid_id_id = u.valid_id LIMIT 1) AS validID,
                (SELECT valid_id_filetype FROM valid_id WHERE valid_id.valid_id_id = u.valid_id LIMIT 1) AS validID_type
            {base_query}
            ORDER BY a.accounts_id ASC
            LIMIT %s OFFSET %s
            """
            
            select_params = params + [user_per_page, offset]
            print(f"Select params: {select_params}", file=sys.stderr)
            
            cursor.execute(select_query, select_params)
            users = cursor.fetchall() or []
            print(f"Users fetched: {len(users)}", file=sys.stderr)
            
            cursor.close()
            conn.close()
            print("Connection closed", file=sys.stderr)
            
            # Encode images
            for user in users:
                # Encode profile picture
                if user.get('profilePic'):
                    try:
                        if isinstance(user['profilePic'], str):
                            user['profilePic'] = base64.b64encode(user['profilePic'].encode('latin-1')).decode('utf-8')
                        else:
                            user['profilePic'] = base64.b64encode(user['profilePic']).decode('utf-8')
                    except Exception as e:
                        print(f"Profile pic encode error: {e}", file=sys.stderr)
                        user['profilePic'] = None
                else:
                    user['profilePic'] = None
                
                # Encode PSA
                if user.get('psa'):
                    try:
                        if isinstance(user['psa'], str):
                            user['psa'] = base64.b64encode(user['psa'].encode('latin-1')).decode('utf-8')
                        else:
                            user['psa'] = base64.b64encode(user['psa']).decode('utf-8')
                    except Exception as e:
                        print(f"PSA encode error: {e}", file=sys.stderr)
                        user['psa'] = None
                else:
                    user['psa'] = None
                
                # Keep PSA type
                user['psa_type'] = user.get('psa_type', 'application/pdf')
                
                # Encode valid ID
                if user.get('validID'):
                    try:
                        if isinstance(user['validID'], str):
                            user['validID'] = base64.b64encode(user['validID'].encode('latin-1')).decode('utf-8')
                        else:
                            user['validID'] = base64.b64encode(user['validID']).decode('utf-8')
                    except Exception as e:
                        print(f"Valid ID encode error: {e}", file=sys.stderr)
                        user['validID'] = None
                else:
                    user['validID'] = None
                
                # Keep Valid ID type
                user['validID_type'] = user.get('validID_type', 'image/jpeg')
            
            total_pages = (total_records + user_per_page - 1) // user_per_page if total_records > 0 else 1
            
            print("SUCCESS - Returning response", file=sys.stderr)
            
            return jsonify({
                'success': True,
                'users': users,
                'total_records': total_records,
                'total_pages': total_pages,
                'user_page': user_page,
                'user_per_page': user_per_page
            })
        else:
            print("UNAUTHORIZED ROLE", file=sys.stderr)
            return jsonify({'success': False, 'error': 'Unauthorized role'}), 403
            
    except Exception as e:
        print("=" * 60, file=sys.stderr)
        print("!!! ERROR !!!", file=sys.stderr)
        print(f"Exception: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500