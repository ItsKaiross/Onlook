document.addEventListener('DOMContentLoaded', function() {
    // Create global dropdown element (once)
    let globalDropdown = document.querySelector('.kebab-dropdown-global');
    if (!globalDropdown) {
        globalDropdown = document.createElement('div');
        globalDropdown.className = 'kebab-dropdown-global';
        document.body.appendChild(globalDropdown);
    }

    // Get modal elements
    const detailsModal = document.getElementById('report-details-modal');
    const modalContent = document.getElementById('report-details-content');
    const closeModalBtn = document.querySelector('#report-details-modal .close-modal');
    
    // Get edit modal elements
    const editModal = document.getElementById('edit-report-modal');
    const editForm = document.getElementById('edit-report-form');
    const cancelEditBtn = document.querySelector('.cancel-edit-btn');
    const closeEditModalBtn = document.querySelector('#edit-report-modal .close-modal');
    
    // Function to open modal with report details
    function openReportDetails(caseId) {
        // Clear existing content and show loading
        modalContent.innerHTML = '';
        
        const loadingDiv = document.createElement('div');
        loadingDiv.style.textAlign = 'center';
        loadingDiv.style.padding = '40px';
        
        const spinner = document.createElement('div');
        spinner.style.display = 'inline-block';
        spinner.style.width = '40px';
        spinner.style.height = '40px';
        spinner.style.border = '3px solid #f3f3f3';
        spinner.style.borderTop = '3px solid #1A1B41';
        spinner.style.borderRadius = '50%';
        spinner.style.animation = 'spin 1s linear infinite';
        
        const loadingText = document.createElement('p');
        loadingText.textContent = 'Loading report details...';
        loadingText.style.marginTop = '20px';
        
        loadingDiv.appendChild(spinner);
        loadingDiv.appendChild(loadingText);
        
        // Add CSS animation if not already present
        if (!document.querySelector('#spin-animation')) {
            const style = document.createElement('style');
            style.id = 'spin-animation';
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
        
        modalContent.appendChild(loadingDiv);
        detailsModal.style.display = 'flex';
        
        secureFetch('/police-report-details/', caseId)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.report) {
                    renderReportDetails(data.report);
                } else {
                    throw new Error(data.error || 'Report not found');
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                showErrorMessage(error.message);
            });
    }
    
    // Function to show error message safely
    function showErrorMessage(errorMsg) {
        modalContent.innerHTML = '';
        
        const errorDiv = document.createElement('div');
        errorDiv.style.textAlign = 'center';
        errorDiv.style.padding = '40px';
        
        const errorIcon = document.createElement('div');
        errorIcon.textContent = '❌';
        errorIcon.style.fontSize = '48px';
        errorIcon.style.marginBottom = '16px';
        
        const errorTitle = document.createElement('p');
        errorTitle.textContent = 'Unable to load report details';
        errorTitle.style.color = '#e53e3e';
        errorTitle.style.fontFamily = 'SF_BOLD';
        
        const errorDetails = document.createElement('p');
        errorDetails.textContent = errorMsg;
        errorDetails.style.color = '#666';
        errorDetails.style.fontSize = '14px';
        
        const retryBtn = document.createElement('button');
        retryBtn.textContent = 'Retry';
        retryBtn.style.marginTop = '20px';
        retryBtn.style.padding = '8px 20px';
        retryBtn.style.background = '#1A1B41';
        retryBtn.style.color = 'white';
        retryBtn.style.border = 'none';
        retryBtn.style.borderRadius = '6px';
        retryBtn.style.cursor = 'pointer';
        retryBtn.addEventListener('click', () => location.reload());
        
        errorDiv.appendChild(errorIcon);
        errorDiv.appendChild(errorTitle);
        errorDiv.appendChild(errorDetails);
        errorDiv.appendChild(retryBtn);
        
        modalContent.appendChild(errorDiv);
    }
    
    // Function to open edit modal with report data
    function openEditReport(caseId) {
        // Show loading state in edit modal
        document.getElementById('edit-case-id').value = caseId;
        document.getElementById('edit-full-name').value = 'Loading...';
        document.getElementById('edit-age').value = '';
        document.getElementById('edit-date-last-seen').value = '';
        
        // Show the edit modal
        editModal.style.display = 'flex';
        
        // Fetch report data for editing
        secureFetch('/police-report-details/', caseId)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.report) {
                    populateEditForm(data.report);
                } else {
                    throw new Error(data.error || 'Report not found');
                }
            })
            .catch(error => {
                console.error('Error loading report for edit:', error);
                showNotification('Error loading report data: ' + error.message, 'error');
                closeEditModal();
            });
    }
    
    // Function to populate the edit form with report data
    function populateEditForm(report) {
        document.getElementById('edit-case-id').value = report.case_id || '';
        document.getElementById('edit-full-name').value = report.full_name || '';
        document.getElementById('edit-age').value = report.age || '';
        document.getElementById('edit-date-last-seen').value = report.date_last_seen || '';
        document.getElementById('edit-status').value = report.approval_status || 'Pending';
        document.getElementById('edit-case-status').value = report.case_status || 'Open';
        document.getElementById('edit-height').value = report.height || '';
        document.getElementById('edit-weight').value = report.weight || '';
        document.getElementById('edit-hair-color').value = report.hair_color || '';
        document.getElementById('edit-eye-color').value = report.eye_color || '';
        document.getElementById('edit-clothing').value = report.clothing_description || '';
        const genderRadios = document.querySelectorAll('input[name="gender"]');
        genderRadios.forEach(radio => {
            radio.checked = radio.value === (report.gender || 'Male');
        });
    }
    
    function updateReport(caseId, formData) {
        const submitBtn = editForm.querySelector('button[type="submit"]');
        const originalText = submitBtn?.textContent || 'Save Changes';
        if (submitBtn) {
            submitBtn.textContent = 'Saving...';
            submitBtn.disabled = true;
        }
        
        // Get all values
        let fullName = formData.get('full_name');
        let gender = formData.get('gender');
        let age = formData.get('age');
        let height = formData.get('height');
        let weight = formData.get('weight');
        let hairColor = formData.get('hair_color');
        let eyeColor = formData.get('eye_color');
        let clothing = formData.get('clothing_description');
        let dateLastSeen = formData.get('date_last_seen');
        let status = formData.get('status');
        let caseStatus = formData.get('case_status');
        
        // DEBUG: Print all form values
        console.log('=== FORM DATA DEBUG ===');
        console.log('full_name:', fullName);
        console.log('gender:', gender);
        console.log('age:', age);
        console.log('height:', height);
        console.log('weight:', weight);
        console.log('hair_color:', hairColor);
        console.log('eye_color:', eyeColor);
        console.log('clothing_description:', clothing);
        console.log('date_last_seen RAW:', dateLastSeen);
        console.log('status:', status);
        console.log('case_status:', caseStatus);
        console.log('=======================');
        
        const reportData = {
            full_name: fullName || '',
            gender: gender || '',
            age: age || null,
            height: (height === null || height === '') ? '' : height,
            weight: (weight === null || weight === '') ? '' : weight,
            hair_color: hairColor || '',
            eye_color: eyeColor || '',
            clothing_description: clothing || '',
            date_last_seen: dateLastSeen || null,
            approval_status: status || 'Pending',
            case_status: caseStatus || 'Open'
        };
        
        console.log('Sending to server:', JSON.stringify(reportData, null, 2));
        
        secureFetch('/police-edit-report/', caseId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reportData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ Report updated successfully!', 'success');
                closeEditModal();
                location.reload();
            } else {
                throw new Error(data.message || 'Update failed');
            }
        })
        .catch(error => {
            console.error('Update error:', error);
            showNotification('❌ Error updating report: ' + error.message, 'error');
        })
        .finally(() => {
            if (submitBtn) {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
    
    // Function to close edit modal
    function closeEditModal() {
        editModal.style.display = 'none';
        editForm.reset();
    }
    
    // Function to render report details in modal
    function renderReportDetails(report) {
        const statusClass = {
            'approved' : 'approved',
            'rejected' : 'rejected',
            'pending' : 'pending',
            'archived' : 'archived'
        }[report.approval_status?.toLowerCase()] || 'pending';
        
        const dateReported = report.date_and_time_reported ? new Date(report.date_and_time_reported).toLocaleDateString() : 'N/A';
        const lastSeenDate = report.date_last_seen || 'N/A';
        const lastSeenTime = report.time_last_seen || 'N/A';
        
        // Clear existing content safely
        while (modalContent.firstChild) {
            modalContent.removeChild(modalContent.firstChild);
        }
        
        // Create elements safely using DOM methods
        const container = document.createElement('div');
        
        // Case Information Section
        const caseSection = createDetailSection('📋 Case Information', [
            { label: 'Case ID', value: '#' + (report.case_id || 'N/A') },
            { label: 'Case Status', value: report.case_status || 'Open' },
            { label: 'Approval Status', value: report.approval_status || '', isStatus: true, statusClass: statusClass },
            { label: 'Date Reported', value: dateReported }
        ]);
        container.appendChild(caseSection);
        
        // Personal Information Section
        const personalSection = createDetailSection('👤 Personal Information', [
            { label: 'Full Name', value: report.full_name || 'N/A' },
            { label: 'Age', value: report.age || 'N/A' },
            { label: 'Gender', value: report.gender || 'N/A' }
        ]);
        container.appendChild(personalSection);
        
        // Missing Details Section
        const missingSection = createDetailSection('📍 Missing Details', [
            { label: 'Last Seen Date', value: lastSeenDate },
            { label: 'Last Seen Time', value: lastSeenTime },
            { label: 'Clothing Description', value: report.clothing_description || 'No description available' }
        ]);
        container.appendChild(missingSection);
        
        // Physical Description Section
        const physicalSection = createDetailSection('👤 Physical Description', [
            { label: 'Height', value: (report.height || 'N/A') + ' cm' },
            { label: 'Weight', value: (report.weight || 'N/A') + ' kg' },
            { label: 'Hair Color', value: report.hair_color || 'N/A' },
            { label: 'Eye Color', value: report.eye_color || 'N/A' }
        ]);
        container.appendChild(physicalSection);
        
        // Photo Section (if exists)
        if (report.img_src) {
            const photoSection = document.createElement('div');
            photoSection.className = 'detail-section';
            
            const photoTitle = document.createElement('h3');
            photoTitle.textContent = '🖼️ Missing Person Photo';
            photoSection.appendChild(photoTitle);
            
            const photoContainer = document.createElement('div');
            photoContainer.style.textAlign = 'center';
            
            const img = document.createElement('img');
            img.src = report.img_src;
            img.alt = 'Missing person photo';
            img.style.maxWidth = '250px';
            img.style.borderRadius = '8px';
            img.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            
            photoContainer.appendChild(img);
            photoSection.appendChild(photoContainer);
            container.appendChild(photoSection);
        }

        const modalFooter = document.createElement('div');
        modalFooter.className = 'modal-footer';

        const timelineBtn = document.createElement('button');
        timelineBtn.textContent = '🕒 View Timeline';
        timelineBtn.className   = 'btn-timeline';
        timelineBtn.addEventListener('click', function () {
            openTimelinePanel(report.case_id);
        });

        modalFooter.appendChild(timelineBtn);
        container.appendChild(modalFooter);

        modalContent.appendChild(container);
    }
    
    // Helper function to create detail sections safely
    function createDetailSection(title, items) {
        const section = document.createElement('div');
        section.className = 'detail-section';
        
        const titleElement = document.createElement('h3');
        titleElement.textContent = title;
        section.appendChild(titleElement);
        
        items.forEach(item => {
            const row = document.createElement('div');
            row.className = 'detail-row';
            
            const label = document.createElement('div');
            label.className = 'detail-label';
            label.textContent = item.label + ':';
            row.appendChild(label);
            
            const value = document.createElement('div');
            value.className = 'detail-value';
            
            if (item.isStatus) {
                const statusSpan = document.createElement('span');
                statusSpan.className = `status-badge ${item.statusClass}`;
                statusSpan.textContent = item.value;
                value.appendChild(statusSpan);
            } else {
                value.textContent = item.value;
            }
            
            row.appendChild(value);
            section.appendChild(row);
        });
        
        return section;
    }
    
    // Helper function to create dropdown links safely
    function createDropdownLink(text, action, caseId) {
        const link = document.createElement('a');
        link.href = '#';
        link.textContent = text;
        link.dataset.action = action;
        link.dataset.id = caseId;
        
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const actionType = this.dataset.action;
            const id = this.dataset.id;
            
            if (actionType === 'edit') {
                closeGlobalDropdown();
                openEditReport(id);
            } else if (actionType === 'view') {
                closeGlobalDropdown();
                openReportDetails(id);
            } else if (actionType === 'archive') {
                closeGlobalDropdown();
                showConfirmation('Are you sure you want to archive this report?', () => {
                    const row = document.querySelector(`tr[data-report-id="${id}"]`) || 
                               Array.from(document.querySelectorAll('tr')).find(r => 
                                   r.cells[0] && r.cells[0].textContent.trim() === id
                               );
                    if (row) archiveReport(id, row);
                });
            } else if (actionType === 'unarchive') {
                closeGlobalDropdown();
                showConfirmation('Are you sure you want to unarchive this report?', () => {
                    const row = document.querySelector(`tr[data-report-id="${id}"]`) || 
                               Array.from(document.querySelectorAll('tr')).find(r => 
                                   r.cells[0] && r.cells[0].textContent.trim() === id
                               );
                    if (row) unarchiveReport(id, row);
                });
            }
        });
        
        return link;
    }
    
    // Enhanced SSRF protection function
    function validateAndSanitizeCaseId(caseId) {
        // Convert to string and trim
        const id = String(caseId || '').trim();
        
        // Check if empty
        if (!id) {
            throw new Error('Case ID is required');
        }
        
        // Strict numeric validation (only digits, no special characters)
        if (!/^[1-9][0-9]*$/.test(id)) {
            throw new Error('Invalid case ID format - must be a positive integer');
        }
        
        // Length validation (reasonable case ID length)
        if (id.length > 10) {
            throw new Error('Case ID too long');
        }
        
        // Convert to integer and validate range
        const numericId = parseInt(id, 10);
        if (numericId < 1 || numericId > 2147483647) {
            throw new Error('Case ID out of valid range');
        }
        
        return numericId;
    }
    
    // Secure fetch wrapper with SSRF protection
    function secureFetch(endpoint, caseId, options = {}) {
        return new Promise((resolve, reject) => {
            try {
                // Validate and sanitize the case ID
                const validatedId = validateAndSanitizeCaseId(caseId);
                
                // Whitelist of allowed endpoints
                const allowedEndpoints = [
                    '/police-report-details/',
                    '/police-edit-report/',
                    '/police-archive-report/',
                    '/police-unarchive-report/'
                ];
                
                // Validate endpoint
                if (!allowedEndpoints.includes(endpoint)) {
                    reject(new Error('Unauthorized endpoint'));
                    return;
                }
                
                // Construct secure URL with validated components
                const baseUrl = window.location.origin;
                const secureUrl = new URL(endpoint + validatedId, baseUrl);
                
                // Ensure we're only making requests to our own domain
                if (secureUrl.origin !== window.location.origin) {
                    reject(new Error('Cross-origin requests not allowed'));
                    return;
                }
                
                // Add security headers
                const secureOptions = {
                    ...options,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        ...options.headers
                    }
                };
                
                // Make the secure fetch request
                fetch(secureUrl.toString(), secureOptions)
                    .then(resolve)
                    .catch(reject);
                    
            } catch (error) {
                reject(error);
            }
        });
    }
    
    // Custom notification function to replace alert()
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-family: SF_BOLD;
            font-size: 14px;
            z-index: 10000;
            max-width: 300px;
            word-wrap: break-word;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        // Set background color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            info: '#1A1B41',
            warning: '#ffc107'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    // Custom confirmation function to replace confirm()
    function showConfirmation(message, onConfirm, onCancel = null) {
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 30px;
            max-width: 400px;
            width: 90%;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        `;
        
        const messageEl = document.createElement('p');
        messageEl.textContent = message;
        messageEl.style.cssText = `
            margin: 0 0 20px 0;
            font-family: SF_REGULAR;
            font-size: 16px;
            color: #333;
            line-height: 1.5;
        `;
        
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            display: flex;
            gap: 10px;
            justify-content: center;
        `;
        
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.style.cssText = `
            padding: 10px 20px;
            border: 1px solid #ddd;
            background: white;
            color: #666;
            border-radius: 6px;
            cursor: pointer;
            font-family: SF_MEDIUM;
            font-size: 14px;
        `;
        
        const confirmBtn = document.createElement('button');
        confirmBtn.textContent = 'Confirm';
        confirmBtn.style.cssText = `
            padding: 10px 20px;
            border: none;
            background: #1A1B41;
            color: white;
            border-radius: 6px;
            cursor: pointer;
            font-family: SF_BOLD;
            font-size: 14px;
        `;
        
        function closeConfirmation() {
            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
        }
        
        cancelBtn.addEventListener('click', () => {
            closeConfirmation();
            if (onCancel) onCancel();
        });
        
        confirmBtn.addEventListener('click', () => {
            closeConfirmation();
            if (onConfirm) onConfirm();
        });
        
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeConfirmation();
                if (onCancel) onCancel();
            }
        });
        
        buttonContainer.appendChild(cancelBtn);
        buttonContainer.appendChild(confirmBtn);
        modal.appendChild(messageEl);
        modal.appendChild(buttonContainer);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
    }
    
    function showRejectionModal(onConfirm, onCancel = null) {
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 10001;
            display: flex; align-items: center; justify-content: center;
        `;

        const modal = document.createElement('div');
        modal.style.cssText = `
            background: white; border-radius: 8px; padding: 30px;
            max-width: 420px; width: 90%; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        `;

        const title = document.createElement('p');
        title.textContent = 'Rejection Reason';
        title.style.cssText = 'margin: 0 0 8px 0; font-family: SF_BOLD; font-size: 16px; color: #333;';

        const subtitle = document.createElement('p');
        subtitle.textContent = 'This note will be sent to the reporter via email.';
        subtitle.style.cssText = 'margin: 0 0 16px 0; font-family: SF_REGULAR; font-size: 13px; color: #888;';

        const textarea = document.createElement('textarea');
        textarea.placeholder = 'Enter the reason for rejection...';
        textarea.rows = 4;
        textarea.style.cssText = `
            width: 100%; box-sizing: border-box; padding: 10px;
            border: 1px solid #ddd; border-radius: 6px;
            font-family: SF_REGULAR; font-size: 14px; resize: vertical;
        `;

        const errorMsg = document.createElement('p');
        errorMsg.style.cssText = 'color: #dc3545; font-size: 12px; margin: 6px 0 0 0; display: none;';
        errorMsg.textContent = 'Please enter a rejection reason.';

        const btnRow = document.createElement('div');
        btnRow.style.cssText = 'display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px;';

        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.style.cssText = `
            padding: 10px 20px; border: 1px solid #ddd; background: white;
            color: #666; border-radius: 6px; cursor: pointer; font-family: SF_MEDIUM; font-size: 14px;
        `;

        const confirmBtn = document.createElement('button');
        confirmBtn.textContent = 'Reject & Notify';
        confirmBtn.style.cssText = `
            padding: 10px 20px; border: none; background: #dc3545;
            color: white; border-radius: 6px; cursor: pointer; font-family: SF_BOLD; font-size: 14px;
        `;

        function close() { if (overlay.parentNode) overlay.parentNode.removeChild(overlay); }

        cancelBtn.addEventListener('click', () => { close(); if (onCancel) onCancel(); });
        confirmBtn.addEventListener('click', () => {
            const note = textarea.value.trim();
            if (!note) { errorMsg.style.display = 'block'; return; }
            close();
            onConfirm(note);
        });
        overlay.addEventListener('click', (e) => { if (e.target === overlay) { close(); if (onCancel) onCancel(); } });

        btnRow.appendChild(cancelBtn);
        btnRow.appendChild(confirmBtn);
        modal.appendChild(title);
        modal.appendChild(subtitle);
        modal.appendChild(textarea);
        modal.appendChild(errorMsg);
        modal.appendChild(btnRow);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        textarea.focus();
    }

    function escapeHtml(text) {
        if (!text || text === 'N/A') return text;
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    function closeModal() {
        detailsModal.style.display = 'none';
        // Clear content safely
        while (modalContent.firstChild) {
            modalContent.removeChild(modalContent.firstChild);
        }
    }
    
    // Close buttons for details modal
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    
    detailsModal.addEventListener('click', function(e) {
        if (e.target === detailsModal) {
            closeModal();
        }
    });
    
    // Close buttons for edit modal
    if (closeEditModalBtn) {
        closeEditModalBtn.addEventListener('click', closeEditModal);
    }
    
    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', closeEditModal);
    }
    
    editModal.addEventListener('click', function(e) {
        if (e.target === editModal) {
            closeEditModal();
        }
    });
    
    // Handle edit form submission
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const caseId = document.getElementById('edit-case-id').value;
            const formData = new FormData(editForm);
            updateReport(caseId, formData);
        });
    }
    
    // Close modals with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (detailsModal.style.display === 'flex') {
                closeModal();
            }
            if (editModal.style.display === 'flex') {
                closeEditModal();
            }
        }
    });
    
    // Position dropdown function
    function positionDropdown(button, dropdown) {
        const rect = button.getBoundingClientRect();
        const dropdownHeight = dropdown.offsetHeight;
        const viewportHeight = window.innerHeight;
        
        let top = rect.bottom + 5;
        if (top + dropdownHeight > viewportHeight) {
            top = rect.top - dropdownHeight - 5;
        }
        
        dropdown.style.top = top + 'px';
        dropdown.style.left = rect.right - dropdown.offsetWidth + 'px';
    }
    
    function closeGlobalDropdown() {
        globalDropdown.classList.remove('show');
        // Clear content safely
        while (globalDropdown.firstChild) {
            globalDropdown.removeChild(globalDropdown.firstChild);
        }
    }

    // sync data-status and persist to DB when dropdown changes
    document.addEventListener('change', function(e) {
        if (!e.target.classList.contains('status-dropdown')) return;

        const dropdown = e.target;
        const newStatus = dropdown.value;
        const previousStatus = dropdown.dataset.original || newStatus;
        const caseId = dropdown.dataset.caseId;
        const row = dropdown.closest('tr');

        function persistStatus(rejectionNote = '') {
            fetch(`/police-update-approval-status/${caseId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approval_status: newStatus, rejection_note: rejectionNote })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    dropdown.dataset.original = newStatus;
                    if (row) row.dataset.status = newStatus;
                    showNotification('Status updated to ' + newStatus, 'success');
                } else {
                    dropdown.value = previousStatus;
                    showNotification('Failed to update status: ' + data.message, 'error');
                }
            })
            .catch(() => {
                dropdown.value = previousStatus;
                showNotification('An error occurred while updating the status.', 'error');
            });
        }

        if (newStatus === 'Approved') {
            showConfirmation(
                'Are you sure you want to approve this report?',
                persistStatus,
                () => { dropdown.value = previousStatus; }
            );
        } else if (newStatus === 'Rejected') {
            showRejectionModal(
                (note) => persistStatus(note),
                () => { dropdown.value = previousStatus; }
            );
        } else {
            persistStatus();
        }
    });

    // store initial values for rollback
    document.querySelectorAll('.status-dropdown').forEach(function(d) {
        d.dataset.original = d.value;
    });
    
    // Main click handler for kebab menu
    document.addEventListener('click', function(e) {
        const kebabBtn = e.target.closest('.kebab-btn');
        
        if (kebabBtn) {
            e.preventDefault();
            e.stopPropagation();
            
            const row = kebabBtn.closest('tr');
            const firstCell = row ? row.cells[0] : null;
            const caseId = firstCell ? firstCell.textContent.trim() : null;
            const status = row ? row.dataset.status : null;
            
            if (!caseId) {
                console.error('Could not find case ID');
                return;
            }


            const isArchived = status === 'Archived';
            const archiveLabel = isArchived? '📦 Unarchive' : '🗑️ Archive';
            const archiveAction = isArchived? 'unarchive' : 'archive';
            
            // Clear existing content safely
            while (globalDropdown.firstChild) {
                globalDropdown.removeChild(globalDropdown.firstChild);
            }
            
            // Create dropdown items safely
            const editLink = createDropdownLink('✏️ Edit Report', 'edit', caseId);
            const viewLink = createDropdownLink('👁️ View Details', 'view', caseId);
            const archiveLink = createDropdownLink(archiveLabel, archiveAction, caseId);
            
            globalDropdown.appendChild(editLink);
            globalDropdown.appendChild(viewLink);
            globalDropdown.appendChild(archiveLink);
            
            positionDropdown(kebabBtn, globalDropdown);
            globalDropdown.classList.add('show');
            
            // Event handlers are already attached in createDropdownLink function
            
            return;
        }
        
        if (!globalDropdown.contains(e.target)) {
            closeGlobalDropdown();
        }
    });
    
    function archiveReport(caseId, row) {
        secureFetch('/police-archive-report/', caseId, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                row.dataset.status = "Archived";
                // hide row if currently showing active
                if (!showingArchived) row.style.display = "none";
                showNotification("Report archived successfully!", 'success');
            }
        })
        .catch(err => {
            console.error('Archive error:', err);
            showNotification('Error archiving report: ' + (err.message || 'Unknown error'), 'error');
        });
    }

    function unarchiveReport(caseId, row) {
        secureFetch('/police-unarchive-report/', caseId, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                row.dataset.status = "Pending";
                // hide row if currently showing archived
                if (showingArchived) row.style.display = "none";
                showNotification("Report unarchived successfully!", 'success');
            }
        })
        .catch(err => {
            console.error('Unarchive error:', err);
            showNotification('Error unarchiving report: ' + (err.message || 'Unknown error'), 'error');
        });
    }
    
    // Make function globally accessible for notifications
    window.displayReportDetails = openReportDetails;
    
    window.addEventListener('scroll', function() {
        if (globalDropdown.classList.contains('show')) {
            const activeBtn = document.querySelector('.kebab-btn');
            if (activeBtn) {
                positionDropdown(activeBtn, globalDropdown);
            } else {
                closeGlobalDropdown();
            }
        }
    });
    
    window.addEventListener('resize', function() {
        closeGlobalDropdown();
    });

    // ── Timeline Panel ──
    function openTimelinePanel(caseId) {

        // Create overlay panel
        const panel = document.createElement('div');
        panel.className = 'timeline-panel';
        panel.id        = 'timeline-panel';

        // Header
        const header = document.createElement('div');
        header.className = 'timeline-panel-header';

        const title = document.createElement('h3');
        title.textContent = '🕒 Case Timeline';

        const toggle = document.createElement('div');
        toggle.className = 'timeline-toggle';

        const btnAll = document.createElement('button');
        btnAll.textContent = 'All Activity';
        btnAll.className   = 'toggle-btn active';
        btnAll.dataset.view = 'all';

        const btnStatus = document.createElement('button');
        btnStatus.textContent = 'Status Changes';
        btnStatus.className   = 'toggle-btn';
        btnStatus.dataset.view = 'status';

        const btnLayout = document.createElement('button');
        btnLayout.textContent = '⇅ Vertical';
        btnLayout.className   = 'toggle-btn layout-toggle';
        btnLayout.dataset.layout = 'vertical';

        toggle.appendChild(btnAll);
        toggle.appendChild(btnStatus);
        toggle.appendChild(btnLayout);

        const closeBtn = document.createElement('button');
        closeBtn.textContent = '✕';
        closeBtn.className   = 'timeline-close-btn';
        closeBtn.addEventListener('click', function () {
            panel.remove();
        });

        header.appendChild(title);
        header.appendChild(toggle);
        header.appendChild(closeBtn);
        panel.appendChild(header);

        // Body
        const body = document.createElement('div');
        body.className = 'timeline-panel-body';
        body.innerHTML = `
            <div class="timeline-loading">
                <div class="tl-spinner"></div>
                <p>Loading timeline...</p>
            </div>
        `;
        panel.appendChild(body);

        // Append inside the modal content
        modalContent.appendChild(panel);

        // Fetch timeline data
        fetch(`/police/case-timeline-data/${caseId}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    renderTimeline(body, data, 'all', 'vertical');
                    setupTimelineToggles(toggle, body, data);
                } else {
                    body.innerHTML = `<p class="tl-error">Failed to load timeline.</p>`;
                }
            })
            .catch(err => {
                body.innerHTML = `<p class="tl-error">Error: ${err.message}</p>`;
            });
    }

    function renderTimeline(body, data, view, layout) {
        body.innerHTML = '';

        const events = view === 'status' ? data.status_history : data.all_activity;

        if (!events || events.length === 0) {
            body.innerHTML = `<p class="tl-empty">No timeline events found.</p>`;
            return;
        }

        if (layout === 'vertical') {
            renderVerticalTimeline(body, events);
        } else {
            renderStepperTimeline(body, events, data.stages);
        }
    }

    function renderVerticalTimeline(body, events) {
        const tl = document.createElement('div');
        tl.className = 'tl-vertical';

        events.forEach(function (event) {
            const item = document.createElement('div');
            item.className = `tl-item tl-${(event.event_type || 'update').replace(/_/g, '-')}`;

            const dot = document.createElement('div');
            dot.className = 'tl-dot';

            const content = document.createElement('div');
            content.className = 'tl-content';

            const eventTitle = document.createElement('div');
            eventTitle.className = 'tl-event-title';
            eventTitle.textContent = formatEventType(event.event_type || event.action);

            const meta = document.createElement('div');
            meta.className = 'tl-meta';
            meta.textContent = formatDateTime(event.changed_at || event.event_date || event.log_timestamp);

            const actor = document.createElement('div');
            actor.className = 'tl-actor';
            actor.textContent = event.changed_by_name || event.actor || 'System';
            
            content.appendChild(eventTitle);

            // Before/after for status changes
            if (event.previous_status || event.new_status) {
                const change = document.createElement('div');
                change.className = 'tl-status-change';

                if (event.previous_status) {
                    const prev = document.createElement('span');
                    prev.className = `tl-status-badge tl-status-${event.previous_status.toLowerCase()}`;
                    prev.textContent = event.previous_status;
                    change.appendChild(prev);

                    const arrow = document.createElement('span');
                    arrow.className = 'tl-arrow';
                    arrow.textContent = '→';
                    change.appendChild(arrow);
                }

                if (event.new_status) {
                    const next = document.createElement('span');
                    next.className = `tl-status-badge tl-status-${event.new_status.toLowerCase()}`;
                    next.textContent = event.new_status;
                    change.appendChild(next);
                }

                content.appendChild(change);
            }

            if (event.notes) {
                const notes = document.createElement('div');
                notes.className = 'tl-notes';
                notes.textContent = event.notes;
                content.appendChild(notes);
            }

            content.appendChild(meta);
            content.appendChild(actor);

            item.appendChild(dot);
            item.appendChild(content);
            tl.appendChild(item);
        });

        body.appendChild(tl);
    }

    function renderStepperTimeline(body, events, stages) {
        const stepper = document.createElement('div');
        stepper.className = 'tl-stepper';

        const stageList = stages || ['Pending', 'Approved', 'Open', 'Closed', 'Archived'];
        const reachedStages = new Set(events.map(e => e.new_status || e.new_approval).filter(Boolean));

        stageList.forEach(function (stage, index) {
            const step = document.createElement('div');
            step.className = `tl-step ${reachedStages.has(stage) ? 'reached' : ''}`;

            const circle = document.createElement('div');
            circle.className = 'tl-step-circle';
            circle.textContent = index + 1;

            const label = document.createElement('div');
            label.className = 'tl-step-label';
            label.textContent = stage;

            // Find event for this stage
            const stageEvent = events.find(e => e.new_status === stage || e.new_approval === stage);
            if (stageEvent) {
                const date = document.createElement('div');
                date.className = 'tl-step-date';
                date.textContent = formatDateTime(stageEvent.changed_at || stageEvent.event_date);
                step.appendChild(circle);
                step.appendChild(label);
                step.appendChild(date);
            } else {
                step.appendChild(circle);
                step.appendChild(label);
            }

            stepper.appendChild(step);

            // Connector line
            if (index < stageList.length - 1) {
                const connector = document.createElement('div');
                connector.className = `tl-connector ${reachedStages.has(stageList[index + 1]) ? 'reached' : ''}`;
                stepper.appendChild(connector);
            }
        });

        body.appendChild(stepper);
    }

    function setupTimelineToggles(toggle, body, data) {
        let currentView   = 'all';
        let currentLayout = 'vertical';

        toggle.querySelectorAll('.toggle-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                if (btn.dataset.view) {
                    toggle.querySelectorAll('[data-view]').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentView = btn.dataset.view;
                }
                if (btn.dataset.layout !== undefined) {
                    currentLayout = currentLayout === 'vertical' ? 'stepper' : 'vertical';
                    btn.textContent = currentLayout === 'vertical' ? '⇅ Vertical' : '⇆ Stepper';
                }
                renderTimeline(body, data, currentView, currentLayout);
            });
        });
    }

    function formatEventType(type) {
        if (!type) return 'Update';
        return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    }

    function formatDateTime(dt) {
        if (!dt) return 'N/A';
        const d = new Date(dt);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
            + ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
});