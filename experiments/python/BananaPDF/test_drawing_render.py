#!/usr/bin/env python3
"""
Test script to verify drawing works with the fixed positioning
"""
import requests
import json
import base64
import time
from PIL import Image, ImageDraw
import io

BASE_URL = 'http://127.0.0.1:5000'

# Step 1: Upload a test PDF
print("1. Uploading PDF...")
with open('uploads/fresh_test.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(f'{BASE_URL}/api/upload', files=files)
    
if response.status_code == 200:
    print("   ✓ PDF uploaded")
else:
    print(f"   ✗ Upload failed: {response.status_code}")
    exit(1)

# Get page dimensions to size the canvas correctly
print("\n2. Getting page dimensions...")
payload = {'pageNum': 0}
response = requests.post(f'{BASE_URL}/api/page-dimensions', json=payload)

if response.status_code == 200:
    dims = response.json()
    print(f"   ✓ Page dimensions: {dims}")
    page_width = dims.get('width', 600)
    page_height = dims.get('height', 800)
else:
    print(f"   ✗ Failed to get dimensions: {response.status_code}")
    page_width, page_height = 600, 800

# Step 2: Create multiple test drawings with different colors and brush sizes
print("\n3. Creating test drawings...")

# Drawing 1: Black thick line
img1 = Image.new('RGBA', (300, 200), (255, 255, 255, 0))
draw1 = ImageDraw.Draw(img1)
draw1.line([(30, 50), (280, 150)], fill=(0, 0, 0, 255), width=6)  # Black, thick (6px)
buffer1 = io.BytesIO()
img1.save(buffer1, format='PNG')
image_base64_1 = 'data:image/png;base64,' + base64.b64encode(buffer1.getvalue()).decode()

# Drawing 2: Red normal line
img2 = Image.new('RGBA', (250, 150), (255, 255, 255, 0))
draw2 = ImageDraw.Draw(img2)
draw2.line([(20, 30), (230, 130)], fill=(255, 0, 0, 255), width=3)  # Red, normal (2-3px)
buffer2 = io.BytesIO()
img2.save(buffer2, format='PNG')
image_base64_2 = 'data:image/png;base64,' + base64.b64encode(buffer2.getvalue()).decode()

# Drawing 3: Blue thin line
img3 = Image.new('RGBA', (200, 100), (255, 255, 255, 0))
draw3 = ImageDraw.Draw(img3)
draw3.line([(10, 20), (190, 90)], fill=(0, 0, 255, 255), width=1)  # Blue, thin (1px)
buffer3 = io.BytesIO()
img3.save(buffer3, format='PNG')
image_base64_3 = 'data:image/png;base64,' + base64.b64encode(buffer3.getvalue()).decode()

# Step 3: Add the drawings
drawings = [
    {
        'name': 'Black Thick Line',
        'pageNum': 0,
        'x': 50,
        'y': 100,
        'width': 300,
        'height': 200,
        'imageData': image_base64_1,
        'brush': 'thick (6px)'
    },
    {
        'name': 'Red Normal Line',
        'pageNum': 0,
        'x': 50,
        'y': 350,
        'width': 250,
        'height': 150,
        'imageData': image_base64_2,
        'brush': 'normal (3px)'
    },
    {
        'name': 'Blue Thin Line',
        'pageNum': 0,
        'x': 50,
        'y': 550,
        'width': 200,
        'height': 100,
        'imageData': image_base64_3,
        'brush': 'thin (1px)'
    }
]

for drawing in drawings:
    print(f"\n   Adding: {drawing['name']} ({drawing['brush']})...")
    
    payload = {
        'pageNum': drawing['pageNum'],
        'x': drawing['x'],
        'y': drawing['y'],
        'width': drawing['width'],
        'height': drawing['height'],
        'imageData': drawing['imageData']
    }
    
    response = requests.post(f'{BASE_URL}/api/add-drawing', json=payload)
    
    if response.status_code == 200:
        print(f"      ✓ Added successfully")
    else:
        print(f"      ✗ Failed: {response.status_code} - {response.text}")

# Step 4: Verify by getting the rendered page
print("\n4. Rendering page to verify drawings...")
payload = {'pageNum': 0}
response = requests.post(f'{BASE_URL}/api/render-page', json=payload)

if response.status_code == 200:
    print("   ✓ Page rendered successfully with drawings")
    # Could save the rendered image to verify
    data = response.json()
    if 'image' in data:
        print(f"   Page size in response: {len(data['image'])} bytes")
else:
    print(f"   ✗ Failed to render: {response.status_code}")

print("\n✅ Test complete!")
print("\nTo verify drawings in browser:")
print("1. Open http://127.0.0.1:5000/")
print("2. PDFshould be loaded automatically")
print("3. You should see 3 colored lines:")
print("   - Black thick line at top")
print("   - Red normal line in middle")
print("   - Blue thin line at bottom")
