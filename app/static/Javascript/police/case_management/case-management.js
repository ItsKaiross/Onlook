let currentImages = [];
let currentImageIndex = 0;

// ALL OTHER FUNCTION DEFINITIONS

// Notification functions
function toggleNotifications() {
    const overlay = document.getElementById('notificationOverlay');
    if (overlay) overlay.style.display = overlay.style.display === 'block' ? 'none' : 'block';
}

function closeNotifications() {
    const overlay = document.getElementById('notificationOverlay');
    if (overlay) overlay.style.display = 'none';
}

function markNotificationsRead() {
    console.log('Marking notifications as read');
}

function generateReport() {
    const status = document.getElementById('status-filter').value;
    const fromDate = document.getElementById('from-date').value;
    const toDate = document.getElementById('to-date').value;
    
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);
    
    window.location.href = `/police-case-management?${params.toString()}`;
}

function displayCaseDetails(caseData) {
    // Forward to the actual implementation if it exists elsewhere
    if (window.displayCaseDetails && window.displayCaseDetails !== displayCaseDetails) {
        return window.displayCaseDetails(caseData);
    }
    
    // Otherwise use basic implementation
    const modal = document.getElementById('case-details-modal');
    if (!modal) {
        alert('Modal not found');
        return;
    }
    
    const contentElement = document.getElementById('case-details-content');
    if (!contentElement) return;
    
    contentElement.innerHTML = `
        <div class="case-file-view">
            <h3>Case #${caseData.case_id}</h3>
            <div class="case-info">
                <p><strong>Name:</strong> ${caseData.full_name || 'N/A'}</p>
                <p><strong>Age:</strong> ${caseData.age || 'N/A'}</p>
                <p><strong>Status:</strong> ${caseData.case_status || 'N/A'}</p>
            </div>
        </div>
    `;
    
    modal.style.display = 'flex';
    modal.classList.add('show');
}

function populateEditCaseForm(caseData) {
    document.getElementById('edit-case-id').value = caseData.case_id;
    document.getElementById('edit-case-status').value = caseData.case_status || '';
    document.getElementById('edit-priority').value = caseData.priority || '';
    document.getElementById('edit-full-name').value = caseData.full_name || '';
    document.getElementById('edit-gender').value = caseData.gender || '';
    document.getElementById('edit-height').value = caseData.height || '';
    document.getElementById('edit-weight').value = caseData.weight || '';
    document.getElementById('edit-hair-color').value = caseData.hair_color || '';
    document.getElementById('edit-eye-color').value = caseData.eye_color || '';
    document.getElementById('edit-date-last-seen').value = caseData.date_last_seen || '';
    document.getElementById('edit-clothing').value = caseData.clothing_description || '';
}

function openImageModal(index) {
    currentImageIndex = index;
    document.getElementById('modal-image').src = currentImages[index].src;
    document.getElementById('image-modal').style.display = 'block';
}

function closeImageModal() {
    document.getElementById('image-modal').style.display = 'none';
}

function prevImage() {
    currentImageIndex = (currentImageIndex - 1 + currentImages.length) % currentImages.length;
    document.getElementById('modal-image').src = currentImages[currentImageIndex].src;
}

function nextImage() {
    currentImageIndex = (currentImageIndex + 1) % currentImages.length;
    document.getElementById('modal-image').src = currentImages[currentImageIndex].src;
}

function downloadImage() {
    const img = document.getElementById('modal-image');
    const link = document.createElement('a');
    link.href = img.src;
    link.download = `case-image-${currentImageIndex + 1}.jpg`;
    link.click();
}

function switchMainImage(index) {
    // This function is now in kebab file
    if (window.switchMainImage && window.switchMainImage !== switchMainImage) {
        return window.switchMainImage(index);
    }
    console.warn('switchMainImage called from main script - using kebab version');
}

