// Loading screen functionality
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.display = 'none';
    }
}

// Hide loading screen when page loads
window.addEventListener('load', hideLoadingScreen);

// Fallback: hide after DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(hideLoadingScreen, 1000);
});

// Hard fallback: force hide after 3 seconds no matter what
setTimeout(hideLoadingScreen, 3000);