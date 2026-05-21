// Store current case data globally
window.currentCaseData = null;

// Full displayCaseDetails function with complete template
window.displayCaseDetails = function(caseData) {
    // Store case data globally for print function
    window.currentCaseData = caseData;
    
    const modal = document.getElementById('case-details-modal');
    
    if (!modal) {
        alert('Modal not found. Please refresh the page.');
        return;
    }
    
    const imagesSection = `<div id="case-image-gallery"></div>`;
    
    const reportersSection = caseData.reporters && caseData.reporters.length > 0 ?
        `<div class="case-reporters">
            <div class="reporters-header">
                <h4>Follow-up Reports (${caseData.reporters.length})</h4>
                <button class="view-reports-btn" onclick="openFollowupModal(${caseData.case_id})">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                    </svg>
                    View Details
                </button>
            </div>
        </div>` : 
        `<div class="case-reporters">
            <h4>Case Reporters</h4>
            <p class="no-reporters">No additional reports submitted for this case.</p>
        </div>`;
    
    const content = `
        <div class="case-file-view">
            <h3>Case #${caseData.case_id}</h3>
            ${imagesSection}
            <div class="case-info">
                <div class="case-title">Case #${caseData.case_id} - ${caseData.full_name || 'Unknown'}</div>
                <div class="section-title">Personal Information</div>
                <div class="info-grid">
                    <div class="info-item name-case-item">
                    <h1>Full Name:</h1> 
                    <p> ${caseData.full_name || 'N/A'} </p>
                    </div>
                    <div class="info-item age-case-item">
                    <h1>Age:</h1> 
                    <p>${caseData.age !== null && caseData.age !== undefined ? caseData.age + ' years old' : 'N/A'}</p>
                    </div>
                    <div class="info-item gender-case-item">
                    <h1>Gender:</h1> 
                    <p>${caseData.gender || 'N/A'}</p>
                    </div>
                    <div class="info-item height-case-item">
                    <h1>Height:</h1> 
                    <p>${caseData.height ? caseData.height + ' cm' : 'N/A'}</p>
                    </div>
                    <div class="info-item weight-case-item">
                    <h1>Weight:</h1> 
                    <p>${caseData.weight ? caseData.weight + ' kg' : 'N/A'}</p>
                    </div>
                    <div class="info-item hair-case-item">
                    <h1>Hair Color:</h1> 
                    <p>${caseData.hair_color || 'N/A'}</p>
                    </div>
                    <div class="info-item eye-case-item">
                    <h1>Eye Color:</h1> 
                    <p>${caseData.eye_color || 'N/A'}</p>
                    </div>
                    <div class="info-item last-seen-case-item">
                    <h1>Date Last Seen:</h1> 
                    <p>${caseData.date_last_seen || 'N/A'}</p>
                    </div>
                    <div class="info-item clothing-case-item full-width">
                    <h1>Clothing Description:</h1> 
                    <p>${caseData.clothing_description || 'N/A'}</p>
                    </div>
                </div>
                
                <div class="section-title">Case Information</div>
                <div class="info-grid">
                    <div class="info-item status-case-item">
                    <h1>Case Status:</h1> 
                    <p>${caseData.case_status || 'N/A'}</p>
                    </div>
                    <div class="info-item priority-case-item">
                    <h1>Priority Level:</h1> 
                    <p>${caseData.priority || 'N/A'}</p>
                    </div>
                    <div class="info-item assigned-case-item">
                    <h1>Assigned Officer:</h1> 
                    <p>${caseData.assigned_officer || 'Unassigned'}</p>
                    </div>
                </div>
            </div>
            ${reportersSection}
        </div>
    `;
    
    const contentElement = document.getElementById('case-details-content');
    if (!contentElement) return;
    
    contentElement.innerHTML = content;
    
    // Initialize gallery
    setTimeout(() => {
        const container = document.getElementById('case-image-gallery');
        if (container) {
            if (caseData.images && caseData.images.length > 0) {
                container.innerHTML = `
                    <div class="case-gallery">
                        <div class="gallery-header">
                            <h4>Evidence Photos (${caseData.images.length})</h4>
                            <button class="archived-images-btn" onclick="viewArchivedImages(${caseData.case_id})" title="View Archived Images">📁 Archived</button>
                        </div>
                        <div class="gallery-layout">
                            <div class="main-photo">
                                <img id="main-gallery-image" src="${caseData.images[0].src}">
                                <div class="photo-info">
                                    <span class="photo-counter">1 / ${caseData.images.length}</span>
                                </div>
                            </div>
                            <div class="thumbnails">
                                ${caseData.images.map((image, index) => `
                                    <div class="thumb ${index === 0 ? 'active' : ''}" onclick="switchMainImage(${index})">
                                        <img src="${image.src}">
                                        <button class="delete-image-btn" onclick="deleteImage(${image.id}, ${index})" title="Archive Image">×</button>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
                window.currentCaseImages = caseData.images;
                window.currentMainImageIndex = 0;
            } else {
                container.innerHTML = `
                    <div class="no-images">
                        <div class="gallery-header">
                            <h4>Evidence Photos (0)</h4>
                            <button class="archived-images-btn" onclick="viewArchivedImages(${caseData.case_id})" title="View Archived Images">📁 Archived</button>
                        </div>
                        <div class="no-images-icon">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                            </svg>
                        </div>
                        <h3>No Images Available</h3>
                        <p>No evidence photos have been uploaded for this case.</p>
                    </div>
                `;
            }
        }
    }, 100);
    
    modal.style.display = 'flex';
    modal.classList.add('show');
};

