async function openEditProfilePopup() {
    document.getElementById('editProfilePopup').style.display = 'flex';

    try {
        const response = await fetch("/edit-profile");
        const data = await response.json();

        document.getElementById('firstName').value = data.first_name;
        document.getElementById('lastName').value = data.last_name;
        document.getElementById('phone').value = data.contact_number;
        document.getElementById('email').value = data.email;
        document.getElementById("currentPassword").value = "";
        document.getElementById("newPassword").value = "";
        document.getElementById("confirmPassword").value = "";
        

        // Load profile picture
        if (data.profile_filedata) {
            document.getElementById("profilePreview").src =
                `data:${data.profile_filetype};base64,${data.profile_filedata}`;
        }
    } catch (error) {
        console.error('Error fetching user data:', error);
    }
}

function closeEditProfilePopup() {
    document.getElementById('editProfilePopup').style.display = 'none';
}

function previewProfilePic() {
    const file = document.getElementById('profilePic').files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('profilePreview').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// Close popup when clicking outside
window.onclick = function(event) {
    const popup = document.getElementById('editProfilePopup');
    if (event.target == popup) {
        closeEditProfilePopup();
    }
}


const saveChangesBtn = document.getElementById('save-changes-btn');

saveChangesBtn.addEventListener("click", async () => {
    
    // Validate password fields
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // If any password field is filled, all must be filled
    if (currentPassword || newPassword || confirmPassword) {
        if (!currentPassword || !newPassword || !confirmPassword) {
            alert("If changing password, all password fields must be filled.");
            return;
        }
        
        if (newPassword !== confirmPassword) {
            alert("New password and confirm password do not match.");
            return;
        }
    }
    
    saveChangesBtn.disabled = true;
    saveChangesBtn.textContent = "Saving...";

    const formData = new FormData(document.getElementById('edit-profile-form'));


    try{
        const response = await fetch('/edit-profile', {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if(result.error) {
            alert("Error: " + result.error);
        } else {
            alert("Profile updated successfully!");
            closeEditProfilePopup();
            location.reload();
        }

        }catch (error){
            console.error("Error saving profile: ", error);
            alert("An error occured while saving. ");

        }
        
    saveChangesBtn.disabled = false;
    saveChangesBtn.textContent = "Save Changes";
});