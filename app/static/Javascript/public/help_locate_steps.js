// Help locate popup step navigation with validation
document.addEventListener('DOMContentLoaded', function() {
    // Store form submit handlers for later removal
    const waccForm = document.querySelector('#help-locate-wacc-popup form');
    const noAccForm = document.querySelector('#help-locate-no-acc-popup form');
    
    const waccFormHandler = function(e) {
        e.preventDefault();
        return false;
    };
    
    const noAccFormHandler = function(e) {
        e.preventDefault();
        return false;
    };
    
    if (waccForm) {
        waccForm.addEventListener('submit', waccFormHandler);
        waccForm._submitHandler = waccFormHandler;
    }
    
    if (noAccForm) {
        noAccForm.addEventListener('submit', noAccFormHandler);
        noAccForm._submitHandler = noAccFormHandler;
    }
    // No account popup validation - more specific targeting
    const noAccPopup = document.getElementById('help-locate-no-acc-popup');
    const nextBtns = noAccPopup ? noAccPopup.querySelectorAll('.next_button') : [];
    const prevBtns = noAccPopup ? noAccPopup.querySelectorAll('.prev_button') : [];
    
    // With account popup validation
    const nextBtnsWacc = document.querySelectorAll('#help-locate-wacc-popup .next_button');
    const prevBtnsWacc = document.querySelectorAll('#help-locate-wacc-popup .prev_button');
    
    nextBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const currentStep = noAccPopup.querySelector('.step.active');
            if (!currentStep) {
                return;
            }
            
            const nextStep = currentStep.nextElementSibling;
            
            // Get all required fields directly by ID to ensure we find them
            const fieldIds = [
                'helpEmailNoAcc',
                'HelpLocateFirstNameNoAcc', 
                'HelpLocateLastNameNoAcc',
                'HelpLocateContactNoAcc',
                'HelpRelationshipNoAcc',
                'helpTimeSightingNoAcc',
                'helpDateSightingNoAcc',
                'help_locate_description_no_acc'
            ];
            
            let isValid = true;
            let emptyFields = [];
            
            fieldIds.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    if (!field.value || !field.value.trim()) {
                        field.style.border = '2px solid red';
                        emptyFields.push(field.name || field.id);
                        isValid = false;
                    } else {
                        field.style.border = '';
                    }
                }
            });
            

            

            
            if (!isValid) {
                alert('Please fill all required fields');
                return;
            }
            
            if (nextStep && nextStep.classList.contains('step')) {
                currentStep.classList.remove('active');
                nextStep.classList.add('active');
                updateHelpLocateProgress();
                
                // Initialize map on step 2
                if (nextStep.classList.contains('step-2')) {
                    setTimeout(initHelpLocateMapNoAcc, 300);
                }
            }
        });
    });
    
    // No account popup submit button validation
    const submitBtnNoAcc = document.querySelector('#help-locate-no-acc-popup .submit_button');
    if (submitBtnNoAcc) {
        submitBtnNoAcc.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            // Prevent multiple submissions
            if (this.disabled) return false;
            
            let isValid = true;
            let errorMessage = '';
            
            // Check if location is selected
            const latitude = document.getElementById('helpLatitude').value;
            const longitude = document.getElementById('helpLongitude').value;
            if (!latitude || latitude === '0' || !longitude || longitude === '0') {
                errorMessage += 'Please select a location on the map.\n';
                isValid = false;
            }
            
            if (!isValid) {
                alert(errorMessage);
                return false;
            }
            
            // Disable button and submit form
            this.disabled = true;
            this.textContent = 'Submitting...';
            const form = document.querySelector('#help-locate-no-acc-popup form');
            // Remove the form submit prevention
            if (form._submitHandler) {
                form.removeEventListener('submit', form._submitHandler);
            }
            form.submit();
        }, true);
    }
    
    prevBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const currentStep = noAccPopup.querySelector('.step.active');
            const prevStep = currentStep.previousElementSibling;
            
            if (prevStep && prevStep.classList.contains('step')) {
                currentStep.classList.remove('active');
                prevStep.classList.add('active');
                updateHelpLocateProgress();
            }
        });
    });
    
    // With account popup next button validation
    nextBtnsWacc.forEach(btn => {
        btn.addEventListener('click', function() {
            const currentStep = document.querySelector('#help-locate-wacc-popup .step.active');
            const nextStep = currentStep.nextElementSibling;
            
            // Validate only visible required fields (skip hidden inputs)
            const requiredFields = currentStep.querySelectorAll('input[required]:not([type="hidden"]), textarea[required], select[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value || !field.value.trim()) {
                    field.style.border = '2px solid red';
                    isValid = false;
                } else {
                    field.style.border = '';
                }
            });
            
            if (!isValid) {
                alert('Please fill all required fields');
                return;
            }
            
            if (nextStep && nextStep.classList.contains('step')) {
                currentStep.classList.remove('active');
                nextStep.classList.add('active');
                updateHelpLocateProgressWacc();
                
                // Initialize map on step 2 for with-account popup
                if (nextStep.classList.contains('step-2')) {
                    setTimeout(initHelpLocateMap, 300);
                }
            }
        });
    });
    
    // With account popup submit button validation
    const submitBtnWacc = document.querySelector('#help-locate-wacc-popup .submit_button');
    if (submitBtnWacc) {
        submitBtnWacc.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            // Prevent multiple submissions
            if (this.disabled) return false;
            
            let isValid = true;
            let errorMessage = '';
            
            // Check if location is selected
            const latitude = document.getElementById('helpLatitude').value;
            const longitude = document.getElementById('helpLongitude').value;
            if (!latitude || latitude === '0' || !longitude || longitude === '0') {
                errorMessage += 'Please select a location on the map.\n';
                isValid = false;
            }
            
            if (!isValid) {
                alert(errorMessage);
                return false;
            }
            
            // Disable button and submit form
            this.disabled = true;
            this.textContent = 'Submitting...';
            const form = document.querySelector('#help-locate-wacc-popup form');
            // Remove the form submit prevention
            if (form._submitHandler) {
                form.removeEventListener('submit', form._submitHandler);
            }
            form.submit();
        }, true);
    }
    
    // With account popup prev button
    prevBtnsWacc.forEach(btn => {
        btn.addEventListener('click', function() {
            const currentStep = document.querySelector('#help-locate-wacc-popup .step.active');
            const prevStep = currentStep.previousElementSibling;
            
            if (prevStep && prevStep.classList.contains('step')) {
                currentStep.classList.remove('active');
                prevStep.classList.add('active');
                updateHelpLocateProgressWacc();
            }
        });
    });
});