function openFollowupModal(caseId) {
    document.getElementById('followup-modal').style.display = 'block';
    
    fetch(`/police-case-details/${caseId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.case.reporters) {
                displayFollowupReports(data.case.reporters);
            }
        })
        .catch(error => {
            console.error('Error loading follow-up reports:', error);
        });
}

function closeFollowupModal() {
    document.getElementById('followup-modal').style.display = 'none';
}

function displayFollowupReports(reporters) {
    const content = document.getElementById('followup-content');
    
    if (!reporters || reporters.length === 0) {
        content.innerHTML = `
            <div class="no-reports">
                <div class="no-reports-icon">ðŸ“‹</div>
                <h4>No Follow-up Reports</h4>
                <p>No additional reports have been submitted for this case.</p>
            </div>
        `;
        return;
    }
    
    
    content.innerHTML = `
        <div class="reports-grid">
            ${reporters.map((reporter, index) => `
                <div class="report-card">
                    <div class="card-header">
                        <div class="reporter-avatar">${reporter.name ? reporter.name.charAt(0).toUpperCase() : '?'}</div>
                        <div class="reporter-details">
                            <h5>${reporter.name || 'Anonymous Reporter'}</h5>
                            <span class="reporter-badge ${reporter.reporter_type}">${reporter.reporter_type || 'Unknown'}</span>
                        </div>
                        <div class="report-number">#${index + 1}</div>
                    </div>
                    <div class="card-body">
                        <div class="info-item">
                            <span class="label">Relationship:</span>
                            <span class="value">${reporter.relationship || 'Not specified'}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Contact:</span>
                            <span class="value">${reporter.contact || 'Not provided'}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Email:</span>
                            <span class="value">${reporter.email || 'Not provided'}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Report Date:</span>
                            <span class="value">${reporter.report_date || 'Unknown'}</span>
                        </div>
                        ${reporter.description && reporter.description !== 'N/A' ? `
                        <div class="info-item description-item">
                            <span class="label">Description:</span>
                            <div class="description-text">${reporter.description}</div>
                        </div>` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function printCaseDetails() {
    // Delegate to the actual implementation in case-details-display.js
    console.log('printCaseDetails wrapper called');
    console.log('window.currentCaseData:', window.currentCaseData);
    
    if (!window.currentCaseData) {
        alert('No case data available to print. Please open a case first.');
        return;
    }
    
    // Call the actual print function
    if (window.printCaseDetailsActual && typeof window.printCaseDetailsActual === 'function') {
        window.printCaseDetailsActual();
    } else {
        alert('Print function not loaded. Please refresh the page.');
    }
}

function emailCaseDetails() {
    console.log('Email function called');
    
    // Quick validation
    const caseContent = document.getElementById('case-details-content');
    if (!caseContent) {
        alert('Case details not available');
        return;
    }
    
    // Fast data extraction - get only essential info
    const caseTitle = caseContent.querySelector('h3')?.textContent || 'Case Details';
    const caseInfo = caseContent.querySelector('.case-info');
    
    if (!caseInfo) {
        alert('Case information not available');
        return;
    }
    
    // Simplified data extraction
    const fullName = caseInfo.querySelector('.name-case-item p')?.textContent?.trim() || 'N/A';
    const status = caseInfo.querySelector('.status-case-item p')?.textContent?.trim() || 'N/A';
    const priority = caseInfo.querySelector('.priority-case-item p')?.textContent?.trim() || 'N/A';
    const officer = caseInfo.querySelector('.assigned-case-item p')?.textContent?.trim() || 'N/A';
    
    // Simple email content
    const subject = `OnLook Case Report - ${caseTitle}`;
    const body = `Case: ${caseTitle}
Name: ${fullName}
Status: ${status}
Priority: ${priority}
Officer: ${officer}

Generated from OnLook System`;
    
    console.log('Opening email client...');
    
    // Use simple mailto - fastest method
    const mailtoLink = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    
    try {
        window.location.href = mailtoLink;
        console.log('Email client opened');
    } catch (error) {
        console.error('Email error:', error);
        // Fallback - copy to clipboard
        const emailText = `${subject}\n\n${body}`;
        navigator.clipboard.writeText(emailText).then(() => {
            alert('Email content copied to clipboard!');
        }).catch(() => {
            alert('Please copy this email content:\n\n' + emailText);
        });
    }
}

function previewAdditionalImages() {
    const files = document.getElementById('additional-images').files;
    const container = document.getElementById('image-preview-container');
    container.innerHTML = '';
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.width = '100px';
            img.style.height = '100px';
            img.style.objectFit = 'cover';
            img.style.margin = '5px';
            img.style.border = '1px solid #ddd';
            img.style.borderRadius = '4px';
            container.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
}

function closeCaseDetails() {
    const modal = document.getElementById('case-details-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
    }
}

function closeEditCaseModal() {
    const modal = document.getElementById('edit-case-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
    }
}

function assignOfficer(caseId, officerId) {
    if (!caseId) {
        return;
    }
    
    // Check if user is Police Chief
    if (window.userRole !== 'policeChief') {
        alert('Only Police Chief can assign officers');
        return;
    }
    
    fetch(`/police-assign-officer/${caseId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ officer_id: officerId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const dropdown = document.querySelector(`.officer-dropdown[data-case-id="${caseId}"]`);
            if (dropdown) {
                const selectedText = dropdown.options[dropdown.selectedIndex]?.text || 'Unassigned';
                const nameSpan = dropdown.closest('.assigned-officer-display')?.querySelector('.assigned-officer-name');
                if (nameSpan) nameSpan.textContent = officerId ? selectedText : 'Unassigned';
                
                const cell = dropdown.closest('.assignment-cell');
                if (cell) {
                    cell.classList.add('assignment-changed');
                    setTimeout(() => cell.classList.remove('assignment-changed'), 2000);
                }
            }
        } else {
            alert('Error assigning officer: ' + data.message);
        }
    })
    .catch(error => {
        alert('Network error assigning officer: ' + error.message);
    });
}

// Make ALL functions globally accessible IMMEDIATELY
window.printCaseDetails = printCaseDetails;
window.emailCaseDetails = emailCaseDetails;
window.assignOfficer = assignOfficer;
window.openImageModal = openImageModal;
window.closeImageModal = closeImageModal;
window.deleteImage = deleteImage;
window.viewArchivedImages = viewArchivedImages;
window.openFollowupModal = openFollowupModal;
window.closeFollowupModal = closeFollowupModal;
window.toggleNotifications = toggleNotifications;
window.closeNotifications = closeNotifications;
window.markNotificationsRead = markNotificationsRead;
window.generateReport = generateReport;
window.previewAdditionalImages = previewAdditionalImages;
window.prevImage = prevImage;
window.nextImage = nextImage;
window.downloadImage = downloadImage;
window.closeCaseDetails = closeCaseDetails;
window.closeEditCaseModal = closeEditCaseModal;
window.displayFollowupReports = displayFollowupReports;
window.displayArchivedImages = displayArchivedImages;
window.unarchiveImage = unarchiveImage;

// Handle edit form submission and all event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Setting up event listeners');
    
    // Global event delegation for modal buttons
    document.addEventListener('click', function(e) {
        // Check if print button was clicked
        const printBtn = e.target.closest('.print-btn');
        if (printBtn) {
            e.preventDefault();
            e.stopPropagation();
            console.log('=== PRINT BUTTON CLICKED (via delegation) ===');
            console.log('window.printCaseDetails type:', typeof window.printCaseDetails);
            console.log('printCaseDetails type:', typeof printCaseDetails);
            
            // Check if function exists
            if (typeof window.printCaseDetails === 'function') {
                console.log('printCaseDetails function exists, calling it...');
                try {
                    window.printCaseDetails();
                } catch (error) {
                    console.error('Error calling printCaseDetails:', error);
                    console.error('Error stack:', error.stack);
                    alert('Error printing case details: ' + error.message);
                }
            } else {
                console.error('printCaseDetails function NOT FOUND!');
                console.error('window object keys:', Object.keys(window).filter(k => k.includes('print')));
                alert('Print function not available. Please refresh the page.');
            }
            return;
        }
        
        // Check if email button was clicked
        const emailBtn = e.target.closest('.email-btn');
        if (emailBtn) {
            e.preventDefault();
            e.stopPropagation();
            console.log('=== EMAIL BUTTON CLICKED (via delegation) ===');
            
            const originalHTML = emailBtn.innerHTML;
            
            // Show loading state
            emailBtn.innerHTML = 'â³';
            emailBtn.disabled = true;
            
            // Quick email function call
            setTimeout(() => {
                emailCaseDetails();
                // Reset button
                setTimeout(() => {
                    emailBtn.innerHTML = originalHTML;
                    emailBtn.disabled = false;
                }, 1000);
            }, 50);
            return;
        }
    }, true); // Use capture phase to catch events early
    
    // Notification event listeners
    const notificationFrame = document.querySelector('._public_notification_frame');
    if (notificationFrame) notificationFrame.addEventListener('click', toggleNotifications);
    
    const closeNotificationBtns = document.querySelectorAll('.close-notifications');
    closeNotificationBtns.forEach(btn => btn.addEventListener('click', closeNotifications));
    
    const notificationItems = document.querySelectorAll('.notification-item');
    notificationItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const caseId = this.dataset.caseId;
            markNotificationsRead();
            viewCaseDetails(caseId);
            e.stopPropagation();
        });
    });
    
    // Generate and print table buttons
    const generateBtn = document.querySelector('.generate-btn');
    if (generateBtn) generateBtn.addEventListener('click', generateReport);
    
    // Clickable table rows
    const clickableRows = document.querySelectorAll('.clickable-row');
    clickableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on kebab menu, assignment cell, or action cell
            if (!e.target.closest('.kebab-menu') && 
                !e.target.closest('.assignment-cell') && 
                !e.target.closest('.action-cell')) {
                viewCaseDetails(this.dataset.caseId);
            }
        });
    });
    
    // Officer assignment dropdowns
    const officerDropdowns = document.querySelectorAll('.officer-dropdown');
    officerDropdowns.forEach((dropdown) => {
        dropdown.addEventListener('change', function(e) {
            e.stopPropagation();
            const caseId = this.dataset.caseId;
            const officerId = this.value;
            if (!caseId) return;
            assignOfficer(caseId, officerId);
        });
    });
    
    // Prevent propagation on assignment cell only
    document.querySelectorAll('.assignment-cell').forEach(cell => {
        cell.addEventListener('click', e => e.stopPropagation());
    });
    
    // DON'T stop propagation on action-cell - let kebab menu events bubble up
    // The kebab menu handlers in case-management-kebab.js need these events
    
    // Note: Kebab menu handlers are in case-management-kebab.js
    
    // Close buttons for all modals
    document.querySelectorAll('.close-btn, .close-modal').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = this.closest('.modern-case-modal, .edit-case-modal, .followup-modal');
            if (modal) {
                modal.style.display = 'none';
                modal.classList.remove('show');
            }
        });
    });
    
    // Modal backdrops
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', function() {
            const modal = this.closest('.modern-case-modal, .followup-modal');
            if (modal) modal.style.display = 'none';
        });
    });
    
    // Image modal controls
    const closeImageBtn = document.querySelector('.close-image-modal');
    if (closeImageBtn) closeImageBtn.addEventListener('click', closeImageModal);
    
    const prevImageBtn = document.querySelector('.prev-image-btn');
    if (prevImageBtn) prevImageBtn.addEventListener('click', prevImage);
    
    const nextImageBtn = document.querySelector('.next-image-btn');
    if (nextImageBtn) nextImageBtn.addEventListener('click', nextImage);
    
    const downloadImageBtn = document.querySelector('.download-image-btn');
    if (downloadImageBtn) downloadImageBtn.addEventListener('click', downloadImage);
    
    // Additional images preview
    const additionalImagesInput = document.getElementById('additional-images');
    if (additionalImagesInput) additionalImagesInput.addEventListener('change', previewAdditionalImages);
    
    // Cancel button
    const cancelEditCaseBtn = document.querySelector('.cancel-edit-case-btn');
    if (cancelEditCaseBtn) cancelEditCaseBtn.addEventListener('click', closeEditCaseModal);
    
    // Edit form submission
    const editForm = document.getElementById('edit-case-form');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData();
            
            formData.append('case_id', document.getElementById('edit-case-id').value);
            formData.append('case_status', document.getElementById('edit-case-status').value);
            formData.append('priority', document.getElementById('edit-priority').value);
            formData.append('full_name', document.getElementById('edit-full-name').value);
            formData.append('gender', document.getElementById('edit-gender').value);
            formData.append('height', document.getElementById('edit-height').value);
            formData.append('weight', document.getElementById('edit-weight').value);
            formData.append('hair_color', document.getElementById('edit-hair-color').value);
            formData.append('eye_color', document.getElementById('edit-eye-color').value);
            formData.append('date_last_seen', document.getElementById('edit-date-last-seen').value);
            formData.append('clothing_description', document.getElementById('edit-clothing').value);
            
            const additionalImages = document.getElementById('additional-images').files;
            for (let i = 0; i < additionalImages.length; i++) {
                formData.append('additional_images', additionalImages[i]);
            }
            
            fetch(`/police-edit-case/${document.getElementById('edit-case-id').value}`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Case updated successfully');
                    closeEditCaseModal();
                    location.reload();
                } else {
                    alert('Error updating case: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating case');
            });
        });
    }
});

