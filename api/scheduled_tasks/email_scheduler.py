from app import app
from flask import url_for
from flask_mail import Mail, Message
from api.database import db
from datetime import datetime, timedelta
import schedule
import time
import threading

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'onlook2025@gmail.com'
app.config['MAIL_PASSWORD'] = 'ncts ioap hhrd hlwk'  
app.config['MAIL_DEFAULT_SENDER'] = 'onlook2025@gmail.com'

mail = Mail(app)

def send_post_approval_email():
    """Check for reports submitted 24 hours ago and send email to informants"""
    with app.app_context():
        conn = None
        cursor = None
        try:
            conn = db.get_db_connection()
            if not conn:
                return
                
            cursor = conn.cursor(dictionary=True)
            
            # Get reports submitted exactly 24 hours ago that haven't been emailed yet
            cursor.execute("""
                SELECT cf.case_id, cf.date_and_time_reported, cf.reporter_type, cf.reporter_id,
                       CONCAT(mpi.first_name, ' ', IFNULL(mpi.middle_name, ''), ' ', mpi.last_name) as missing_person_name,
                       CASE 
                           WHEN cf.reporter_type = 'user' THEN u.email
                           WHEN cf.reporter_type = 'no_account' THEN nau.email
                       END as informant_email,
                       CASE 
                           WHEN cf.reporter_type = 'user' THEN CONCAT(u.first_name, ' ', u.last_name)
                           WHEN cf.reporter_type = 'no_account' THEN CONCAT(nau.first_name, ' ', nau.last_name)
                       END as informant_name
                FROM case_file cf
                LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id
                LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
                LEFT JOIN accounts u ON cf.reporter_type = 'user' AND cf.reporter_id = u.accounts_id
                LEFT JOIN no_account_user nau ON cf.reporter_type = 'no_account' AND cf.reporter_id = nau.no_account_user_id
                WHERE DATE(cf.date_and_time_reported) = DATE(NOW() - INTERVAL 1 DAY)
                AND cf.email_sent_24h IS NULL
                AND mpi.person_id IS NOT NULL
                AND (u.email IS NOT NULL OR nau.email IS NOT NULL)
            """)
            
            reports = cursor.fetchall()
            
            for report in reports:
                if report['informant_email']:
                    # Generate unique token for response
                    token = f"{report['case_id']}_{int(time.time())}"
                    
                    # Send email
                    msg = Message(
                        subject='Post Your Missing Person Report - Onlook',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[report['informant_email']]
                    )
                    
                    post_url = f"http://localhost:5001/post-report-response/{token}/yes"
                    decline_url = f"http://localhost:5001/post-report-response/{token}/no"
                    
                    msg.html = f"""
                    <h2>Post Your Missing Person Report</h2>
                    <p>Dear {report['informant_name']},</p>
                    <p>Your missing person report for <strong>{report['missing_person_name']}</strong> was submitted 24 hours ago.</p>
                    <p>Would you like to post this report publicly to help with the search?</p>
                    <div style="margin: 20px 0;">
                        <a href="{post_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; margin-right: 10px;">Yes, Post Publicly</a>
                        <a href="{decline_url}" style="background-color: #f44336; color: white; padding: 10px 20px; text-decoration: none;">No, Keep Private</a>
                    </div>
                    <p>Thank you,<br>Onlook Team</p>
                    """
                    
                    mail.send(msg)
                    
                    # Update database to mark email as sent
                    cursor.execute("""
                        UPDATE case_file 
                        SET email_sent_24h = NOW(), post_token = %s 
                        WHERE case_id = %s
                    """, (token, report['case_id']))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error sending 24h emails: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass

def run_scheduler():
    """Run the scheduler in a separate thread"""
    schedule.every().hour.do(send_post_approval_email)
    
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"Scheduler error: {e}")
        time.sleep(60)

def start_email_scheduler():
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
