document.addEventListener('DOMContentLoaded', function() {
    var modal_add_user = document.getElementById('add-report-popup');
    var add_police_btn = document.getElementById('field-report-btn');
    var background = document.getElementById('bg-black');

    if (!add_police_btn || !modal_add_user || !background) {
        console.error('Manual report button or modal elements not found');
        return;
    }

    add_police_btn.onclick = function(){
        modal_add_user.style.visibility = 'visible'
        modal_add_user.style.top = "50%"
        modal_add_user.style.transform = "translate(-50%, -50%)"
        modal_add_user.style.transition = ".5s"
        background.style.pointerEvents = "none"
        background.style.display = "block"
        
        // Initialize map when modal opens
        setTimeout(function() {
            if (typeof initPopupMap === 'function') {
                initPopupMap();
            }
        }, 300);
    }
});

//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//

function closeModal() {
    var modal_add_user = document.getElementById('add-report-popup');
    var background = document.getElementById('bg-black');
    
    if (modal_add_user && background) {
        modal_add_user.style.visibility = "hidden";
        background.style.display = "none";
        modal_add_user.style.top = "-10%"
        modal_add_user.style.transform = "translate(-50%, -20%)"
        modal_add_user.style.transition = ".5s"
        background.style.transition = ".5s"
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var closeButtons = document.querySelectorAll('.add-report-close, .add-report-close2, .add-report-close3, .add-report-close4');
    closeButtons.forEach(function(btn) {
        btn.onclick = closeModal;
    });
});
