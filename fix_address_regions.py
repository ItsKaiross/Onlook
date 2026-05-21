import re
import json

# Read the address_complete.js file
with open('app/static/Javascript/registration/address_complete.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Region name mappings to convert to Roman numerals
region_mappings = {
    '"Ilocos Region"': '"Region I (Ilocos Region)"',
    '"Cagayan Valley"': '"Region II (Cagayan Valley)"',
    '"Central Luzon"': '"Region III (Central Luzon)"',
    '"CALABARZON"': '"Region IV-A (CALABARZON)"',
    '"MIMAROPA"': '"Region IV-B (MIMAROPA)"',
    '"Bicol Region"': '"Region V (Bicol Region)"',
    '"Western Visayas"': '"Region VI (Western Visayas)"',
    '"Central Visayas"': '"Region VII (Central Visayas)"',
    '"Eastern Visayas"': '"Region VIII (Eastern Visayas)"',
    '"Zamboanga Peninsula"': '"Region IX (Zamboanga Peninsula)"',
    '"Northern Mindanao"': '"Region X (Northern Mindanao)"',
    '"Davao Region"': '"Region XI (Davao Region)"',
    '"SOCCSKSARGEN"': '"Region XII (SOCCSKSARGEN)"',
    '"Caraga"': '"Region XIII (Caraga)"',
    '"National Capital Region"': '"NCR (National Capital Region)"',
    '"Bangsamoro Autonomous Region in Muslim Mindanao"': '"BARMM (Bangsamoro Autonomous Region in Muslim Mindanao)"',
    '"Cordillera Administrative Region"': '"CAR (Cordillera Administrative Region)"'
}

# Replace region names
for old_name, new_name in region_mappings.items():
    content = content.replace(old_name, new_name)

# Write to the main address.js file (backup current one first)
print("Creating backup of current address.js...")
with open('app/static/Javascript/registration/address_backup_old.js', 'w', encoding='utf-8') as f_backup:
    with open('app/static/Javascript/registration/address.js', 'r', encoding='utf-8') as f_current:
        f_backup.write(f_current.read())

print("Writing complete address data to address.js...")
with open('app/static/Javascript/registration/address.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated address.js with all 42,000+ barangays!")
print("✅ Old address.js backed up to address_backup_old.js")
