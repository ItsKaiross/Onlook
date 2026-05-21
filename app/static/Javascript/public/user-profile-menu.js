// User Profile Dropdown Menu
function toggleUserProfileMenu() {
    const menu = document.getElementById('userProfileMenu');
    if (menu) {
        menu.classList.toggle('show');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const profileBtn = document.querySelector('.profile-dropdown-btn');
    const menu = document.getElementById('userProfileMenu');
    
    if (menu && profileBtn) {
        if (!profileBtn.contains(event.target) && !menu.contains(event.target)) {
            menu.classList.remove('show');
        }
    }
});

// Logout Modal Functions
function openLogoutModal() {
    const modal = document.getElementById('logoutModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeLogoutModal() {
    const modal = document.getElementById('logoutModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Handle logout confirmation
document.addEventListener('DOMContentLoaded', function() {
    // Find all logout confirmation buttons
    const logoutConfirmBtns = document.querySelectorAll('.confirm-btn[href="/logout"], a[href="/logout"]');
    logoutConfirmBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Set flag to stop session checking
            window.isLoggingOut = true;
            localStorage.setItem('justLoggedOut', 'true');
            // Stop session check interval if it exists
            if (window.sessionCheckInterval) {
                clearInterval(window.sessionCheckInterval);
                window.sessionCheckInterval = null;
            }
        });
    });
});

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('logoutModal');
    const logoutBox = document.querySelector('.logout-box');
    
    if (modal && logoutBox) {
        if (event.target === modal) {
            closeLogoutModal();
        }
    }
});