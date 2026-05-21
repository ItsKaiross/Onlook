"""
Generate complete address.js with all Philippine barangays
This script fetches data from PSGC API and creates a local address.js file
"""

import requests
import json
import time

def fetch_regions():
    """Fetch all regions"""
    url = "https://psgc.gitlab.io/api/regions/"
    response = requests.get(url)
    return response.json()

def fetch_provinces(region_code):
    """Fetch provinces for a region"""
    url = f"https://psgc.gitlab.io/api/regions/{region_code}/provinces/"
    response = requests.get(url)
    return response.json()

def fetch_cities(province_code):
    """Fetch cities for a province"""
    url = f"https://psgc.gitlab.io/api/provinces/{province_code}/cities-municipalities/"
    response = requests.get(url)
    return response.json()

def fetch_barangays(city_code):
    """Fetch barangays for a city"""
    url = f"https://psgc.gitlab.io/api/cities-municipalities/{city_code}/barangays/"
    response = requests.get(url)
    return response.json()

def convert_region_name(name):
    """Convert region names to use Roman numerals"""
    replacements = {
        'Region 1': 'Region I',
        'Region 2': 'Region II',
        'Region 3': 'Region III',
        'Region 4': 'Region IV',
        'Region 5': 'Region V',
        'Region 6': 'Region VI',
        'Region 7': 'Region VII',
        'Region 8': 'Region VIII',
        'Region 9': 'Region IX',
        'Region 10': 'Region X',
        'Region 11': 'Region XI',
        'Region 12': 'Region XII',
        'Region 13': 'Region XIII',
    }
    
    for old, new in replacements.items():
        if old in name:
            name = name.replace(old, new)
    
    return name

def generate_address_data():
    """Generate complete address data structure"""
    print("Fetching regions...")
    regions = fetch_regions()
    
    address_data = {}
    
    for region in regions:
        region_name = convert_region_name(region['name'])
        print(f"\nProcessing {region_name}...")
        address_data[region_name] = {}
        
        # Fetch provinces
        provinces = fetch_provinces(region['code'])
        
        for province in provinces:
            province_name = province['name']
            print(f"  - {province_name}")
            address_data[region_name][province_name] = {}
            
            # Fetch cities
            cities = fetch_cities(province['code'])
            
            for city in cities:
                city_name = city['name']
                print(f"    - {city_name}")
                
                # Fetch barangays
                try:
                    barangays = fetch_barangays(city['code'])
                    barangay_names = [b['name'] for b in barangays]
                    address_data[region_name][province_name][city_name] = barangay_names
                    print(f"      ({len(barangay_names)} barangays)")
                    time.sleep(0.1)  # Rate limiting
                except Exception as e:
                    print(f"      Error fetching barangays: {e}")
                    address_data[region_name][province_name][city_name] = []
    
    return address_data

