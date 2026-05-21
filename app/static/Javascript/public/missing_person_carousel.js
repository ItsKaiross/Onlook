// Function to show person details in popup
function showPersonDetails(personId) {
    // Set the current case ID for help locate functionality
    window.currentCaseId = personId;
    
    // Find the person card with matching ID
    const personCard = document.querySelector(`[data-person-id="${personId}"]`);
    if (!personCard) return;
    
    // Get person data from hidden elements
    const personData = personCard.querySelector('.person-data');
    if (!personData) return;
    
    const name = personData.querySelector('.person-name').textContent;
    const birthdate = personData.querySelector('.person-birthdate').textContent;
    const lastSeen = personData.querySelector('.person-last-seen').textContent;
    const image = personData.querySelector('.person-image').textContent;
    const allImagesElement = personData.querySelector('.person-all-images');
    const allImages = allImagesElement?.dataset.images ? JSON.parse(allImagesElement.dataset.images) : [];
    
    // Set images for the modal gallery system
    const imagesToUse = allImages.length > 0 ? allImages : [image || 'static/images/public_page/missing.jpg'];
    if (window.setReportedImages) {
        window.setReportedImages(imagesToUse);
    }
    
    // Update popup content with data
    const popupContent = document.querySelector('#reported-missing-popup');
    
    // Update name
    const existingNameLabel = popupContent.querySelector('.first_name_reported_frame label');
    if (existingNameLabel) {
        existingNameLabel.innerHTML = `Name: ${name || 'Unknown'}`;
    }
    
    // Update birthdate
    const existingBirthdateLabel = popupContent.querySelector('.birth_reported_frame label');
    if (existingBirthdateLabel) {
        existingBirthdateLabel.innerHTML = `Date of Birth: ${birthdate || 'Unknown'}`;
    }
    
    // Update last seen
    const existingLastSeenLabel = popupContent.querySelector('.last_seen_reported_frame label');
    if (existingLastSeenLabel) {
        existingLastSeenLabel.innerHTML = `Last Seen: ${lastSeen || 'Unknown'}`;
    }
    
    // Update help locate button with correct person ID
    const helpLocateBtn = document.getElementById('help_locate_no_acc_btn');
    if (helpLocateBtn) {
        // Remove any existing event listeners
        helpLocateBtn.onclick = null;
        
        // Add new event listener for help locate functionality
        helpLocateBtn.addEventListener('click', function() {
            // Update the form action and hidden input
            const helpLocateForm = document.getElementById('help-locate-no-acc-form');
            if (helpLocateForm) {
                helpLocateForm.action = `/help-locate-additional-report/${personId}`;
            }
            const helpLocateCaseId = document.getElementById('help-locate-case-id');
            if (helpLocateCaseId) {
                helpLocateCaseId.value = personId;
            }
            
            // Set the global case ID
            window.currentCaseId = personId;
            
            // Show help locate popup
            if (typeof openHelpLocateNoAccPopup === 'function') {
                openHelpLocateNoAccPopup();
            }
        });
    }
    
    // Show the popup modal using the unified modal function
    if (window.showReportedMissingModal) {
        window.showReportedMissingModal();
    }
}

// Close popup function
function closePopup() {
    if (window.closeReportedMissingModal) {
        window.closeReportedMissingModal();
    }
}

// Carousel functionality
let currentIndex = 0;
const cardsPerView = 4;

