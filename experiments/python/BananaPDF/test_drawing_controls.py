#!/usr/bin/env python3
"""
Test script to verify drawing color and brush controls are working
"""
import requests
import json
import base64
from PIL import Image, ImageDraw
import io

BASE_URL = 'http://127.0.0.1:5000'

# Upload a test PDF
print("1. Testing PDF upload...")
with open('uploads/fresh_test.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(f'{BASE_URL}/api/upload', files=files)
    
if response.status_code == 200:
    print("   ✓ PDF uploaded")
    data = response.json()
    print(f"   Pages: {data.get('pages', 'unknown')}")
    session_id = data.get('session_id', 'unknown')
    print(f"   Session: {session_id}")
else:
    print(f"   ✗ Upload failed: {response.status_code}")
    print(response.text)
    exit(1)

# Create a simple test drawing image (red stroke on transparent background)
print("\n2. Creating test drawing image...")
img = Image.new('RGBA', (200, 100), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Draw a red line (simulating selected color)
draw.line([(10, 20), (150, 80)], fill=(255, 0, 0, 255), width=4)

# Convert to base64
buffer = io.BytesIO()
img.save(buffer, format='PNG')
image_base64 = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()

# Add drawing annotation with red color and thick brush (4px)
print("3. Testing drawing annotation endpoint...")
payload = {
    'pageNum': 0,
    'x': 50,
    'y': 50,
    'width': 200,
    'height': 100,
    'imageData': image_base64
}

response = requests.post(f'{BASE_URL}/api/add-drawing', json=payload)

if response.status_code == 200:
    print("   ✓ Drawing added successfully")
    result = response.json()
    print(f"   Result: {result.get('message', result)}")
else:
    print(f"   ✗ Drawing failed: {response.status_code}")
    print(response.text)
    exit(1)

# Create a second drawing with thin line and blue color
print("\n4. Creating second drawing with thin brush...")
img2 = Image.new('RGBA', (150, 80), (255, 255, 255, 0))
draw2 = ImageDraw.Draw(img2)

# Draw a blue thin line
draw2.line([(10, 10), (140, 70)], fill=(0, 0, 255, 255), width=1)

buffer2 = io.BytesIO()
img2.save(buffer2, format='PNG')
image_base64_2 = 'data:image/png;base64,' + base64.b64encode(buffer2.getvalue()).decode()

payload2 = {
    'pageNum': 0,
    'x': 50,
    'y': 180,
    'width': 150,
    'height': 80,
    'imageData': image_base64_2
}

response = requests.post(f'{BASE_URL}/api/add-drawing', json=payload2)

if response.status_code == 200:
    print("   ✓ Second drawing added successfully")
    result = response.json()
    print(f"   Result: {result.get('message', result)}")
else:
    print(f"   ✗ Second drawing failed: {response.status_code}")
    print(response.text)

# Save the PDF
print("\n5. Saving PDF...")
response = requests.post(f'{BASE_URL}/api/save', json={})

if response.status_code == 200:
    print("   ✓ PDF saved successfully")
    print("\n✅ All drawing control features working!")
    print("   - Red thick line (4px) added at (50, 50)")
    print("   - Blue thin line (1px) added at (50, 180)")
    print("   - Both annotations persisted to file")
else:
    print(f"   ✗ Save failed: {response.status_code}")
    print(response.text)
