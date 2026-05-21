let reportMissingMap, reportMissingMarker;

function getLocation(){
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}


//Send location to FLASK BACKEND
function sendLocation(position){
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    fetch('/submit-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch((error) => {
        console.error('Error:', error);
        alert("Error saving location");
    });
}

function showPosition(position){
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    // Update hidden form fields
    const latField = document.getElementById('latitude');
    const lngField = document.getElementById('longitude');
    const latField2 = document.getElementById('latitude2');
    const lngField2 = document.getElementById('longitude2');
    
    if (latField) latField.value = latitude;
    if (lngField) lngField.value = longitude;
    if (latField2) latField2.value = latitude;
    if (lngField2) lngField2.value = longitude;

    // Get place name from coordinates
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: { lat: latitude, lng: longitude } }, function(results, status) {
        if (status === 'OK' && results[0]) {
            const locationName = results[0].formatted_address;
            document.getElementById("location").innerHTML = `Current Location:<br>${results[0].formatted_address}`;
            
            if (reportMissingMarker) reportMissingMarker.setMap(null);
            reportMissingMarker = new google.maps.Marker({
                position: { lat: latitude, lng: longitude },
                map: reportMissingMap,
                title: "Current Location",
                label: {
                    text: locationName,
                    color: "black",
                    fontWeight: "bold",
                    fontSize: "10px"
                }
            });
        } else {
            document.getElementById("location").innerHTML = `Latitude: ${latitude} <br> Longitude: ${longitude}`;
            
            if (reportMissingMarker) reportMissingMarker.setMap(null);
            reportMissingMarker = new google.maps.Marker({
                position: { lat: latitude, lng: longitude },
                map: reportMissingMap,
                title: "Current Location",
                label: {
                    text: "Location",
                    color: "black",
                    fontWeight: "bold",
                    fontSize: "12px"
                }
            });
        }
    });

    // Center map on user location and zoom in
    reportMissingMap.setCenter({ lat: latitude, lng: longitude});
    reportMissingMap.setZoom(15);
}

function showError(error){
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("User denied the request for geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
    }
}

function searchLocation() {
    const searchInput = document.getElementById('customLocation').value.trim();
    if (!searchInput) return;

    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: searchInput }, function(results, status) {
        if (status === 'OK') {
            const location = results[0].geometry.location;
            const lat = location.lat();
            const lng = location.lng();

            // Update hidden form fields
            const latField = document.getElementById('latitude');
            const lngField = document.getElementById('longitude');
            const latField2 = document.getElementById('latitude2');
            const lngField2 = document.getElementById('longitude2');
            
            if (latField) latField.value = lat;
            if (lngField) lngField.value = lng;
            if (latField2) latField2.value = lat;
            if (lngField2) lngField2.value = lng;

            reportMissingMap.setCenter({ lat: lat, lng: lng });
            reportMissingMap.setZoom(15);

            if (reportMissingMarker) reportMissingMarker.setMap(null);


            const locationName = results[0].formatted_address;
            document.getElementById("location").innerHTML = `Searched Location:<br>${results[0].formatted_address}`;
            
            if (reportMissingMarker) reportMissingMarker.setMap(null);
            reportMissingMarker = new google.maps.Marker({
                position: { lat: lat, lng: lng },
                map: reportMissingMap,
                title: "Searched Location",
                label: {
                    text: locationName,
                    color: "black",
                    fontWeight: "bold",
                    fontSize: "10px"
                }
            });
        } else {
            alert('Location not found');
        }
    });
}

function initMap() {
    // Called by Google Maps API - do nothing here
}

