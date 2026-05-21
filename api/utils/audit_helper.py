from api.audit import log_audit
from flask import session
import json

def safe_log_audit(cursor, module, action, target_table=None, target_id=None,
                   before=None, after=None, status='success', remarks=None):
    """
    Safe wrapper for log_audit that handles exceptions gracefully
    """
    try:
        log_audit(cursor, module, action, target_table, target_id,
                  before, after, status, remarks)
    except Exception as e:
        print(f"[audit_helper] Failed to log audit: {e}")

def log_data_change(cursor, module, action, table_name, record_id, 
                    old_data=None, new_data=None, remarks=None):
    """
    Helper function to log data changes with before/after comparison
    """
    try:
        # Convert data to JSON-serializable format
        before_json = None
        after_json = None
        
        if old_data:
            before_json = {k: str(v) if v is not None else None for k, v in old_data.items()}
        if new_data:
            after_json = {k: str(v) if v is not None else None for k, v in new_data.items()}
        
        safe_log_audit(cursor, module=module, action=action,
                       target_table=table_name, target_id=record_id,
                       before=before_json, after=after_json,
                       status='success', remarks=remarks)
    except Exception as e:
        print(f"[audit_helper] Failed to log data change: {e}")

def log_file_operation(cursor, action, file_info, remarks=None):
    """
    Helper function to log file upload/delete operations
    """
    try:
        safe_log_audit(cursor, module='files', action=action,
                       target_table='files', target_id=file_info.get('file_id'),
                       after=file_info, status='success', remarks=remarks)
    except Exception as e:
        print(f"[audit_helper] Failed to log file operation: {e}")

def log_security_event(cursor, event_type, details=None, status='success'):
    """
    Helper function to log security-related events
    """
    try:
        safe_log_audit(cursor, module='security', action=event_type,
                       after=details, status=status,
                       remarks=f'Security event: {event_type}')
    except Exception as e:
        print(f"[audit_helper] Failed to log security event: {e}")

def log_system_event(cursor, event_type, details=None, remarks=None):
    """
    Helper function to log system-level events
    """
    try:
        safe_log_audit(cursor, module='system', action=event_type,
                       after=details, status='success', remarks=remarks)
    except Exception as e:
        print(f"[audit_helper] Failed to log system event: {e}")
