import requests

url = "http://localhost:8000/api/ocr-ask"

# We'll use the same image but adds a specific text constraint
files = {'image': ('test_ocr_input.png', open('test_ocr_input.png', 'rb'), 'image/png')}
data = {'text': 'Limit the results to the top 3 states'}

try:
    print("Sending request to /api/ocr-ask with text input...")
    response = requests.post(url, files=files, data=data) 
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
