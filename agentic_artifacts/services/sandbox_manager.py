import json
import logging
from lzstring import LZString
from urllib.parse import quote
import requests
from litellm import completion

logger = logging.getLogger(__name__)

def compress_and_encode(json_data):
    """Compress and encode JSON data for embedding in URL."""
    lz = LZString()
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
                    "Ensure the code is fully functional and formatted correctly. "
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

def generate_code(prompt):
    files = generate_code_files(prompt)
    if files:
        sandbox_url = create_codesandbox(files)
        if sandbox_url:
            logger.info(f"Generated sandbox URL: {sandbox_url}")
            response = requests.get(sandbox_url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to retrieve sandbox URL. Status code: {response.status_code}")
                return None
        else:
            logger.error("Failed to create sandbox URL.")
            return None
    else:
        logger.error("Failed to generate code files.")
        return None

if __name__ == "__main__":
    prompt = "Create a simple React application that displays a 'Hello World' button. When the button is clicked, it should show an alert saying 'Hello, World!'."
    generated_sandbox_response = generate_code(prompt)
    if generated_sandbox_response:
        print(f"INFO:agentic_artifacts.api.routes:Generated code files: {generated_sandbox_response}")
    else:
        print("ERROR:agentic_artifacts.api.routes:Failed to generate code files.")
