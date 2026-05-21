//Opens the popup
function openChangePasswordPopup() {
    document.getElementById('changePassPopup').style.display = 'flex';
}


//Using close button
function closeChangePassPopup(){
    document.getElementById('changePassPopup').style.display = 'none';
}

//Close when clicking outside
window.onclick = function(event) {
    const popup = this.document.getElementById('changePassPopup');
    if (event.target == popup){
        closeChangePassPopup();
    }
}

// Checking if the password is match
const password = document.getElementById("newPass");
const confirmPassword = document.getElementById("confirmPass");

if (password !== null && confirmPassword !== null)
{
    function validatePassword(){
        if(password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity("Passwords Don't Match");
        } else {
            confirmPassword.setCustomValidity('');
        }
    }

    password.addEventListener('keyup', validatePassword);
    confirmPassword.addEventListener('keyup', validatePassword);
}

// Saving the password

const savePassBtn = document.getElementById('save-btn');

savePassBtn.addEventListener("click", async () =>{

    savePassBtn.disabled = true;
    savePassBtn.textContent = "Saving...";

    const formData = new formData(document.getElementById('change-pass-form'));


    try{
        const response = await fetch('/change-password', {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.error) {
            alert("Error: " + result.error);
        }else {
            alert("Profile updated successfully");
            closeChangePassPopup();
        }
    }catch (error){
        alert("An error occured while saving.");
    }

    savePassBtn.disabled = false;
    savePassBtn.textContent = "Save";
});