// Print individual case details with exact format
window.printCaseDetailsActual = function(preparedBy = '', approvedBy = '') {
    const caseData = window.currentCaseData;
    
    if (!caseData) {
        alert('No case data available to print');
        return;
    }
    
    try {
        let printWrapper = document.getElementById('print-preview-wrapper');
        if (!printWrapper) {
            printWrapper = document.createElement('div');
            printWrapper.id = 'print-preview-wrapper';
            document.body.appendChild(printWrapper);
        }
        
        const photoHTML = (caseData.images && caseData.images.length > 0) ? 
            `<img src="${caseData.images[0].src}" class="subject-photo" alt="Missing Person">` : 
            `<div class="subject-photo-placeholder">No Photo<br>Available</div>`;
        
        const statusBadgeClass = caseData.case_status === 'Resolved' ? 'status-badge' : 'status-badge-open';
        const priorityBadgeClass = caseData.priority === 'High' ? 'priority-badge-high' : (caseData.priority === 'Low' ? 'priority-badge-low' : 'priority-badge');
        
        const signatureSection = (preparedBy && approvedBy) ? `
  <div class="sig-row">
    <div class="sig-block">
      <div class="sig-line"></div>
      <div class="sig-label">${preparedBy}</div>
      <div class="sig-title">Prepared By</div>
    </div>
    <div class="sig-block">
      <div class="sig-line"></div>
      <div class="sig-label">${approvedBy}</div>
      <div class="sig-title">Approved By</div>
    </div>
  </div>
        ` : `
  <div class="sig-row">
    <div class="sig-block">
      <div class="sig-line"></div>
      <div class="sig-label">Investigating Officer</div>
    </div>
    <div class="sig-block">
      <div class="sig-line"></div>
      <div class="sig-label">Station Commander</div>
    </div>
  </div>
        `;
        
        printWrapper.innerHTML = `
<div class="report-wrap">
  <div class="report-header">
    <h1>PHILIPPINE NATIONAL POLICE</h1>
    <h2>Laguna Provincial Police Office</h2>
    <p>Missing Person Case Report</p>
    <span class="case-badge">Case #${caseData.case_id}</span>
  </div>

  <div class="section">
    <div class="card">
      <div class="subject-row">
        ${photoHTML}
        <div style="flex:1;">
          <div class="subject-info-title">Subject Information</div>
          <hr class="divider">
          <div class="info-row">
            <div class="info-label">Full Name:</div>
            <div class="info-value">${caseData.full_name || 'N/A'}</div>
          </div>
          <div class="info-row">
            <div class="info-label">Age:</div>
            <div class="info-value">${caseData.age !== null && caseData.age !== undefined ? caseData.age + ' years old' : 'N/A'}</div>
          </div>
          <div class="info-row">
            <div class="info-label">Gender:</div>
            <div class="info-value">${caseData.gender || 'N/A'}</div>
          </div>
          <div class="info-row">
            <div class="info-label">Date Last Seen:</div>
            <div class="info-value">${caseData.date_last_seen || 'N/A'}</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Physical Description &amp; Case Status</div>
    <div class="two-col">
      <div class="card">
        <div class="info-row">
          <div class="info-label">Height:</div>
          <div class="info-value">${caseData.height ? caseData.height + ' cm' : 'N/A'}</div>
        </div>
        <div class="info-row">
          <div class="info-label">Weight:</div>
          <div class="info-value">${caseData.weight ? caseData.weight + ' kg' : 'N/A'}</div>
        </div>
        <div class="info-row">
          <div class="info-label">Hair Color:</div>
          <div class="info-value">${caseData.hair_color || 'N/A'}</div>
        </div>
        <div class="info-row">
          <div class="info-label">Eye Color:</div>
          <div class="info-value">${caseData.eye_color || 'N/A'}</div>
        </div>
      </div>
      <div class="card">
        <div class="info-row">
          <div class="info-label">Case Status:</div>
          <div class="info-value"><span class="${statusBadgeClass}">${caseData.case_status || 'N/A'}</span></div>
        </div>
        <div class="info-row">
          <div class="info-label">Priority Level:</div>
          <div class="info-value"><span class="${priorityBadgeClass}">${caseData.priority || 'N/A'}</span></div>
        </div>
        <div class="info-row">
          <div class="info-label">Assigned Officer:</div>
          <div class="info-value">${caseData.assigned_officer || 'Unassigned'}</div>
        </div>
        <div class="info-row">
          <div class="info-label">Report Generated:</div>
          <div class="info-value">${new Date().toLocaleDateString()}</div>
        </div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Clothing Description</div>
    <div class="card">
      <div style="font-size: 13px; color: var(--color-text-primary);">${caseData.clothing_description || 'No clothing description available'}</div>
    </div>
  </div>

  ${signatureSection}

  <div class="confidential">CONFIDENTIAL DOCUMENT — For Official Use Only</div>
  <div class="generated">Generated: ${new Date().toLocaleString()} | OnLook Case Management System</div>
</div>
        `;
        
        window.print();
        
    } catch (error) {
        console.error('Error printing case details:', error);
        alert('Error printing case details: ' + error.message);
    }
}

