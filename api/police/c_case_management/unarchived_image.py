from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
import base64
import os
from werkzeug.utils import secure_filename
from api.utils.activity_logger import log_user_activity
now = datetime.now()
current_date_time = now
from api.audit import log_audit

######################################################
#########  U N A R C H I V E D  I M A G E S  #########
######################################################

@app.route('/police-unarchive-image/<int:image_id>', methods=['POST'])
def police_unarchive_image(image_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Database connection failed'})
            
        cursor = conn.cursor()
        
        # Check if image exists and is archived
        cursor.execute("""
            SELECT missing_person_media_id, is_archived 
            FROM missing_person_media 
            WHERE missing_person_media_id = %s
        """, (image_id,))
        
        result = cursor.fetchone()
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Image not found'})
        
        if not result[1]:  # is_archived is False
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Image is not archived'})
        
        before_data = {'is_archived': True}
        
        # Unarchive the image
        cursor.execute("""
            UPDATE missing_person_media 
            SET is_archived = 0, archived_at = NULL 
            WHERE missing_person_media_id = %s
        """, (image_id,))
        
        # Log audit for image unarchiving
        log_audit(cursor, module='media', action='unarchive_image',
                  target_table='missing_person_media', target_id=image_id,
                  before=before_data, after={'is_archived': False})
        
        conn.commit()
        log_user_activity('image_unarchived', 'success', f'{{"image_id": "{image_id}"}}', session.get('accounts_id'))
        print(f'Image {image_id} unarchived by user {session.get("accounts_id")}')
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Image unarchived successfully'})
        
    except Exception as e:
        print(f'Error unarchiving image {image_id}: {str(e)}')
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})