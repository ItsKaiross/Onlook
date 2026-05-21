fetch('/users/filter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ search: '', role: '', status: '', user_page: 1, user_per_page: 1 })
})
.then(res => res.json())
.then(data => {
    var user = data.users[0];
    console.log('=== IMAGE DEBUG ===');
    console.log('validID type:', typeof user.validID);
    console.log('validID value:', user.validID);
    console.log('validID length:', user.validID ? user.validID.length : 0);
    console.log('validID null?', user.validID === null);
    console.log('validID undefined?', user.validID === undefined);
});

// User Filter Module
const UserFilter = {
    currentPage: 1,
    totalPages: 1,
    
    init: function() {
        console.log('Initializing UserFilter');
        this.bindEvents();
        this.loadUsers(1); // Load initial data
    },
    
    bindEvents: function() {
        const self = this;
        
        // Search input with debounce
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                console.log('Search changed, loading page 1');
                self.loadUsers(1);
            }, 300));
        }
        
        // Role filter
        const roleFilter = document.getElementById('roleFilter');
        if (roleFilter) {
            roleFilter.addEventListener('change', () => {
                console.log('Role filter changed');
                self.loadUsers(1);
            });
        }
        
        // Status filter
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                console.log('Status filter changed');
                self.loadUsers(1);
            });
        }
        
        // Per page selector
        const perPageSelect = document.getElementById('perPageSelect');
        if (perPageSelect) {
            perPageSelect.addEventListener('change', () => {
                console.log('Per page changed');
                self.loadUsers(1);
            });
        }
    },
    
    loadUsers: function(page) {
        const self = this;
        const search = document.getElementById('searchInput')?.value || '';
        const role = document.getElementById('roleFilter')?.value || '';
        const status = document.getElementById('statusFilter')?.value || '';
        const perPage = document.getElementById('perPageSelect')?.value || 10;
        
        console.log('Loading users:', { search, role, status, page, perPage });
        
        // Show loading
        this.showLoading();
        
        fetch('/users/filter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search: search,
                role: role,
                status: status,
                user_page: page,
                user_per_page: parseInt(perPage)
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            
            if (data.success) {
                self.currentPage = data.user_page;
                self.totalPages = data.total_pages;
                
                console.log(`Rendering ${data.users.length} users, page ${data.user_page} of ${data.total_pages}`);
                
                self.renderTable(data.users);
                self.renderPagination(data.user_page, data.total_pages, data.total_records);
                self.updateInfo(data.total_records, data.user_page, data.user_per_page, data.users.length);
            } else {
                console.error('Server error:', data.error);
                self.showError(data.error || 'Failed to load users');
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            self.showError('Failed to load users: ' + error.message);
        });
    },
    
    renderTable: function(users) {
        const tbody = document.querySelector('.user-management-tbl tbody');
        if (!tbody) {
            console.error('Table body not found!');
            return;
        }
        
        
        if (!users || users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-4">
                        <p class="text-muted">No users found matching your criteria</p>
                    </td>
                </tr>`;
            return;
        }
        
        let html = '';
        users.forEach(user => {
            
            // DEBUG
            console.log('User ' + user.accounts_id + ' validID:', 
                user.validID ? user.validID.substring(0, 30) + '...' : 'NONE');
            
            // Profile Picture handling
            let profilePicHtml = '<span class="no-image">No Image</span>';
            if (user.profilePic && user.profilePic.length > 10) {
                profilePicHtml = `<span class="view_txt" onclick="openDocumentModal('profilePictureModal', 'data:image/jpeg;base64,${user.profilePic}', 'image')">VIEW</span>`;
            }
            
            // PSA handling (PDF/Document)
            let psaHtml = '<span class="no-image">No Document</span>';
            if (user.psa && user.psa.length > 10) {
                const psaType = user.psa_type || 'application/pdf';
                const psaMimeType = psaType.includes('pdf') ? 'application/pdf' : psaType;
                psaHtml = `<span class="view_txt" onclick="openDocumentModal('psaModal', 'data:${psaMimeType};base64,${user.psa}', 'pdf')">VIEW</span>`;
            }
            
            // Valid ID handling (Image or PDF)
            let validIDHtml = '<span class="no-image">No Document</span>';
            if (user.validID && user.validID.length > 10) {
                const validIDType = user.validID_type || 'image/jpeg';
                const isImage = validIDType.includes('image');
                const isPDF = validIDType.includes('pdf');
                
                if (isImage) {
                    validIDHtml = `<span class="view_txt" onclick="openDocumentModal('validIdModal', 'data:${validIDType};base64,${user.validID}', 'image')">VIEW</span>`;
                } else if (isPDF) {
                    validIDHtml = `<span class="view_txt" onclick="openDocumentModal('validIdModal', 'data:application/pdf;base64,${user.validID}', 'pdf')">VIEW</span>`;
                } else {
                    // For other document types (doc, docx, etc.)
                    validIDHtml = `<span class="view_txt" onclick="openDocumentModal('validIdModal', 'data:${validIDType};base64,${user.validID}', 'document')">VIEW</span>`;
                }
            }
            
            // Status Class
            let statusClass = '';
            let statusText = user.status || '';
            if (user.status === 'active') {
                statusClass = 'account-status';
            }else if (user.status === 'pending'){
                statusClass = 'account-status-pending';
            }else if (user.status === 'restricted') {
                statusClass = 'account-status-restricted';
                statusText = 'Restricted';
            }else if (user.status === 'archived') {
                statusClass = 'account-status-archived';
                statusText = 'Archived';
            }

            // Role options (same as your server-side)
            const roleOptions = `
                <optgroup label="Admin Roles">
                    <option value="systemAdmin" ${user.role === 'systemAdmin' ? 'selected' : ''}>System Admin</option>
                    <option value="policeAdmin" ${user.role === 'policeAdmin' ? 'selected' : ''}>Police Admin</option>
                    <option value="policeChief" ${user.role === 'policeChief' ? 'selected' : ''}>Police Chief</option>
                </optgroup>
                <optgroup label="Police">
                    <option value="police" ${user.role === 'police' ? 'selected' : ''}>Police</option>
                    <option value="alaminos-mps" ${user.role === 'alaminos-mps' ? 'selected' : ''}>Alaminos Municipal Police Station</option>
                    <option value="bay-mps" ${user.role === 'bay-mps' ? 'selected' : ''}>Bay Municipal Police Station</option>
                    <option value="binan-ps" ${user.role === 'binan-ps' ? 'selected' : ''}>Biñan City Police Station</option>
                    <option value="cabuyao-ps" ${user.role === 'cabuyao-ps' ? 'selected' : ''}>Cabuyao City Police Station</option>
                    <option value="calamba-ps" ${user.role === 'calamba-ps' ? 'selected' : ''}>Calamba City Police Station</option>
                    <option value="calauan-mps" ${user.role === 'calauan-mps' ? 'selected' : ''}>Calauan Municipal Police Station</option>
                    <option value="cavinti-mps" ${user.role === 'cavinti-mps' ? 'selected' : ''}>Cavinti Municipal Police Station</option>
                    <option value="famy-mps" ${user.role === 'famy-mps' ? 'selected' : ''}>Famy Municipal Police Station</option>
                    <option value="kalayaan-mps" ${user.role === 'kalayaan-mps' ? 'selected' : ''}>Kalayaan Municipal Police Station</option>
                    <option value="liliw-mps" ${user.role === 'liliw-mps' ? 'selected' : ''}>Liliw Municipal Police Station</option>
                    <option value="sanpablo-ps" ${user.role === 'sanpablo-ps' ? 'selected' : ''}>San Pablo City Police Station</option>
                    <option value="stacruz-mps" ${user.role === 'stacruz-mps' ? 'selected' : ''}>Santa Cruz Municipal Police Station</option>
                    <option value="starosa-ps" ${user.role === 'starosa-ps' ? 'selected' : ''}>Santa Rosa Police Station</option>
                    <option value="siniloan-mps" ${user.role === 'siniloan-mps' ? 'selected' : ''}>Siniloan Municipal Police Station</option>
                    <option value="victoria-mps" ${user.role === 'victoria-mps' ? 'selected' : ''}>Victoria Municipal Police Station</option>
                </optgroup>
                <optgroup label="User">
                    <option value="user" ${user.role === 'user' ? 'selected' : ''}>User</option>
                </optgroup>
            `;
            
            
            html += `
                <tr>
                    <td>${this.escapeHtml(user.full_name || 'N/A')}</td>
                    <td>${this.escapeHtml(user.email || 'N/A')}</td>
                    <td>
                        <select data-id="${user.accounts_id}" onchange="updateRole(this)" ${user.role === 'user' || user.role === 'systemAdmin' ? 'disabled' : ''}>
                            ${roleOptions}
                        </select>
                        <br>
                        <span id="user-${user.accounts_id}" class="role-status"></span>
                    </td>
                    <td>
                        ${profilePicHtml}
                    </td>
                    <td>
                        ${psaHtml}
                    </td>
                    <td>
                        ${validIDHtml}
                    </td>
                    <td><span class="${statusClass}">${statusText}</span></td>
                    <td>
                        <div class="kebab-menu">
                            <button class="kebab-btn" onclick="toggleKebab(this)">&#8942;</button>
                            <div class="kebab-info">
                                <a href="#"
                                onclick="openEditPopup(this)"
                                data-user-id="${user.accounts_id}"
                                data-roles="${user.role}"
                                data-first-name="${this.escapeHtml(user.firstName || '')}"
                                data-last-name="${this.escapeHtml(user.lastName || '')}"
                                data-middle-name="${this.escapeHtml(user.middleName || '')}"
                                data-contact-number="${this.escapeHtml(user.contact_number || '')}"
                                data-email="${this.escapeHtml(user.email || '')}">
                                    Edit
                                </a>
                                ${user.role !== 'systemAdmin' ? `
                                <a href="/admin-user-management/restrict-user/${user.accounts_id}">
                                    Restrict
                                </a>
                                <a href="#" onclick="archiveUser(${user.accounts_id}, '${this.escapeHtml(user.full_name || 'User')}'); return false;">
                                    Archive
                                </a>
                                ` : ''}
                            </div>
                        </div>
                    </td>
                </tr>`;
        });
        
        tbody.innerHTML = html;
    },
    
    renderPagination: function(currentPage, totalPages, totalRecords) {
        const paginationDiv = document.getElementById('pagination');
        if (!paginationDiv) return;
        
        if (totalPages <= 1) {
            paginationDiv.innerHTML = '';
            return;
        }
        
        // Match your original design class names
        let html = '<div class="pagination-controls">';
        
        // First page &laquo;
        if (currentPage > 1) {
            html += `<a href="javascript:void(0)" onclick="UserFilter.loadUsers(1)">&laquo;</a>`;
            html += `<a href="javascript:void(0)" onclick="UserFilter.loadUsers(${currentPage - 1})">&lsaquo;</a>`;
        }
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            html += `<a href="javascript:void(0)" onclick="UserFilter.loadUsers(${i})" 
                        class="${i === currentPage ? 'active' : ''}">${i}</a>`;
        }
        
        // Last page &raquo;
        if (currentPage < totalPages) {
            html += `<a href="javascript:void(0)" onclick="UserFilter.loadUsers(${currentPage + 1})">&rsaquo;</a>`;
            html += `<a href="javascript:void(0)" onclick="UserFilter.loadUsers(${totalPages})">&raquo;</a>`;
        }
        
        html += '</div>';
        paginationDiv.innerHTML = html;
    },
    
    updateInfo: function(totalRecords, currentPage, perPage, currentCount) {
        const infoDiv = document.getElementById('tableInfo');
        if (!infoDiv) {
            console.error('Info div not found!');
            return;
        }
        
        const start = (currentPage - 1) * perPage + 1;
        const end = Math.min(currentPage * perPage, totalRecords);
        
        infoDiv.innerHTML = `
            Showing <strong>${start}-${end}</strong> of <strong>${totalRecords}</strong> users
            ${totalRecords > 0 ? `(Page ${currentPage} of ${Math.ceil(totalRecords / perPage)})` : ''}
        `;
    },
    
    showLoading: function() {
        const tbody = document.querySelector('.user-management-tbl tbody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 text-muted">Loading users...</p>
                    </td>
                </tr>`;
        }
    },
    
    showError: function(message) {
        const tbody = document.querySelector('.user-management-tbl tbody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-4">
                        <i class="fas fa-exclamation-triangle fa-2x text-warning mb-2"></i>
                        <p class="text-danger">${this.escapeHtml(message)}</p>
                        <button class="btn btn-sm btn-primary" onclick="UserFilter.loadUsers(1)">
                            <i class="fas fa-sync-alt"></i> Try Again
                        </button>
                    </td>
                </tr>`;
        }
    },
    
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    escapeHtml: function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', function() {
    UserFilter.init();
});