

// Initialize the map and set default view to Chandigarh, India
var map = L.map('map').setView([30.7333, 76.7794], 13);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Variables to store the markers and coordinates
var startMarker, endMarker, routeLayer;
var startCoords, endCoords;

// Add click event to place start and end markers
map.on('click', function(e) {
    if (!startMarker) {
        // Place start marker
        startMarker = L.marker(e.latlng).addTo(map).bindPopup("Start").openPopup();
        startCoords = e.latlng;
    } else if (!endMarker) {
        // Place end marker
        endMarker = L.marker(e.latlng).addTo(map).bindPopup("End").openPopup();
        endCoords = e.latlng;
        // Enable the 'Find Route' button once both markers are placed
        document.getElementById('findRoute').disabled = false;
    }
});

// Function to send start and end coordinates to the backend and draw the route
document.getElementById('findRoute').addEventListener('click', function() {
    // Check if both start and end coordinates are set
    if (startCoords && endCoords) {
        // Send coordinates to the backend using Fetch API
        fetch('/find_route', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                start: [startCoords.lat, startCoords.lng],
                end: [endCoords.lat, endCoords.lng]
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);  // Debugging to see if we receive data from the backend
            if (data.error) {
                alert(data.error);
            } else {
                // Remove existing route layer if it exists
                if (routeLayer) {
                    map.removeLayer(routeLayer);
                }

                // Draw the new route on the map
                routeLayer = L.polyline(data.path, {color: 'blue'}).addTo(map);
                map.fitBounds(routeLayer.getBounds());

                // Show route distance found alert
                // alert(`Route Length: ${data.length.toFixed(2)} meters`);
                alert(`Optimal Route Found.`);
            }
        })
        .catch(error => console.error('Error:', error));
    } else {
        alert('Please select both start and end points.');
    }
});

// Reset map (clear markers and route)
document.getElementById('resetMap').addEventListener('click', function() {
    // Remove start marker if it exists
    if (startMarker) {
        map.removeLayer(startMarker);
        startMarker = null;
    }

    // Remove end marker if it exists
    if (endMarker) {
        map.removeLayer(endMarker);
        endMarker = null;
    }

    // Remove the route if it exists
    if (routeLayer) {
        map.removeLayer(routeLayer);
        routeLayer = null;
    }

    // Reset coordinates and disable the 'Find Route' button
    startCoords = null;
    endCoords = null;
    document.getElementById('findRoute').disabled = true;
});
