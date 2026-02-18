import requests

url = "http://localhost:8000/api/ocr-ask"
files = {'image': ('test_ocr_input.png', open('test_ocr_input.png', 'rb'), 'image/png')}

try:
    print("Sending request to /api/ocr-ask...")
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
