// Image archiving notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `case-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Add styles if not already present
    if (!document.getElementById('case-notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'case-notification-styles';
        styles.textContent = `
            .case-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                min-width: 300px;
                max-width: 500px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                animation: slideInRight 0.3s ease-out;
            }
            .case-notification.success { background: #d4edda; border-left: 4px solid #28a745; color: #155724; }
            .case-notification.error { background: #f8d7da; border-left: 4px solid #dc3545; color: #721c24; }
            .case-notification.info { background: #d1ecf1; border-left: 4px solid #17a2b8; color: #0c5460; }
            .notification-content {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                gap: 8px;
            }
            .notification-message { flex: 1; font-weight: 500; }
            .notification-close {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideInRight 0.3s ease-in reverse';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Enhanced archive image function with better feedback
function archiveImageWithFeedback(imageId, index) {
    const caseTitle = document.querySelector('.case-file-view h3')?.textContent || 'Case #0';
    const caseId = caseTitle.match(/\d+/)?.[0] || '0';
    
    if (confirm('Are you sure you want to archive this image? It will be moved to the archived images section.')) {
        const deleteBtn = document.querySelector(`button[onclick*="deleteImage(${imageId}, ${index})"]`);
        if (deleteBtn) {
            deleteBtn.disabled = true;
            deleteBtn.textContent = '⏳';
        }
        
        fetch(`/police-delete-image/${imageId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (deleteBtn) {
                deleteBtn.disabled = false;
                deleteBtn.textContent = '×';
            }
            
            if (data && data.success === true) {
                showNotification('Image archived successfully', 'success');
                // Trigger gallery refresh
                if (typeof refreshImageGallery === 'function') {
                    refreshImageGallery(caseId);
                }
            } else {
                showNotification(`Error archiving image: ${data?.message || 'Unknown error'}`, 'error');
            }
        })
        .catch(error => {
            if (deleteBtn) {
                deleteBtn.disabled = false;
                deleteBtn.textContent = '×';
            }
            showNotification(`Network error: ${error.message}`, 'error');
        });
    }
}