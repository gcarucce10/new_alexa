import requests
import json

url_post = "http://localhost:5000/perform_action"  # Replace with your Flask endpoint
url_get = "http://localhost:5000/action_attributes"  # Replace with your Flask endpoint
data = {"param": {"sides": 6}}  # Example parameter for the action

# Option 1: Using the 'json' argument (recommended for JSON)
response_post: requests.Response = requests.post(url_post, json=data)
response_get: requests.Response = requests.get(url_get)

# Option 2: Manually serializing and setting 'Content-Type' header
# headers = {'Content-Type': 'application/json'}
# response = requests.post(url, headers=headers, data=json.dumps(data))

print(response_post.status_code)
if response_post.status_code != 404: print(response_post.json()) # If your Flask server returns JSON
print(response_get.status_code)
if response_get.status_code != 404: print(response_get.json()) # If your Flask server returns JSON