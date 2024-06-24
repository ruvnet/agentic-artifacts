import os
import httpx
import json
import time

# Define the API endpoint
url = "https://codesandbox.io/api/v1/sandboxes/define?json=1"

# Retrieve the API key from the environment variables
api_key = os.getenv('CODESANDBOX_API_KEY', '')

if not api_key:
    raise ValueError("API key not found. Please set the 'CODESANDBOX_API_KEY' environment variable.")

# Define the JSON payload
data = {
    "files": {
        "index.html": {
            "content": "<!DOCTYPE html><html><head><title>Hello World Button</title></head><body><button id=\"helloButton\">Click me!</button><script src=\"index.js\"></script></body></html>",
            "isBinary": False
        },
        "index.js": {
            "content": "document.getElementById(\"helloButton\").addEventListener(\"click\", function() { console.log(\"Hello, world, ruv!\"); alert(\"Hello, world, ruv!\"); });",
            "isBinary": False
        },
        "package.json": {
            "content": "{\"dependencies\": {}}",
            "isBinary": False
        }
    }
}

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Print headers and payload for debugging
print("Headers:", headers)
print("Payload:", json.dumps(data, indent=4))

# Function to make the POST request and handle errors
def make_request():
    try:
        response = httpx.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except httpx.HTTPStatusError as errh:
        return f"Http Error: {errh}"
    except httpx.RequestError as errc:
        return f"Error Connecting: {errc}"

# First request
print("First response:")
response_data = make_request()
print(response_data)
if isinstance(response_data, dict) and "sandbox_id" in response_data:
    sandbox_id = response_data["sandbox_id"]
    final_url = f"https://codesandbox.io/s/{sandbox_id}"
    print(f"Generated sandbox URL: {final_url}")

# Wait for 5 seconds
time.sleep(5)

# Second request
print("\nSecond response:")
response_data = make_request()
print(response_data)
if isinstance(response_data, dict) and "sandbox_id" in response_data:
    sandbox_id = response_data["sandbox_id"]
    final_url = f"https://codesandbox.io/s/{sandbox_id}"
    print(f"Generated sandbox URL: {final_url}")
