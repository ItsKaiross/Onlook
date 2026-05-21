document.addEventListener('DOMContentLoaded', function() {
    console.log('CASE MANAGEMENT KEBAB LOADED');
    
    // Create global dropdown element (once)
    let globalDropdown = document.querySelector('.kebab-dropdown-global');
    if (!globalDropdown) {
        globalDropdown = document.createElement('div');
        globalDropdown.className = 'kebab-dropdown-global';
        document.body.appendChild(globalDropdown);
        console.log('Global dropdown created');
    }

    // Get modal elements
    const detailsModal = document.getElementById('case-details-modal');
    const editModal = document.getElementById('edit-case-modal');
    
    // Function to open case details
    function openCaseDetails(caseId) {
        console.log('Opening case details for:', caseId);
        fetch(`/police-case-details/${caseId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.displayCaseDetails(data.case);
                } else {
                    alert('Error loading case details: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading case details');
            });
    }
    
    // Function to open edit modal
    function openEditCase(caseId) {
        console.log('Opening edit for:', caseId);
        fetch(`/police-case-details/${caseId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    populateEditForm(data.case);
                    if (editModal) {
                        editModal.style.display = 'flex';
                        editModal.classList.add('show');
                    }
                } else {
                    alert('Error loading case data: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading case data');
            });
    }
    
    // Function to populate edit form
    function populateEditForm(caseData) {
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
    
    // Function to archive case
    function archiveCase(caseId) {
        if (confirm('Are you sure you want to archive this case?')) {
            fetch(`/police-archive-case/${caseId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Case archived successfully');
                    location.reload();
                } else {
                    alert('Error archiving case: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error archiving case');
            });
        }
    }
    
    // Helper function to create dropdown links
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
            
            console.log('Dropdown action clicked:', actionType, id);
            
            closeGlobalDropdown();
            
            if (actionType === 'view') {
                openCaseDetails(id);
            } else if (actionType === 'edit') {
                openEditCase(id);
            } else if (actionType === 'archive') {
                archiveCase(id);
            }
        });
        
        return link;
    }
    
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
        while (globalDropdown.firstChild) {
            globalDropdown.removeChild(globalDropdown.firstChild);
        }
    }
    
    // Main click handler for kebab menu
    document.addEventListener('click', function(e) {
        const kebabBtn = e.target.closest('.kebab-btn');
        
        if (kebabBtn) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Kebab button clicked');
            
            const caseId = kebabBtn.getAttribute('data-case-id');
            
            if (!caseId) {
                console.error('Could not find case ID');
                return;
            }
            
            console.log('Case ID:', caseId);
            
            // Clear existing content
            while (globalDropdown.firstChild) {
                globalDropdown.removeChild(globalDropdown.firstChild);
            }
            
            // Create dropdown items
            const viewLink = createDropdownLink('👁️ View Details', 'view', caseId);
            const editLink = createDropdownLink('✏️ Edit', 'edit', caseId);
            const archiveLink = createDropdownLink('🗑️ Archive', 'archive', caseId);
            
            globalDropdown.appendChild(viewLink);
            globalDropdown.appendChild(editLink);
            globalDropdown.appendChild(archiveLink);
            
            positionDropdown(kebabBtn, globalDropdown);
            globalDropdown.classList.add('show');
            
            console.log('Dropdown shown');
            
            return;
        }
        
        if (!globalDropdown.contains(e.target)) {
            closeGlobalDropdown();
        }
    });
    
    window.addEventListener('scroll', function() {
        if (globalDropdown.classList.contains('show')) {
            closeGlobalDropdown();
        }
    });
    
    window.addEventListener('resize', function() {
        closeGlobalDropdown();
    });
    
    console.log('Kebab menu initialized');
});