// Progress bar update function
function updateHelpLocateProgress() {
    const activeStep = document.querySelector('#help-locate-no-acc-popup .step.active');
    const progressFill = document.getElementById('progress_fill_help_locate_no_acc');
    const progressSteps = document.querySelectorAll('#help-locate-no-acc-popup .progress_step');
    
    if (!activeStep || !progressFill) return;
    
    let currentStepNumber = 1;
    if (activeStep.classList.contains('step-1')) currentStepNumber = 1;
    else if (activeStep.classList.contains('step-2')) currentStepNumber = 2;
    
    const progressPercentage = (currentStepNumber / 2) * 100;
    progressFill.style.width = progressPercentage + '%';
    
    progressSteps.forEach((step, index) => {
        if (index < currentStepNumber) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

function initHelpMap() {
    if (!window.google || !window.google.maps) {
        setTimeout(initHelpMap, 500);
        return;
    }
    
    const mapElement = document.getElementById('helpMap');
    if (!mapElement) return;
    
    window.helpLocateMap = new google.maps.Map(mapElement, {
        center: { lat: 14.5995, lng: 120.9842 },
        zoom: 12
    });

    window.helpLocateMap.addListener('click', function(event) {
        if (window.helpLocateMarker) window.helpLocateMarker.setMap(null);
        window.helpLocateMarker = new google.maps.Marker({
            position: event.latLng,
            map: window.helpLocateMap
        });
        document.getElementById('helpLatitude').value = event.latLng.lat();
        document.getElementById('helpLongitude').value = event.latLng.lng();
    });
}

// Progress bar update function for with account popup
function updateHelpLocateProgressWacc() {
    const activeStep = document.querySelector('#help-locate-wacc-popup .step.active');
    const progressFill = document.getElementById('progress_fill_help_locate');
    const progressSteps = document.querySelectorAll('#help-locate-wacc-popup .progress_step');
    
    if (!activeStep || !progressFill) return;
    
    let currentStepNumber = 1;
    if (activeStep.classList.contains('step-1')) currentStepNumber = 1;
    else if (activeStep.classList.contains('step-2')) currentStepNumber = 2;
    
    const progressPercentage = (currentStepNumber / 2) * 100;
    progressFill.style.width = progressPercentage + '%';
    
    progressSteps.forEach((step, index) => {
        if (index < currentStepNumber) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

function initHelpLocateWaccMap() {
    initHelpMap();
}