function deleteImage(imageId, index) {
    // Store case ID globally for access in this function
    const caseTitle = document.querySelector('.case-file-view h3')?.textContent || 'Case #0';
    const caseId = caseTitle.match(/\d+/)?.[0] || '0';
    window.currentCaseId = caseId;
    if (confirm('Are you sure you want to archive this image?')) {
        fetch(`/police-delete-image/${imageId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success === true) {
                // Remove from current images array
                currentImages.splice(index, 1);
                window.currentCaseImages.splice(index, 1);
                
                // Refresh the gallery
                const container = document.getElementById('case-image-gallery');
                if (currentImages.length === 0) {
                    const caseTitle = document.querySelector('.case-file-view h3')?.textContent || 'Case';
                    const caseId = caseTitle.match(/\d+/)?.[0] || '0';
                    container.innerHTML = `
                        <div class="no-images">
                            <div class="gallery-header">
                                <h4>Evidence Photos (0)</h4>
                                <button class="archived-images-btn" onclick="viewArchivedImages(${caseId})" title="View Archived Images">ðŸ“ Archived</button>
                            </div>
                            <div class="no-images-icon">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                                </svg>
                            </div>
                            <h3>No Images Available</h3>
                            <p>All images have been archived.</p>
                        </div>`;
                } else {
                    // Rebuild thumbnails
                    const thumbnails = container.querySelector('.thumbnails');
                    thumbnails.innerHTML = currentImages.map((image, i) => `
                        <div class="thumb ${i === 0 ? 'active' : ''}" onclick="switchMainImage(${i})">
                            <img src="${image.src}">
                            <button class="delete-image-btn" onclick="deleteImage(${image.id}, ${i})" title="Archive Image">\u00d7</button>
                        </div>
                    `).join('');
                    
                    // Update main image if needed
                    if (index === window.currentMainImageIndex) {
                        switchMainImage(0);
                    }
                }
                
                alert('Image archived successfully');
            } else {
                alert('Error archiving image: ' + (data ? data.message : 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert('Network error: ' + error.message);
        });
    }
}
function viewArchivedImages(caseId) {
    fetch(`/police-archived-images/${caseId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayArchivedImages(data.images);
            } else {
                alert('Error loading archived images: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading archived images');
        });
}

function displayArchivedImages(images) {
    const content = images.length > 0 ? 
        `<div class="archived-gallery">
            ${images.map(img => `
                <div class="archived-image">
                    <img src="${img.src}" onclick="openImageModal(0)" style="width: 100px; height: 100px; object-fit: cover;">
                    <p>Archived: ${img.archived_at}</p>
                    <button class="unarchive-btn" onclick="unarchiveImage(${img.id})" title="Unarchive Image">â†© Unarchive</button>
                </div>
            `).join('')}
        </div>` :
        '<p>No archived images found.</p>';
    
    document.getElementById('case-details-content').innerHTML = `
        <div class="archived-images-view">
            <h3>Archived Images</h3>
            <button onclick="location.reload()" style="float: right;">Back to Case</button>
            ${content}
        </div>
    `;
}

function unarchiveImage(imageId, caseId) {
    if (confirm('Are you sure you want to restore this image? It will be moved back to the active images.')) {
        const unarchiveBtn = document.querySelector(`button[onclick*="unarchiveImage(${imageId}"]`);
        if (unarchiveBtn) {
            unarchiveBtn.disabled = true;
            unarchiveBtn.textContent = 'â³ Restoring...';
        }
        
        fetch(`/police-unarchive-image/${imageId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Image restored successfully');
                setTimeout(() => viewArchivedImages(caseId), 1000);
            } else {
                if (unarchiveBtn) {
                    unarchiveBtn.disabled = false;
                    unarchiveBtn.textContent = 'â†©ï¸ Restore';
                }
                alert('Error restoring image: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error unarchiving image:', error);
            if (unarchiveBtn) {
                unarchiveBtn.disabled = false;
                unarchiveBtn.textContent = 'â†©ï¸ Restore';
            }
            alert('Network error restoring image');
        });
    }
}
