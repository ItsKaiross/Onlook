// Hybrid Address Handler - Uses local data for regions/provinces/cities, API for barangays
class AddressHandler {
    constructor() {
        this.apiBaseUrl = 'https://psgc.gitlab.io/api';
        this.barangayCache = {};
    }

    // Fetch barangays from API
    async fetchBarangays(cityCode) {
        if (this.barangayCache[cityCode]) {
            return this.barangayCache[cityCode];
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/cities-municipalities/${cityCode}/barangays/`);
            if (!response.ok) throw new Error('Failed to fetch barangays');
            const barangays = await response.json();
            this.barangayCache[cityCode] = barangays;
            return barangays;
        } catch (error) {
            console.error('Error fetching barangays:', error);
            return [];
        }
    }

    // Get city code from PSGC API by name
    async getCityCode(regionName, provinceName, cityName) {
        try {
            // This is a simplified version - you may need to implement proper mapping
            // For now, return null to use local barangay data if available
            return null;
        } catch (error) {
            console.error('Error getting city code:', error);
            return null;
        }
    }

    // Populate barangays - tries local data first, then API
    async populateBarangaysDropdown(regionSelect, provinceSelect, citySelect, barangaySelect) {
        if (!barangaySelect) return;

        const selectedRegion = regionSelect.value;
        const selectedProvince = provinceSelect.value;
        const selectedCity = citySelect.value;

        barangaySelect.innerHTML = '<option value="" disabled selected>Loading barangays...</option>';

        if (!selectedCity || !addressData[selectedRegion] || !addressData[selectedRegion][selectedProvince]) {
            barangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';
            return;
        }

        const provinceData = addressData[selectedRegion][selectedProvince];

        // Check if we have local barangay data
        if (typeof provinceData === 'object' && !Array.isArray(provinceData) && provinceData[selectedCity]) {
            // Use local barangay data
            const barangays = provinceData[selectedCity];
            barangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';
            barangays.forEach(barangay => {
                let option = document.createElement('option');
                option.value = barangay;
                option.text = barangay;
                barangaySelect.add(option);
            });
        } else {
            // Try to fetch from API
            const cityCode = await this.getCityCode(selectedRegion, selectedProvince, selectedCity);
            if (cityCode) {
                const barangays = await this.fetchBarangays(cityCode);
                barangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';
                barangays.forEach(barangay => {
                    let option = document.createElement('option');
                    option.value = barangay.name;
                    option.text = barangay.name;
                    barangaySelect.add(option);
                });
            } else {
                // No barangay data available
                barangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';
            }
        }
    }
}

// Initialize the address handler
const addressHandler = new AddressHandler();

// Override the populateBarangays function to use the hybrid approach
async function populateBarangays() {
    const regionSelect = document.getElementById('region');
    const provinceSelect = document.getElementById('province');
    const citySelect = document.getElementById('city');
    const barangaySelect = document.getElementById('barangay');

    if (regionSelect && provinceSelect && citySelect && barangaySelect) {
        await addressHandler.populateBarangaysDropdown(regionSelect, provinceSelect, citySelect, barangaySelect);
    }
}

// Override for informant barangays
async function populateIBarangays() {
    const iregionSelect = document.getElementById('iregion');
    const iprovinceSelect = document.getElementById('iprovince');
    const icitySelect = document.getElementById('icity');
    const ibarangaySelect = document.getElementById('ibarangay');

    if (iregionSelect && iprovinceSelect && icitySelect && ibarangaySelect) {
        await addressHandler.populateBarangaysDropdown(iregionSelect, iprovinceSelect, icitySelect, ibarangaySelect);
    }
}
