import requests
import json
import time

# Send a request to add a text box
data = {
    "pageNum": 0,
    "x": 100,
    "y": 150,
    "width": 200,
    "height": 30,
    "text": "TEST TEXT - " + time.strftime("%H:%M:%S"),
    "fontSize": 12,
    "color": "#FF0000"
}

response = requests.post('http://127.0.0.1:5000/api/add-textbox', json=data)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Success: {result.get('success')}")
print(f"Error: {result.get('error')}")
if 'textbox' in result:
    print(f"Textbox added: {result['textbox']['text']}")
