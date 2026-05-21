// Police Dashboard JavaScript Functions

// Initialize police dashboard map
function initPoliceDashboardMap() {
    const mapElement = document.getElementById('police-dashboard-map');
    if (!mapElement) return;
    
    // Center map on whole Laguna province
    const map = new google.maps.Map(mapElement, {
        zoom: 10,
        center: { lat: 14.2691, lng: 121.4577 }
    });
    
    // Location data from backend (will be set by the HTML template)
    const locations = window.dashboardLocations || [];
    
    // Add markers for each report location
    locations.forEach(function(location) {
        let pinColor = 'orange';
        let statusText = 'Pending';
        
        if (location.status && location.status.toLowerCase() === 'approved') {
            pinColor = 'green';
            statusText = 'Approved';
        }
        
        const marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.name + ' - ' + statusText,
            icon: {
                url: `https://maps.google.com/mapfiles/ms/icons/${pinColor}-dot.png`,
                scaledSize: new google.maps.Size(32, 32)
            }
        });
        
        const infoWindow = new google.maps.InfoWindow({
            content: `<div><strong>${location.name}</strong><br>Status: ${statusText}</div>`
        });
        
        marker.addListener('click', function() {
            infoWindow.open(map, marker);
        });
    });
}

// Create monthly cases bar chart
function createMonthlyChart() {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    const monthlyData = window.dashboardMonthlyData || { labels: [], data: [] };
    const selectedYear = window.dashboardSelectedYear || new Date().getFullYear();
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(26, 27, 65, 0.9)');
    gradient.addColorStop(1, 'rgba(26, 27, 65, 0.6)');
    
    const hoverGradient = ctx.createLinearGradient(0, 0, 0, 400);
    hoverGradient.addColorStop(0, 'rgba(189, 19, 16, 0.9)');
    hoverGradient.addColorStop(1, 'rgba(189, 19, 16, 0.7)');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthlyData.labels,
            datasets: [{
                label: 'Number of Cases',
                data: monthlyData.data,
                backgroundColor: gradient,
                borderColor: 'transparent',
                borderWidth: 0,
                borderRadius: {
                    topLeft: 12,
                    topRight: 12,
                    bottomLeft: 4,
                    bottomRight: 4
                },
                borderSkipped: false,
                hoverBackgroundColor: hoverGradient,
                hoverBorderColor: 'rgba(189, 19, 16, 0.3)',
                hoverBorderWidth: 3,
                barThickness: 'flex',
                maxBarThickness: 60
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 20,
                    bottom: 10,
                    left: 10,
                    right: 10
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: '#64748b',
                        font: {
                            family: 'SF_MEDIUM',
                            size: 13,
                            weight: '500'
                        },
                        padding: 15
                    },
                    border: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(148, 163, 184, 0.08)',
                        drawBorder: false,
                        lineWidth: 1
                    },
                    ticks: {
                        stepSize: 1,
                        color: '#64748b',
                        font: {
                            family: 'SF_MEDIUM',
                            size: 12,
                            weight: '500'
                        },
                        padding: 15,
                        callback: function(value) {
                            return value === 0 ? '0' : value;
                        }
                    },
                    border: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#f8fafc',
                    bodyColor: '#e2e8f0',
                    borderColor: 'rgba(148, 163, 184, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 12,
                    displayColors: false,
                    padding: 16,
                    titleFont: {
                        family: 'SF_BOLD',
                        size: 15,
                        weight: 'bold'
                    },
                    bodyFont: {
                        family: 'SF_MEDIUM',
                        size: 13,
                        weight: '500'
                    },
                    titleMarginBottom: 8,
                    bodySpacing: 4,
                    usePointStyle: false,
                    callbacks: {
                        title: function(context) {
                            return context[0].label + ' ' + selectedYear;
                        },
                        label: function(context) {
                            const value = context.parsed.y;
                            return `📊 ${value} case${value !== 1 ? 's' : ''} reported`;
                        }
                    },
                    external: function(context) {
                        const tooltip = context.tooltip;
                        if (tooltip.opacity === 0) return;
                        
                        const tooltipEl = document.getElementById('chartjs-tooltip');
                        if (tooltipEl) {
                            tooltipEl.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.25)';
                        }
                    }
                }
            },
            animation: {
                duration: 1200,
                easing: 'easeOutCubic',
                delay: (context) => {
                    return context.dataIndex * 100;
                }
            },
            onHover: (event, activeElements) => {
                event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
            }
        }
    });
}

// Switch between tabs
function switchTab(tabName) {
    // Remove active class from all tabs and content
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to clicked tab and corresponding content
    event.target.classList.add('active');
    document.getElementById(tabName + 'Cases').classList.add('active');
}

