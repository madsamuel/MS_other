import requests

# Upload the PDF to Flask
with open('uploads/fresh_test.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://127.0.0.1:5000/api/upload', files=files)
    
print(f"Upload response status: {response.status_code}")
print(f"Response: {response.json()}")
