#!/usr/bin/env python
"""Test the /api/save endpoint"""
import requests
import json

# Create test save data
save_data = {
    'pages': [{'pageNum': 1, 'deleted': False}],
    'annotations': {},
    'textBoxes': {},
    'originalFilename': 'test.pdf'
}

print("Testing /api/save endpoint...")
print(f"Sending data: {json.dumps(save_data, indent=2)}")

# Send save request
response = requests.post('http://127.0.0.1:5001/api/save', json=save_data)
print(f"\nStatus: {response.status_code}")

if response.status_code == 200:
    print("✓ SUCCESS - Got PDF blob")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {len(response.content)} bytes")
else:
    print(f"✗ ERROR")
    print(f"Response text:\n{response.text}")
