import os
import httpx
import json
import logging
import lzstring
from urllib.parse import quote
from litellm import completion

logger = logging.getLogger(__name__)

def compress_and_encode(json_data):
    """Compress and encode JSON data for embedding in URL."""
    lz = lzstring.LZString()
    compressed = lz.compressToBase64(json_data)
    return quote(compressed)

def create_codesandbox(files):
    """Generate CodeSandbox URL based on the provided files."""
    parameters = {"files": files}
    parameters_json = json.dumps(parameters)
    encoded_compressed_parameters = compress_and_encode(parameters_json)
    sandbox_url = f"https://codesandbox.io/api/v1/sandboxes/define?parameters={encoded_compressed_parameters}"
    return sandbox_url

def is_valid_verification(response):
    """Check if the verification response is valid."""
    try:
        message_content = response['choices'][0]['message']['content'].strip().upper()
        return "VALID" in message_content
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing verification response: {e}")
        return False

def generate_code_files(prompt):
    response = completion(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert in generating clean, efficient, and modern code. "
                    "Generate only the necessary code files based on the given prompt. "
                    "Ensure the code is fully functional, formatted correctly, and includes all necessary dependencies. "
                    "Make sure to use correct import paths for all modules, including 'react-dom/client'. "
                    "The response should be a JSON object with each file name as a key and the code content as a value. "
                    "No additional text, markdown, or explanations should be included. "
                    "For example, respond with: "
                    '{"index.js": {"content": "code here"}, "App.css": {"content": "code here"}, "package.json": {"content": "code here"}}'
                )
            },
            {"role": "user", "content": prompt}
        ],

        functions=[
            {
                "name": "generate_code_files",
                "description": "Generates code files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "index.js": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"}
                            },
                            "required": ["content"]
                        },
                        "App.css": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"}
                            },
                            "required": ["content"]
                        },
                        "package.json": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"}
                            },
                            "required": ["content"]
                        },
                        "App.js": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"}
                            },
                            "required": ["content"]
                        }
                    },
                    "required": ["index.js", "App.css", "package.json", "App.js"]
                }
            }
        ],
        function_call="auto"
    )

    logger.info(f"Raw response: {response}")

    if response.choices[0].finish_reason == 'function_call':
        function_response = response.choices[0].message.function_call.arguments
        if not function_response:
            logger.error("Function call returned empty response.")
            return None

        verification_prompt = (
            "Please verify that the following code files are correct and functional. "
            "Respond with 'VALID' if the code is correct or 'INVALID' if there are issues. "
            f"Here are the code files: {function_response}"
        )

        valid_count = 0
        for _ in range(3):
            verification_response = completion(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in code verification."},
                    {"role": "user", "content": verification_prompt}
                ]
            )

            logger.info(f"Verification response: {verification_response}")
            if is_valid_verification(verification_response):
                valid_count += 1

        if valid_count >= 2:
            code_files = json.loads(function_response)
            logger.info(f"Verified code files: {code_files}")
            return code_files

    logger.error("No valid function call arguments found in the response")
    return None

def get_final_sandbox_url(sandbox_id):
    """Retrieve the final sandbox URL using the sandbox_id."""
    if sandbox_id:
        final_url = f"https://codesandbox.io/s/{sandbox_id}"
        return final_url
    return None

def generate_code(prompt):
    files = generate_code_files(prompt)
    if files:
        sandbox_url = create_codesandbox(files)
        return sandbox_url
    else:
        return None
