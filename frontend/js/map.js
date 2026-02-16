// Map initialization and management
let map;
let currentGeoJsonLayer;
let currentCBSABounds;

function initializeMap() {
    // Initialize map centered on US
    map = L.map('map').setView([39.8283, -98.5795], 4);
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
}

function getColor(value, max) {
    // Color scale for choropleth
    if (value === 0) return '#ffffcc';
    if (value < max * 0.25) return '#ffffcc';
    if (value < max * 0.5) return '#c7e9b4';
    if (value < max * 0.75) return '#7fbc41';
    return '#2b8a0b';
}

function style(feature, maxValue) {
    const jobCount = feature.properties.total_jobs || feature.properties.metric_value || 0;
    return {
        fillColor: getColor(jobCount, maxValue),
        weight: 1,
        opacity: 0.8,
        color: '#666',
        dashArray: '3',
        fillOpacity: 0.65
    };
}

function onEachFeature(feature, layer) {
    const props = feature.properties;
    const popup = L.popup()
        .setContent(`
            <div class="popup-content">
                <h3>Block Group ${props.bg_geoid}</h3>
                <p><strong>Total Jobs:</strong> ${(props.total_jobs || props.metric_value || 0).toLocaleString()}</p>
                ${props.ca01 ? `<p><strong>Age 29 or younger:</strong> ${props.ca01.toLocaleString()}</p>` : ''}
                ${props.ca02 ? `<p><strong>Age 30-54:</strong> ${props.ca02.toLocaleString()}</p>` : ''}
                ${props.ca03 ? `<p><strong>Age 55+:</strong> ${props.ca03.toLocaleString()}</p>` : ''}
            </div>
        `);
    layer.bindPopup(popup);
    layer.on('mouseover', () => layer.openPopup());
    layer.on('mouseout', () => layer.closePopup());
}

function loadBlockGroupsOnMap(geojsonData) {
    // Remove existing layer
    if (currentGeoJsonLayer) {
        map.removeLayer(currentGeoJsonLayer);
    }

    if (!geojsonData || geojsonData.features.length === 0) {
        console.warn('No features to display');
        return;
    }

    // Calculate max value for color scaling
    const maxValue = Math.max(
        ...geojsonData.features.map(f => f.properties.total_jobs || f.properties.metric_value || 0)
    );

    // Add GeoJSON layer
    currentGeoJsonLayer = L.geoJSON(geojsonData, {
        style: (feature) => style(feature, maxValue),
        onEachFeature: onEachFeature
    }).addTo(map);

    // Fit map to bounds
    const bounds = currentGeoJsonLayer.getBounds();
    map.fitBounds(bounds, { padding: [50, 50] });
    currentCBSABounds = bounds;
}

function clearMap() {
    if (currentGeoJsonLayer) {
        map.removeLayer(currentGeoJsonLayer);
        currentGeoJsonLayer = null;
    }
}
