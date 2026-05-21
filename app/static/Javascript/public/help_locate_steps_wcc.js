// Help locate popup step navigation with validation
document.addEventListener('DOMContentLoaded', function() {
    const nextBtns = document.querySelectorAll('#help-locate-wacc-popup .next_button');
    const prevBtns = document.querySelectorAll('#help-locate-wacc-popup .prev_button');
    
    nextBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const currentStep = document.querySelector('#help-locate-wacc-popup .step.active');
            const nextStep = currentStep.nextElementSibling;
            
            // Validate current step fields
            const requiredFields = currentStep.querySelectorAll('[required]');
            let isValid = true;
            let missingFields = [];
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    const label = field.closest('div').previousElementSibling;
                    const fieldName = label ? label.textContent : field.name;
                    missingFields.push(fieldName);
                    isValid = false;
                }
            });
            
            // Show flash message if validation fails
            const flashMessage = document.getElementById('help-locate-flash-message');
            if (!isValid && flashMessage) {
                flashMessage.textContent = `Please fill in the following required fields: ${missingFields.join(', ')}`;
                flashMessage.style.display = 'block';
                setTimeout(() => {
                    flashMessage.style.display = 'none';
                }, 5000);
            } else if (flashMessage) {
                flashMessage.style.display = 'none';
            }
            
            // Only proceed if validation passes
            if (isValid && nextStep && nextStep.classList.contains('step')) {
                currentStep.classList.remove('active');
                nextStep.classList.add('active');
                
                // Update progress bar
                updateHelpLocateProgress();
                
                // Initialize map when step 2 becomes active
                if (nextStep.classList.contains('step-2')) {
                    setTimeout(initHelpLocateMap, 100);
                }
            }
        });
    });
    
    prevBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const currentStep = document.querySelector('#help-locate-wacc-popup .step.active');
            const prevStep = currentStep.previousElementSibling;
            
            if (prevStep && prevStep.classList.contains('step')) {
                currentStep.classList.remove('active');
                prevStep.classList.add('active');
                
                // Update progress bar
                updateHelpLocateProgress();
            }
        });
    });
});

// Progress bar update function for help locate popup
function updateHelpLocateProgress() {
    const activeStep = document.querySelector('#help-locate-wacc-popup .step.active');
    const progressFill = document.getElementById('progress_fill_help_locate');
    const progressSteps = document.querySelectorAll('#help-locate-wacc-popup .progress_step');
    
    if (!activeStep || !progressFill) return;
    
    let currentStepNumber = 1;
    if (activeStep.classList.contains('step-1')) currentStepNumber = 1;
    else if (activeStep.classList.contains('step-2')) currentStepNumber = 2;
    
    // Update progress bar fill
    const progressPercentage = (currentStepNumber / 2) * 100;
    progressFill.style.width = progressPercentage + '%';
    
    // Update progress step indicators
    progressSteps.forEach((step, index) => {
        if (index < currentStepNumber) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}