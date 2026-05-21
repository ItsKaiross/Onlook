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

    [...fields].forEach(field => {
        if (!field.checkValidity()) {
            field.reportValidity();
            isValid = false;
        }
    });

    return isValid;
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
    updateProgressBar(index + 1);
    updateScrollable(index);
}

function updateScrollable(stepIndex) {
    const regFrame = document.querySelector('.reg_frame');
    // Step 2 (index 1) and Step 4 (index 3) should be scrollable
    if (stepIndex === 1 || stepIndex === 3) {
        regFrame.classList.add('scrollable');
    } else {
        regFrame.classList.remove('scrollable');
    }
}

function updateProgressBar(currentStep) {
    const progressFill = document.getElementById('progress_fill');
    const progressSteps = document.querySelectorAll('.progress_step');
    
    // Update progress bar fill
    const progressPercentage = (currentStep / 4) * 100;
    progressFill.style.width = progressPercentage + '%';
    
    // Update step indicators
    progressSteps.forEach((step, index) => {
        step.classList.remove('active', 'completed');
        if (index + 1 < currentStep) {
            step.classList.add('completed');
        } else if (index + 1 === currentStep) {
            step.classList.add('active');
        }
    });
}