// Session Management
window.sessionCheckInterval = null;
window.isLoggingOut = false;

document.addEventListener('DOMContentLoaded', function() {
    
    // Check if user just logged out (flag persists across page loads)
    const justLoggedOut = localStorage.getItem('justLoggedOut');
    if (justLoggedOut) {
        // Clear the flag and don't run session checks
        localStorage.removeItem('justLoggedOut');
        window.isLoggingOut = true;
        return;
    }
    
    // Only run session checks if user is logged in
    // Check for profile dropdown (only exists for logged in users)
    const profileDropdown = document.querySelector('.profile-dropdown-btn');
    
    // Double check - also verify logout link exists
    const logoutLink = document.querySelector('a[href="/logout"]');
    
    // Only start session checking if BOTH indicators exist (user is definitely logged in)
    if (profileDropdown && logoutLink) {
        
        // Check session status every 30 seconds
        window.sessionCheckInterval = setInterval(checkSession, 30000);
        
        // Also check on page load after a short delay
        setTimeout(checkSession, 1000);
        
        // Intercept logout clicks to stop session checking
        const logoutLinks = document.querySelectorAll('a[href="/logout"], .confirm-btn[href="/logout"]');
        logoutLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                window.isLoggingOut = true;
                localStorage.setItem('justLoggedOut', 'true');
                if (window.sessionCheckInterval) {
                    clearInterval(window.sessionCheckInterval);
                    window.sessionCheckInterval = null;
                }
            });
        });
    }
});

function checkSession() {
    // Don't check if user is logging out
    if (window.isLoggingOut) {
        return;
    }
    
    // Don't check if no logged-in indicator exists (user not logged in)
    const profileDropdown = document.querySelector('.profile-dropdown-btn');
    const logoutLink = document.querySelector('a[href="/logout"]');
    
    if (!profileDropdown || !logoutLink) {
        // Stop the interval if it's running
        if (window.sessionCheckInterval) {
            clearInterval(window.sessionCheckInterval);
            window.sessionCheckInterval = null;
        }
        return;
    }
    
    fetch('/check-session')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data.valid) {
                // Stop checking session before showing popup
                if (window.sessionCheckInterval) {
                    clearInterval(window.sessionCheckInterval);
                    window.sessionCheckInterval = null;
                }
                // Only show popup if not manually logging out
                if (!data.manual_logout && !window.isLoggingOut) {
                    showSessionExpiredPopup();
                }
            }
        })
        .catch(error => {
            console.error('Session check failed:', error);
            // Don't show popup on network errors, just log them
        });
}

function showSessionExpiredPopup() {
    
    // Remove existing popup if any
    const existingPopup = document.getElementById('session-expired-popup');
    if (existingPopup) {
        existingPopup.remove();
    }
    
    // Create popup
    const popup = document.createElement('div');
    popup.id = 'session-expired-popup';
    popup.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 10001;
        display: flex;
        justify-content: center;
        align-items: center;
    `;
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        max-width: 400px;
        width: 90%;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    `;
    
    modal.innerHTML = `
        <h2 style="color: #1A1B41; margin-bottom: 15px; font-family: SF_BOLD;">Session Expired</h2>
        <p style="color: #666; margin-bottom: 25px; font-family: SF_REGULAR;">Your session has expired. Please log in again to continue.</p>
        <button onclick="handleSessionExpired()" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-family: SF_MEDIUM;
            font-size: 16px;
        ">OK</button>
    `;
    
    popup.appendChild(modal);
    document.body.appendChild(popup);
}

function handleSessionExpired() {
    
    // Stop any session checking
    if (window.sessionCheckInterval) {
        clearInterval(window.sessionCheckInterval);
        window.sessionCheckInterval = null;
    }
    
    // Remove the popup
    const popup = document.getElementById('session-expired-popup');
    if (popup) {
        popup.remove();
    }
    
    // Redirect to home page (public view) instead of logout
    window.location.href = '/';
}
