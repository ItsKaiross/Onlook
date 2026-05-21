// Modern Lightbox for Case Images
let currentImageIndex = 0;
let currentImages = [];
let currentMainImageIndex = 0;

function openLightbox(images, startIndex = 0) {
    currentImages = images;
    currentImageIndex = startIndex;
    
    const lightbox = document.getElementById('lightbox-modal');
    const lightboxImage = document.getElementById('lightbox-image');
    
    if (currentImages.length > 0) {
        updateLightboxImage();
        lightbox.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Add keyboard navigation
        document.addEventListener('keydown', handleLightboxKeyboard);
    }
}

function closeLightbox() {
    const lightbox = document.getElementById('lightbox-modal');
    lightbox.style.display = 'none';
    document.body.style.overflow = 'auto';
    
    // Remove keyboard navigation
    document.removeEventListener('keydown', handleLightboxKeyboard);
}

function nextLightboxImage() {
    if (currentImages.length > 1) {
        currentImageIndex = (currentImageIndex + 1) % currentImages.length;
        updateLightboxImage();
    }
}

function prevLightboxImage() {
    if (currentImages.length > 1) {
        currentImageIndex = currentImageIndex === 0 ? currentImages.length - 1 : currentImageIndex - 1;
        updateLightboxImage();
    }
}

function updateLightboxImage() {
    const lightboxImage = document.getElementById('lightbox-image');
    const imageCounter = document.getElementById('image-counter');
    const imageTitle = document.getElementById('image-title');
    
    if (currentImages[currentImageIndex]) {
        lightboxImage.src = currentImages[currentImageIndex].src;
        imageCounter.textContent = `${currentImageIndex + 1} / ${currentImages.length}`;
        imageTitle.textContent = currentImages[currentImageIndex].title || 'Case Evidence Photo';
        
        // Add loading animation
        lightboxImage.style.opacity = '0';
        lightboxImage.onload = function() {
            this.style.opacity = '1';
        };
    }
}

function handleLightboxKeyboard(event) {
    switch(event.key) {
        case 'Escape':
            closeLightbox();
            break;
        case 'ArrowLeft':
            prevLightboxImage();
            break;
        case 'ArrowRight':
            nextLightboxImage();
            break;
    }
}

function createImageGallery(images, containerId) {
    const container = document.getElementById(containerId);
    if (!container || !images || images.length === 0) {
        container.innerHTML = `
            <div class="no-images">
                <div class="no-images-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                    </svg>
                </div>
                <h3>No Images Available</h3>
                <p>No evidence photos have been uploaded for this case.</p>
            </div>
        `;
        return;
    }
    
    let galleryHTML = `
        <div class="gallery-header">
            <div class="gallery-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                </svg>
                Evidence Photos
                <span class="gallery-count">${images.length}</span>
            </div>
            <div class="gallery-controls">
                <button class="gallery-btn" onclick="downloadAllImages()">Download All</button>
                <button class="gallery-btn" onclick="openLightbox(currentCaseImages, currentMainImageIndex)">Full Screen</button>
            </div>
        </div>
        <div class="gallery-container">
            <div class="main-image-container">
                <img id="main-gallery-image" src="${images[0].src}" alt="Main Evidence Photo" class="main-image" onclick="openLightbox(currentCaseImages, currentMainImageIndex)">
                <div class="main-image-overlay">
                    <div class="image-title">Evidence Photo 1</div>
                    <div class="image-meta">
                        <span>${images[0].timestamp || new Date().toLocaleDateString()}</span>
                        <span class="image-counter">1 / ${images.length}</span>
                    </div>
                </div>
            </div>
            <div class="thumbnail-grid">
    `;
    
    images.forEach((image, index) => {
        const isActive = index === 0 ? 'active' : '';
        galleryHTML += `
            <div class="thumbnail-item ${isActive}" onclick="switchMainImage(${index})">
                <img src="${image.src}" alt="Thumbnail ${index + 1}" loading="lazy">
                <div class="thumbnail-overlay">
                    <div class="thumbnail-icon">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                        </svg>
                    </div>
                </div>
            </div>
        `;
    });
    
    galleryHTML += '</div></div>';
    container.innerHTML = galleryHTML;
    
    // Store images globally
    window.currentCaseImages = images;
    currentMainImageIndex = 0;
}

function switchMainImage(index) {
    const mainImage = document.getElementById('main-gallery-image');
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    const imageTitle = document.querySelector('.image-title');
    const imageMeta = document.querySelector('.image-meta span:first-child');
    const imageCounter = document.querySelector('.image-counter');
    
    if (mainImage && currentCaseImages[index]) {
        // Update main image
        mainImage.src = currentCaseImages[index].src;
        currentMainImageIndex = index;
        
        // Update active thumbnail
        thumbnails.forEach((thumb, i) => {
            thumb.classList.toggle('active', i === index);
        });
        
        // Update overlay info
        if (imageTitle) imageTitle.textContent = `Evidence Photo ${index + 1}`;
        if (imageMeta) imageMeta.textContent = currentCaseImages[index].timestamp || new Date().toLocaleDateString();
        if (imageCounter) imageCounter.textContent = `${index + 1} / ${currentCaseImages.length}`;
        
        // Add transition effect
        mainImage.style.opacity = '0';
        setTimeout(() => {
            mainImage.style.opacity = '1';
        }, 150);
    }
}

function downloadAllImages() {
    if (currentImages && currentImages.length > 0) {
        currentImages.forEach((image, index) => {
            const link = document.createElement('a');
            link.href = image.src;
            link.download = `case-evidence-${index + 1}.jpg`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }
}

function nextMainImage() {
    const nextIndex = (currentMainImageIndex + 1) % currentCaseImages.length;
    switchMainImage(nextIndex);
}

function prevMainImage() {
    const prevIndex = currentMainImageIndex === 0 ? currentCaseImages.length - 1 : currentMainImageIndex - 1;
    switchMainImage(prevIndex);
}

// Close lightbox when clicking outside the image
document.addEventListener('click', function(event) {
    const lightbox = document.getElementById('lightbox-modal');
    
    if (event.target === lightbox) {
        closeLightbox();
    }
});

// Prevent image dragging
document.addEventListener('dragstart', function(event) {
    if (event.target.tagName === 'IMG') {
        event.preventDefault();
    }
});