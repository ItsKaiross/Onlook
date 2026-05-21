var modal_help_locate_no_acc_public = document.getElementById('help-locate-no-acc-popup');
var add_btn_no_acc = document.getElementById('help_locate_no_acc_btn');

var background = document.getElementById('bg-black');

// Function to open help locate no-account popup
function openHelpLocateNoAccPopup() {
    // Set case_id dynamically
    let caseId = 0;
    if (window.currentCaseId) {
        caseId = window.currentCaseId;
    }
    
    const caseIdInput = document.getElementById('help-locate-case-id');
    const form = document.getElementById('help-locate-no-acc-form');
    if (caseIdInput) {
        caseIdInput.value = caseId;
        console.log('Set case_id to:', caseId);
    }
    if (form) {
        form.action = `/help-locate-additional-report/${caseId}`;
        console.log('Set form action to:', form.action);
    }
    modal_help_locate_no_acc_public.style.visibility = 'visible'
    modal_help_locate_no_acc_public.style.top = "50%"
    modal_help_locate_no_acc_public.style.transform = "translate(-50%, -50%)"
    modal_help_locate_no_acc_public.style.transition = ".5s"
    modal_help_locate_no_acc_public.style.pointerEvents = "auto"
    modal_help_locate_no_acc_public.style.zIndex = "9999"
    
    // Set current date and time immediately
    setCurrentDateTime();
    
    // Disable body scroll and interaction
    document.body.style.overflow = 'hidden'
    document.body.classList.add('popup-open')
    background.style.display = "block"
    background.style.pointerEvents = "none"
    

    
    // Don't initialize map here - it will be initialized when navigating to step 2
    
    // Create overlay and blur the first popup
    var firstPopup = document.getElementById('reported-missing-waccount-popup');
    if (firstPopup) {
        firstPopup.style.filter = 'blur(3px)';
        
        var overlay = document.createElement('div');
        overlay.id = 'popup-overlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.zIndex = '9998';
        overlay.style.pointerEvents = 'none';
        document.body.appendChild(overlay);
    }
}

// Bind both buttons to the same function
if (add_btn_no_acc) {
    add_btn_no_acc.onclick = openHelpLocateNoAccPopup;
}

// Also bind the button in the popup using event delegation
document.addEventListener('click', function(e) {
    if (e.target && e.target.id === 'help_locate_no_acc_btn') {
        e.preventDefault();
        openHelpLocateNoAccPopup();
    }
});


//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//

var close_btn = document.getElementsByClassName('help-locate-no-acc-close')[0];

close_btn.onclick = function(){
    modal_help_locate_no_acc_public.style.visibility = "hidden";
    background.style.display = "none";
    modal_help_locate_no_acc_public.style.top = "-10%"
    modal_help_locate_no_acc_public.style.transform = "translate(-50%, -20%)"
    modal_help_locate_no_acc_public.style.transition = ".5s"
    background.style.transition = ".5s"
    
    // Restore body scroll
    document.body.style.overflow = 'auto'
    document.body.classList.remove('popup-open')
    
    // Remove blur
    var firstPopup = document.getElementById('reported-missing-popup');
    if (firstPopup) {
        firstPopup.style.filter = 'none';
    }
    
    var overlay = document.getElementById('popup-overlay');
    if (overlay) {
        overlay.remove();
    }
}




// Additional event handler for help locate close button
document.addEventListener('DOMContentLoaded', function() {
    const closeBtn = document.querySelector('.help-locate-no-acc-close2');
    const modal = document.getElementById('help-locate-no-acc-popup');
    const bg = document.getElementById('bg-black');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (modal) {
                modal.style.visibility = 'hidden';
                modal.style.top = '-10%';
                modal.style.transform = 'translate(-50%, -20%)';
                modal.style.transition = '.5s';
            }
            if (bg) {
                bg.style.display = 'none';
                bg.style.transition = '.5s';
            }
            
            // Restore body scroll
            document.body.style.overflow = 'auto'
            document.body.classList.remove('popup-open')
            
            // Remove blur
            var firstPopup = document.getElementById('reported-missing-popup');
            if (firstPopup) {
                firstPopup.style.filter = 'none';
            }
            
            var overlay = document.getElementById('popup-overlay');
            if (overlay) {
                overlay.remove();
            }
        });
    }
});

