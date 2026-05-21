let currentConversation = null;
let conversations = [];
let currentMessages = [];

// Load conversations on page load
document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    
    // Enter key to send message
    document.getElementById('message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});

function loadConversations() {
    fetch('/api/messages/conversations')
        .then(response => {
            return response.json();
        })
        .then(data => {
            if (data.success) {
                conversations = data.conversations;
                displayConversations(conversations);
            } else {
                console.error('Error loading conversations:', data.error);
                document.getElementById('conversations-list').innerHTML = '<div class="error">Error loading conversations</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('conversations-list').innerHTML = '<div class="error">Error loading conversations</div>';
        });
}

function displayConversations(convs) {
    const container = document.getElementById('conversations-list');
    container.innerHTML = '';
    
    convs.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        item.onclick = () => openConversation(conv.room_id, conv.display_name, item);
        
        const avatar = '/static/icons/user-default.png';
        const lastMessage = conv.last_message || 'No messages yet';
        const time = formatTime(conv.last_message_time);
        
        item.innerHTML = `
            <div class="conversation-info">
                <div class="conversation-name">${conv.display_name}</div>
                <div class="conversation-preview">${lastMessage}</div>
            </div>
            <div class="conversation-time">${time}</div>
        `;
        
        container.appendChild(item);
    });
}

function openConversation(roomId, displayName, element) {
    
    // Check if this is a user ID format but treat it as a room ID
    // Don't redirect to startConversation for existing conversations
    
    currentConversation = roomId;
    
    // Update active conversation
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    if (element) {
        element.classList.add('active');
    }
    
    // Hide no-conversation message
    const noConv = document.querySelector('.no-conversation');
    if (noConv) {
        noConv.style.display = 'none';
    }
    
    // Show chat header and input
    const chatHeader = document.getElementById('chat-header');
    const inputArea = document.getElementById('message-input-area');
    
    if (chatHeader) {
        chatHeader.style.display = 'block';
    }
    if (inputArea) {
        inputArea.style.display = 'block';
    }
    
    // Update header
    const chatUsername = document.getElementById('chat-username');
    if (chatUsername) {
        chatUsername.textContent = displayName;
    }
    
    // Load messages
    loadMessages(roomId);
}

function loadMessages(roomId) {
    fetch(`/api/messages/room/${roomId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentMessages = data.messages;
                displayMessages(data.messages);
            } else {
                console.error('Failed to load messages:', data.error);
            }
        })
        .catch(error => console.error('Error loading messages:', error));
}

function displayMessages(messages) {
    const container = document.getElementById('messages-area');
    if (!container) {
        console.error('Messages area container not found');
        return;
    }
    
    container.innerHTML = '';
    
    if (messages.length === 0) {
        container.innerHTML = '<div class="no-messages">No messages yet. Start the conversation!</div>';
        return;
    }
    
    messages.forEach(msg => {
        const messageDiv = document.createElement('div');
        const isSent = msg.sender_id == getCurrentUserId();
        messageDiv.className = `message ${isSent ? 'sent' : 'received'}`;
        
        const time = formatTime(msg.sent_at);
        
        messageDiv.innerHTML = `
            <div>
                <div class="message-content">${msg.message_text}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
        
        container.appendChild(messageDiv);
    });
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const messageText = input.value.trim();
    
    if (!messageText || !currentConversation) return;
    
    // Send message to current room
    fetch('/api/messages/send-to-room', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            room_id: currentConversation,
            message_text: messageText,
            message_type: 'text'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            input.value = '';
            loadMessages(currentConversation);
            loadConversations();
        }
    })
    .catch(error => console.error('Error:', error));
}

function openNewMessageModal() {
    document.getElementById('new-message-modal').style.display = 'block';
}

function closeNewMessageModal() {
    document.getElementById('new-message-modal').style.display = 'none';
    document.getElementById('user-search').value = '';
    document.getElementById('users-list').innerHTML = '';
}

function searchUsers() {
    const query = document.getElementById('user-search').value.trim();
    if (query.length < 2) {
        document.getElementById('users-list').innerHTML = '';
        return;
    }
    
    fetch(`/api/users/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayUsers(data.users);
            }
        })
        .catch(error => console.error('Error:', error));
}

function displayUsers(users) {
    const container = document.getElementById('users-list');
    container.innerHTML = '';
    
    users.forEach(user => {
        const item = document.createElement('div');
        item.className = 'user-item';
        item.onclick = () => startConversation(user.accounts_id, `${user.first_name} ${user.last_name}`);
        
        const avatar = '/static/icons/user-default.png';
        
        item.innerHTML = `
            <div class="user-item-info">
                <h4>${user.first_name} ${user.last_name}</h4>
                <p>${user.email}</p>
            </div>
        `;
        
        container.appendChild(item);
    });
}

function startConversation(userId, displayName) {
    // Send initial message to create room
    fetch('/api/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            receiver_id: userId,
            message_text: 'Hello!',
            message_type: 'text'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeNewMessageModal();
            loadConversations();
            setTimeout(() => openConversation(data.room_id, displayName), 100);
        }
    })
    .catch(error => console.error('Error:', error));
}

function formatTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'now';
    if (diff < 3600000) return Math.floor(diff / 60000) + 'm';
    if (diff < 86400000) return Math.floor(diff / 3600000) + 'h';
    if (diff < 604800000) return Math.floor(diff / 86400000) + 'd';
    
    return date.toLocaleDateString();
}

function getCurrentUserId() {
    // This should be set from the session or passed from the backend
    return window.currentUserId || 1; // Placeholder
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('new-message-modal');
    if (event.target == modal) {
        closeNewMessageModal();
    }
}