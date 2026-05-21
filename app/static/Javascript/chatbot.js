// Chatbot functionality
document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('chatbot-toggle');
    const window = document.getElementById('chatbot-window');
    const close = document.getElementById('chatbot-close');
    const input = document.getElementById('chatbot-input');
    const send = document.getElementById('chatbot-send');
    const messages = document.getElementById('chatbot-messages');
    
    // Check if all elements exist
    if (!toggle || !window || !close || !input || !send || !messages) {
        console.error('Chatbot elements not found');
        return;
    }
    
    // Toggle chatbot
    toggle.addEventListener('click', () => {
        const isHidden = window.style.display === 'none' || window.style.display === '' || !window.style.display;
        if (isHidden) {
            window.style.display = 'flex';
            // Clear existing messages and show initial buttons
            messages.innerHTML = '';
            showInitialButtons();
        } else {
            window.style.display = 'none';
        }
    });
    
    // Close chatbot
    close.addEventListener('click', () => {
        window.style.display = 'none';
    });
    
    // Send message
    function sendMessage() {
        const message = input.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, 'user');
        input.value = '';
        
        // Generate bot response
        setTimeout(() => {
            const response = getBotResponse(message);
            if (response) addMessage(response, 'bot');
        }, 500);
    }
    
    // Add message to chat
    function addMessage(text, sender, buttons = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = sender + '-message';
        
        if (text) {
            // Handle line breaks in text
            const lines = text.split('\n');
            lines.forEach((line, index) => {
                if (index > 0) {
                    messageDiv.appendChild(document.createElement('br'));
                }
                const textNode = document.createTextNode(line);
                messageDiv.appendChild(textNode);
            });
        }
        
        if (buttons) {
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'chatbot-button-container';
            buttons.forEach(btn => {
                const button = document.createElement('button');
                button.textContent = btn.text;
                button.className = 'chatbot-button';
                button.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    btn.action();
                };
                buttonContainer.appendChild(button);
            });
            messageDiv.appendChild(buttonContainer);
        }
        
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }
    
    // Show initial greeting buttons
    function showInitialButtons() {
        addMessage('Welcome to OnLook! How can I help you today?', 'bot', [
            { text: '👋 Say Hello', action: function() {
                addMessage('Hello!', 'user');
                setTimeout(() => {
                    const response = getBotResponse('hello');
                    if (response) addMessage(response, 'bot');
                }, 100);
            }},
            { text: '📝 Report Missing Person', action: function() {
                addMessage('I want to report a missing person', 'user');
                openReportPopup();
            }},
            { text: '👁️ Report Sighting', action: function() {
                addMessage('I want to report a sighting', 'user');
                showMissingPersonsList();
            }},
            { text: '📞 Contact Us', action: function() {
                addMessage('I need contact information', 'user');
                setTimeout(() => {
                    addMessage('Here are our contact details:\n\n📞 Phone: 09173831684\n🏢 Hotline: 523 4544\n📧 Email: onlook2025@gmail.com\n\nWe\'re here to help 24/7!', 'bot');
                }, 100);
            }}
        ]);
    }
    
    // Bot responses
    function getBotResponse(message) {
        const msg = message.toLowerCase();
        
        // Greetings
        if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey')) {
            setTimeout(() => {
                addMessage('What can I help you with?', 'bot', [
                    { text: '📝 Report Missing Person', action: function() {
                        addMessage('I want to report a missing person', 'user');
                        openReportPopup();
                    }},
                    { text: '👁️ Report Sighting', action: function() {
                        addMessage('I want to report a sighting', 'user');
                        showMissingPersonsList();
                    }},
                    { text: '📞 Contact Us', action: function() {
                        addMessage('I need contact information', 'user');
                        addMessage('Here are our contact details:\n\n📞 Phone: 09173831684\n🏢 Hotline: 523 4544\n📧 Email: onlook2025@gmail.com\n\nWe\'re here to help 24/7!', 'bot');
                    }}
                ]);
            }, 600);
            return "Hello! I'm here to help you with OnLook.";
        }
        
        // Report missing person
        if (msg.includes('report') && (msg.includes('missing') || msg.includes('person'))) {
            openReportPopup();
            return 'Opening report form for you...';
        }
        
        // Report sighting
        if (msg.includes('report') && msg.includes('sighting')) {
            showMissingPersonsList();
            return 'Let me show you the missing persons list...';
        }
        
        // Default helpful response
        setTimeout(() => {
            addMessage('Choose what you need help with:', 'bot', [
                { text: '📝 Report Missing Person', action: function() {
                    addMessage('I want to report a missing person', 'user');
                    openReportPopup();
                }},
                { text: '👁️ Report Sighting', action: function() {
                    addMessage('I want to report a sighting', 'user');
                    showMissingPersonsList();
                }},
                { text: '📞 Contact Us', action: function() {
                    addMessage('I need contact information', 'user');
                    addMessage('Here are our contact details:\n\n📞 Phone: 09173831684\n🏢 Hotline: 523 4544\n📧 Email: onlook2025@gmail.com\n\nWe\'re here to help 24/7!', 'bot');
                }}
            ]);
        }, 600);
        return 'I can help you with several things:';
    }
    
    // Open existing report popup
    function openReportPopup() {
        // Try to find and click the existing report missing button
        const reportBtn = document.querySelector('.report_missing_btn');
        if (reportBtn) {
            reportBtn.click();
            return;
        }
        
        // Try to show the popup directly
        const popup = document.getElementById('report-missing-popup');
        if (popup) {
            popup.style.display = 'flex';
            document.getElementById('bg-black').style.display = 'block';
            return;
        }
        
        // Fallback - redirect to report page
        window.location.href = '/report-missing';
    }
    
    // Show missing persons list for sighting reports
    function showMissingPersonsList() {
        const missingPersons = document.querySelectorAll('.picture_card');
        const buttons = [];
        
        missingPersons.forEach((card, index) => {
            // Try multiple selectors to find the person's name
            const nameElement = card.querySelector('.person-name') || 
                               card.querySelector('a') || 
                               card.querySelector('.reported_missing_person_waccount_btn a') ||
                               card.querySelector('.reported_missing_person_info a');
            
            let name = 'Unknown Person';
            if (nameElement) {
                name = nameElement.textContent.trim();
            }
            
            // Skip if no valid name or if it's the "No Missing Persons" placeholder
            if (name && name !== 'No Missing Persons' && name !== 'Unknown Person' && name.length > 0) {
                const personId = card.getAttribute('data-person-id');
                buttons.push({
                    text: `👤 ${name}`,
                    action: function() {
                        addMessage(`I want to report a sighting of ${name}`, 'user');
                        // Store selected person info for the help locate popup
                        window.selectedPersonForSighting = {
                            id: personId,
                            name: name
                        };
                        openHelpLocatePopup();
                    }
                });
            }
        });
        
        if (buttons.length === 0) {
            addMessage('No missing persons available to report sightings for at the moment. Please check back later or contact us directly.', 'bot');
        } else {
            setTimeout(() => {
                addMessage('Select the missing person you want to report a sighting for:', 'bot', buttons);
            }, 100);
        }
    }
    
    // Open help locate popup
    function openHelpLocatePopup() {
        // Try multiple selectors for help locate popup
        const popupSelectors = [
            '#help-locate-no-acc-popup',
            '.help-locate-no-acc-modal',
            '#help-locate-popup',
            '.help-locate-modal'
        ];
        
        let popupOpened = false;
        
        for (const selector of popupSelectors) {
            const popup = document.querySelector(selector);
            if (popup) {
                // Show the popup
                popup.style.display = 'flex';
                popup.style.visibility = 'visible';
                popup.style.position = 'fixed';
                popup.style.top = '50%';
                popup.style.left = '50%';
                popup.style.transform = 'translate(-50%, -50%)';
                popup.style.zIndex = '10000';
                popup.style.justifyContent = 'center';
                popup.style.alignItems = 'center';
                
                // Show background overlay
                const bg = document.getElementById('bg-black');
                if (bg) {
                    bg.style.display = 'block';
                    bg.style.position = 'fixed';
                    bg.style.top = '0';
                    bg.style.left = '0';
                    bg.style.width = '100%';
                    bg.style.height = '100%';
                    bg.style.zIndex = '9999';
                }
                
                // Auto-fill current date and time
                setTimeout(() => {
                    fillCurrentDateTime(popup);
                }, 100);
                
                popupOpened = true;
                break;
            }
        }
        
        // If popup wasn't opened directly, try clicking help locate buttons
        if (!popupOpened) {
            const buttonSelectors = [
                '#help_locate_btn',
                '.help_locate_btn',
                '.help_locate_button',
                '.help_locate_reported_frame'
            ];
            
            for (const selector of buttonSelectors) {
                const btn = document.querySelector(selector);
                if (btn) {
                    btn.click();
                    
                    // Auto-fill date and time after clicking button
                    setTimeout(() => {
                        fillCurrentDateTime();
                    }, 500);
                    
                    popupOpened = true;
                    break;
                }
            }
        }
        
        // If still no popup opened, show error message
        if (!popupOpened) {
            addMessage('Sorry, I couldn\'t open the sighting report form. Please try clicking on a missing person card directly or contact us for assistance.', 'bot');
        }
    }
    
    // Helper function to fill current date and time
    function fillCurrentDateTime(container = document) {
        const now = new Date();
        const today = now.toISOString().split('T')[0];
        const currentTime = now.toTimeString().slice(0, 5);
        
        // Try multiple selectors for date and time inputs
        const dateSelectors = ['#helpDateSighting', '[name="DateSighting"]', 'input[type="date"]'];
        const timeSelectors = ['#helpTimeSighting', '[name="TimeSighting"]', 'input[type="time"]'];
        
        dateSelectors.forEach(selector => {
            const dateInput = container.querySelector(selector);
            if (dateInput && !dateInput.value) {
                dateInput.value = today;
            }
        });
        
        timeSelectors.forEach(selector => {
            const timeInput = container.querySelector(selector);
            if (timeInput && !timeInput.value) {
                timeInput.value = currentTime;
            }
        });
    }
    
    // Event listeners
    send.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});