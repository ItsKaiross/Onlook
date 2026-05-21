//################################################################################//
//#####################  R E G I S T R A T I O N  S T E P S  #####################//
//################################################################################//

const steps = Array.from(document.querySelectorAll('form .step')) ;

const nextBtn = document.querySelectorAll('#report-missing-popup .next_button');
const prevBtn = document.querySelectorAll('#report-missing-popup .prev_button');
const form = document.querySelector('form');

const isValidStep = () => {
    const active_step = document.querySelector('form .step.active');

    if (!active_step){
        return false;
    }
    
    // Get all input fields in active step, not just required ones
    const allFields = active_step.querySelectorAll('input, select, textarea');
    const requiredFields = [];
    let isValid = true;
    let missingFields = [];

    // Determine which fields should be required based on step
    [...allFields].forEach(field => {
        if (shouldFieldBeRequired(field, active_step)) {
            requiredFields.push(field);
        }
    });

    requiredFields.forEach(field => {
        let fieldValid = true;
        
        if (field.type === 'radio') {
            const radioGroup = active_step.querySelectorAll(`input[name="${field.name}"]`);
            fieldValid = [...radioGroup].some(radio => radio.checked);
        } else if (field.tagName === 'SELECT') {
            fieldValid = field.value && field.selectedIndex > 0;
        } else if (field.type === 'file') {
            // Special handling for image uploads - check both main and additional images
            if (field.name === 'upload_last_seen') {
                const mainImage = document.querySelector('input[name="upload_last_seen"]');
                const additionalImages = document.querySelector('input[name="additional_images"]');
                const hasMainImage = mainImage && mainImage.files.length > 0;
                const hasAdditionalImages = additionalImages && additionalImages.files.length > 0;
                fieldValid = hasMainImage || hasAdditionalImages;
                
                // Also validate additional images field if it exists and has files
                if (!fieldValid && additionalImages) {
                    additionalImages.classList.add('field-error');
                } else if (additionalImages) {
                    additionalImages.classList.remove('field-error');
                }
            } else {
                fieldValid = field.files.length > 0;
            }
        } else {
            fieldValid = field.value.trim() !== '';
        }
        
        if (!fieldValid) {
            const label = field.closest('div').previousElementSibling || field.closest('label');
            let fieldName;
            
            // Special handling for image upload fields
            if (field.name === 'upload_last_seen') {
                fieldName = 'At least one photo (main or additional)';
            } else {
                fieldName = label ? label.textContent.replace(':', '').trim() : field.placeholder || field.name;
            }
            
            if (!missingFields.includes(fieldName)) {
                missingFields.push(fieldName);
            }
            field.classList.add('field-error');
            field.classList.remove('field-valid');
            isValid = false;
        } else {
            field.classList.remove('field-error');
            field.classList.add('field-valid');
        }
    });

    if (!isValid) {
        showFlashMessage(`Please fill in: ${missingFields.join(', ')}`);
    }

    return isValid;
}

function shouldFieldBeRequired(field, step) {
    const stepClass = [...step.classList].find(cls => cls.startsWith('step-'));
    const fieldName = field.name;
    
    switch(stepClass) {
        case 'step-1': // Personal Info
            return ['firstName', 'lastName', 'gender', 'dob', 'civil_status', 'citizenship', 'contact_number'].includes(fieldName);
        case 'step-2': // Address
            return ['houseNumber', 'street', 'brgy', 'region', 'province', 'city'].includes(fieldName);
        case 'step-3': // Health & Physical
            return ['health_type_dropdown', 'health_description', 'hair_color', 'eye_color', 'height', 'weight', 'distinguish', 'attire'].includes(fieldName) || 
                   (fieldName === 'occupation' && !document.getElementById('progress_fill_wacc'));
        case 'step-4': // Last Seen
            return ['lastSeen', 'timeLastSeen', 'upload_last_seen'].includes(fieldName) || 
                   (fieldName === 'circumstances' && !document.getElementById('progress_fill_wacc'));
        case 'step-5': // Location
            return ['locLastSeen'].includes(fieldName);
        case 'step-6': // Informant (no account) or Review (with account)
            if (document.getElementById('progress_fill_wacc')) return false; // Review step, no validation needed
            return ['FirstName', 'LastName', 'MiddleName', 'informant_gender', 'relation', 'ContactNumber', 'email'].includes(fieldName);
        case 'step-7': // Informant Address (no account only)
            return ['informant_houseNo', 'informant_street', 'informant_brgy', 'iregion', 'iprovince', 'icity'].includes(fieldName);
        case 'step-8': // Review (no account)
            return false; // Review step, no validation needed
        default:
            return field.hasAttribute('required');
    }
}