function initHelpLocateMap() {
    const mapElement = document.getElementById('helpMap');
    if (!mapElement || !window.googleMapsLoaded || typeof google === 'undefined') {
        setTimeout(initHelpLocateMap, 200);
        return;
    }
    
    try {
        window.helpLocateMap = new google.maps.Map(mapElement, {
            center: { lat: 14.2691, lng: 121.1074 },
            zoom: 13,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        });
        
        // Trigger resize after initialization
        setTimeout(() => {
            google.maps.event.trigger(window.helpLocateMap, 'resize');
            window.helpLocateMap.setCenter({ lat: 14.2691, lng: 121.1074 });
        }, 100);
        
        window.helpLocateMap.addListener('click', function(event) {
            if (window.helpLocateMarker) window.helpLocateMarker.setMap(null);
            window.helpLocateMarker = new google.maps.Marker({
                position: event.latLng,
                map: window.helpLocateMap
            });
            document.getElementById('helpLatitude').value = event.latLng.lat();
            document.getElementById('helpLongitude').value = event.latLng.lng();
            updateHelpLocationDisplay(event.latLng);
        });
        

    } catch (error) {
        console.error('Error in initHelpLocateMap:', error);
        setTimeout(initHelpLocateMap, 500);
    }
}

function initHelpLocateMapNoAcc() {
    const mapElement = document.getElementById('helpMapNoAcc');
    if (!mapElement || !window.googleMapsLoaded || typeof google === 'undefined') {
        setTimeout(initHelpLocateMapNoAcc, 200);
        return;
    }
    
    try {
        window.helpLocateMapNoAcc = new google.maps.Map(mapElement, {
            center: { lat: 14.2691, lng: 121.1074 },
            zoom: 13,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        });
        
        // Trigger resize after initialization
        setTimeout(() => {
            google.maps.event.trigger(window.helpLocateMapNoAcc, 'resize');
            window.helpLocateMapNoAcc.setCenter({ lat: 14.2691, lng: 121.1074 });
        }, 100);
        
        window.helpLocateMapNoAcc.addListener('click', function(event) {
            if (window.helpLocateMarkerNoAcc) window.helpLocateMarkerNoAcc.setMap(null);
            window.helpLocateMarkerNoAcc = new google.maps.Marker({
                position: event.latLng,
                map: window.helpLocateMapNoAcc
            });
            document.getElementById('helpLatitude').value = event.latLng.lat();
            document.getElementById('helpLongitude').value = event.latLng.lng();
            updateHelpLocationDisplayNoAcc(event.latLng);
        });
        

    } catch (error) {
        console.error('Error in initHelpLocateMapNoAcc:', error);
        setTimeout(initHelpLocateMapNoAcc, 500);
    }
}

// Update location display
function updateHelpLocationDisplay(latLng) {
    const geocoder = new google.maps.Geocoder();
    const location = { lat: parseFloat(latLng.lat()), lng: parseFloat(latLng.lng()) };
    geocoder.geocode({ location: location }, function(results, status) {
        if (status === 'OK' && results[0]) {
            const locationText = document.getElementById('helpLocationText');
            if (locationText) {
                locationText.innerHTML = `Selected Location:<br>${results[0].formatted_address}`;
                locationText.style.display = 'block';
            }
        }
    });
}

function updateHelpLocationDisplayNoAcc(latLng) {
    const geocoder = new google.maps.Geocoder();
    const location = { lat: parseFloat(latLng.lat()), lng: parseFloat(latLng.lng()) };
    geocoder.geocode({ location: location }, function(results, status) {
        if (status === 'OK' && results[0]) {
            const locationText = document.getElementById('helpLocationTextNoAcc');
            if (locationText) {
                locationText.innerHTML = `Selected Location:<br>${results[0].formatted_address}`;
                locationText.style.display = 'block';
            }
        }
    });
}

