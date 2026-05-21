from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify, current_app
from flask import request
from api.database import db
from flask_mail import Mail, Message
from datetime import datetime, date
now = datetime.now()
current_date_time = now
import base64
import bcrypt
import logging
import os
from api.audit import log_audit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

a_user_management_bp = Blueprint('a_user_management_bp', __name__)

#############################################################
#########  A D M I N  U S E R  M A N A G E M E N T  #########
#############################################################

@a_user_management_bp.route('/admin-user-management')
def admin_user_management():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    roles = session.get('role')
    
    
    # Original code for page load
    search_query = request.args.get('search', '')
    role_filter = request.args.get('role_filter', '')
    status_filter = request.args.get('status_filter', '')
    
    user_page = request.args.get('user_page', 1, type=int)
    user_per_page = request.args.get('user_per_page', 10, type=int)
    offset = (user_page - 1) * user_per_page
    
    restricted_data = getRestrictedAccounts()
    
    loggedIn_email = None
    if loggedIn == True:
        loggedIn_email = userEmail
    
    # Database connection
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    if 'accounts_id' in session and session['role'] == 'systemAdmin':
        if conn is None:
            flash('Database connection error', 'error')
            return redirect(url_for('admin'))
        
        # Build dynamic query for system admin
        base_query = """
            FROM accounts a
            LEFT JOIN public_user u ON a.user_id = u.user_id
            LEFT JOIN police p ON a.officer_id = p.officer_id
            LEFT JOIN profile_pictures ppu ON u.profile_picture_id = ppu.profile_id
            LEFT JOIN profile_pictures ppp ON p.profile_picture_id = ppp.profile_id
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        if search_query:
            base_query += """ AND (
                COALESCE(u.first_name, p.first_name) LIKE %s 
                OR COALESCE(u.last_name, p.last_name) LIKE %s 
                OR a.email LIKE %s
                OR CONCAT(COALESCE(u.first_name, p.first_name), ' ', COALESCE(u.last_name, p.last_name)) LIKE %s
            )"""
            search_param = f'%{search_query}%'
            params.extend([search_param, search_param, search_param, search_param])
        
        if role_filter:
            base_query += " AND a.role = %s"
            params.append(role_filter)
        
        if status_filter:
            base_query += " AND a.status = %s"
            params.append(status_filter)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total {base_query}"
        cursor.execute(count_query, params)
        total_records = cursor.fetchone()['total']
        
        # Get filtered users
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
                COALESCE(ppu.profile_filedata, ppp.profile_filedata) AS validID
            {base_query}
            ORDER BY a.accounts_id ASC
            LIMIT %s OFFSET %s
        """
        
        select_params = params + [user_per_page, offset]
        cursor.execute(select_query, select_params)
        users = cursor.fetchall() or []
        total_pages = (total_records + user_per_page - 1) // user_per_page

    
    return render_template(
        'admin/admin-base.html',
        page='admin-user-management',
        user_page=user_page,
        user_per_page=user_per_page,
        total_pages=total_pages,
        total_records=total_records,
        loggedIn_email=loggedIn_email,
        users=users,
        roles=roles,
        search_query=search_query,
        role_filter=role_filter,
        status_filter=status_filter,
        restricted=restricted_data['restricted_users'],
        restricted_page=restricted_data['restricted_page'],
        restricted_per_page=restricted_data['restricted_per_page'],
        total_restricted_pages=restricted_data['total_restricted_pages'],
        total_restricted_records=restricted_data['total_restricted_records'],
        
    )

def getRestrictedAccounts():
    userEmail = session.get('email')
    loggedIn = session.get('loggedIn')
    roles = session.get('role')
    
    restricted_page = request.args.get('restricted_page', 1, type=int)
    restricted_per_page = request.args.get('restricted_per_page', 10, type=int)
    offset = (restricted_page - 1) * restricted_per_page
    
    conn = db.get_db_connection()
    if conn is None:
        return {
            'restricted_users': [],
            'restricted_page': restricted_page,
            'restricted_per_page': restricted_per_page,
            'total_restricted_pages': 1,
            'total_restricted_records': 0
        }
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    cursor.execute(
        """
        SELECT COUNT(*) as total
        FROM accounts
        WHERE status='restricted'
        """
    )
    total_restricted_records = cursor.fetchone()['total']
    
    cursor.execute(
        """
        SELECT
            a.accounts_id,
            a.email,
            a.role,
            a.status,
            COALESCE(u.contact_number, p.contact_number) AS contact_number,
            COALESCE(u.first_name, p.first_name) AS firstName,
            COALESCE(u.last_name, p.last_name) AS lastName,
            COALESCE(u.middle_name, p.middle_name) AS middleName,
            COALESCE(CONCAT(u.first_name, ' ', u.last_name), CONCAT(p.first_name, ' ', p.last_name)) AS full_name,
            COALESCE(ppu.profile_filedata, ppp.profile_filedata) AS validID
        FROM accounts a
        LEFT JOIN public_user u ON a.user_id = u.user_id
        LEFT JOIN police p ON a.officer_id = p.officer_id
        LEFT JOIN profile_pictures ppu ON u.profile_picture_id = ppu.profile_id
        LEFT JOIN profile_pictures ppp ON p.profile_picture_id = ppp.profile_id
        WHERE a.status='restricted'
        ORDER BY a.accounts_id ASC
        LIMIT %s OFFSET %s
        """, (restricted_per_page, offset)
        )
    restricted_users = cursor.fetchall() or []
    total_restricted_pages = (total_restricted_records + restricted_per_page - 1) // restricted_per_page
    
    cursor.close()
    conn.close()
    
    # Encode validID images to base64
    for user in restricted_users:
        if user.get('validID'):
            user['validID'] = base64.b64encode(user['validID']).decode('utf-8')
        else:
            user['validID'] = None
            
    return {
        'restricted_users' : restricted_users,
        'restricted_page' : restricted_page,
        'restricted_per_page' : restricted_per_page,
        'total_restricted_pages' : total_restricted_pages,
        'total_restricted_records' : total_restricted_records
    }



