// Table responsive enhancements
document.addEventListener('DOMContentLoaded', function() {
    
    // Add horizontal scroll indicators for tables
    function addScrollIndicators() {
        const tableContainers = document.querySelectorAll('.user-management-tbl-frame, .restricted-accounts-tbl');
        
        tableContainers.forEach(container => {
            const table = container.querySelector('table');
            if (!table) return;
            
            // Check if table is wider than container
            if (table.scrollWidth > container.clientWidth) {
                container.classList.add('scrollable-table');
                
                // Add scroll indicator
                if (!container.querySelector('.scroll-indicator')) {
                    const indicator = document.createElement('div');
                    indicator.className = 'scroll-indicator';
                    indicator.innerHTML = '← Scroll to see more →';
                    container.appendChild(indicator);
                }
            }
        });
    }
    
    // Mobile table optimization
    function optimizeTableForMobile() {
        if (window.innerWidth <= 768) {
            const tables = document.querySelectorAll('.user-management-tbl table, .restricted-accounts-tbl table');
            
            tables.forEach(table => {
                // Add mobile-optimized class
                table.classList.add('mobile-table');
                
                // Wrap long text in cells
                const cells = table.querySelectorAll('td');
                cells.forEach(cell => {
                    if (cell.textContent.length > 20) {
                        cell.style.whiteSpace = 'normal';
                        cell.style.wordBreak = 'break-word';
                    }
                });
            });
        }
    }
    
    // Add touch scroll for mobile
    function addTouchScroll() {
        const scrollableElements = document.querySelectorAll('.user-management-tbl-frame, .restricted-accounts-tbl');
        
        scrollableElements.forEach(element => {
            let isScrolling = false;
            let startX = 0;
            let scrollLeft = 0;
            
            element.addEventListener('touchstart', (e) => {
                isScrolling = true;
                startX = e.touches[0].pageX - element.offsetLeft;
                scrollLeft = element.scrollLeft;
            });
            
            element.addEventListener('touchmove', (e) => {
                if (!isScrolling) return;
                e.preventDefault();
                const x = e.touches[0].pageX - element.offsetLeft;
                const walk = (x - startX) * 2;
                element.scrollLeft = scrollLeft - walk;
            });
            
            element.addEventListener('touchend', () => {
                isScrolling = false;
            });
        });
    }
    
    // Initialize functions
    addScrollIndicators();
    optimizeTableForMobile();
    addTouchScroll();
    
    // Re-run on window resize
    window.addEventListener('resize', function() {
        setTimeout(() => {
            addScrollIndicators();
            optimizeTableForMobile();
        }, 100);
    });
    
    // Add CSS for scroll indicator
    const style = document.createElement('style');
    style.textContent = `
        .scrollable-table {
            position: relative;
        }
        
        .scroll-indicator {
            position: absolute;
            bottom: 5px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            pointer-events: none;
            z-index: 10;
        }
        
        .mobile-table {
            font-size: 12px !important;
        }
        
        @media screen and (max-width: 480px) {
            .scroll-indicator {
                font-size: 10px;
                padding: 3px 8px;
            }
        }
    `;
    document.head.appendChild(style);
});