function toggleMobileMenu() {
    const hamburger = document.querySelector('.mobile-hamburger');
    const menu = document.getElementById('mobileMenu');
    const backdrop = document.querySelector('.mobile-menu-backdrop');
    
    hamburger.classList.toggle('active');
    menu.classList.toggle('active');
    backdrop.classList.toggle('active');
    
    // Prevent body scroll when menu is open
    if (menu.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

function closeMobileMenu() {
    const hamburger = document.querySelector('.mobile-hamburger');
    const menu = document.getElementById('mobileMenu');
    const backdrop = document.querySelector('.mobile-menu-backdrop');
    
    hamburger.classList.remove('active');
    menu.classList.remove('active');
    backdrop.classList.remove('active');
    document.body.style.overflow = '';
}

// Close menu when clicking on menu links or close button
document.addEventListener('DOMContentLoaded', function() {
    const menuLinks = document.querySelectorAll('.mobile-menu-overlay a');
    menuLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
    
    // Add close button to menu header
    const menuHeader = document.querySelector('.mobile-menu-header');
    if (menuHeader && !menuHeader.querySelector('.mobile-menu-close')) {
        const closeBtn = document.createElement('div');
        closeBtn.className = 'mobile-menu-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = closeMobileMenu;
        menuHeader.appendChild(closeBtn);
    }
});