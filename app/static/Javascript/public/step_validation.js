// Manage required fields for help locate popup based on active step
document.addEventListener('DOMContentLoaded', function() {
    function updateRequiredFields() {
        const helpLocatePopup = document.getElementById('help-locate-no-acc-popup');
        if (!helpLocatePopup) return;
        
        const activeStep = helpLocatePopup.querySelector('.step.active');
        const allSteps = helpLocatePopup.querySelectorAll('.step');
        
        // Remove required from all help locate fields
        allSteps.forEach(step => {
            const fields = step.querySelectorAll('input, textarea, select');
            fields.forEach(field => field.removeAttribute('required'));
        });
        
        // Add required to active step fields only
        if (activeStep) {
            if (activeStep.classList.contains('step-1')) {
                const step1Fields = activeStep.querySelectorAll('input[name="HelpLocateFullName"], input[name="TimeSighting"], input[name="DateSighting"], textarea[name="help_locate_description"]');
                step1Fields.forEach(field => field.setAttribute('required', 'required'));
            }
            
            if (activeStep.classList.contains('step-2')) {
                const locationRadios = activeStep.querySelectorAll('input[name="helpLocateLocation"]');
                locationRadios.forEach(radio => radio.setAttribute('required', 'required'));
            }
        }
    }
    
    // Initial setup
    updateRequiredFields();
    
    // Update when popup opens
    const helpLocateBtn = document.getElementById('help_locate_btn');
    if (helpLocateBtn) {
        helpLocateBtn.addEventListener('click', updateRequiredFields);
    }
    
    // Update when steps change
    const observer = new MutationObserver(updateRequiredFields);
    const helpLocatePopup = document.getElementById('help-locate-no-acc-popup');
    if (helpLocatePopup) {
        observer.observe(helpLocatePopup, {
            attributes: true,
            subtree: true,
            attributeFilter: ['class']
        });
    }
});