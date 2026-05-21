//################################################################################//
//#####################  R E G I S T R A T I O N  S T E P S  #####################//
//################################################################################//

const steps = Array.from(document.querySelectorAll('form .step')) ;

const nextBtn = document.querySelectorAll('form .next_button');
const prevBtn = document.querySelectorAll('form .prev_button');
const form = document.querySelector('form');

const isValidStep = () => {
    const active_step = document.querySelector('form .step.active');

    if (!active_step){
        console.error('No active step found.');
        return false;
    }
    const fields = active_step.querySelectorAll('input, select, textarea');

    if(!fields || fields.length === 0){
        console.warn('no fields');
        return true;
    }

    let isValid = true;
    let missingFields = [];

    [...fields].forEach(field => {
        if (!field.checkValidity()) {
            const label = field.closest('div').previousElementSibling;
            const fieldName = label ? label.textContent : field.placeholder || field.name;
            missingFields.push(fieldName);
            isValid = false;
        }
    });

    // Show flash message if validation fails
    if (!isValid) {
        showFlashMessage(`Please fill in the following required fields: ${missingFields.join(', ')}`);
    }

    return isValid;
}

function showFlashMessage(message) {
    // Create flash message if it doesn't exist
    let flashMessage = document.getElementById('report-missing-flash-message');
    if (!flashMessage) {
        flashMessage = document.createElement('div');
        flashMessage.id = 'report-missing-flash-message';
        flashMessage.style.cssText = 'background: #f8d7da; color: #721c24; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #f5c6cb;';
        
        const activeStep = document.querySelector('form .step.active');
        const titleDiv = activeStep.querySelector('.add-field-txt');
        if (titleDiv) {
            titleDiv.parentNode.insertBefore(flashMessage, titleDiv.nextSibling);
        }
    }
    
    flashMessage.textContent = message;
    flashMessage.style.display = 'block';
    
    setTimeout(() => {
        flashMessage.style.display = 'none';
    }, 5000);
}

// Disable required validation on inactive steps
function toggleRequiredFields() {
    const allSteps = document.querySelectorAll('.step');
    allSteps.forEach(step => {
        const fields = step.querySelectorAll('input[required], select[required], textarea[required]');
        if (step.classList.contains('active')) {
            fields.forEach(field => field.setAttribute('required', 'required'));
        } else {
            fields.forEach(field => field.removeAttribute('required'));
        }
    });
}

nextBtn.forEach(button=>{
    button.addEventListener('click', () => {
        if(!isValidStep()) return;
        changeStep('next');
    })
})

prevBtn.forEach(button => {
    button.addEventListener('click', () => {
        changeStep('prev')
    })
})

function changeStep(button){
    let index = 0;
    const active = document.querySelector('form .step.active');
    index = steps.indexOf(active);
    steps[index].classList.remove('active');
    if(button == 'next'){
        index++;
    }else if( button == 'prev'){
        index--;
    }
    steps[index].classList.add('active');
    toggleRequiredFields();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    toggleRequiredFields();
});