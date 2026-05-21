// Global Messages Widget
class GlobalMessages {
    constructor() {
        this.isOpen = false;
        this.conversations = [];
        this.unreadCount = 0;
        this.lastTotalMessages = 0;
        this.init();
    }

    init() {
        this.createWidget();
        this.loadConversations();
        this.bindEvents();
        this.startPolling();
    }

    createWidget() {
        const widget = document.createElement('div');
        widget.className = 'messages-widget';
        widget.innerHTML = `
            <button class="messages-toggle" onclick="globalMessages.toggle()">
                <svg viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 2.98.97 4.29L1 23l6.71-1.97C9.02 21.64 10.46 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
                <span class="message-count" id="message-count" style="display: none;">0</span>
            </button>
            <div class="messages-popup" id="messages-popup">
                <div class="popup-header">
                    <h3>Messages</h3>
                    <button class="close-popup" onclick="globalMessages.close()">&times;</button>
                </div>
                <div class="popup-conversations" id="popup-conversations">
                    <div class="no-conversations">Loading conversations...</div>
                </div>
            </div>
        `;
        document.body.appendChild(widget);
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        document.getElementById('messages-popup').classList.add('show');
        this.isOpen = true;
        this.loadConversations();
    }

    close() {
        document.getElementById('messages-popup').classList.remove('show');
        this.isOpen = false;
    }

    loadConversations() {
        fetch('/api/messages/conversations')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const oldCount = this.conversations.length;
                    this.conversations = data.conversations;
                    this.displayConversations();
                    this.updateUnreadCount();
                    
                    // Show notification if new conversations
                    if (oldCount > 0 && data.conversations.length > oldCount) {
                        this.showNotification('New message received!');
                    }
                } else if (data.error === 'Not authenticated') {
                    this.showNotLoggedIn();
                } else {
                    this.showError();
                }
            })
            .catch(error => {
                console.error('Error loading conversations:', error);
                this.showError();
            });
    }

    displayConversations() {
        const container = document.getElementById('popup-conversations');
        if (!container) {
            console.error('popup-conversations element not found');
            return;
        }
        
        if (this.conversations.length === 0) {
            container.innerHTML = '<div class="no-conversations">No conversations yet</div>';
            return;
        }

        container.innerHTML = this.conversations.map(conv => `
            <div class="popup-conversation" onclick="globalMessages.openConversation('${conv.user_id}')">
                <div class="popup-info">
                    <div class="popup-name">${conv.display_name}</div>
                    <div class="popup-preview">${conv.last_message || 'No messages yet'}</div>
                </div>
                <div class="popup-time">${this.formatTime(conv.last_message_time)}</div>
            </div>
        `).join('');
    }

    openConversation(userId) {
        // Open full messages page in same window
        window.location.href = '/messages';
    }

    showError() {
        const container = document.getElementById('popup-conversations');
        if (container) {
            container.innerHTML = '<div class="no-conversations">Error loading messages</div>';
        }
    }

    showNotLoggedIn() {
        const container = document.getElementById('popup-conversations');
        if (container) {
            container.innerHTML = '<div class="no-conversations">Please log in to view messages</div>';
        }
    }

    formatTime(timestamp) {
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

    updateUnreadCount() {
        fetch('/api/messages/unread-count')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.unreadCount = data.unread_count;
                    const countElement = document.getElementById('message-count');
                    if (countElement) {
                        countElement.style.display = 'none';
                    }
                }
            })
            .catch(error => console.error('Error getting unread count:', error));
    }

    showNotification(message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('OnLook Messages', {
                body: message,
                icon: '/static/icons/onlook_icon.png'
            });
        } else if ('Notification' in window && Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification('OnLook Messages', {
                        body: message,
                        icon: '/static/icons/onlook_icon.png'
                    });
                }
            });
        }
    }

    startPolling() {
        // Poll for new messages every 5 seconds
        setInterval(() => {
            this.loadConversations();
        }, 5000);
    }

    bindEvents() {
        // Close popup when clicking outside
        document.addEventListener('click', (e) => {
            const widget = document.querySelector('.messages-widget');
            if (this.isOpen && !widget.contains(e.target)) {
                this.close();
            }
        });
    }
}

// Initialize global messages when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.globalMessages = new GlobalMessages();
});