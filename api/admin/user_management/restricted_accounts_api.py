from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
import base64

restricted_accounts_bp = Blueprint('restricted_accounts_bp', __name__)

@restricted_accounts_bp.route('/admin-user-management/restricted-accounts', methods=['POST'])
def get_restricted_accounts():
    try:
        # Check auth
        if 'accounts_id' not in session or session.get('role') != 'systemAdmin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get pagination params
        data = request.get_json()
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 10))
        
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        offset = (page - 1) * per_page
        
        # Database connection
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get total count
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM accounts
            WHERE status='restricted'
            """
        )
        total_records = cursor.fetchone()['total']
        
        # Get restricted users
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
            """, (per_page, offset)
        )
        users = cursor.fetchall() or []
        
        cursor.close()
        conn.close()
        
        # Encode validID images to base64
        for user in users:
            if user.get('validID'):
                user['validID'] = base64.b64encode(user['validID']).decode('utf-8')
            else:
                user['validID'] = None
        
        total_pages = (total_records + per_page - 1) // per_page if total_records > 0 else 1
        
        return jsonify({
            'success': True,
            'users': users,
            'total_records': total_records,
            'total_pages': total_pages,
            'page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


