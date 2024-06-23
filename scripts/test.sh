#!/bin/bash

# Define the API endpoint
API_ENDPOINT="https://codesandbox.io/api/v1/sandboxes/define?json=1"

# Get the API key from the environment variable (GitHub Secret)
API_KEY=$CODESANDBOX_API_KEY

# Define the JSON payload
JSON_PAYLOAD='{
           "files": {
             "index.html": {
               "content": "<!DOCTYPE html><html><head><title>Hello World Button</title></head><body><button id=\"helloButton\">Click me!</button><script src=\"index.js\"></script></body></html>",
               "isBinary": false
             },
             "index.js": {
               "content": "document.getElementById(\"helloButton\").addEventListener(\"click\", function() { console.log(\"Hello, world, ruv!\"); alert(\"Hello, world, ruv!\"); });",
               "isBinary": false
             },
             "package.json": {
               "content": "{\"dependencies\": {}}",
               "isBinary": false
             }
           }
         }'

# Make the POST request
response=$(curl -s -X POST \
   -H "Content-Type:application/json" \
   -H "Authorization:Bearer $API_KEY" \
   -d "$JSON_PAYLOAD" \
   "$API_ENDPOINT")

# Extract the sandbox_id from the response
sandbox_id=$(echo $response | jq -r '.sandbox_id')

# Construct the URL
sandbox_url="https://codesandbox.io/s/$sandbox_id"

# Output the sandbox URL
echo "Sandbox URL: $sandbox_url"
