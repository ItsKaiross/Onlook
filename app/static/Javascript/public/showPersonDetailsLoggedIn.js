function showPersonDetailsLoggedIn(personId) {
    console.log('showPersonDetailsLoggedIn called with personId:', personId);
    
    // Get the person data from the card to check if reported by user
    const card = document.querySelector(`.picture_card[data-person-id="${personId}"]`);
    
    const isReportedByUser = card ? card.dataset.reportedByUser === 'true' : false;
    console.log('isReportedByUser:', isReportedByUser);
    
    // Get case_id from the card's hidden data
    let caseId = personId; // Default to personId if case_id not found
    if (card) {
        const personData = card.querySelector('.person-data');
        if (personData) {
            // Try to find case_id in the data
            const caseIdSpan = personData.querySelector('.person-case-id');
            if (caseIdSpan) {
                caseId = caseIdSpan.textContent;
            }
        }
    }
    console.log('Using case_id:', caseId);
    
    // Store case_id globally for use in help locate popup
    window.currentCaseId = caseId;
    
    // Create and show loading overlay
    let loadingOverlay = document.getElementById('modal-loading-overlay');
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'modal-loading-overlay';
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 99998;
        `;
        loadingOverlay.innerHTML = `
            <div style="
                background: white;
                padding: 30px 50px;
                border-radius: 10px;
                text-align: center;
                font-size: 18px;
                color: #1A1B41;
            ">
                <div style="
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #1A1B41;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 15px;
                "></div>
                Loading...
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(loadingOverlay);
    }
    loadingOverlay.style.display = 'flex';
    
    // Make AJAX call to get person data
    fetch(`/get-person-data/${personId}`)
        .then(response => response.json())
        .then(data => {
            // Hide loading overlay
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
            
            console.log('Received data:', data);
            if (data.success) {
                const person = data.person;
                
                if (isReportedByUser) {
                    console.log('Showing waccount modal');
                    showWaccountModal(person, caseId);
                } else {
                    console.log('Showing regular modal');
                    showRegularModal(person, caseId);
                }
            } else {
                console.error('Failed to load person data:', data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching person data:', error);
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
        });
}

function showWaccountModal(person, caseId) {
    console.log('showWaccountModal - Setting case_id to:', caseId);
    
    // Update waccount popup content
    document.getElementById('popup-name').textContent = person.name || 'Unknown';
    document.getElementById('popup-age').textContent = person.age || 'Unknown';
    document.getElementById('popup-gender').textContent = person.gender || 'Unknown';
    document.getElementById('popup-height').textContent = person.height || 'Unknown';
    document.getElementById('popup-eyes').textContent = person.eye_color || 'Unknown';
    document.getElementById('popup-hair').textContent = person.hair_color || 'Unknown';
    document.getElementById('popup-attire').textContent = person.last_seen_attire || 'Unknown';
    document.getElementById('popup-last-seen').textContent = person.location || 'Unknown';
    document.getElementById('popup-missing-from').textContent = person.missing_from || 'Unknown';
    document.getElementById('popup-missing-since').textContent = person.last_seen || 'Unknown';
    
    // Handle images
    const leftFrame = document.querySelector('#reported-missing-waccount-popup .left_frame');
    if (person.all_images && person.all_images.length > 1) {
        leftFrame.innerHTML = `
            <div class="image-gallery">
                <div class="main-image-container">
                    <img src="${person.image}" alt="Missing Person" id="popup-image" class="main-image">
                    <button class="gallery-nav-btn gallery-prev-btn" onclick="prevGalleryImage()">&lt;</button>
                    <button class="gallery-nav-btn gallery-next-btn" onclick="nextGalleryImage()">&gt;</button>
                    <div class="image-counter">1 / ${person.all_images.length}</div>
                </div>
            </div>
        `;
        window.galleryImages = person.all_images;
        window.currentGalleryIndex = 0;
    } else {
        leftFrame.innerHTML = `
            <div class="single-image-container" style="position: relative;">
                <img src="${person.image}" alt="Missing Person" id="popup-image">
                <button class="gallery-nav-btn gallery-prev-btn" onclick="prevGalleryImage()">&lt;</button>
                <button class="gallery-nav-btn gallery-next-btn" onclick="nextGalleryImage()">&gt;</button>
            </div>
        `;
        window.galleryImages = [person.image];
        window.currentGalleryIndex = 0;
    }
    
    // Set case_id for help locate popup
    window.currentCaseId = caseId;
    document.getElementById('help-locate-case-id-wacc').value = caseId;
    console.log('Set help-locate-case-id-wacc to:', caseId);
    
    const modal = document.getElementById('reported-missing-waccount-popup');
    const background = document.getElementById('bg-black');
    modal.style.visibility = 'visible';
    modal.style.top = "50%";
    modal.style.transform = "translate(-50%, -50%)";
    modal.style.transition = ".5s";
    modal.style.zIndex = "100002";
    modal.classList.add('show');
    background.style.pointerEvents = "auto";
    background.style.display = "block";
    background.style.zIndex = "100001";
    document.body.style.overflow = "hidden";
}

function showRegularModal(person, caseId) {
    console.log('showRegularModal called with person:', person, 'caseId:', caseId);
    
    const reportedPopup = document.querySelector('#reported-missing-popup');
    console.log('reportedPopup element:', reportedPopup);
    
    if (!reportedPopup) {
        console.error('reported-missing-popup not found!');
        return;
    }
    
    const nameLabel = reportedPopup.querySelector('.first_name_reported_frame label');
    const birthLabel = reportedPopup.querySelector('.birth_reported_frame label');
    const lastSeenLabel = reportedPopup.querySelector('.last_seen_reported_frame label');
    
    if (nameLabel) nameLabel.innerHTML = `Name: ${person.name || 'Unknown'}`;
    if (birthLabel) birthLabel.innerHTML = `Date of Birth: ${person.birthdate || 'Unknown'}`;
    if (lastSeenLabel) lastSeenLabel.innerHTML = `Last Seen: ${person.last_seen || 'Unknown'}`;
    
    const reportedFrame = reportedPopup.querySelector('.reported_frame');
    
    if (reportedFrame) {
        const imageGallery = reportedFrame.querySelector('.image-gallery');
        
        if (imageGallery) {
            const mainImage = imageGallery.querySelector('#reported-main-image');
            
            if (mainImage) {
                mainImage.src = person.image;
                window.reportedImages = person.all_images || [person.image];
                window.currentReportedIndex = 0;
            }
        }
    }
    
    // Set case_id for help locate popup
    window.currentCaseId = caseId;
    const caseIdInput = document.getElementById('help-locate-case-id');
    if (caseIdInput) {
        caseIdInput.value = caseId;
        console.log('Set help-locate-case-id to:', caseId);
    }
    
    const modal = document.querySelector('.reported-missing-modal');
    const background = document.getElementById('bg-black');
    
    if (!modal) {
        console.error('reported-missing-modal not found!');
        return;
    }
    
    modal.classList.add('show');
    modal.style.zIndex = "100001";
    reportedPopup.style.visibility = 'visible';
    reportedPopup.style.opacity = '1';
    reportedPopup.style.zIndex = "100002";
    
    if (background) {
        background.style.pointerEvents = "auto";
        background.style.display = "block";
        background.style.zIndex = "100001";
    }
    
    document.body.style.overflow = "hidden";
    
    console.log('Regular modal should now be visible and centered');
}

function showWaccountPopup() {
    const modal = document.getElementById('reported-missing-waccount-popup');
    const background = document.getElementById('bg-black');
    
    modal.style.visibility = 'visible';
    modal.style.top = "50%";
    modal.style.transform = "translate(-50%, -50%)";
    modal.style.transition = ".5s";
    modal.classList.add('show'); // Add show class for arrows
    background.style.pointerEvents = "none";
    background.style.display = "block";
    
    // Force show navigation buttons after modal is displayed
    setTimeout(() => {
        const navButtons = modal.querySelectorAll('.gallery-nav-btn');
        navButtons.forEach(btn => {
            btn.style.display = 'flex';
            btn.style.visibility = 'visible';
            btn.style.opacity = '1';
        });
    }, 100);
}