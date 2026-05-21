//#####################################################################//
//#####################  DOCUMENT MODALS  ###########################//
//#####################################################################//

function openDocumentModal(modalId, content, type = 'image') {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    const body = modal.querySelector('.document-modal-body');
    
    if (type === 'image') {
        // For images (Profile Picture, Valid ID if image)
        body.innerHTML = `<img src="${content}" alt="Document" onerror="this.parentElement.innerHTML='<div class=\'no-document-message\'>Unable to load image</div>'">`;
    } else if (type === 'pdf') {
        // For PDF documents (PSA, Valid ID if PDF)
        body.innerHTML = `
            <iframe src="${content}" type="application/pdf"></iframe>
            <a href="${content}" download class="document-download-link">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 8px;">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Download PDF Document
            </a>
        `;
    } else if (type === 'document') {
        // For other document types (DOC, DOCX, etc.)
        body.innerHTML = `
            <div class="no-document-message" style="padding: 60px 40px;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#1A1B41" stroke-width="2" style="margin-bottom: 20px;">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <h3 style="margin: 0 0 10px 0; color: #1A1B41; font-family: SF_BOLD;">Document Available</h3>
                <p style="margin: 0 0 20px 0; color: #666;">This document cannot be previewed in the browser.</p>
                <a href="${content}" download class="document-download-link">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 8px;">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download Document
                </a>
            </div>
        `;
    } else {
        body.innerHTML = '<div class="no-document-message">No document available</div>';
    }
    
    modal.classList.add('active');
}

function closeDocumentModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('document-modal')) {
        event.target.classList.remove('active');
    }
});

// Close modal with ESC key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        document.querySelectorAll('.document-modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
});

//#####################################################################//
//#####################  V I E W  P O P U P  #########################//
//#####################################################################//

function showViewPopup(imageSrc) {
    var popup = document.getElementById('viewPopup');
    var popupImage = document.getElementById('viewPopupImage');
    
    if (popup && popupImage && imageSrc) {
        popupImage.src = imageSrc;
        popup.style.display = 'flex';
    }
}

function closeViewPopup() {
    var popup = document.getElementById('viewPopup');
    if (popup) {
        popup.style.display = 'none';
    }
}

function showImage(imageSrc) {
    showViewPopup(imageSrc);
}

function toggle() {
    closeViewPopup();
}

//#####################################################################//
//#####################  T A B L E  V I E W  I D  #####################//
//#####################################################################//

document.addEventListener('click', function(event) {
    var target = event.target;
    
    // Check if clicked on validID image
    if (target.classList.contains('validID')) {
        showViewPopup(target.src);
        return;
    }
    
    // Check if clicked on VIEW text
    if (target.classList.contains('view_txt')) {
        var row = target.closest('tr');
        if (!row) return;
        
        var img = row.querySelector('img.validID');
        if (img && img.src) {
            showViewPopup(img.src);
        }
        return;
    }
});


// tbl_view.onclick = function(){
//     tbl_modal.style.display = "block";
//     tbl_modalImage.src = tbl_image.src;
//     tbl_caption.innerHTML = tbl_image.alt;
// }

//############################################################//
//#####################  V A L I D  I D  #####################//
//############################################################//

function valid_id_img(){
    imageFile = document.getElementById('valid_id')
    validIdImage = document.getElementById('valid_id_view');

    if (imageFile.files.length === 0){
        return;
    }

    const file = imageFile.files[0];

    if(file.size > 1e+6){
        alert('File is too big!')
        imageFile.value = ''
        validIdImage.src = '';
        validIdImage.removeAttribute('data-loaded');
        return;
    }
    
    validIdImage.src = URL.createObjectURL(file);
    validIdImage.setAttribute('data-loaded', 'true');
}


view.onclick = function(){
    const image = document.getElementById('valid_id_view');
    if (image.getAttribute('data-loaded') !== 'true') {
        alert('Please upload an image first.');
        return;
    }
    modal.style.display = "block";
    modalImage.src = image.src;
    captionText.innerHTML = image.alt;
}

//##################################################################//
//#####################  P R O F I L E  P I C  #####################//
//##################################################################//

let profileImageSrc = null;

function profile_img(){
    const imageFile = document.getElementById('profile_picture');
    const previewContainer = document.getElementById('last_seen_preview2');

    if (imageFile.files.length === 0){
        return;
    }

    const file = imageFile.files[0];

    if(file.size > 1e+6){
        alert('File is too big!')
        imageFile.value = ''
        profileImageSrc = null;
        previewContainer.innerHTML = '';
        previewContainer.style.display = 'none';
        return;
    }
    
    profileImageSrc = URL.createObjectURL(file);
    previewContainer.innerHTML = `<img src="${profileImageSrc}" alt="Profile Picture Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px;">`;
    previewContainer.style.display = 'block';
}

function toggleFilePreview() {
    const previewContainer = document.getElementById('last_seen_preview2');
    
    if (!profileImageSrc) {
        alert('Please upload an image first.');
        return;
    }
    
    showViewPopup(profileImageSrc);
}


//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//

// Close popup when clicking outside
document.addEventListener('click', function(event) {
    var popup = document.getElementById('viewPopup');
    if (event.target === popup) {
        closeViewPopup();
    }
});


