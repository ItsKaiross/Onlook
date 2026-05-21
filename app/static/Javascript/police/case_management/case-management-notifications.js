// Notification functions
function toggleNotifications() {
    const overlay = document.getElementById('notificationOverlay');
    if (!overlay) return;
    
    if (overlay.classList.contains('show')) {
        overlay.classList.remove('show');
        setTimeout(() => overlay.style.display = 'none', 300);
    } else {
        overlay.style.display = 'block';
        setTimeout(() => overlay.classList.add('show'), 10);
    }
}

function closeNotifications() {
    const overlay = document.getElementById('notificationOverlay');
    if (!overlay) return;
    
    overlay.classList.remove('show');
    setTimeout(() => overlay.style.display = 'none', 300);
}

function viewReportDetails(reportId) {
    console.log('Viewing case from notification:', reportId);
    
    // Mark notifications as read
    fetch('/police-mark-notifications-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(() => {
        const badge = document.querySelector('.notification-badge');
        if (badge) badge.style.display = 'none';
    });
    
    // Close notifications
    closeNotifications();
    
    // Check which page we're on
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('field-report')) {
        // On field report page - open field report modal
        fetch(`/police-field-report-details/${reportId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (typeof window.displayReportDetails === 'function') {
                        window.displayReportDetails(data.report);
                    } else {
                        console.error('displayReportDetails function not found');
                        alert('Error loading report details. Please refresh the page.');
                    }
                } else {
                    alert('Error loading report details: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading report details');
            });
    } else if (currentPath.includes('case-management')) {
        // On case management page - open case details modal
        fetch(`/police-case-details/${reportId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (typeof window.displayCaseDetails === 'function') {
                        window.displayCaseDetails(data.case);
                    } else {
                        console.error('displayCaseDetails function not found');
                        alert('Error loading case details. Please refresh the page.');
                    }
                } else {
                    alert('Error loading case details: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading case details');
            });
    } else {
        // Default - redirect to field report page
        window.location.href = `/police-field-report?case_id=${reportId}`;
    }
}

// Close notifications when clicking outside
document.addEventListener('click', function(event) {
    const overlay = document.getElementById('notificationOverlay');
    const notificationFrame = document.querySelector('._public_notification_frame');
    
    if (!overlay || !notificationFrame) return;
    
    if (!overlay.contains(event.target) && !notificationFrame.contains(event.target)) {
        closeNotifications();
    }
});