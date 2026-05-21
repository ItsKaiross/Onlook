// Image preview function
function last_seen_img() {
    const fileInput = document.querySelector('input[name="upload_last_seen"]');
    const imageView = document.getElementById('image_view');
    
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imageView.src = e.target.result;
            imageView.style.display = 'block';
        };
        reader.readAsDataURL(fileInput.files[0]);
    }
}

// View image modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const viewImageBtn = document.getElementById('view_last_seen');
    const imageView = document.getElementById('image_view');
    
    if (viewImageBtn) {
        viewImageBtn.addEventListener('click', function() {
            if (imageView.src && imageView.src !== window.location.href) {
                showImageModal(imageView.src);
            } else {
                alert('Please upload an image first.');
            }
        });
    }
});

// Image modal functions
function showImageModal(imageSrc) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('imageModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'imageModal';
        modal.style.cssText = `
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
        `;
        
        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            position: relative;
            margin: 5% auto;
            width: 80%;
            max-width: 700px;
            text-align: center;
        `;
        
        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = `
            position: absolute;
            top: -40px;
            right: 0;
            color: white;
            font-size: 35px;
            font-weight: bold;
            cursor: pointer;
        `;
        closeBtn.onclick = closeImageModal;
        
        const modalImg = document.createElement('img');
        modalImg.id = 'modalImage';
        modalImg.style.cssText = `
            width: 100%;
            height: auto;
            max-height: 80vh;
            object-fit: contain;
        `;
        
        modalContent.appendChild(closeBtn);
        modalContent.appendChild(modalImg);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
    }
    
    const modalImg = document.getElementById('modalImage');
    modalImg.src = imageSrc;
    modal.style.display = 'block';
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside the image
window.onclick = function(event) {
    const modal = document.getElementById('imageModal');
    if (event.target === modal) {
        closeImageModal();
    }
}