// Function to update case_id for help locate popup
function setHelpLocateCaseId(caseId) {
    console.log('setHelpLocateCaseId called with:', caseId);
    const caseIdInput = document.getElementById('help-locate-case-id');
    const form = document.getElementById('help-locate-no-acc-form');
    if (caseIdInput) {
        caseIdInput.value = caseId;
        console.log('Updated case_id input to:', caseId);
    }
    if (form) {
        form.action = `/help-locate-additional-report/${caseId}`;
        console.log('Updated form action to:', form.action);
    }
}

// Get user's current location for help locate popup
function getHelpLocateLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            document.getElementById('helpLatitude').value = lat;
            document.getElementById('helpLongitude').value = lng;
            
            // Check which map is active
            if (window.helpLocateMap) {
                window.helpLocateMap.setCenter({ lat: lat, lng: lng });
                window.helpLocateMap.setZoom(15);
                
                if (window.helpLocateMarker) {
                    window.helpLocateMarker.setMap(null);
                }
                
                window.helpLocateMarker = new google.maps.Marker({
                    position: { lat: lat, lng: lng },
                    map: window.helpLocateMap
                });
                
                updateHelpLocationDisplay({ lat: () => lat, lng: () => lng });
            }
            
            if (window.helpLocateMapNoAcc) {
                window.helpLocateMapNoAcc.setCenter({ lat: lat, lng: lng });
                window.helpLocateMapNoAcc.setZoom(15);
                
                if (window.helpLocateMarkerNoAcc) {
                    window.helpLocateMarkerNoAcc.setMap(null);
                }
                
                window.helpLocateMarkerNoAcc = new google.maps.Marker({
                    position: { lat: lat, lng: lng },
                    map: window.helpLocateMapNoAcc
                });
                
                updateHelpLocationDisplayNoAcc({ lat: () => lat, lng: () => lng });
            }
        }, function(error) {
            console.error('Geolocation error:', error);
            alert('Unable to get your location. Please use custom location instead.');
        });
    } else {
        alert('Geolocation is not supported by this browser.');
    }
}

// Search custom location for help locate popup
function searchHelpLocation() {
    const address = document.getElementById('helpCustomLocation').value.trim();
    if (!address) {
        alert('Please enter a location to search.');
        return;
    }
    
    if (typeof google !== 'undefined' && google.maps && window.helpLocateMap) {
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: address }, function(results, status) {
            if (status === 'OK') {
                const location = results[0].geometry.location;
                const lat = location.lat();
                const lng = location.lng();
                
                document.getElementById('helpLatitude').value = lat;
                document.getElementById('helpLongitude').value = lng;
                
                window.helpLocateMap.setCenter({ lat: lat, lng: lng });
                window.helpLocateMap.setZoom(15);
                
                if (window.helpLocateMarker) {
                    window.helpLocateMarker.setMap(null);
                }
                
                document.getElementById('helpLocationText').innerHTML = `Searched Location:<br>${results[0].formatted_address}`;
                document.getElementById('helpLocationText').style.display = 'block';
                
                window.helpLocateMarker = new google.maps.Marker({
                    position: { lat: lat, lng: lng },
                    map: window.helpLocateMap,
                    title: 'Searched Location',
                    draggable: true
                });
                
                window.helpLocateMarker.addListener('dragend', function(event) {
                    document.getElementById('helpLatitude').value = event.latLng.lat();
                    document.getElementById('helpLongitude').value = event.latLng.lng();
                    updateHelpLocationDisplay(event.latLng);
                });
            } else {
                alert('Location not found: ' + status);
            }
        });
    } else {
        alert('Google Maps is not loaded yet. Please try again in a moment.');
    }
}