function updateCarousel(direction = 'none') {
    const cards = document.querySelectorAll('.picture_card');
    const totalCards = cards.length;
    
    // Clear all fade classes
    cards.forEach(card => {
        card.classList.remove('fade-edge');
    });
    
    // Show/hide cards without animations
    cards.forEach((card, index) => {
        if (index >= currentIndex && index < currentIndex + cardsPerView) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Update button states
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    prevBtn.disabled = currentIndex === 0;
    nextBtn.disabled = currentIndex + cardsPerView >= totalCards;
}

function fadeEdgeCard(direction) {
    const cards = document.querySelectorAll('.picture_card');
    
    if (direction === 'next') {
        // Fade the last visible card
        const lastVisibleIndex = currentIndex + cardsPerView - 1;
        if (cards[lastVisibleIndex]) {
            cards[lastVisibleIndex].classList.add('fade-edge');
            setTimeout(() => {
                cards[lastVisibleIndex].classList.remove('fade-edge');
            }, 300);
        }
    } else if (direction === 'prev') {
        // Fade the first visible card
        if (cards[currentIndex]) {
            cards[currentIndex].classList.add('fade-edge');
            setTimeout(() => {
                cards[currentIndex].classList.remove('fade-edge');
            }, 300);
        }
    }
}

function nextCards() {
    const totalCards = document.querySelectorAll('.picture_card').length;
    if (currentIndex + cardsPerView < totalCards) {
        fadeEdgeCard('next');
        setTimeout(() => {
            currentIndex++;
            updateCarousel();
        }, 150);
    }
}

function previousCards() {
    if (currentIndex > 0) {
        fadeEdgeCard('prev');
        setTimeout(() => {
            currentIndex--;
            updateCarousel();
        }, 150);
    }
}

// Logged-in carousel functionality
let currentIndexLoggedIn = 0;
const cardsPerViewLoggedIn = 4;

function updateCarouselLoggedIn() {
    const cards = document.querySelectorAll('#loggedInCarousel .picture_card');
    const totalCards = cards.length;
    
    cards.forEach(card => {
        card.classList.remove('fade-edge');
    });
    
    cards.forEach((card, index) => {
        if (index >= currentIndexLoggedIn && index < currentIndexLoggedIn + cardsPerViewLoggedIn) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
    
    const prevBtn = document.getElementById('prevBtnLoggedIn');
    const nextBtn = document.getElementById('nextBtnLoggedIn');
    if (prevBtn) prevBtn.disabled = currentIndexLoggedIn === 0;
    if (nextBtn) nextBtn.disabled = currentIndexLoggedIn + cardsPerViewLoggedIn >= totalCards;
}

function fadeEdgeCardLoggedIn(direction) {
    const cards = document.querySelectorAll('#loggedInCarousel .picture_card');
    
    if (direction === 'next') {
        const lastVisibleIndex = currentIndexLoggedIn + cardsPerViewLoggedIn - 1;
        if (cards[lastVisibleIndex]) {
            cards[lastVisibleIndex].classList.add('fade-edge');
            setTimeout(() => {
                cards[lastVisibleIndex].classList.remove('fade-edge');
            }, 300);
        }
    } else if (direction === 'prev') {
        if (cards[currentIndexLoggedIn]) {
            cards[currentIndexLoggedIn].classList.add('fade-edge');
            setTimeout(() => {
                cards[currentIndexLoggedIn].classList.remove('fade-edge');
            }, 300);
        }
    }
}

function nextCardsLoggedIn() {
    const totalCards = document.querySelectorAll('#loggedInCarousel .picture_card').length;
    if (currentIndexLoggedIn + cardsPerViewLoggedIn < totalCards) {
        fadeEdgeCardLoggedIn('next');
        setTimeout(() => {
            currentIndexLoggedIn++;
            updateCarouselLoggedIn();
        }, 150);
    }
}

function previousCardsLoggedIn() {
    if (currentIndexLoggedIn > 0) {
        fadeEdgeCardLoggedIn('prev');
        setTimeout(() => {
            currentIndexLoggedIn--;
            updateCarouselLoggedIn();
        }, 150);
    }
}

function showPersonDetailsLoggedIn(personId) {
    // Find the person card with matching ID
    const personCard = document.querySelector(`[data-person-id="${personId}"]`);
    if (!personCard) {
        // Fallback to fetch from backend if card not found
        fetch(`/get-person-data/${personId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayPersonDetailsLoggedIn(data.person, personId);
                }
            })
            .catch(error => {
                console.error('Error fetching person data:', error);
            });
        return;
    }
    
    // Get person data from hidden elements
    const personData = personCard.querySelector('.person-data');
    if (!personData) return;
    
    const name = personData.querySelector('.person-name').textContent;
    const age = personData.querySelector('.person-age').textContent;
    const gender = personData.querySelector('.person-gender').textContent;
    const height = personData.querySelector('.person-height').textContent;
    const eyeColor = personData.querySelector('.person-eye-color').textContent;
    const hairColor = personData.querySelector('.person-hair-color').textContent;
    const attire = personData.querySelector('.person-attire').textContent;
    const location = personData.querySelector('.person-location').textContent;
    const birthdate = personData.querySelector('.person-birthdate').textContent;
    const lastSeen = personData.querySelector('.person-last-seen').textContent;
    const image = personData.querySelector('.person-image').textContent;
    const allImagesElement = personData.querySelector('.person-all-images');
    const allImages = allImagesElement?.dataset.images ? JSON.parse(allImagesElement.dataset.images) : [];
    
    const personObj = {
        name: name || 'Unknown',
        age: age || 'Unknown',
        gender: gender || 'Unknown',
        height: height || 'Unknown',
        eye_color: eyeColor || 'Unknown',
        hair_color: hairColor || 'Unknown',
        last_seen_attire: attire || 'Unknown',
        location: location || 'Unknown',
        missing_from: 'Laguna, Philippines',
        last_seen: lastSeen || 'Unknown',
        image: image || 'static/images/public_page/missing.jpg',
        all_images: allImages.length > 0 ? allImages : [image || 'static/images/public_page/missing.jpg']
    };
    
    displayPersonDetailsLoggedIn(personObj, personId);
}

function displayPersonDetailsLoggedIn(person, personId) {
    // Set the current case ID for help locate functionality
    window.currentCaseId = personId;
    
    // Store images globally for switchImage function
    window.currentImages = person.all_images || [person.image];
    window.currentImageIndex = 0;
    
    // Update the left frame with image gallery or single image
    const leftFrame = document.querySelector('#reported-missing-waccount-popup .left_frame');
    if (person.all_images && person.all_images.length > 1) {
        leftFrame.innerHTML = `
            <div class="image-gallery">
                <div class="main-image-container">
                    <img src="${person.all_images[0]}" alt="Missing Person" id="popup-image" class="main-image" onerror="this.src='static/images/public_page/missing.jpg'">
                    <button class="gallery-nav-btn gallery-prev-btn" onclick="prevGalleryImage()">&lt;</button>
                    <button class="gallery-nav-btn gallery-next-btn" onclick="nextGalleryImage()">&gt;</button>
                    <div class="gallery-image-dots">
                        ${person.all_images.map((_, index) => `
                            <span class="gallery-dot ${index === 0 ? 'active' : ''}" onclick="switchToGalleryImage(${index})"></span>
                        `).join('')}
                    </div>
                    <div class="image-counter">1 / ${person.all_images.length}</div>
                </div>
            </div>
        `;
    } else {
        leftFrame.innerHTML = `<img src="${person.image || 'static/images/public_page/missing.jpg'}" alt="Missing Person" id="popup-image" onerror="this.src='static/images/public_page/missing.jpg'">`;
    }
                
    // Update text elements
    const elements = {
        'popup-name': person.name || 'Unknown',
        'popup-age': person.age || 'Unknown',
        'popup-gender': person.gender || 'Unknown',
        'popup-missing-from': person.missing_from || 'Unknown',
        'popup-last-seen': person.location || 'Unknown',
        'popup-eyes': person.eye_color || 'Unknown',
        'popup-height': person.height || 'Unknown',
        'popup-hair': person.hair_color || 'Unknown',
        'popup-attire': person.last_seen_attire || 'Unknown',
        'popup-missing-since': person.last_seen || 'Unknown'
    };
    
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = elements[id];
        }
    });
                
    // Show the popup
    const modal = document.getElementById('reported-missing-waccount-popup');
    const bg = document.getElementById('bg-black');
    const base = document.querySelector('.base');
    
    modal.classList.add('show');
    modal.style.top = '50%';
    bg.style.display = 'block';
    document.body.classList.add('popup-open');
    
    if (base) {
        base.classList.add('disabled');
    }
    
    // Update help locate button with correct case ID
    const helpLocateBtn = document.getElementById('help_locate_wacc_btn');
    if (helpLocateBtn) {
        helpLocateBtn.onclick = function() {
            document.getElementById('help-locate-case-id-wacc').value = personId;
        };
    }
}

// Image gallery switching functions
function switchImage(index, imageSrc) {
    const mainImage = document.getElementById('popup-image');
    const thumbnails = document.querySelectorAll('#reported-missing-waccount-popup .thumbnail');
    const counter = document.querySelector('#reported-missing-waccount-popup .image-counter');
    
    if (mainImage) {
        mainImage.src = imageSrc;
        window.currentImageIndex = index;
        
        // Update active thumbnail
        thumbnails.forEach((thumb, i) => {
            thumb.classList.toggle('active', i === index);
        });
        
        // Update counter
        if (counter) {
            counter.textContent = `${index + 1} / ${thumbnails.length}`;
        }
    }
}

function switchImageNoAcc(index, imageSrc) {
    const mainImage = document.getElementById('popup-no-acc-image');
    const thumbnails = document.querySelectorAll('#reported-missing-popup .thumbnail');
    const counter = document.querySelector('#reported-missing-popup .image-counter');
    
    if (mainImage) {
        mainImage.src = imageSrc;
        window.currentImageIndex = index;
        
        // Update active thumbnail
        thumbnails.forEach((thumb, i) => {
            thumb.classList.toggle('active', i === index);
        });
        
        // Update counter
        if (counter) {
            counter.textContent = `${index + 1} / ${thumbnails.length}`;
        }
    }
}

    // Initialize when DOM loads
    document.addEventListener('DOMContentLoaded', function() {
        updateCarousel();
        updateCarouselLoggedIn();
        
        // Remove duplicate close button handlers since they're handled in modal-gallery.js
        const bg = document.getElementById('bg-black');
        if (bg) {
            bg.addEventListener('click', function(e) {
                if (e.target === bg) {
                    closePopup();
                }
            });
        }
    });