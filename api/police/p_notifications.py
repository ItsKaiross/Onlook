from flask import Blueprint, session, render_template, redirect, url_for
from api.database import db
import base64

p_notifications_bp = Blueprint('p_notifications_bp', __name__)

@p_notifications_bp.route('/police-notifications')
def police_notifications():
    if 'accounts_id' not in session or not (session.get('role') == 'police' or session.get('role', '').endswith('-mps') or session.get('role', '').endswith('-ps')):
        return redirect(url_for('login_bp.home'))

    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    accounts_id = session['accounts_id']

    cursor.execute("""
        SELECT
            cf.case_id,
            CONCAT(mpi.first_name, ' ', mpi.last_name) as reporter_name,
            cf.date_and_time_reported,
            TIMESTAMPDIFF(HOUR, cf.date_and_time_reported, NOW()) as hours_ago,
            COALESCE(pn.is_read, FALSE) as is_read
        FROM case_file cf
        LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
        LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
        LEFT JOIN police_notifications pn ON cf.case_id = pn.case_id AND pn.police_id = %s
        WHERE cf.date_and_time_reported >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        ORDER BY cf.date_and_time_reported DESC
        LIMIT 50
    """, (accounts_id,))
    results = cursor.fetchall()

    notifications = []
    unread_count = 0
    for notif in results:
        hours_ago = notif['hours_ago']
        if hours_ago < 1:
            time_ago = "Just now"
        elif hours_ago < 24:
            time_ago = f"{hours_ago} hours ago"
        else:
            days_ago = hours_ago // 24
            time_ago = f"{days_ago} day{'s' if days_ago > 1 else ''} ago"

        is_read = bool(notif['is_read'])
        if not is_read:
            unread_count += 1

        notifications.append({
            'case_id': notif['case_id'],
            'message': f"New missing person report for {notif['reporter_name'] or 'Unknown'}",
            'time_ago': time_ago,
            'is_read': is_read
        })

    cursor.execute("""
        SELECT p.first_name, p.last_name, p.middle_name, p.email,
        pp.profile_filedata, pp.profile_filetype
        FROM police p
        JOIN accounts acc ON p.officer_id = acc.accounts_id
        LEFT JOIN profile_pictures pp ON p.profile_picture_id = pp.profile_id
        WHERE acc.accounts_id = %s
    """, (accounts_id,))
    profile = cursor.fetchone()
    if profile and profile['profile_filedata']:
        profile['profile_filedata'] = base64.b64encode(profile['profile_filedata']).decode('utf-8')

    cursor.close()
    conn.close()

    return render_template(
        'police/police-base.html',
        page='police-notifications',
        notifications=notifications,
        notification_count=unread_count,
        profile=profile,
        loggedIn_email=session.get('email')
    )


