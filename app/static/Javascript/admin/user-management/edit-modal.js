var background = document.getElementById('bg-black');

function openEditPopup(element){
    const userId = element.getAttribute('data-user-id');
    const firstName = element.getAttribute('data-first-name');
    const lastName = element.getAttribute('data-last-name');
    const middleName = element.getAttribute('data-middle-name');
    const email = element.getAttribute('data-email');
    const roles = element.getAttribute('data-roles');
    const contact_number = element.getAttribute('data-contact-number');

    document.querySelector('#edit_popup input[name = "firstName"]').value = firstName;
    document.querySelector('#edit_popup input[name = "lastName"]').value = lastName;
    document.querySelector('#edit_popup input[name = "middleName"]').value = middleName;
    document.querySelector('#edit_popup input[name = "email"]').value = email;
    document.querySelector('#edit_popup input[name = "number"]').value = contact_number;

    let hiddenID= document.querySelector('#edit_popup input[name="user_id"]');
    if (!hiddenID){
        hiddenID = document.createElement('input');
        hiddenID.type = 'hidden';
        hiddenID.name = 'user_id';
        document.querySelector('#edit_popup form').appendChild(hiddenID);
    }
    hiddenID.value = userId;

    const roleFrame = document.querySelector('#edit_popup .role_frame');
    if (roles === 'user'){
        roleFrame.style.display = 'none';
    }else {
        roleFrame.style.display = 'block';
        document.querySelector('#edit_popup select[name="role"]').value = roles;

    }

    var modal_edit_user = document.getElementById('edit_popup');
    modal_edit_user.style.visibility = 'visible'
    modal_edit_user.style.top = "50%"
    modal_edit_user.style.transform = "translate(-50%, -50%)"
    modal_edit_user.style.transition = ".5s"
    background.style.pointerEvents = "none"
    background.style.display = "block"
}

// Add form submission handling
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.querySelector('#edit_popup form');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            const submitBtn = editForm.querySelector('.update-btn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Updating...';
        });
    }
});

//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//

var edit_close_btn = document.getElementsByClassName('edit-close')[0];

edit_close_btn.onclick = function(){
    closeEditModal();
}

function closeEditModal() {
    var modal_edit_user = document.getElementById('edit_popup');
    modal_edit_user.style.visibility = "hidden";
    background.style.display = "none";
    modal_edit_user.style.top = "-10%"
    modal_edit_user.style.transform = "translate(-50%, -20%)"
    modal_edit_user.style.transition = ".5s"
    background.style.transition = ".5s"
    
    // Reset form button
    const submitBtn = modal_edit_user.querySelector('.update-btn');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'update';
    }
}