// Search custom location for help locate no-acc popup
function searchHelpLocationNoAcc() {
    const address = document.getElementById('helpCustomLocationNoAcc').value.trim();
    if (!address) {
        alert('Please enter a location to search.');
        return;
    }
    
    if (typeof google !== 'undefined' && google.maps && window.helpLocateMapNoAcc) {
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: address }, function(results, status) {
            if (status === 'OK') {
                const location = results[0].geometry.location;
                const lat = location.lat();
                const lng = location.lng();
                
                document.getElementById('helpLatitude').value = lat;
                document.getElementById('helpLongitude').value = lng;
                
                window.helpLocateMapNoAcc.setCenter({ lat: lat, lng: lng });
                window.helpLocateMapNoAcc.setZoom(15);
                
                if (window.helpLocateMarkerNoAcc) {
                    window.helpLocateMarkerNoAcc.setMap(null);
                }
                
                document.getElementById('helpLocationTextNoAcc').innerHTML = `Searched Location:<br>${results[0].formatted_address}`;
                document.getElementById('helpLocationTextNoAcc').style.display = 'block';
                
                window.helpLocateMarkerNoAcc = new google.maps.Marker({
                    position: { lat: lat, lng: lng },
                    map: window.helpLocateMapNoAcc,
                    title: 'Searched Location',
                    draggable: true
                });
                
                window.helpLocateMarkerNoAcc.addListener('dragend', function(event) {
                    document.getElementById('helpLatitude').value = event.latLng.lat();
                    document.getElementById('helpLongitude').value = event.latLng.lng();
                    updateHelpLocationDisplayNoAcc(event.latLng);
                });
            } else {
                alert('Location not found: ' + status);
            }
        });
    } else {
        alert('Google Maps is not loaded yet. Please try again in a moment.');
    }
}

// Help Locate image upload functions
function previewHelpLocateImage() {
    const fileInput = document.getElementById('help_upload_last_seen');
    const preview = document.getElementById('help_last_seen_preview');
    const viewBtn = document.getElementById('help_view_last_seen_btn');
    
    preview.innerHTML = '';
    
    if (fileInput.files.length > 0) {
        viewBtn.style.display = 'block';
        viewBtn.textContent = 'View Image (1)';
        
        const file = fileInput.files[0];
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item';
        fileDiv.style.cssText = 'margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: inline-block; cursor: pointer;';
        fileDiv.onclick = () => openFileModal(file);

        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.cssText = 'width: 100px; height: 100px; object-fit: cover; border-radius: 5px;';
        fileDiv.appendChild(img);

        const fileName = document.createElement('p');
        fileName.textContent = file.name;
        fileName.style.cssText = 'margin: 5px 0; font-size: 12px; text-align: center;';
        fileDiv.appendChild(fileName);

        preview.appendChild(fileDiv);
    } else {
        viewBtn.style.display = 'none';
    }
}

function toggleHelpLocatePreview() {
    const preview = document.getElementById('help_last_seen_preview');
    const btn = document.getElementById('help_view_last_seen_btn');
    
    if (preview.style.display === 'none') {
        preview.style.display = 'block';
        btn.textContent = btn.textContent.replace('View', 'Hide');
    } else {
        preview.style.display = 'none';
        btn.textContent = btn.textContent.replace('Hide', 'View');
    }
}

function openFileModal(file) {
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; display: flex; align-items: center; justify-content: center;';
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };

    const closeBtn = document.createElement('div');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = 'position: absolute; top: 20px; right: 30px; color: white; font-size: 40px; cursor: pointer; z-index: 10001;';
    closeBtn.onclick = () => modal.remove();
    modal.appendChild(closeBtn);

    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.style.cssText = 'max-width: 90%; max-height: 90%; border-radius: 10px;';
    modal.appendChild(img);

    // Add escape key listener
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);

    document.body.appendChild(modal);
}

// Function to set current date and time
function setCurrentDateTime() {
    var now = new Date();
    var timeField = document.getElementById('helpTimeSightingNoAcc');
    var dateField = document.getElementById('helpDateSightingNoAcc');
    
    if (timeField) {
        timeField.value = now.toTimeString().slice(0, 5);
    }
    if (dateField) {
        dateField.value = now.toISOString().slice(0, 10);
    }
}

