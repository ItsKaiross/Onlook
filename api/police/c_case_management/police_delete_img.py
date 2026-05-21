from flask import Blueprint, session, jsonify
from flask import request
from api.database import db
from datetime import datetime
import base64
import os
from api.utils.activity_logger import log_user_activity
now = datetime.now()
from api.audit import log_audit

police_delete_img_bp = Blueprint('police_delete_img_bp', __name__)

############################################
#########  D E L E T E  I M A G E  #########
############################################

@police_delete_img_bp.route('/police-delete-image/<int:image_id>', methods=['DELETE'])
def police_delete_image(image_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Database connection failed'})
            
        cursor = conn.cursor()
        
        # Check if columns exist and add them if needed
        cursor.execute("SHOW COLUMNS FROM missing_person_media LIKE 'is_archived'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE missing_person_media ADD COLUMN is_archived BOOLEAN DEFAULT FALSE")
            conn.commit()
        
        cursor.execute("SHOW COLUMNS FROM missing_person_media LIKE 'archived_at'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE missing_person_media ADD COLUMN archived_at TIMESTAMP NULL")
            conn.commit()
        
        # Check if image exists and get current state for audit logging
        cursor.execute("SELECT missing_person_media_id, is_archived FROM missing_person_media WHERE missing_person_media_id = %s", (image_id,))
        current_image = cursor.fetchone()
        if not current_image:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Image not found'})
        
        before_data = {'is_archived': current_image[1] if len(current_image) > 1 else False}
        
        # Archive the image instead of deleting
        cursor.execute("""
            UPDATE missing_person_media 
            SET is_archived = 1, archived_at = NOW() 
            WHERE missing_person_media_id = %s
        """, (image_id,))
        
        # Log audit for image archiving
        log_audit(cursor, module='media', action='archive_image',
                  target_table='missing_person_media', target_id=image_id,
                  before=before_data, after={'is_archived': True})
        
        rowcount = cursor.rowcount
        conn.commit()
        
        conn.commit()
        log_user_activity('image_archived', 'success', f'{{"image_id": "{image_id}"}}', session.get('accounts_id'))
        print(f'Image {image_id} archived by user {session.get("accounts_id")}')
        
        cursor.close()
        conn.close()
        
        if rowcount > 0:
            return jsonify({'success': True, 'message': 'Image archived successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to archive image'})
        
    except Exception as e:
        print(f'Error archiving image {image_id}: {str(e)}')
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})


