// API client functions
const API_BASE = '/api';

async function fetchCBSAs() {
    try {
        const response = await fetch(`${API_BASE}/cbsas`);
        if (!response.ok) throw new Error('Failed to fetch CBSAs');
        return await response.json();
    } catch (error) {
        console.error('Error fetching CBSAs:', error);
        return [];
    }
}

async function fetchBlockGroups(cbsaCode) {
    try {
        const response = await fetch(`${API_BASE}/blockgroups/${cbsaCode}`);
        if (!response.ok) throw new Error('Failed to fetch block groups');
        return await response.json();
    } catch (error) {
        console.error('Error fetching block groups:', error);
        return null;
    }
}

async function fetchFilterOptions() {
    try {
        const response = await fetch(`${API_BASE}/filters`);
        if (!response.ok) throw new Error('Failed to fetch filters');
        return await response.json();
    } catch (error) {
        console.error('Error fetching filters:', error);
        return null;
    }
}

async function fetchFilteredBlockGroups(cbsaCode, filters) {
    try {
        const params = new URLSearchParams({
            cbsa_code: cbsaCode,
            ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v))
        });
        
        const response = await fetch(`${API_BASE}/blockgroups/filtered?${params}`);
        if (!response.ok) throw new Error('Failed to fetch filtered data');
        return await response.json();
    } catch (error) {
        console.error('Error fetching filtered data:', error);
        return null;
    }
}

async function fetchCBSADetails(cbsaCode) {
    try {
        const response = await fetch(`${API_BASE}/cbsa/${cbsaCode}`);
        if (!response.ok) throw new Error('Failed to fetch CBSA details');
        return await response.json();
    } catch (error) {
        console.error('Error fetching CBSA details:', error);
        return null;
    }
}
