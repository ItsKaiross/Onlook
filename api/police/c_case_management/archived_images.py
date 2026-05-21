from flask import Blueprint, session, jsonify
from flask import request
from api.database import db
from datetime import datetime
import base64
import os
from api.utils.activity_logger import log_user_activity
now = datetime.now()
from api.audit import log_audit

archived_images_bp = Blueprint('archived_images_bp', __name__)

##################################################
#########  A R C H I V E D  I M A G E S  #########
##################################################

@archived_images_bp.route('/police-archived-images/<int:case_id>')
def police_archived_images(case_id):
    if not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        conn = db.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'error': 'Database connection failed'})
            
        cursor = conn.cursor(dictionary=True)
        
        # Check if archived columns exist
        cursor.execute("SHOW COLUMNS FROM missing_person_media LIKE 'is_archived'")
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'images': []})
        
        # Get archived images for this case
        cursor.execute("""
            SELECT mpm2.missing_person_media_id, mpm2.missing_filedata, mpm2.missing_filetype, mpm2.archived_at
            FROM missing_person_media mpm2
            JOIN missing_person_information mpi ON mpm2.missing_person_id = mpi.person_id
            JOIN missing_person_media mpm ON mpi.person_id = mpm.missing_person_id
            JOIN case_file cf ON mpm.missing_person_media_id = cf.media_id
            WHERE cf.case_id = %s AND mpm2.is_archived = 1 AND mpm2.missing_filedata IS NOT NULL
            ORDER BY mpm2.archived_at DESC
        """, (case_id,))
        
        archived_images = cursor.fetchall()
        case_images = []
        
        for i, img in enumerate(archived_images):
            if img.get('missing_filedata'):
                try:
                    img_data = base64.b64encode(img['missing_filedata']).decode('utf-8')
                    case_images.append({
                        'id': img['missing_person_media_id'],
                        'src': f"data:{img['missing_filetype']};base64,{img_data}",
                        'title': f"Archived Image {i + 1}",
                        'archived_at': str(img.get('archived_at', 'Unknown date'))
                    })
                except Exception as img_error:
                    print(f'Error processing archived image {img["missing_person_media_id"]}: {str(img_error)}')
                    continue
        
        cursor.close()
        conn.close()
        
        print(f'Retrieved {len(case_images)} archived images for case {case_id}')
        return jsonify({'success': True, 'images': case_images})
        
    except Exception as e:
        print(f'Error retrieving archived images for case {case_id}: {str(e)}')
        if 'conn' in locals():
            conn.close()
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'})


