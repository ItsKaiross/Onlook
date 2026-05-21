    document.addEventListener('DOMContentLoaded', function() {
        const lastSeenInputs = document.querySelectorAll('#lastSeen');
        lastSeenInputs.forEach(input => {
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            input.value = `${year}-${month}-${day}`;
        });
        
        const timeInputs = document.querySelectorAll('input[name="timeLastSeen"]');
        timeInputs.forEach(input => {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            input.value = `${hours}:${minutes}`;
        });
        
        // Set case_id for help locate form
        const helpLocateForm = document.getElementById('help-locate-form');
        if (helpLocateForm && window.currentCaseId) {
            helpLocateForm.action = `/help-locate-additional-report/${window.currentCaseId}`;
        }
    });
    
    // Function to update help locate form with case_id
    function updateHelpLocateForm(caseId) {
        const helpLocateForm = document.getElementById('help-locate-form');
        if (helpLocateForm && caseId) {
            helpLocateForm.action = `/help-locate-additional-report/${caseId}`;
            window.currentCaseId = caseId;
        }
    }