function initPopupMap() {
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.error('Map element not found');
        return;
    }
    
    if (!window.google || !window.google.maps) {
        console.error('Google Maps not loaded yet');
        setTimeout(initPopupMap, 500);
        return;
    }
    
    
    // Clear any existing map
    mapElement.innerHTML = '';
    
    reportMissingMap = new google.maps.Map(mapElement, {
        center: { lat: 14.5995, lng: 120.9842 },
        zoom: 10,
        styles: [
            {"featureType": "all", "elementType": "geometry.fill", "stylers": [{"weight": "2.00"}]},
            {"featureType": "all", "elementType": "geometry.stroke", "stylers": [{"color": "#9c9c9c"}]},
            {"featureType": "all", "elementType": "labels.text", "stylers": [{"visibility": "on"}]},
            {"featureType": "landscape", "elementType": "all", "stylers": [{"color": "#f2f2f2"}]},
            {"featureType": "landscape", "elementType": "geometry.fill", "stylers": [{"color": "#ffffff"}]},
            {"featureType": "landscape.man_made", "elementType": "geometry.fill", "stylers": [{"color": "#ffffff"}]},
            {"featureType": "poi", "elementType": "all", "stylers": [{"visibility": "off"}]},
            {"featureType": "road", "elementType": "all", "stylers": [{"saturation": -100}, {"lightness": 45}]},
            {"featureType": "road", "elementType": "geometry.fill", "stylers": [{"color": "#eeeeee"}]},
            {"featureType": "road", "elementType": "labels.text.fill", "stylers": [{"color": "#7b7b7b"}]},
            {"featureType": "road", "elementType": "labels.text.stroke", "stylers": [{"color": "#ffffff"}]},
            {"featureType": "road.highway", "elementType": "all", "stylers": [{"visibility": "simplified"}]},
            {"featureType": "road.arterial", "elementType": "labels.icon", "stylers": [{"visibility": "off"}]},
            {"featureType": "transit", "elementType": "all", "stylers": [{"visibility": "off"}]},
            {"featureType": "water", "elementType": "all", "stylers": [{"color": "#46bcec"}, {"visibility": "on"}]},
            {"featureType": "water", "elementType": "geometry.fill", "stylers": [{"color": "#c8d7d4"}]},
            {"featureType": "water", "elementType": "labels.text.fill", "stylers": [{"color": "#070707"}]},
            {"featureType": "water", "elementType": "labels.text.stroke", "stylers": [{"color": "#ffffff"}]}
        ],
        disableDefaultUI: true,
        zoomControl: true,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false
    });

    reportMissingMap.addListener('click', function(event) {
        const clickedLat = event.latLng.lat();
        const clickedLng = event.latLng.lng();
        
        // Update hidden form fields
        const latField = document.getElementById('latitude');
        const lngField = document.getElementById('longitude');
        const latField2 = document.getElementById('latitude2');
        const lngField2 = document.getElementById('longitude2');
        
        if (latField) latField.value = clickedLat;
        if (lngField) lngField.value = clickedLng;
        if (latField2) latField2.value = clickedLat;
        if (lngField2) lngField2.value = clickedLng;
        
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ location: { lat: clickedLat, lng: clickedLng } }, function(results, status) {
            if (status === 'OK' && results[0]) {
                const locationName = results[0].formatted_address;
                document.getElementById("location").innerHTML = `Selected Location:<br>${results[0].formatted_address}`;
                
                if (reportMissingMarker) reportMissingMarker.setMap(null);
                reportMissingMarker = new google.maps.Marker({
                    position: { lat: clickedLat, lng: clickedLng },
                    map: reportMissingMap,
                    title: "Selected Location",
                    label: {
                        text: locationName,
                        color: "black",
                        fontWeight: "bold",
                        fontSize: "10px"
                    }
                });
            } else {
                document.getElementById("location").innerHTML = `Selected Location:<br>Latitude: ${clickedLat}<br>Longitude: ${clickedLng}`;
                
                if (reportMissingMarker) reportMissingMarker.setMap(null);
                reportMissingMarker = new google.maps.Marker({
                    position: { lat: clickedLat, lng: clickedLng },
                    map: reportMissingMap,
                    title: "Selected Location",
                    label: {
                        text: "Location",
                        color: "black",
                        fontWeight: "bold",
                        fontSize: "12px"
                    }
                });
            }
        });
    });
}



// Handle location radio button changes
document.addEventListener('DOMContentLoaded', function() {
    const myLocationRadio = document.getElementById('my-location-radio');
    const customLocationRadio = document.getElementById('custom-location-radio');
    const customLocationInput = document.getElementById('customLocation');
    const searchBtn = document.getElementById('searchBtn');
    
    if (myLocationRadio) {
        myLocationRadio.addEventListener('change', function() {
            if (this.checked) {
                customLocationInput.disabled = true;
                searchBtn.disabled = true;
                getLocation();
            }
        });
    }
    
    if (customLocationRadio) {
        customLocationRadio.addEventListener('change', function() {
            if (this.checked) {
                customLocationInput.disabled = false;
                searchBtn.disabled = false;
            }
        });
    }
});
