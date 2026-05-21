function toggleProfileMenu() {
    document.getElementById("profileMenu").classList.toggle("active");
}

// close when clicking outside
document.addEventListener("click", function(e) {
    const menu = document.getElementById("profileMenu");
    const button = document.querySelector(".profile-btn");

    if (!button.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove("active");
    }
});

function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('profile-pic').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}