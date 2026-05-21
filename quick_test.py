import requests
response = requests.get('http://127.0.0.1:5001/api/messages/conversations')
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
if 'json' in response.headers.get('content-type', ''):
    print(f"JSON: {response.json()}")
else:
    print(f"HTML: {response.text[:100]}")