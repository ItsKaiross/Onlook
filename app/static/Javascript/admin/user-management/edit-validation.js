// Client-side validation for edit user form
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.querySelector('#edit_popup form');
    
    if (editForm) {
        // Add real-time validation
        const emailInput = editForm.querySelector('input[name="email"]');
        const phoneInput = editForm.querySelector('input[name="number"]');
        const roleSelect = editForm.querySelector('select[name="role"]');
        
        // Email validation
        if (emailInput) {
            emailInput.addEventListener('blur', function() {
                const email = this.value.trim();
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                
                if (email && !emailRegex.test(email)) {
                    showFieldError(this, 'Please enter a valid email address');
                } else {
                    clearFieldError(this);
                }
            });
        }
        
        // Phone validation
        if (phoneInput) {
            phoneInput.addEventListener('blur', function() {
                const phone = this.value.trim();
                const phoneRegex = /^(\+639|09)\d{9}$/;
                
                if (phone && !phoneRegex.test(phone)) {
                    showFieldError(this, 'Please enter a valid Philippine phone number');
                } else {
                    clearFieldError(this);
                }
            });
        }
        
        // Role change warning
        if (roleSelect) {
            let originalRole = roleSelect.value;
            
            roleSelect.addEventListener('change', function() {
                const newRole = this.value;
                
                // Warn about systemAdmin to police role changes
                if (originalRole === 'systemAdmin' && 
                    (newRole === 'police' || newRole === 'policeAdmin' || newRole.includes('-mps') || newRole.includes('-ps'))) {
                    showRoleChangeWarning('Changing from System Admin to Police role may fail if no police record exists.');
                }
                // Warn about citizen to police role changes
                else if (originalRole === 'citizen' && 
                    (newRole === 'police' || newRole === 'policeAdmin' || newRole.includes('-mps') || newRole.includes('-ps'))) {
                    showRoleChangeWarning('Citizens cannot be changed to Police roles without proper registration.');
                }
                else {
                    clearRoleChangeWarning();
                }
            });
        }
        
        // Form submission validation
        editForm.addEventListener('submit', function(e) {
            let hasErrors = false;
            
            // Check all required fields
            const requiredFields = editForm.querySelectorAll('input[required], select[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    showFieldError(field, 'This field is required');
                    hasErrors = true;
                }
            });
            
            // Check email format
            if (emailInput && emailInput.value.trim()) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailInput.value.trim())) {
                    showFieldError(emailInput, 'Please enter a valid email address');
                    hasErrors = true;
                }
            }
            
            // Check phone format
            if (phoneInput && phoneInput.value.trim()) {
                const phoneRegex = /^(\+639|09)\d{9}$/;
                if (!phoneRegex.test(phoneInput.value.trim())) {
                    showFieldError(phoneInput, 'Please enter a valid Philippine phone number');
                    hasErrors = true;
                }
            }
            
            if (hasErrors) {
                e.preventDefault();
                return false;
            }
        });
    }
});

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '5px';
    
    field.style.borderColor = '#dc3545';
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    field.style.borderColor = '';
}

function showRoleChangeWarning(message) {
    clearRoleChangeWarning();
    
    const warningDiv = document.createElement('div');
    warningDiv.className = 'role-change-warning';
    warningDiv.innerHTML = `
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 10px; border-radius: 5px; margin: 10px 0; font-size: 12px;">
            <strong>⚠️ Warning:</strong> ${message}
        </div>
    `;
    
    const roleFrame = document.querySelector('#edit_popup .role_frame');
    if (roleFrame) {
        roleFrame.appendChild(warningDiv);
    }
}

function clearRoleChangeWarning() {
    const existingWarning = document.querySelector('.role-change-warning');
    if (existingWarning) {
        existingWarning.remove();
    }
}