// Archive User Function
function archiveUser(userId, userName) {
    if (confirm(`Are you sure you want to archive ${userName}?\n\nThis will set their account status to 'archived' and they will no longer be able to login.`)) {
        fetch(`/admin-user-management/archive-user/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message || 'User archived successfully');
                // Reload the user list
                if (typeof UserFilter !== 'undefined' && UserFilter.loadUsers) {
                    UserFilter.loadUsers(UserFilter.currentPage || 1);
                } else {
                    location.reload();
                }
            } else {
                alert('Error: ' + (data.message || 'Failed to archive user'));
            }
        })
        .catch(error => {
            console.error('Error archiving user:', error);
            alert('Network error: Failed to archive user');
        });
    }
}