function showFlashMessage(message) {
    const activeStep = document.querySelector('form .step.active');
    let flashMessage = activeStep.querySelector('#report-missing-flash-message');
    
    if (!flashMessage) {
        flashMessage = document.createElement('div');
        flashMessage.id = 'report-missing-flash-message';
        flashMessage.style.cssText = 'background: #f8d7da; color: #721c24; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #f5c6cb; font-size: 14px;';
        
        const titleDiv = activeStep.querySelector('.report-missing-txt, .address h1');
        if (titleDiv) {
            titleDiv.parentNode.insertBefore(flashMessage, titleDiv.nextSibling);
        } else {
            activeStep.insertBefore(flashMessage, activeStep.firstChild);
        }
    }
    
    flashMessage.textContent = message;
    flashMessage.style.display = 'block';
    
    setTimeout(() => {
        if (flashMessage) flashMessage.style.display = 'none';
    }, 5000);
}

// Disable required validation on inactive steps
function toggleRequiredFields() {
    const reportMissingModal = document.getElementById('report-missing-popup');
    if (!reportMissingModal) return;
    
    const allSteps = reportMissingModal.querySelectorAll('.step');
    allSteps.forEach(step => {
        const fields = step.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            if (step.classList.contains('active') && shouldFieldBeRequired(field, step)) {
                field.setAttribute('required', 'required');
            } else {
                field.removeAttribute('required');
            }
        });
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
        // Populate review data when entering review step
        if(steps[index].classList.contains('step-6') || steps[index].classList.contains('step-8')){
            populateReviewData();
        }
    }else if( button == 'prev'){
        index--;
    }
    steps[index].classList.add('active');
    updateProgressBar(index + 1);
    toggleRequiredFields();
    
    // Initialize map when reaching step 5 (location step)
    if (steps[index].classList.contains('step-5')) {
        setTimeout(function() {
            if (typeof initPopupMap === 'function') {
                initPopupMap();
            }
        }, 500);
    }
}

