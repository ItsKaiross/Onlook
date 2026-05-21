document.addEventListener('DOMContentLoaded', function() {
    // Report missing button
    const reportBtn = document.getElementById('report-missing');
    if (reportBtn) {
        reportBtn.addEventListener('click', function () {
            const modal = document.getElementById('report-missing-popup');
            const bg = document.getElementById('bg-black');
            const base = document.querySelector('.base');
            
            if (modal && bg && base) {
                modal.style.visibility = 'visible';
                modal.style.top = '50%';
                modal.style.transform = 'translate(-50%, -50%)';
                modal.style.transition = '.5s';
                bg.style.display = 'block';
                base.classList.add('disabled');
                document.body.classList.add('popup-open');
            }
        });
    }

    // Close buttons for report missing popup
    document.querySelectorAll('.w-noacc-missing-report-close, .w-noacc-missing-report-close2, .w-noacc-missing-report-close3, .w-noacc-missing-report-close4, .w-noacc-missing-report-close5').forEach(btn => {
        btn.addEventListener('click', function(){
            const modal = document.getElementById('report-missing-popup');
            const bg = document.getElementById('bg-black');
            const base = document.querySelector('.base');
            
            if (modal) {
                modal.style.visibility = 'hidden';
                modal.style.top = '-10%';
                modal.style.transform = 'translate(-50%, -20%)';
                modal.style.transition = '.5s';
            }
            
            if (bg) {
                bg.style.display = 'none';
            }
            
            if (base) {
                base.classList.remove('disabled');
            }
            
            // Remove body restrictions
            document.body.classList.remove('popup-open');
            document.body.style.pointerEvents = 'auto';
            document.body.style.overflow = 'auto';
        });
    });

    // Close buttons for reported missing popup
    document.querySelectorAll('.reported-missing-close, .reported-missing-waccount-close').forEach(btn => {
        btn.addEventListener('click', function(){
            const regularModal = document.getElementById('reported-missing-popup');
            const waccountModal = document.getElementById('reported-missing-waccount-popup');
            const bg = document.getElementById('bg-black');
            const base = document.querySelector('.base');
            
            // Close regular popup
            if (regularModal) {
                regularModal.style.visibility = 'hidden';
                regularModal.style.transition = '.5s';
            }
            
            // Close waccount popup
            if (waccountModal) {
                waccountModal.style.visibility = 'hidden';
                waccountModal.style.transition = '.5s';
            }
            
            // Remove background and disabled effects
            if (bg) {
                bg.style.display = 'none';
                bg.style.transition = '.5s';
            }
            
            if (base) {
                base.classList.remove('disabled');
            }
            
            // Remove body restrictions
            document.body.classList.remove('popup-open');
            document.body.style.pointerEvents = 'auto';
            document.body.style.overflow = 'auto';
        });
    });
    
    // Background click to close popups
    const bg = document.getElementById('bg-black');
    if (bg) {
        bg.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const regularModal = document.getElementById('reported-missing-popup');
            const waccountModal = document.getElementById('reported-missing-waccount-popup');
            const reportModal = document.getElementById('report-missing-popup');
            const base = document.querySelector('.base');
            
            // Close all modals
            if (regularModal) {
                regularModal.style.visibility = 'hidden';
                regularModal.style.top = '-10%';
                regularModal.style.transform = 'translate(-50%, -20%)';
                regularModal.style.transition = '.5s';
            }
            
            if (waccountModal) {
                waccountModal.style.visibility = 'hidden';
                waccountModal.style.top = '-10%';
                waccountModal.style.transform = 'translate(-50%, -20%)';
                waccountModal.style.transition = '.5s';
            }
            
            if (reportModal) {
                reportModal.style.visibility = 'hidden';
                reportModal.style.top = '-10%';
                reportModal.style.transform = 'translate(-50%, -20%)';
                reportModal.style.transition = '.5s';
            }
            
            // Remove background and effects
            bg.style.display = 'none';
            bg.style.transition = '.5s';
            
            if (base) {
                base.classList.remove('disabled');
            }
            
            // Remove body restrictions
            document.body.classList.remove('popup-open');
            document.body.style.pointerEvents = 'auto';
            document.body.style.overflow = 'auto';
        });
    }
});