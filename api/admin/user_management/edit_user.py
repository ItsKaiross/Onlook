from flask import Blueprint, session, render_template, redirect, url_for, flash, jsonify
from flask import request
from api.database import db
from datetime import datetime
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

edit_user_bp = Blueprint('edit_user_bp', __name__)

######################################
#########  E D I T  U S E R  #########
######################################

@edit_user_bp.route('/admin-user-management/edit-user', methods=['POST', 'GET'])
def admin_edit_user():
    if request.method == 'POST':
        userId = request.form.get('user_id', '')
        firstName = request.form.get('firstName', '')
        lastName = request.form.get('lastName', '')
        middleName = request.form.get('middleName', '')
        email = request.form.get('email', '')
        role = request.form.get('role', '')
        contact_number = request.form.get('number', '')
        
        # Database connection
        conn = db.get_db_connection()
        
        if conn is None:
            flash('Database connection failed', 'error')
            return redirect(url_for('admin_user_management'))
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get current user info
            cursor.execute(
                """
                SELECT role, officer_id, user_id
                FROM accounts
                WHERE accounts_id=%s
                """,
                (userId,)
            )
            user = cursor.fetchone()
            
            if not user:
                logger.warning(f'User not found for ID: {userId}')
                flash('User not found', 'error')
                return redirect(url_for('admin_user_management'))
            
            current_role = user['role']
            logger.info(f'Updating user {userId}: {current_role} -> {role}')
            logger.info(f'User data: officer_id={user["officer_id"]}, user_id={user["user_id"]}')
            
            # Validate role changes
            police_roles = ['policeAdmin', 'police'] + [
                'alaminos-mps', 'bay-mps', 'binancity-ps', 'cabuyaocity-ps',
                'calambacity-ps', 'calauan-mps', 'cavinti-mps', 'famy-mps',
                'kalayaan-mps', 'liliw-mps', 'sanpablocity-ps', 'santacruz-mps',
                'santarosacity-ps', 'siniloan-mps', 'victoria-mps'
            ]
            
            # Check if role change is valid
            if current_role == 'systemAdmin' and role in police_roles:
                # Changing from systemAdmin to police roles requires police record
                if not user['officer_id']:
                    logger.warning(f'Attempted to change systemAdmin to police role without officer_id for user {userId}')
                    flash('Cannot change System Admin to Police role: User must have a police record first', 'error')
                    return redirect(url_for('admin_user_management'))
            
            elif current_role in police_roles and role == 'systemAdmin':
                # Changing from police to systemAdmin - this should be allowed but with warning
                flash('Warning: Changing police user to System Admin role', 'warning')
            
            elif current_role == 'citizen' and role in police_roles:
                # Citizens cannot be changed to police roles without proper police record
                logger.warning(f'Attempted to change citizen to police role for user {userId}')
                flash('Cannot change Citizen to Police role: User must be registered as police officer first', 'error')
                return redirect(url_for('admin_user_management'))
            
            # Update based on current and new role
            if current_role in police_roles or current_role == 'systemAdmin':
                # Update accounts table
                cursor.execute('UPDATE accounts SET email=%s, role=%s WHERE accounts_id=%s', (email, role, userId))
                
                # Update police table if officer_id exists
                if user['officer_id']:
                    cursor.execute(
                        """
                        UPDATE police
                        SET first_name=%s,
                        last_name=%s,
                        middle_name=%s,
                        email=%s,
                        contact_number=%s
                        WHERE officer_id=%s
                        """,
                        (firstName, lastName, middleName, email, contact_number, user['officer_id'])
                    )
                else:
                    # Only show warning if trying to update police-related info without police record
                    if role in police_roles:
                        flash('Warning: Police record not found for this user', 'warning')
                    
            elif current_role == 'citizen':
                # Update accounts table
                cursor.execute('UPDATE accounts SET email=%s WHERE accounts_id=%s', (email, userId))
                
                # Update users table if user_id exists
                if user['user_id']:
                    cursor.execute(
                        """
                        UPDATE public_user
                        SET first_name=%s,
                        last_name=%s,
                        middle_name=%s,
                        email=%s
                        WHERE user_id=%s
                        """,
                        (firstName, lastName, middleName, email, user['user_id'])
                    )
            
            conn.commit()
            
            # Log audit for editing user
            before_data = {'role': current_role}
            after_data = {'email': email, 'role': role, 'firstName': firstName, 'lastName': lastName}
            log_audit(cursor, module='users', action='edit_user',
                      target_table='accounts', target_id=userId,
                      before=before_data, after=after_data)
            
            # Success message with role change info
            if current_role != role:
                flash(f'User updated successfully! Role changed from {current_role} to {role}', 'success')
            else:
                flash('User updated successfully!', 'success')
            
        except Exception as e:
            conn.rollback()
            logger.error(f'Error updating user {userId}: {str(e)}')
            flash(f'Error updating user: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
            
    return redirect(url_for('admin_user_management'))


