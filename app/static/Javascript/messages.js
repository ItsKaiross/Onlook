let currentConversation = null;
let conversations = [];
let currentMessages = [];
let messagePollingInterval = null;
let lastMessageCount = 0;
let isSending = false;

// Load conversations on page load
document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    
    // Enter key to send message
    document.getElementById('message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
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
    
    // Start real-time polling for this conversation
    startMessagePolling(roomId);
}

function startMessagePolling(roomId) {
    // Clear any existing polling
    if (messagePollingInterval) {
        clearInterval(messagePollingInterval);
    }
    
    // Poll for new messages every 2 seconds
    messagePollingInterval = setInterval(() => {
        if (currentConversation === roomId) {
            loadMessages(roomId, true);
        }
    }, 2000);
}

function stopMessagePolling() {
    if (messagePollingInterval) {
        clearInterval(messagePollingInterval);
        messagePollingInterval = null;
    }
}

function loadMessages(roomId, isPolling = false) {
    if (!isPolling) {
    }
    
    fetch(`/api/messages/room/${roomId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Only update if message count changed (for polling)
                if (!isPolling || data.messages.length !== lastMessageCount) {
                    currentMessages = data.messages;
                    lastMessageCount = data.messages.length;
                    displayMessages(data.messages);
                    
                    if (isPolling && data.messages.length > lastMessageCount) {
                        // New message received, also update conversations list
                        loadConversations();
                    }
                }
            } else if (!isPolling) {
                console.error('Failed to load messages:', data.error);
            }
        })
        .catch(error => {
            if (!isPolling) {
                console.error('Error loading messages:', error);
            }
        });
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
        const senderName = isSent ? 'You' : msg.email;
        
        messageDiv.innerHTML = `
            <div>
                ${!isSent ? `<div class="message-sender">${senderName}</div>` : ''}
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
    
    if (!messageText || !currentConversation || isSending) return;
    
    isSending = true;
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.textContent = 'Sending...';
    }
    
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
        }
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
        isSending = false;
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
        }
    });
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
        item.onclick = () => startConversation(user.accounts_id, user.email);
        
        item.innerHTML = `
            <div class="user-item-info">
                <h4>${user.email}</h4>
            </div>
        `;
        
        container.appendChild(item);
    });
}

function startConversation(userId, displayName) {
    // Create conversation without sending initial message
    const roomId = `user_${userId}`;
    closeNewMessageModal();
    loadConversations();
    setTimeout(() => openConversation(roomId, displayName), 100);
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
    return window.currentUserId;
}

// Stop polling when page is hidden/closed
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopMessagePolling();
    } else if (currentConversation) {
        startMessagePolling(currentConversation);
    }
});

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('new-message-modal');
    if (event.target == modal) {
        closeNewMessageModal();
    }
}