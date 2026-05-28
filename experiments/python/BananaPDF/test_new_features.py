import requests
import json
import time
import base64
from PIL import Image, ImageDraw
from io import BytesIO

BASE_URL = 'http://127.0.0.1:5000'

def create_test_image(width=400, height=200, color='red', label=''):
    """Create a simple test image"""
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple shape
    if color == 'red':
        draw.rectangle([20, 20, width-20, height-20], outline='red', width=3)
        draw.line([20, 20, width-20, height-20], fill='red', width=2)
        draw.line([width-20, 20, 20, height-20], fill='red', width=2)
    else:  # signature
        draw.line([50, 150, 100, 50, 150, 100, 200, 80], fill='black', width=3)
        draw.text((250, 100), 'Signature', fill='black')
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format='PNG')
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f'data:image/png;base64,{img_str}'

print("=" * 60)
print("BananaPDF - Comment, Draw, and Signature Test")
print("=" * 60)

# Step 1: Upload PDF
print("\n1. Uploading PDF...")
with open('uploads/fresh_test.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(f'{BASE_URL}/api/upload', files=files)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json().get('success')}")

# Step 2: Test Comment endpoint
print("\n2. Testing Comment endpoint...")
comment_data = {
    "pageNum": 0,
    "x": 250,
    "y": 200,
    "text": "This is a test comment added programmatically!"
}
response = requests.post(f'{BASE_URL}/api/add-comment', json=comment_data)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Step 3: Test Drawing endpoint
print("\n3. Testing Drawing endpoint...")
drawing_image = create_test_image(width=300, height=200, color='red', label='Drawing')
drawing_data = {
    "pageNum": 0,
    "x": 100,
    "y": 300,
    "width": 200,
    "height": 120,
    "imageData": drawing_image
}
response = requests.post(f'{BASE_URL}/api/add-drawing', json=drawing_data)
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   Success: {result.get('success')}")
print(f"   Message: {result.get('message')}")

# Step 4: Test Signature endpoint
print("\n4. Testing Signature endpoint...")
signature_image = create_test_image(width=300, height=200, color='blue', label='Signature')
signature_data = {
    "pageNum": 0,
    "x": 100,
    "y": 450,
    "width": 180,
    "height": 100,
    "imageData": signature_image
}
response = requests.post(f'{BASE_URL}/api/add-signature', json=signature_data)
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   Success: {result.get('success')}")
print(f"   Message: {result.get('message')}")

print("\n" + "=" * 60)
print("✓ All tests completed!")
print("=" * 60)
