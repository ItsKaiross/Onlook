// Modal and Image Gallery JavaScript Functions

// Global variables
window.reportedImages = [];
window.currentReportedIndex = 0;
window.galleryImages = [];
window.currentGalleryIndex = 0;

// Reported frame image navigation functions
function nextReportedImage() {
    if (window.reportedImages && window.reportedImages.length > 1) {
        window.currentReportedIndex = (window.currentReportedIndex + 1) % window.reportedImages.length;
        updateReportedImage();
    }
}

function prevReportedImage() {
    if (window.reportedImages && window.reportedImages.length > 1) {
        window.currentReportedIndex = (window.currentReportedIndex - 1 + window.reportedImages.length) % window.reportedImages.length;
        updateReportedImage();
    }
}

// Function to set reported images from person data
function setReportedImages(images) {
    window.reportedImages = images || [];
    window.currentReportedIndex = 0;
    updateReportedImage();
}

function updateReportedImage() {
    const mainImage = document.getElementById('reported-main-image');
    const counter = document.querySelector('.image-counter');
    
    if (mainImage && window.reportedImages && window.reportedImages.length > 0) {
        mainImage.src = window.reportedImages[window.currentReportedIndex];
        if (counter) {
            counter.textContent = `${window.currentReportedIndex + 1} / ${window.reportedImages.length}`;
        }
        
        // Update dots
        const dots = document.querySelectorAll('.reported-dot');
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === window.currentReportedIndex);
        });
    }
}

// Function to update reported images when popup opens
function updateReportedImagesFromPersonData() {
    // This function will be called by the carousel when showing person details
    // The images are already set by the showPersonDetails function
    if (window.reportedImages && window.reportedImages.length > 0) {
        updateReportedImage();
        
        // Update dots if they exist
        const dots = document.querySelectorAll('.reported-dot');
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === window.currentReportedIndex);
        });
    }
}

// Show reported missing modal
function showReportedMissingModal() {
    const modal = document.querySelector('.reported-missing-modal');
    const popup = document.getElementById('reported-missing-popup');
    const blackBg = document.getElementById('bg-black');
    
    if (modal && popup) {
        // Show modal elements
        modal.style.display = 'flex';
        modal.classList.add('show');
        popup.style.visibility = 'visible';
        popup.style.opacity = '1';
        
        // Show background if it exists
        if (blackBg) {
            blackBg.style.display = 'block';
            blackBg.style.pointerEvents = 'auto';
        }
        
        // Add body class to prevent scrolling
        document.body.classList.add('popup-open');
        
        // Initialize images from first missing person
        const firstPerson = document.querySelector('.person-all-images');
        if (firstPerson) {
            updateReportedImagesFromPersonData();
        }
    }
}

// Close reported missing modal
function closeReportedMissingModal() {
    const modal = document.querySelector('.reported-missing-modal');
    const popup = document.getElementById('reported-missing-popup');
    const blackBg = document.getElementById('bg-black');
    
    if (modal && popup) {
        modal.style.display = 'none';
        modal.classList.remove('show');
        popup.style.visibility = 'hidden';
        popup.style.opacity = '0';
        
        // Hide background if it exists
        if (blackBg) {
            blackBg.style.display = 'none';
            blackBg.style.pointerEvents = 'none';
        }
        
        // Remove body class
        document.body.classList.remove('popup-open');
    }
}

// Gallery navigation functions
function nextGalleryImage() {
    if (window.galleryImages && window.galleryImages.length > 1) {
        window.currentGalleryIndex = (window.currentGalleryIndex + 1) % window.galleryImages.length;
        updateGalleryImage();
    }
}

function prevGalleryImage() {
    if (window.galleryImages && window.galleryImages.length > 1) {
        window.currentGalleryIndex = (window.currentGalleryIndex - 1 + window.galleryImages.length) % window.galleryImages.length;
        updateGalleryImage();
    }
}

function updateGalleryImage() {
    const mainImage = document.getElementById('popup-image');
    const counter = document.querySelector('#reported-missing-waccount-popup .image-counter');
    const dots = document.querySelectorAll('#reported-missing-waccount-popup .gallery-dot');
    
    if (mainImage && window.galleryImages) {
        mainImage.src = window.galleryImages[window.currentGalleryIndex];
        if (counter) {
            counter.textContent = `${window.currentGalleryIndex + 1} / ${window.galleryImages.length}`;
        }
        
        // Update dots
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === window.currentGalleryIndex);
        });
    }
}

// Function to switch to specific image via dots
function switchToGalleryImage(index) {
    if (window.galleryImages && index >= 0 && index < window.galleryImages.length) {
        window.currentGalleryIndex = index;
        updateGalleryImage();
    }
}

// Card Image Carousel Functions
function nextCardImage(button) {
    const carousel = button.closest('.card-image-carousel');
    const img = carousel.querySelector('.card_img');
    const dots = carousel.querySelectorAll('.card-dot');
    const images = JSON.parse(carousel.dataset.images);
    
    let currentIndex = 0;
    dots.forEach((dot, index) => {
        if (dot.classList.contains('active')) {
            currentIndex = index;
        }
    });
    
    const nextIndex = (currentIndex + 1) % images.length;
    
    img.src = images[nextIndex];
    dots[currentIndex].classList.remove('active');
    dots[nextIndex].classList.add('active');
}

function prevCardImage(button) {
    const carousel = button.closest('.card-image-carousel');
    const img = carousel.querySelector('.card_img');
    const dots = carousel.querySelectorAll('.card-dot');
    const images = JSON.parse(carousel.dataset.images);
    
    let currentIndex = 0;
    dots.forEach((dot, index) => {
        if (dot.classList.contains('active')) {
            currentIndex = index;
        }
    });
    
    const prevIndex = (currentIndex - 1 + images.length) % images.length;
    
    img.src = images[prevIndex];
    dots[currentIndex].classList.remove('active');
    dots[prevIndex].classList.add('active');
}

// Auto-cycle through images (optional)
function initCardImageCarousels() {
    const carousels = document.querySelectorAll('.card-image-carousel');
    
    carousels.forEach(carousel => {
        const images = JSON.parse(carousel.dataset.images);
        if (images.length > 1) {
            let currentIndex = 0;
            
            // Auto-cycle every 3 seconds
            setInterval(() => {
                const img = carousel.querySelector('.card_img');
                const dots = carousel.querySelectorAll('.card-dot');
                
                dots[currentIndex].classList.remove('active');
                currentIndex = (currentIndex + 1) % images.length;
                dots[currentIndex].classList.add('active');
                img.src = images[currentIndex];
            }, 3000);
        }
    });
}

// Initialize modal functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize carousels
    initCardImageCarousels();
    
    // Close button functionality
    const closeBtn = document.querySelector('.reported-missing-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeReportedMissingModal);
    }
    
    // Background click to close
    const blackBg = document.getElementById('bg-black');
    if (blackBg) {
        blackBg.addEventListener('click', function(e) {
            // Only close if clicking the background itself, not child elements
            if (e.target === blackBg) {
                closeReportedMissingModal();
            }
        });
    }
    
    // Make functions globally available
    window.showReportedMissingModal = showReportedMissingModal;
    window.closeReportedMissingModal = closeReportedMissingModal;
    window.nextReportedImage = nextReportedImage;
    window.prevReportedImage = prevReportedImage;
    window.updateReportedImage = updateReportedImage;
    window.setReportedImages = setReportedImages;
});