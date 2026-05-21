from flask import Blueprint, jsonify, session, render_template, redirect, url_for, request
from api.database import db

messages_bp = Blueprint('messages_api', __name__)

@messages_bp.route('/messages')
def messages_page():
    if 'accounts_id' not in session:
        return redirect(url_for('login'))
    return render_template('messages.html', loggedIn_email=session.get('email'))

@messages_bp.route('/api/messages/conversations')
def get_conversations():
    if 'accounts_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        current_user_id = session.get('accounts_id')
        
        cursor.execute("""
            SELECT DISTINCT 
                CASE 
                    WHEN m.sender_id = %s THEN m.receiver_id 
                    ELSE m.sender_id 
                END as other_user_id,
                a.email, a.role,
                (SELECT message_text FROM messages m2 
                WHERE (m2.sender_id = %s AND m2.receiver_id = other_user_id) 
                    OR (m2.sender_id = other_user_id AND m2.receiver_id = %s)
                ORDER BY m2.sent_at DESC LIMIT 1) as last_message,
                (SELECT sent_at FROM messages m2 
                WHERE (m2.sender_id = %s AND m2.receiver_id = other_user_id) 
                    OR (m2.sender_id = other_user_id AND m2.receiver_id = %s)
                ORDER BY m2.sent_at DESC LIMIT 1) as last_message_time
            FROM messages m
            JOIN accounts a ON (CASE WHEN m.sender_id = %s THEN m.receiver_id ELSE m.sender_id END) = a.accounts_id
            WHERE m.sender_id = %s OR m.receiver_id = %s
            ORDER BY last_message_time DESC
        """, (current_user_id, current_user_id, current_user_id, current_user_id, current_user_id, current_user_id, current_user_id, current_user_id))
        
        users = cursor.fetchall()
        
        conversations = []
        for user in users:
            display_name = f"{user['email']} ({user['role']})"
            conversations.append({
                'room_id': f"user_{user['other_user_id']}",
                'display_name': display_name,
                'last_message': user['last_message'] or 'No messages yet',
                'last_message_time': user['last_message_time'],
                'user_id': user['other_user_id']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'conversations': conversations})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'})

@messages_bp.route('/api/users/search')
def search_users():
    if 'accounts_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        query = request.args.get('q', '')
        if len(query) < 2:
            return jsonify({'success': True, 'users': []})
        
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        current_user_id = session.get('accounts_id')
        cursor.execute("""
            SELECT accounts_id, email
            FROM accounts 
            WHERE accounts_id != %s 
            AND email LIKE %s
            LIMIT 10
        """, (current_user_id, f'%{query}%'))
        
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@messages_bp.route('/api/messages/send', methods=['POST'])
def send_message():
    from api.audit import log_audit
    from api.utils.activity_logger import log_user_activity

    if 'accounts_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        message_text = data.get('message_text')
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message_text, sent_at)
            VALUES (%s, %s, %s, NOW())
        """, (session['accounts_id'], receiver_id, message_text))
        
        message_id = cursor.lastrowid
        
        log_audit(cursor, module='messages', action='send',
                  target_table='messages', target_id=message_id,
                  after={'receiver_id': receiver_id, 'message_text': message_text[:50] + '...' if len(message_text) > 50 else message_text},
                  status='success', remarks=f'Message sent to user {receiver_id}')
        
        conn.commit()
        log_user_activity('message_sent', 'success', f'{{"receiver_id": "{receiver_id}"}}', session['accounts_id'])
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Message sent', 'room_id': f'user_{receiver_id}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@messages_bp.route('/api/messages/room/<room_id>')
def get_room_messages(room_id):
    if 'accounts_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        if room_id.startswith('user_'):
            other_user_id = room_id.replace('user_', '')
        else:
            return jsonify({'success': False, 'error': 'Invalid room ID'})
        
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        current_user_id = session.get('accounts_id')
        
        cursor.execute("""
            SELECT m.*, a.email
            FROM messages m
            JOIN accounts a ON m.sender_id = a.accounts_id
            WHERE (m.sender_id = %s AND m.receiver_id = %s) 
            OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.sent_at ASC
        """, (current_user_id, other_user_id, other_user_id, current_user_id))
        
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@messages_bp.route('/api/messages/send-to-room', methods=['POST'])
def send_message_to_room():
    from api.audit import log_audit
    from api.utils.activity_logger import log_user_activity

    if 'accounts_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        data = request.get_json()
        room_id = data.get('room_id')
        message_text = data.get('message_text')
        
        if room_id.startswith('user_'):
            receiver_id = room_id.replace('user_', '')
        else:
            return jsonify({'success': False, 'error': 'Invalid room ID'})
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message_text, sent_at)
            VALUES (%s, %s, %s, NOW())
        """, (session['accounts_id'], receiver_id, message_text))
        
        message_id = cursor.lastrowid
        
        log_audit(cursor, module='messages', action='send_to_room',
                  target_table='messages', target_id=message_id,
                  after={'receiver_id': receiver_id, 'room_id': room_id, 'message_text': message_text[:50] + '...' if len(message_text) > 50 else message_text},
                  status='success', remarks=f'Message sent to room {room_id}')
        
        conn.commit()
        log_user_activity('message_sent_to_room', 'success', f'{{"room_id": "{room_id}"}}', session['accounts_id'])
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Message sent'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@messages_bp.route('/api/messages/unread-count')
def get_unread_count():
    if 'accounts_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        current_user_id = session.get('accounts_id')
        
        cursor.execute("""
            SELECT COUNT(*) as unread_count
            FROM messages 
            WHERE receiver_id = %s
        """, (current_user_id,))
        
        result = cursor.fetchone()
        unread_count = result[0] if result else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'unread_count': unread_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