def create_js_file(address_data, output_file):
    """Create the JavaScript file"""
    print(f"\nCreating {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("//###########################################################//\n")
        f.write("//#####################  A D D R E S S  #####################//\n")
        f.write("//###########################################################//\n")
        f.write("// Complete Philippine Address Data with All Barangays\n")
        f.write("// Total: 42,000+ barangays\n\n")
        
        f.write("const addressData = ")
        f.write(json.dumps(address_data, ensure_ascii=False, indent=2))
        f.write(";\n\n")
        
        # Add the JavaScript functions
        f.write("""
window.onload = function() {
    const regionSelect = document.getElementById('region');
    if (regionSelect && addressData) {
        for (let region in addressData) {
            let option = document.createElement('option');
            option.value = region;
            option.text = region;
            regionSelect.add(option);
        }
    }

    const iregionSelect = document.getElementById('iregion');
    if (iregionSelect && addressData) {
        for (let region in addressData) {
            let option = document.createElement('option');
            option.value = region;
            option.text = region;
            iregionSelect.add(option);
        }
    }

    const regionSelectz = document.getElementById('regionz');
    if (regionSelectz && addressData) {
        for (let region in addressData) {
            let option = document.createElement('option');
            option.value = region;
            option.text = region;
            regionSelectz.add(option);
        }
    }
};

function populateProvinces() {
    const regionSelect = document.getElementById('region');
    const provinceSelect = document.getElementById('province');
    const citySelect = document.getElementById('city');
    const barangaySelect = document.getElementById('barangay');
    const selectedRegion = regionSelect.value;

    provinceSelect.innerHTML = '<option value="" disabled selected>Select a province</option>';
    citySelect.innerHTML = '<option value="" disabled selected>Select a city/municipality</option>';
    if (barangaySelect) {
        barangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';
    }

    if (selectedRegion) {
        const provinces = Object.keys(addressData[selectedRegion]);
        provinces.forEach(province => {
            let option = document.createElement('option');
            option.value = province;
            option.text = province;
            provinceSelect.add(option);
        });
    }
}

function populateCities() {
    const regionSelect = document.getElementById('region');
    const provinceSelect = document.getElementById('province');
    const citySelect = document.getElementById('city');
    const barangaySelect = document.getElementById('barangay');
    const selectedRegion = regionSelect.value;
    const selectedProvince = provinceSelect.value;

    citySelect.innerHTML = '<option value="" disabled selected>Select a city/municipality</option>';
    if (barangaySelect) {
        barangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';
    }

    if (selectedProvince) {
        const provinceData = addressData[selectedRegion][selectedProvince];
        const cities = Object.keys(provinceData);
        cities.forEach(city => {
            let option = document.createElement('option');
            option.value = city;
            option.text = city;
            citySelect.add(option);
        });
    }
}

function populateBarangays() {
    const regionSelect = document.getElementById('region');
    const provinceSelect = document.getElementById('province');
    const citySelect = document.getElementById('city');
    const barangaySelect = document.getElementById('barangay');
    const selectedRegion = regionSelect.value;
    const selectedProvince = provinceSelect.value;
    const selectedCity = citySelect.value;

    if (!barangaySelect) return;

    barangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';

    if (selectedCity && addressData[selectedRegion] && addressData[selectedRegion][selectedProvince] && addressData[selectedRegion][selectedProvince][selectedCity]) {
        const barangays = addressData[selectedRegion][selectedProvince][selectedCity];
        barangays.forEach(barangay => {
            let option = document.createElement('option');
            option.value = barangay;
            option.text = barangay;
            barangaySelect.add(option);
        });
    }
}

function populateIProvinces() {
    const iregionSelect = document.getElementById('iregion');
    const iprovinceSelect = document.getElementById('iprovince');
    const icitySelect = document.getElementById('icity');
    const ibarangaySelect = document.getElementById('ibarangay');
    const iselectedRegion = iregionSelect.value;

    iprovinceSelect.innerHTML = '<option value="" disabled selected>Select a province</option>';
    icitySelect.innerHTML = '<option value="" disabled selected>Select a city/municipality</option>';
    if (ibarangaySelect) {
        ibarangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';
    }

    if (iselectedRegion) {
        const provinces = Object.keys(addressData[iselectedRegion]);
        provinces.forEach(province => {
            let option = document.createElement('option');
            option.value = province;
            option.text = province;
            iprovinceSelect.add(option);
        });
    }
}

function populateICities() {
    const iregionSelect = document.getElementById('iregion');
    const iprovinceSelect = document.getElementById('iprovince');
    const icitySelect = document.getElementById('icity');
    const ibarangaySelect = document.getElementById('ibarangay');
    const iselectedRegion = iregionSelect.value;
    const iselectedProvince = iprovinceSelect.value;

    icitySelect.innerHTML = '<option value="" disabled selected>Select a city/municipality</option>';
    if (ibarangaySelect) {
        ibarangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';
    }

    if (iselectedProvince) {
        const provinceData = addressData[iselectedRegion][iselectedProvince];
        const icities = Object.keys(provinceData);
        icities.forEach(city => {
            let option = document.createElement('option');
            option.value = city;
            option.text = city;
            icitySelect.add(option);
        });
    }
}

function populateIBarangays() {
    const iregionSelect = document.getElementById('iregion');
    const iprovinceSelect = document.getElementById('iprovince');
    const icitySelect = document.getElementById('icity');
    const ibarangaySelect = document.getElementById('ibarangay');
    const iselectedRegion = iregionSelect.value;
    const iselectedProvince = iprovinceSelect.value;
    const iselectedCity = icitySelect.value;

    if (!ibarangaySelect) return;

    ibarangaySelect.innerHTML = '<option value="" disabled selected>Select a barangay</option>';

    if (iselectedCity && addressData[iselectedRegion] && addressData[iselectedRegion][iselectedProvince] && addressData[iselectedRegion][iselectedProvince][iselectedCity]) {
        const ibarangays = addressData[iselectedRegion][iselectedProvince][iselectedCity];
        ibarangays.forEach(barangay => {
            let option = document.createElement('option');
            option.value = barangay;
            option.text = barangay;
            ibarangaySelect.add(option);
        });
    }
}
""")
    
    print(f"File created successfully: {output_file}")
    print(f"File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    print("=" * 60)
    print("Philippine Address Data Generator")
    print("This will fetch all regions, provinces, cities, and barangays")
    print("=" * 60)
    
    try:
        # Generate the data
        address_data = generate_address_data()
        
        # Create the JavaScript file
        output_file = "address_complete.js"
        create_js_file(address_data, output_file)
        
        print("\n" + "=" * 60)
        print("SUCCESS! Complete address.js file has been generated.")
        print(f"File: {output_file}")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Copy 'address_complete.js' to:")
        print("   app/static/Javascript/registration/address.js")
        print("2. Clear browser cache")
        print("3. Test the dropdowns")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Please check your internet connection and try again.")