window.openCaseDetailsPrintModal = function() {
    const modal = document.getElementById('caseDetailsPrintModal');
    modal.style.display = 'flex';
    loadCaseDetailsOfficers();
}

window.closeCaseDetailsPrintModal = function() {
    const modal = document.getElementById('caseDetailsPrintModal');
    modal.style.display = 'none';
}

window.loadCaseDetailsOfficers = async function() {
    try {
        const response = await fetch('/police-case-report/get-officers');
        const data = await response.json();
        
        const preparedBySelect = document.getElementById('caseDetailsPreparedBy');
        const approvedBySelect = document.getElementById('caseDetailsApprovedBy');
        
        preparedBySelect.innerHTML = '<option value="">Select Officer</option>';
        approvedBySelect.innerHTML = '<option value="">Select Officer</option>';
        
        data.officers.forEach(officer => {
            const option1 = new Option(officer.full_name, officer.full_name);
            const option2 = new Option(officer.full_name, officer.full_name);
            preparedBySelect.add(option1);
            approvedBySelect.add(option2);
        });
    } catch (error) {
        console.error('Error loading officers:', error);
    }
}

window.confirmCaseDetailsPrint = function() {
    const preparedBy = document.getElementById('caseDetailsPreparedBy').value;
    const approvedBy = document.getElementById('caseDetailsApprovedBy').value;
    
    if (!preparedBy || !approvedBy) {
        alert('Please select both Prepared By and Approved By officers');
        return;
    }
    
    closeCaseDetailsPrintModal();
    printCaseDetailsActual(preparedBy, approvedBy);
}

// switchMainImage function
window.switchMainImage = function(index) {
    const mainImage = document.getElementById('main-gallery-image');
    const thumbnails = document.querySelectorAll('.thumb');
    const photoCounter = document.querySelector('.photo-counter');
    
    if (mainImage && window.currentCaseImages && window.currentCaseImages[index]) {
        mainImage.src = window.currentCaseImages[index].src;
        window.currentMainImageIndex = index;
        
        thumbnails.forEach((thumb, i) => {
            thumb.classList.toggle('active', i === index);
        });
        
        if (photoCounter) photoCounter.textContent = `${index + 1} / ${window.currentCaseImages.length}`;
    }
};

console.log('Case details display functions loaded');
