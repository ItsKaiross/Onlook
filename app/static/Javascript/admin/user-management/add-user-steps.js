//################################################################################//
//#####################  A D D  U S E R  F O R M  V A L I D A T I O N  #####################//
//################################################################################//

// Simple form validation for add user modal
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#add-user-popup form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const fields = form.querySelectorAll('input[required], select[required]');
            let isValid = true;
            
            fields.forEach(field => {
                if (!field.checkValidity()) {
                    field.reportValidity();
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
});