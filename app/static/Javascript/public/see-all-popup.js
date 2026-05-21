function openSeeAllModal() {
    console.log('Opening see-all modal');
    const modal = document.getElementById('seeAllModal');
    console.log('Modal element:', modal);
    
    if (modal) {
        const grid = modal.querySelector('.see-all-grid');
        const cards = grid ? grid.querySelectorAll('.see-all-card') : [];
        console.log('Number of cards in see-all modal:', cards.length);
        
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        
        // Check content and grid
        const content = modal.querySelector('.see-all-content');
        if (content) {
            const contentStyle = window.getComputedStyle(content);
            console.log('Content display:', contentStyle.display);
            console.log('Content height:', contentStyle.height);
        }
        
        if (grid) {
            const gridStyle = window.getComputedStyle(grid);
            console.log('Grid display:', gridStyle.display);
            console.log('Grid height:', gridStyle.height);
        }
        
        // Check first card
        if (cards.length > 0) {
            const firstCard = cards[0];
            const cardStyle = window.getComputedStyle(firstCard);
            console.log('First card display:', cardStyle.display);
            console.log('First card height:', cardStyle.height);
            console.log('First card width:', cardStyle.width);
        }
        
        document.body.style.overflow = 'hidden';
    } else {
        console.error('seeAllModal not found!');
    }
}

function closeSeeAllModal() {
    const modal = document.getElementById('seeAllModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

window.onclick = function(event) {
    const modal = document.getElementById('seeAllModal');
    if (event.target === modal) {
        closeSeeAllModal();
    }
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeSeeAllModal();
    }
});
