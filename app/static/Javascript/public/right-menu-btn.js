document.addEventListener("DOMContentLoaded", function(){
    const menuBtn = document.querySelector(".right-menu-btn");
    const rightMenu = document.querySelector(".right-menu");

    if (menuBtn && rightMenu) {
        menuBtn.addEventListener("click", function(e) {
            e.stopPropagation(); // Prevent the click from reaching document
            rightMenu.classList.toggle("open");
        });

        // Close dropdown if clicked outside
        document.addEventListener("click", function(e) {
            if (!rightMenu.contains(e.target)) {
                rightMenu.classList.remove("open");
            }
        });
    }
});
