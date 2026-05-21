// Mobile table enhancements
function showImage(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('imgModal');
    
    if (modal && modalImg) {
        modal.style.display = 'block';
        modalImg.src = imageSrc;
    }
}

// Close image modal
function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Add click handler for modal close
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('imageModal');
    const closeBtn = modal?.querySelector('.close');
    
    if (closeBtn) {
        closeBtn.onclick = closeImageModal;
    }
    
    if (modal) {
        modal.onclick = function(event) {
            if (event.target === modal) {
                closeImageModal();
            }
        };
    }
    
    // Enhance mobile card interactions
    const userCards = document.querySelectorAll('.user-card');
    userCards.forEach(card => {
        // Add touch feedback
        card.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        card.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
});