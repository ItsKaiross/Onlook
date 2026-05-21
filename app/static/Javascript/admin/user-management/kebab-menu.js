function toggleKebab(btn) {
    const menu = btn.nextElementSibling;
    const isOpen = menu.classList.contains("open");

    // close all other open menus first
    closeKebab();

    if (!isOpen) {
        menu.classList.add("open");
        positionKebabMenu(btn, menu);
    }
}

function positionKebabMenu(btn, menu) {
    const btnRect = btn.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Get menu dimensions (make it visible temporarily to measure)
    menu.style.visibility = 'hidden';
    menu.style.display = 'block';
    const menuWidth = menu.offsetWidth;
    const menuHeight = menu.offsetHeight;
    menu.style.visibility = '';
    menu.style.display = '';
    
    let left, top;
    
    // Horizontal positioning
    const spaceRight = viewportWidth - btnRect.right;
    const spaceLeft = btnRect.left;
    
    if (spaceRight >= menuWidth) {
        // Position to the right of button
        left = btnRect.right - menuWidth;
    } else if (spaceLeft >= menuWidth) {
        // Position to the left of button
        left = btnRect.left;
    } else {
        // Center align if not enough space on either side
        left = Math.max(10, (viewportWidth - menuWidth) / 2);
    }
    
    // Vertical positioning
    const spaceBelow = viewportHeight - btnRect.bottom;
    const spaceAbove = btnRect.top;
    
    if (spaceBelow >= menuHeight) {
        // Position below button
        top = btnRect.bottom + 5;
    } else if (spaceAbove >= menuHeight) {
        // Position above button
        top = btnRect.top - menuHeight - 5;
    } else {
        // Position at top of viewport if not enough space
        top = 10;
    }
    
    // Apply positioning
    menu.style.left = left + 'px';
    menu.style.top = top + 'px';
}

function closeKebab() {
    document.querySelectorAll(".kebab-info.open").forEach(m => m.classList.remove("open"));
}

// close when clicking outside
document.addEventListener("click", function(e) {
    if (!e.target.closest(".kebab-menu")) {
        closeKebab();
    }
});

// Reposition on scroll
const tableContainer = document.querySelector('.user-management-tbl');
if (tableContainer) {
    tableContainer.addEventListener('scroll', function() {
        const openMenu = document.querySelector('.kebab-info.open');
        if (openMenu) {
            const btn = openMenu.previousElementSibling;
            positionKebabMenu(btn, openMenu);
        }
    });
}

// Reposition on window scroll
window.addEventListener('scroll', function() {
    const openMenu = document.querySelector('.kebab-info.open');
    if (openMenu) {
        const btn = openMenu.previousElementSibling;
        positionKebabMenu(btn, openMenu);
    }
});

// Reposition on window resize
window.addEventListener('resize', function() {
    const openMenu = document.querySelector('.kebab-info.open');
    if (openMenu) {
        const btn = openMenu.previousElementSibling;
        positionKebabMenu(btn, openMenu);
    }
});