function populateReviewData() {
    // Check if it's with account or no account popup
    const isWithAccount = document.getElementById('progress_fill_wacc') !== null;
    const suffix = isWithAccount ? '_wacc' : '';
    
    // Get the correct form - the report missing form
    const reportForm = document.querySelector('#report-missing-popup form');
    
    // Get form values - these are the MISSING PERSON's details
    const firstName = reportForm?.querySelector('input[name="firstName"]')?.value || '';
    const middleName = reportForm?.querySelector('input[name="middleName"]')?.value || '';
    const lastName = reportForm?.querySelector('input[name="lastName"]')?.value || '';
    const fullName = [firstName, middleName, lastName].filter(n => n).join(' ').trim();
    
    console.log('Review Data - First Name:', firstName);
    console.log('Review Data - Middle Name:', middleName);
    console.log('Review Data - Last Name:', lastName);
    console.log('Review Data - Full Name:', fullName);
    
    // Populate review fields
    const reviewName = document.getElementById(`review_name${suffix}`);
    if(reviewName) {
        reviewName.textContent = fullName || 'Not provided';
        console.log('Set review name to:', reviewName.textContent);
    }
    
    const reviewGender = document.getElementById(`review_gender${suffix}`);
    if(reviewGender) reviewGender.textContent = reportForm?.querySelector('select[name="gender"]')?.value || 'Not provided';
    
    const reviewDob = document.getElementById(`review_dob${suffix}`);
    if(reviewDob) reviewDob.textContent = reportForm?.querySelector('input[name="dob"]')?.value || 'Not provided';
    
    const reviewHeight = document.getElementById(`review_height${suffix}`);
    if(reviewHeight) reviewHeight.textContent = reportForm?.querySelector('input[name="height"]')?.value || 'Not provided';
    
    const reviewWeight = document.getElementById(`review_weight${suffix}`);
    if(reviewWeight) reviewWeight.textContent = reportForm?.querySelector('input[name="weight"]')?.value || 'Not provided';
    
    const reviewHair = document.getElementById(`review_hair${suffix}`);
    if(reviewHair) reviewHair.textContent = reportForm?.querySelector('select[name="hair_color"]')?.value || 'Not provided';
    
    const reviewEyes = document.getElementById(`review_eyes${suffix}`);
    if(reviewEyes) reviewEyes.textContent = reportForm?.querySelector('select[name="eye_color"]')?.value || 'Not provided';
    
    const reviewAttire = document.getElementById(`review_attire${suffix}`);
    if(reviewAttire) reviewAttire.textContent = reportForm?.querySelector('textarea[name="attire"]')?.value || 'Not provided';
    
    const reviewDateSeen = document.getElementById(`review_date_seen${suffix}`);
    if(reviewDateSeen) reviewDateSeen.textContent = reportForm?.querySelector('input[name="lastSeen"]')?.value || 'Not provided';
    
    const reviewTimeSeen = document.getElementById(`review_time_seen${suffix}`);
    if(reviewTimeSeen) reviewTimeSeen.textContent = reportForm?.querySelector('input[name="timeLastSeen"]')?.value || 'Not provided';
    
    // Populate image preview
    const reviewImage = document.getElementById(`review_image${suffix}`);
    if(reviewImage) {
        const mainImageInput = reportForm?.querySelector('input[name="upload_last_seen"]');
        if(mainImageInput && mainImageInput.files && mainImageInput.files.length > 0) {
            const file = mainImageInput.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {
                reviewImage.src = e.target.result;
                reviewImage.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            reviewImage.style.display = 'none';
        }
    }
    
    // For no account popup, also populate informant info
    if(!isWithAccount) {
        const informantFirst = reportForm?.querySelector('input[name="FirstName"]')?.value || '';
        const informantLast = reportForm?.querySelector('input[name="LastName"]')?.value || '';
        const informantName = `${informantFirst} ${informantLast}`.trim();
        
        const reviewInformantName = document.getElementById('review_informant_name');
        if(reviewInformantName) reviewInformantName.textContent = informantName || 'Not provided';
        
        const reviewRelationship = document.getElementById('review_relationship');
        if(reviewRelationship) reviewRelationship.textContent = reportForm?.querySelector('input[name="relation"]')?.value || 'Not provided';
        
        const reviewContact = document.getElementById('review_contact');
        if(reviewContact) reviewContact.textContent = reportForm?.querySelector('input[name="ContactNumber"]')?.value || 'Not provided';
    }
}

function toggleSameAddress() {
    const checkbox = document.getElementById('sameAddress');
    if (!checkbox) return;
    
    const isChecked = checkbox.checked;
    
    // Get missing person address fields
    const mpHouseNumber = document.getElementById('houseNumber')?.value || '';
    const mpStreet = document.getElementById('street')?.value || '';
    const mpBrgy = document.getElementById('brgy')?.value || '';
    const mpRegion = document.getElementById('region')?.value || '';
    const mpProvince = document.getElementById('province')?.value || '';
    const mpCity = document.getElementById('city')?.value || '';
    
    // Get informant address fields
    const informantHouseNumber = document.getElementById('informant_houseNo');
    const informantStreet = document.getElementById('informant_street');
    const informantBrgy = document.getElementById('informant_brgy');
    const informantRegion = document.getElementById('iregion');
    const informantProvince = document.getElementById('iprovince');
    const informantCity = document.getElementById('icity');
    
    if (isChecked) {
        // Fill informant address fields with missing person data
        if (informantHouseNumber) informantHouseNumber.value = mpHouseNumber;
        if (informantStreet) informantStreet.value = mpStreet;
        if (informantBrgy) informantBrgy.value = mpBrgy;
        
        if (informantRegion && mpRegion) {
            informantRegion.value = mpRegion;
            if (typeof populateIProvinces === 'function') {
                populateIProvinces();
            }
            
            setTimeout(() => {
                if (informantProvince && mpProvince) {
                    informantProvince.value = mpProvince;
                    if (typeof populateICities === 'function') {
                        populateICities();
                    }
                    
                    setTimeout(() => {
                        if (informantCity && mpCity) {
                            informantCity.value = mpCity;
                        }
                    }, 100);
                }
            }, 100);
        }
        
        // Disable fields when same address is checked
        [informantHouseNumber, informantStreet, informantBrgy, informantRegion, informantProvince, informantCity].forEach(field => {
            if (field) field.disabled = true;
        });
    } else {
        // Clear and enable fields when unchecked
        [informantHouseNumber, informantStreet, informantBrgy].forEach(field => {
            if (field) {
                field.disabled = false;
                field.value = '';
            }
        });
        
        if (informantRegion) {
            informantRegion.disabled = false;
            informantRegion.selectedIndex = 0;
        }
        if (informantProvince) {
            informantProvince.disabled = false;
            informantProvince.innerHTML = '<option value="" disabled selected>Select a province</option>';
        }
        if (informantCity) {
            informantCity.disabled = false;
            informantCity.innerHTML = '<option value="" disabled selected>Select a city/municipality</option>';
        }
    }
}

function updateProgressBar(currentStep) {
    const progressFillWacc = document.getElementById('progress_fill_wacc');
    const progressFillNoacc = document.getElementById('progress_fill_noacc');
    const progressSteps = document.querySelectorAll('.progress_step');
    
    // Determine total steps based on which popup is active
    const totalSteps = progressFillNoacc ? 8 : 6;
    
    // Update progress bar fill
    const progressPercentage = (currentStep / totalSteps) * 100;
    if (progressFillWacc) {
        progressFillWacc.style.width = progressPercentage + '%';
    }
    if (progressFillNoacc) {
        progressFillNoacc.style.width = progressPercentage + '%';
    }
    
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    toggleRequiredFields();
    
    // Handle form submission for submit buttons
    const submitButtons = document.querySelectorAll('.submit_button, .submit-btn');
    submitButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const form = this.closest('form');
            if (form) {
                // Remove all required attributes before submission
                const allFields = form.querySelectorAll('input, select, textarea');
                allFields.forEach(field => field.removeAttribute('required'));
                
                // Submit the form
                form.submit();
            }
        });
    });
});