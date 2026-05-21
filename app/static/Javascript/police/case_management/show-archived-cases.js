let showingArchivedCases = false;

function toggleArchivedCases() {
    const btn = document.getElementById('toggle-archived-btn');
    const urlParams = new URLSearchParams(window.location.search);
    
    // Toggle the state
    showingArchivedCases = !showingArchivedCases;
    
    // Update button text
    if (showingArchivedCases) {
        btn.textContent = 'View Active Cases';
        urlParams.set('show_archived', 'true');
    } else {
        btn.textContent = 'View Archived';
        urlParams.delete('show_archived');
    }
    
    // Preserve other filters
    urlParams.set('case_page', '1'); // Reset to first page
    
    // Reload page with new parameter
    window.location.search = urlParams.toString();
}

// Initialize button text on page load
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const showArchived = urlParams.get('show_archived') === 'true';
    const btn = document.getElementById('toggle-archived-btn');
    
    if (showArchived) {
        showingArchivedCases = true;
        if (btn) btn.textContent = 'View Active Cases';
    } else {
        showingArchivedCases = false;
        if (btn) btn.textContent = 'View Archived';
    }
});
