// Map initialization and management
let map;
let currentGeoJsonLayer;
let currentCBSABounds;

function initializeMap() {
    // Initialize map centered on US
    map = L.map('map').setView([39.8283, -98.5795], 4);
    
    // Add tile layer
    // Use CartoDB Positron basemap for a light, clean background
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://carto.com/attributions">CARTO</a> &mdash; &copy; OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    // Ensure Leaflet measures the container correctly
    setTimeout(() => map.invalidateSize(), 200);
}

// Show/hide map loading overlay
let _mapLoaderTimer = null;
const MAP_LOADER_DELAY = 250; // ms - only show loader for requests longer than this

function showMapLoading() {
    // If a timer or visible marker already exists, do nothing
    if (_mapLoaderTimer) return;
    _mapLoaderTimer = setTimeout(() => {
        const el = document.getElementById('map-loader');
        if (el) {
            el.classList.add('visible');
            el.setAttribute('aria-hidden', 'false');
        }
        // mark as visible
        _mapLoaderTimer = 'visible';
    }, MAP_LOADER_DELAY);
}

function hideMapLoading() {
    // If a timer is scheduled but not fired yet, cancel it
    if (_mapLoaderTimer && _mapLoaderTimer !== 'visible') {
        clearTimeout(_mapLoaderTimer);
        _mapLoaderTimer = null;
        return;
    }

    // If loader is visible, hide it
    if (_mapLoaderTimer === 'visible') {
        const el = document.getElementById('map-loader');
        if (el) {
            el.classList.remove('visible');
            el.setAttribute('aria-hidden', 'true');
        }
        _mapLoaderTimer = null;
    }
}

function getColor(value, max) {
    // Interpolate between two hex colors based on value proportion
    // Gradient: #F2F5D0 (low) -> #F9957F (high)
    const start = { r: 0xF2, g: 0xF5, b: 0xD0 };
    const end = { r: 0xF9, g: 0x95, b: 0x7F };

    if (!max || max <= 0) return rgbToHex(start.r, start.g, start.b);
    const t = Math.max(0, Math.min(1, value / max));

    function lerp(a, b, t) { return Math.round(a + (b - a) * t); }
    function rgbToHex(r, g, b) {
        return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
    }

    const r = lerp(start.r, end.r, t);
    const g = lerp(start.g, end.g, t);
    const b = lerp(start.b, end.b, t);
    return rgbToHex(r, g, b);
}

function style(feature, maxValue) {
    // Prefer filtered metric_value for styling when present
    const jobCount = (feature.properties.metric_value !== undefined && feature.properties.metric_value !== null)
        ? feature.properties.metric_value
        : (feature.properties.total_jobs || 0);
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
    // Build human-readable labels for active filters (if any)
    let filterLabels = [];
    if (props.active_filters && Array.isArray(props.active_filters) && typeof filterOptions !== 'undefined') {
        const codes = props.active_filters.map(c => (c || '').toUpperCase());
        codes.forEach(code => {
            // check each filter list for a matching code
            const emp = (filterOptions.employment_codes || []).find(e => e.code === code);
            if (emp) {
                filterLabels.push(`${emp.code} - ${emp.name}`);
                return;
            }
            const age = (filterOptions.age_groups || []).find(a => a.code === code);
            if (age) {
                filterLabels.push(`${age.code} - ${age.name}`);
                return;
            }
            const earn = (filterOptions.earnings_brackets || []).find(e => e.code === code);
            if (earn) {
                filterLabels.push(`${earn.code} - ${earn.name}`);
                return;
            }
            const edu = (filterOptions.education_levels || []).find(d => d.code === code);
            if (edu) {
                filterLabels.push(`${edu.code} - ${edu.name}`);
                return;
            }
            // fallback to raw code
            filterLabels.push(code);
        });
    }

    const popup = L.popup()
        .setContent(`
            <div class="popup-content">
                <h3>Block Group ${props.bg_geoid}</h3>
                ${filterLabels.length > 0 ?
                    `<p><strong>Filtered (${filterLabels.join(', ')}):</strong> ${ (props.metric_value || 0).toLocaleString() }</p>` :
                    `<p><strong>Total Jobs:</strong> ${(props.total_jobs || props.metric_value || 0).toLocaleString()}</p>`
                }
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

    // Filter out features with no jobs (prefer filtered metric_value when present)
    const filteredFeatures = geojsonData.features.filter(f => {
        const val = (f.properties.metric_value !== undefined && f.properties.metric_value !== null)
            ? f.properties.metric_value
            : (f.properties.total_jobs || 0);
        return Number(val) > 0;
    });

    if (filteredFeatures.length === 0) {
        console.warn('No block groups with jobs to display');
        clearMap();
        return;
    }

    const filteredGeojson = Object.assign({}, geojsonData, { features: filteredFeatures });

    // Calculate max value for color scaling using filtered features
    const maxValue = Math.max(
        ...filteredFeatures.map(f => (f.properties.metric_value !== undefined && f.properties.metric_value !== null)
            ? f.properties.metric_value
            : (f.properties.total_jobs || 0))
    );

    // Add GeoJSON layer
    currentGeoJsonLayer = L.geoJSON(filteredGeojson, {
        style: (feature) => style(feature, maxValue),
        onEachFeature: onEachFeature
    }).addTo(map);

    // Force Leaflet to recalculate size/layout before fitting
    setTimeout(() => map.invalidateSize(), 100);

    // Fit map to bounds
    const bounds = currentGeoJsonLayer.getBounds();
    map.fitBounds(bounds, { padding: [50, 50] });
    currentCBSABounds = bounds;
    // done updating map
    hideMapLoading();
}

// Keep map layout correct on window resize
window.addEventListener('resize', () => {
    if (map) map.invalidateSize();
});

function clearMap() {
    if (currentGeoJsonLayer) {
        map.removeLayer(currentGeoJsonLayer);
        currentGeoJsonLayer = null;
    }
}
