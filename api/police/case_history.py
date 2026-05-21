# api/case_history.py
from app import app
from flask import Flask, session, render_template, redirect, url_for, flash, request, jsonify
from api.database import db
from datetime import datetime
import base64
from flask_mail import Mail, Message
import os
from api.audit import log_audit
import sys

def log_case_status_change(cursor, case_id, previous_status=None, new_status=None,
                            previous_approval=None, new_approval=None, notes=None):
    """
    Call this whenever case_status or approval_status changes.
    Drop this into any route that updates case_file.
    """
    try:
        print(f"[case_history] Input values - case_id: {case_id}, previous: '{previous_status}' (type: {type(previous_status)}), new: '{new_status}' (type: {type(new_status)})")
        print(f"[case_history] Session data - accounts_id: {session.get('accounts_id')}, full_name: '{session.get('full_name')}', role: '{session.get('role')}'")
        print(f"[case_history] All session keys: {list(session.keys())}")
        
        # Ensure we have valid status values
        final_new_status = new_status if new_status is not None and new_status != '' else 'Unknown'
        final_previous_status = previous_status if previous_status is not None and previous_status != '' else 'Unknown'
        
        print(f"[case_history] Final values - previous: '{final_previous_status}', new: '{final_new_status}'")
        
        # Get user name from session - try different possible keys
        user_name = session.get('full_name')
        if not user_name:
            first_name = session.get('firstName', '')
            last_name = session.get('lastName', '')
            if first_name or last_name:
                user_name = f"{first_name} {last_name}".strip()
            else:
                user_name = 'Unknown'
        
        cursor.execute("""
            INSERT INTO case_status_history (
                case_id,
                changed_by,
                changed_by_name,
                changed_by_role,
                previous_status,
                new_status,
                previous_approval,
                new_approval,
                notes,
                changed_at,
                ip_address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            case_id,
            session.get('accounts_id'),
            user_name,
            session.get('role', 'Unknown'),
            final_previous_status,
            final_new_status,
            previous_approval,
            new_approval if new_approval is not None else previous_approval,
            notes,
            datetime.now(),
            request.remote_addr,
        ])
        print(f"[case_history] Successfully logged status change for case {case_id}: {final_previous_status} -> {final_new_status} by {user_name}")
        
        # Verify the insert was successful
        cursor.execute("SELECT changed_by_name, changed_by_role FROM case_status_history WHERE case_id = %s ORDER BY changed_at DESC LIMIT 1", [case_id])
        last_entry = cursor.fetchone()
        if last_entry:
            print(f"[case_history] Verified stored data - Name: '{last_entry['changed_by_name']}', Role: '{last_entry['changed_by_role']}'")
    except Exception as e:
        print(f"[case_history] Logging error for case {case_id}: {e}", file=sys.stderr)
        raise e  # Re-raise to ensure calling code knows about the failure