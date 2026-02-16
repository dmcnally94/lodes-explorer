// Main application logic
let currentCBSA = null;
let filterOptions = {};

document.addEventListener('DOMContentLoaded', async () => {
    initializeMap();
    await initializeUI();
});

async function initializeUI() {
    // Load and populate CBSAs
    const cbsas = await fetchCBSAs();
    const cbsaSelect = document.getElementById('cbsa-select');
    
    cbsas.forEach(cbsa => {
        const option = document.createElement('option');
        option.value = cbsa.cbsa_code;
        option.textContent = `${cbsa.cbsa_code} - ${cbsa.cbsa_name} (${cbsa.total_jobs.toLocaleString()} jobs)`;
        cbsaSelect.appendChild(option);
    });

    // Set up CBSA selection
    cbsaSelect.addEventListener('change', async (e) => {
        if (e.target.value) {
            await selectCBSA(e.target.value);
        } else {
            clearMap();
            document.getElementById('filters-section').style.display = 'none';
            document.getElementById('stats-section').style.display = 'none';
        }
    });

    // Load filter options
    const filters = await fetchFilterOptions();
    if (filters) {
        filterOptions = filters;
        populateFilters(filters);
    }

    // Set up filter buttons
    document.getElementById('apply-filters').addEventListener('click', applyFilters);
    document.getElementById('clear-filters').addEventListener('click', clearFilters);
}

async function selectCBSA(cbsaCode) {
    currentCBSA = cbsaCode;
    
    // Show loading state
    document.getElementById('filters-section').style.display = 'block';
    document.getElementById('stats-section').style.display = 'block';

    // Fetch and display block groups
    try {
        if (typeof showMapLoading === 'function') showMapLoading();
        const geojsonData = await fetchBlockGroups(cbsaCode);
        if (geojsonData) {
            loadBlockGroupsOnMap(geojsonData);
        }

        // Update statistics
        const cbsaDetails = await fetchCBSADetails(cbsaCode);
        if (cbsaDetails) {
            document.getElementById('total-jobs').textContent = 
                cbsaDetails.total_jobs.toLocaleString();
        }
    } catch (err) {
        console.error('Error loading CBSA block groups', err);
    } finally {
        if (typeof hideMapLoading === 'function') hideMapLoading();
    }
}

function populateFilters(filters) {
    // Populate employment codes
    const employmentSelect = document.getElementById('employment-code');
    filters.employment_codes.forEach(code => {
        const option = document.createElement('option');
        option.value = code.code;
        option.textContent = `${code.code} - ${code.name}`;
        employmentSelect.appendChild(option);
    });

    // Populate age groups
    const ageSelect = document.getElementById('age-group');
    filters.age_groups.forEach(group => {
        const option = document.createElement('option');
        option.value = group.code;
        option.textContent = group.name;
        ageSelect.appendChild(option);
    });

    // Populate earnings brackets
    const earningsSelect = document.getElementById('earnings-bracket');
    filters.earnings_brackets.forEach(bracket => {
        const option = document.createElement('option');
        option.value = bracket.code;
        option.textContent = bracket.name;
        earningsSelect.appendChild(option);
    });

    // Populate education levels
    const educationSelect = document.getElementById('education-level');
    filters.education_levels.forEach(level => {
        const option = document.createElement('option');
        option.value = level.code;
        option.textContent = level.name;
        educationSelect.appendChild(option);
    });
}

async function applyFilters() {
    if (!currentCBSA) {
        alert('Please select a CBSA first');
        return;
    }

    const filters = {
        employment_code: document.getElementById('employment-code').value || null,
        age_group: document.getElementById('age-group').value || null,
        earnings_bracket: document.getElementById('earnings-bracket').value || null,
        education_level: document.getElementById('education-level').value || null,
    };

    try {
        if (typeof showMapLoading === 'function') showMapLoading();
        const geojsonData = await fetchFilteredBlockGroups(currentCBSA, filters);
        if (geojsonData) {
            loadBlockGroupsOnMap(geojsonData);
        }
    } catch (err) {
        console.error('Error applying filters', err);
    } finally {
        if (typeof hideMapLoading === 'function') hideMapLoading();
    }
}

function clearFilters() {
    document.getElementById('employment-code').value = '';
    document.getElementById('age-group').value = '';
    document.getElementById('earnings-bracket').value = '';
    document.getElementById('education-level').value = '';
    
    // Reload original block groups
    if (currentCBSA) {
        selectCBSA(currentCBSA);
    }
}
