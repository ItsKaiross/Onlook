// Restricted Accounts Pagination Handler

let currentRestrictedPage = 1;
let restrictedPerPage = 10;

// Load restricted accounts with pagination
function loadRestrictedAccounts(page = 1, perPage = 10) {
    currentRestrictedPage = page;
    restrictedPerPage = perPage;

    // Show loading state
    const tbody = document.querySelector('#restricted-accounts-popup tbody');
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">Loading...</td></tr>';

    fetch('/admin-user-management/restricted-accounts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            page: page,
            per_page: perPage
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error('HTTP error ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received data:', data);
        if (data.success) {
            updateRestrictedTable(data.users);
            updateRestrictedPagination(data.total_pages, data.page, data.per_page, data.total_records);
        } else {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px; color: red;">Error: ' + data.error + '</td></tr>';
            console.error('Error loading restricted accounts:', data.error);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px; color: red;">Error loading data: ' + error.message + '</td></tr>';
    });
}

// Update the restricted accounts table
function updateRestrictedTable(users) {
    const tbody = document.querySelector('#restricted-accounts-popup tbody');
    tbody.innerHTML = '';

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-results">No restricted accounts found</td></tr>';
        return;
    }

    users.forEach(user => {
        if (user.role === 'systemAdmin' || user.status !== 'restricted') {
            return;
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.full_name || ''}</td>
            <td>${user.email || ''}</td>
            <td>
                <select data-id="${user.accounts_id}" onchange="updateRole(this)" ${user.role === 'user' ? 'disabled' : ''}>
                    <optgroup label="Admin Roles">
                        <option value="systemAdmin" ${user.role === 'systemAdmin' ? 'selected disabled' : ''}>System Admin</option>
                        <option value="policeAdmin" ${user.role === 'policeAdmin' ? 'selected disabled' : ''}>Police Admin</option>
                    </optgroup>
                    <optgroup label="Police">
                        <option value="police" ${user.role === 'police' ? 'selected disabled' : ''}>Police</option>
                        <option value="alaminos-mps" ${user.role === 'alaminos-mps' ? 'selected disabled' : ''}>Alaminos Municipal Police Station</option>
                        <option value="bay-mps" ${user.role === 'bay-mps' ? 'selected disabled' : ''}>Bay Municipal Police Station</option>
                        <option value="binan-ps" ${user.role === 'binan-ps' ? 'selected disabled' : ''}>Biñan City Police Station</option>
                        <option value="cabuyao-ps" ${user.role === 'cabuyao-ps' ? 'selected disabled' : ''}>Cabuyao City Police Station</option>
                        <option value="calamba-ps" ${user.role === 'calamba-ps' ? 'selected disabled' : ''}>Calamba City Police Station</option>
                        <option value="calauan-mps" ${user.role === 'calauan-mps' ? 'selected disabled' : ''}>Calauan Municipal Police Station</option>
                        <option value="cavinti-mps" ${user.role === 'cavinti-mps' ? 'selected disabled' : ''}>Cavinti Municipal Police Station</option>
                        <option value="famy-mps" ${user.role === 'famy-mps' ? 'selected disabled' : ''}>Famy Municipal Police Station</option>
                        <option value="kalayaan-mps" ${user.role === 'kalayaan-mps' ? 'selected disabled' : ''}>Kalayaan Municipal Police Station</option>
                        <option value="liliw-mps" ${user.role === 'liliw-mps' ? 'selected disabled' : ''}>Liliw Municipal Police Station</option>
                        <option value="sanpablo-ps" ${user.role === 'sanpablo-ps' ? 'selected disabled' : ''}>San Pablo City Police Station</option>
                        <option value="stacruz-mps" ${user.role === 'stacruz-mps' ? 'selected disabled' : ''}>Santa Cruz Municipal Police Station</option>
                        <option value="starosa-ps" ${user.role === 'starosa-ps' ? 'selected disabled' : ''}>Santa Rosa Police Station</option>
                        <option value="siniloan-mps" ${user.role === 'siniloan-mps' ? 'selected disabled' : ''}>Siniloan Municipal Police Station</option>
                        <option value="victoria-mps" ${user.role === 'victoria-mps' ? 'selected disabled' : ''}>Victoria Municipal Police Station</option>
                    </optgroup>
                    <optgroup label="User">
                        <option value="user" ${user.role === 'user' ? 'selected disabled' : ''} disabled>User</option>
                    </optgroup>
                </select>
                <span id="user-${user.accounts_id}" class="role-status"></span>
            </td>
            <td>
                ${user.validID ? 
                    `<img src="data:image/jpeg;base64,${user.validID}" class="validID">
                    <span class="view_txt">VIEW</span>` : 
                    '<span class="no-image">No Image</span>'}
            </td>
            <td><span class="account-status-restricted">${user.status}</span></td>
            <td>
                <div class="kebab-menu">
                    <button class="kebab-btn" onclick="toggleKebab(this)">&#8942;</button>
                    <div class="kebab-info">
                        <a href="#"
                        onclick="openEditPopup(this)"
                        data-user-id="${user.accounts_id}"
                        data-roles="${user.role}"
                        data-first-name="${user.firstName || ''}"
                        data-last-name="${user.lastName || ''}"
                        data-middle-name="${user.middleName || ''}"
                        data-contact-number="${user.contact_number || ''}"
                        data-email="${user.email}">
                            Edit
                        </a>
                        <a href="/admin-user-management/activate-user/${user.accounts_id}">
                            Activate
                        </a>
                    </div>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update pagination controls
function updateRestrictedPagination(totalPages, currentPage, perPage, totalRecords) {
    const paginationDiv = document.querySelector('#restricted-accounts-popup .pagination-controls');
    const tableInfoDiv = document.querySelector('#restricted-accounts-popup .table-info');
    
    // Update table info
    const start = (currentPage - 1) * perPage + 1;
    const end = Math.min(currentPage * perPage, totalRecords);
    tableInfoDiv.textContent = `Showing ${start} - ${end} of ${totalRecords} entries`;
    
    // Build pagination HTML
    let paginationHTML = '';
    
    // First and Previous buttons
    if (currentPage > 1) {
        paginationHTML += `<a href="#" onclick="loadRestrictedAccounts(1, ${perPage}); return false;">&laquo;</a>`;
        paginationHTML += `<a href="#" onclick="loadRestrictedAccounts(${currentPage - 1}, ${perPage}); return false;">&lsaquo;</a>`;
    }
    
    // Page numbers
    for (let p = 1; p <= totalPages; p++) {
        const activeClass = p === currentPage ? 'active' : '';
        paginationHTML += `<a href="#" class="${activeClass}" onclick="loadRestrictedAccounts(${p}, ${perPage}); return false;">${p}</a>`;
    }
    
    // Next and Last buttons
    if (currentPage < totalPages) {
        paginationHTML += `<a href="#" onclick="loadRestrictedAccounts(${currentPage + 1}, ${perPage}); return false;">&rsaquo;</a>`;
        paginationHTML += `<a href="#" onclick="loadRestrictedAccounts(${totalPages}, ${perPage}); return false;">&raquo;</a>`;
    }
    
    // Per page dropdown
    paginationHTML += `
        <select id="restricted-row-per-page" onchange="loadRestrictedAccounts(1, this.value)">
            <option value="5" ${perPage == 5 ? 'selected' : ''}>5</option>
            <option value="10" ${perPage == 10 ? 'selected' : ''}>10</option>
            <option value="20" ${perPage == 20 ? 'selected' : ''}>20</option>
            <option value="50" ${perPage == 50 ? 'selected' : ''}>50</option>
        </select>
    `;
    
    paginationDiv.innerHTML = paginationHTML;
}
