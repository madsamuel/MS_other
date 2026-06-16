#!/usr/bin/env python
"""Test the complete save flow: upload PDF, then save"""
import requests
import json

print("Step 1: Upload test PDF...")
with open('test.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://127.0.0.1:5001/api/upload', files=files)
    
if response.status_code != 200:
    print(f"ERROR uploading: {response.text}")
    exit(1)

upload_data = response.json()
print(f"✓ PDF uploaded successfully")
print(f"  Filename: {upload_data.get('session', {}).get('filename')}")
print(f"  Pages: {upload_data.get('pageCount')}")

print("\nStep 2: Save the PDF...")
save_data = {
    'pages': [{'pageNum': 1, 'deleted': False}],
    'annotations': {},
    'textBoxes': {},
    'originalFilename': upload_data['session']['originalFilename']
}

response = requests.post('http://127.0.0.1:5001/api/save', json=save_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("✓ SUCCESS - PDF saved and downloaded!")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {len(response.content)} bytes")
    
    # Save the downloaded PDF
    with open('downloaded.pdf', 'wb') as f:
        f.write(response.content)
    print("✓ Saved as 'downloaded.pdf'")
else:
    print("✗ ERROR")
    print(f"Response: {response.text}")
