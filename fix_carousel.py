import re

# Read the template file
with open('d:\\SCHOOL\\CAPSTONE\\Onlook\\app\\templates\\public_users\\1u-public_view.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all occurrences of the JSON encoding issue
content = content.replace("data-images='{{ person.all_images|tojson }}'", "data-images='{{ person.all_images|tojson|safe }}'")

# Write back to file
with open('d:\\SCHOOL\\CAPSTONE\\Onlook\\app\\templates\\public_users\\1u-public_view.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed JSON encoding in template")