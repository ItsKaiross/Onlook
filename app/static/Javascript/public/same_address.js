function toggleSameAddress() {
    const checkbox = document.getElementById('sameAddress');
    if (!checkbox) return;
    
    const isChecked = checkbox.checked;
    
    // Get missing person address fields
    const mpHouseNumber = document.getElementById('houseNumber')?.value || '';
    const mpStreet = document.getElementById('street')?.value || '';
    const mpBrgy = document.getElementById('brgy')?.value || '';
    const mpRegion = document.getElementById('region')?.value || '';
    const mpProvince = document.getElementById('province')?.value || '';
    const mpCity = document.getElementById('city')?.value || '';
    
    // Get informant address fields
    const informantHouseNumber = document.getElementById('informant_houseNo');
    const informantStreet = document.getElementById('informant_street');
    const informantBrgy = document.getElementById('informant_brgy');
    const informantRegion = document.getElementById('iregion');
    const informantProvince = document.getElementById('iprovince');
    const informantCity = document.getElementById('icity');
    
    if (isChecked) {
        // Fill informant address fields with missing person data
        if (informantHouseNumber) informantHouseNumber.value = mpHouseNumber;
        if (informantStreet) informantStreet.value = mpStreet;
        if (informantBrgy) informantBrgy.value = mpBrgy;
        
        if (informantRegion && mpRegion) {
            informantRegion.value = mpRegion;
            if (typeof populateIProvinces === 'function') {
                populateIProvinces();
            }
            
            setTimeout(() => {
                if (informantProvince && mpProvince) {
                    informantProvince.value = mpProvince;
                    if (typeof populateICities === 'function') {
                        populateICities();
                    }
                    
                    setTimeout(() => {
                        if (informantCity && mpCity) {
                            informantCity.value = mpCity;
                        }
                    }, 100);
                }
            }, 100);
        }
        

    } else {
        
        if (informantRegion) {
            informantRegion.disabled = false;
            informantRegion.selectedIndex = 0;
        }
        if (informantProvince) {
            informantProvince.disabled = false;
            informantProvince.innerHTML = '<option value="" disabled selected>Select a province</option>';
        }
        if (informantCity) {
            informantCity.disabled = false;
            informantCity.innerHTML = '<option value="" disabled selected>Select a city/municipality</option>';
        }
    }
}