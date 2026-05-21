var modal_help_locate_wacc_public = document.getElementById('help-locate-wacc-popup');
var add_btn = document.getElementById('help_locate_wacc_btn');
var background = document.getElementById('bg-black');

// Function to open help locate with-account popup
function openHelpLocateWaccPopup() {
    // Set case_id dynamically
    let caseId = 0;
    if (window.currentCaseId) {
        caseId = window.currentCaseId;
    }
    
    const caseIdInput = document.getElementById('help-locate-case-id-wacc');
    const form = document.querySelector('#help-locate-wacc-popup form');
    if (caseIdInput) {
        caseIdInput.value = caseId;
        console.log('Set wacc case_id to:', caseId);
    }
    if (form) {
        form.action = `/help-locate-additional-report/${caseId}`;
        console.log('Set wacc form action to:', form.action);
    }
    
    if (!modal_help_locate_wacc_public) {
        return;
    }
    
    modal_help_locate_wacc_public.style.visibility = 'visible'
    modal_help_locate_wacc_public.style.top = "50%"
    modal_help_locate_wacc_public.style.transform = "translate(-50%, -50%)"
    modal_help_locate_wacc_public.style.transition = ".5s"
    modal_help_locate_wacc_public.style.pointerEvents = "auto"
    modal_help_locate_wacc_public.style.zIndex = "10001"
    modal_help_locate_wacc_public.style.display = "block"
    
    if (background) {
        background.style.display = "block"
        background.style.pointerEvents = "none"
    }
    
    // Disable body scroll and interaction
    document.body.style.overflow = 'hidden'
    document.body.classList.add('popup-open')
    
    // Set current date and time
    var now = new Date();
    var timeField = document.getElementById('helpTimeSightingWacc');
    var dateField = document.getElementById('helpDateSightingWacc');
    
    if (timeField) {
        timeField.value = now.toTimeString().slice(0, 5);
    }
    if (dateField) {
        dateField.value = now.toISOString().slice(0, 10);
    }
    
    // Create overlay and blur the first popup
    var firstPopup = document.getElementById('reported-missing-waccount-popup');
    if (firstPopup) {
        firstPopup.style.filter = 'blur(3px)';
        
        var overlay = document.createElement('div');
        overlay.id = 'popup-overlay-wacc';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.zIndex = '9998';
        overlay.style.pointerEvents = 'none';
        document.body.appendChild(overlay);
    }
}

if (add_btn) {
    add_btn.onclick = openHelpLocateWaccPopup;
}

//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//

var close_btn = document.getElementsByClassName('help-locate-wacc-close')[0];

if (close_btn) {
    close_btn.onclick = function(){
        modal_help_locate_wacc_public.style.visibility = "hidden";
        background.style.display = "none";
        modal_help_locate_wacc_public.style.top = "-10%"
        modal_help_locate_wacc_public.style.transform = "translate(-50%, -20%)"
        modal_help_locate_wacc_public.style.transition = ".5s"
        background.style.transition = ".5s"
        
        // Restore body scroll
        document.body.style.overflow = 'auto'
        document.body.classList.remove('popup-open')
        
        // Remove blur
        var firstPopup = document.getElementById('reported-missing-waccount-popup');
        if (firstPopup) {
            firstPopup.style.filter = 'none';
        }
        
        var overlay = document.getElementById('popup-overlay-wacc');
        if (overlay) {
            overlay.remove();
        }
    }
}

// Additional event handler for help locate close button
document.addEventListener('DOMContentLoaded', function() {
    const closeBtn2 = document.querySelector('.help-locate-wacc-close2');
    const modal = document.getElementById('help-locate-wacc-popup');
    const bg = document.getElementById('bg-black');
    
    if (closeBtn2) {
        closeBtn2.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (modal) {
                modal.style.visibility = 'hidden';
                modal.style.top = '-10%';
                modal.style.transform = 'translate(-50%, -20%)';
                modal.style.transition = '.5s';
            }
            if (bg) {
                bg.style.display = 'none';
                bg.style.transition = '.5s';
            }
            
            // Restore body scroll
            document.body.style.overflow = 'auto'
            document.body.classList.remove('popup-open')
            
            // Remove blur
            var firstPopup = document.getElementById('reported-missing-waccount-popup');
            if (firstPopup) {
                firstPopup.style.filter = 'none';
            }
            
            var overlay = document.getElementById('popup-overlay-wacc');
            if (overlay) {
                overlay.remove();
            }
        });
    }
});

// Function to update case_id for help locate with-account popup
function setHelpLocateWaccCaseId(caseId) {
    console.log('setHelpLocateWaccCaseId called with:', caseId);
    const caseIdInput = document.getElementById('help-locate-case-id-wacc');
    const form = document.querySelector('#help-locate-wacc-popup form');
    if (caseIdInput) {
        caseIdInput.value = caseId;
        console.log('Updated wacc case_id input to:', caseId);
    }
    if (form) {
        form.action = `/help-locate-additional-report/${caseId}`;
        console.log('Updated wacc form action to:', form.action);
    }
}

// Help Locate image upload functions
function previewHelpLocateImage() {
    const fileInput = document.getElementById('help_upload_last_seen');
    const preview = document.getElementById('help_last_seen_preview');
    const viewBtn = document.getElementById('help_view_last_seen_btn');
    
    preview.innerHTML = '';
    
    if (fileInput.files.length > 0) {
        viewBtn.style.display = 'block';
        viewBtn.textContent = 'View Image (1)';
        
        const file = fileInput.files[0];
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item';
        fileDiv.style.cssText = 'margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: inline-block; cursor: pointer;';
        fileDiv.onclick = () => openFileModal(file);

        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.cssText = 'width: 100px; height: 100px; object-fit: cover; border-radius: 5px;';
        fileDiv.appendChild(img);

        const fileName = document.createElement('p');
        fileName.textContent = file.name;
        fileName.style.cssText = 'margin: 5px 0; font-size: 12px; text-align: center;';
        fileDiv.appendChild(fileName);

        preview.appendChild(fileDiv);
    } else {
        viewBtn.style.display = 'none';
    }
}

function toggleHelpLocatePreview() {
    const preview = document.getElementById('help_last_seen_preview');
    const btn = document.getElementById('help_view_last_seen_btn');
    
    if (preview.style.display === 'none') {
        preview.style.display = 'block';
        btn.textContent = btn.textContent.replace('View', 'Hide');
    } else {
        preview.style.display = 'none';
        btn.textContent = btn.textContent.replace('Hide', 'View');
    }
}

function openFileModal(file) {
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; display: flex; align-items: center; justify-content: center;';
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };

    const closeBtn = document.createElement('div');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = 'position: absolute; top: 20px; right: 30px; color: white; font-size: 40px; cursor: pointer; z-index: 10001;';
    closeBtn.onclick = () => modal.remove();
    modal.appendChild(closeBtn);

    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.style.cssText = 'max-width: 90%; max-height: 90%; border-radius: 10px;';
    modal.appendChild(img);

    // Add escape key listener
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);

    document.body.appendChild(modal);
}
