#!/usr/bin/env python3
"""Quick test to verify the BytesIO fix works"""
import requests
import json
import os

BASE_URL = "http://127.0.0.1:5001"

# Step 1: Create a simple test PDF
print("Step 1: Creating test PDF...")
from reportlab.pdfgen import canvas
from io import BytesIO

pdf_buffer = BytesIO()
c = canvas.Canvas(pdf_buffer)
c.drawString(100, 750, "Test PDF for BananaPDF")
c.save()
pdf_buffer.seek(0)

# Step 2: Upload PDF
print("Step 2: Uploading PDF...")
files = {'file': ('test.pdf', pdf_buffer, 'application/pdf')}
response = requests.post(f"{BASE_URL}/api/upload", files=files)
print(f"Upload status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ Uploaded: {data['filename']}")
    original_filename = data['originalFilename']
    page_count = data['pageCount']
else:
    print(f"✗ Upload failed: {response.text}")
    exit(1)

# Step 3: Save the PDF (with no annotations)
print("\nStep 3: Saving PDF...")
save_data = {
    "pages": [{"pageNum": 1, "deleted": False, "rotation": 0}],
    "annotations": {"0": []},
    "textBoxes": {},
    "originalFilename": original_filename,
    "flatten": False
}

response = requests.post(f"{BASE_URL}/api/save", json=save_data)
print(f"Save status: {response.status_code}")

if response.status_code == 200:
    print(f"✓ PDF saved successfully!")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
    print(f"PDF size: {len(response.content)} bytes")
    
    # Verify it's a valid PDF
    if response.content.startswith(b'%PDF'):
        print("✓ Valid PDF file received!")
    else:
        print("✗ Invalid PDF content")
else:
    print(f"✗ Save failed: {response.status_code}")
    print(f"Response: {response.json() if response.headers.get('Content-Type') == 'application/json' else response.text}")

print("\n✓ Test complete!")