// Open case details popup
function openCaseDetails(caseId) {
    fetch(`/police-case-details/${caseId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCaseDetailsPopup(data.case);
            } else {
                alert('Error loading case details');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading case details');
        });
}

function displayCaseDetailsPopup(caseData) {
    const modal = document.getElementById('case-details-modal') || createCaseModal();
    const content = `
        <div class="case-file-view">
            <h3>Case #${caseData.case_id}</h3>
            <div class="case-info">

                <div class="case-title">
                <h1>Case #${caseData.case_id} - ${caseData.full_name || 'Unknown'}</h1>
                </div>

                <div class="info-grid">

                    <div class="name-item">
                    <h1>Name:</h1> 
                    <p>${caseData.full_name || 'N/A'}</p>
                    </div>

                    <div class="age-item">
                    <h1>Age:</h1>
                    <p>${caseData.age || 'N/A'}</p>
                    </div>

                    <div class="gender-item">
                    <h1>Gender:</h1>
                    <p>${caseData.gender || 'N/A'}</p>
                    </div>

                    <div class="status-item">
                    <h1>Status:</h1> 
                    <p>${caseData.case_status || 'N/A'}</p>
                    </div>

                    <div class="priority-item">
                    <h1>Priority:</h1> 
                    <p>${caseData.priority || 'N/A'}</p>
                    </div>

                    <div class="date-seen-item">
                    <h1>Date Last Seen:</h1> 
                    <p>${caseData.date_last_seen || 'N/A'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.getElementById('case-details-content').innerHTML = content;
    modal.style.display = 'block';
}

function createCaseModal() {
    const modal = document.createElement('div');
    modal.id = 'case-details-modal';
    modal.className = 'case-details-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Case Details</h2>
                <span class="close-modal">&times;</span>
            </div>
            <div class="modal-body" id="case-details-content"></div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function closeCaseModal() {
    const modal = document.getElementById('case-details-modal');
    if (modal) modal.style.display = 'none';
}

// Notification functions
function toggleNotifications() {
    const overlay = document.getElementById('notificationOverlay');
    if (overlay.classList.contains('show')) {
        overlay.classList.remove('show');
        setTimeout(() => overlay.style.display = 'none', 300);
    } else {
        overlay.style.display = 'block';
        setTimeout(() => overlay.classList.add('show'), 10);
    }
}

function closeNotifications() {
    const overlay = document.getElementById('notificationOverlay');
    overlay.classList.remove('show');
    setTimeout(() => overlay.style.display = 'none', 300);
}

function markNotificationsRead() {
    fetch('/police-mark-notifications-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(() => {
        const badge = document.querySelector('.notification-badge');
        if (badge) badge.style.display = 'none';
    });
}

function viewReportDetails(reportId) {
    window.location.href = `/police-field-report?case_id=${reportId}`;
}

// Filter by year function
function filterByYear() {
    const selectedYear = document.getElementById('yearFilter').value;
    window.location.href = `/police-dashboard?year=${selectedYear}`;
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize chart
    createMonthlyChart();
    
    // Notification frame click
    const notificationFrame = document.querySelector('._public_notification_frame');
    if (notificationFrame) {
        notificationFrame.addEventListener('click', toggleNotifications);
    }
    
    // Close notification buttons
    const closeNotificationBtns = document.querySelectorAll('.close-notifications');
    closeNotificationBtns.forEach(btn => {
        btn.addEventListener('click', closeNotifications);
    });
    
    // Notification items
    const notificationItems = document.querySelectorAll('.notification-item');
    notificationItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const caseId = this.dataset.caseId;
            markNotificationsRead();
            viewReportDetails(caseId);
            e.stopPropagation();
        });
    });
    
    // Year filter dropdown
    const yearFilter = document.getElementById('yearFilter');
    if (yearFilter) {
        yearFilter.addEventListener('change', filterByYear);
    }
    
    // Tab buttons
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.textContent.toLowerCase().includes('unsolved') ? 'unsolved' : 'solved';
            switchTab(tabName);
        });
    });
    
    // Case cards
    const caseCards = document.querySelectorAll('.case-card');
    caseCards.forEach(card => {
        card.addEventListener('click', function() {
            // Extract case ID from the card content or data attribute
            const caseIdElement = this.querySelector('.case-id');
            if (caseIdElement) {
                const caseId = caseIdElement.textContent.replace('Case #', '');
                openCaseDetails(caseId);
            }
        });
    });
    
    // Modal close button
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('close-modal')) {
            closeCaseModal();
        }
    });
    
    // Close notifications when clicking outside
    document.addEventListener('click', function(event) {
        const overlay = document.getElementById('notificationOverlay');
        const notificationFrame = document.querySelector('._public_notification_frame');
        
        if (overlay && notificationFrame && 
            !overlay.contains(event.target) && 
            !notificationFrame.contains(event.target)) {
            closeNotifications();
        }
    });
});