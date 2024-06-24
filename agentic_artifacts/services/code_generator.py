# code_generator.py file that contains the code generation logic for generating code files and creating a CodeSandbox URL. The file defines functions to generate code files based on a prompt, create a CodeSandbox URL, verify the generated code, and return the final sandbox URL. The generate_code function is called from the generate_artifact route handler in the routes.py file to generate the code files and create the CodeSandbox URL. The code_generator module uses the Litellm completion function to interact with the GPT-4o model for code generation.
#code_generator.py agentic_artifacts/services/code_generator.py
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
    url = f"https://codesandbox.io/api/v1/sandboxes/define?json=1&parameters={encoded_compressed_parameters}"
    
    response = httpx.post(url)
    if response.status_code == 200:
        response_data = response.json()
        sandbox_id = response_data.get('sandbox_id')
        return {
            "sandbox_id": sandbox_id,
            "final_url": f"https://codesandbox.io/s/{sandbox_id}",
            "sandbox_url": f"https://{sandbox_id}.csb.app/"
        }
    else:
        logger.error(f"Error creating sandbox: {response.text}")
        return None

def is_valid_verification(response):
    """Check if the verification response is valid."""
    try:
        message_content = response['choices'][0]['message']['content'].strip().upper()
        return "VALID" in message_content
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing verification response: {e}")
        return False

def verify_and_refine_code(function_response, retry_count=3):
    verification_prompt = (
        "Please verify that the following code files are correct and functional. "
        "Respond with 'VALID' if the code is correct or 'INVALID' if there are issues. "
        "Evaluate the code for the following aspects: "
        "1. Correctness: Ensure the code does what is expected based on the prompt. "
        "2. Functionality: Verify that the code runs without errors and performs the intended task. "
        "3. Completeness: Check that all necessary files and dependencies are included. "
        "4. Formatting: Ensure the code is properly formatted and adheres to coding standards. "
        "5. Syntax: Verify that there are no syntax errors in the code. "
        "6. Best Practices: Ensure the code follows best practices for readability, maintainability, and performance. "
        "7. Deployment: Confirm that the code is ready to be deployed to CodeSandbox and includes necessary configurations. "
        f"Here are the code files: {function_response}"
    )

    for _ in range(retry_count):
        verification_response = completion(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in code verification."},
                {"role": "user", "content": verification_prompt}
            ]
        )
        logger.info(f"Verification response: {verification_response}")
        if is_valid_verification(verification_response):
            return True

    return False

def generate_code_files(prompt, timeout=320.0):
    try:
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
                        "Include error handling, comments, and modular code structure where applicable. "
                        "Provide multiple functionalities and configuration options if relevant. "
                        "Perform recursive self-assessment with three internal loops for code review and improvement. "
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
            function_call="auto",
            timeout=timeout
        )

        logger.info(f"Raw response: {response}")

        if response.choices[0].finish_reason == 'function_call':
            function_response = response.choices[0].message.function_call.arguments
            if not function_response:
                logger.error("Function call returned empty response.")
                return None

            # Try to load the function response as JSON
            try:
                code_files = json.loads(function_response)
            except json.JSONDecodeError as e:
                logger.error(f"JSONDecodeError: {e}")
                prompt += f"\nError encountered: {str(e)}"
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
                                "Include error handling, comments, and modular code structure where applicable. "
                                "Provide multiple functionalities and configuration options if relevant. "
                                "Perform recursive self-assessment with three internal loops for code review and improvement. "
                                "For example, respond with: "
                                '{"index.js": {"content": "code here"}, "App.css": {"content": "code here"}, "package.json": {"content": "code here"}}'
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    function_call="auto",
                    timeout=timeout
                )
                function_response = response.choices[0].message.function_call.arguments

                if not function_response:
                    logger.error("Retry failed: Function call returned empty response.")
                    return None

                code_files = json.loads(function_response)

            # Perform verification
            if verify_and_refine_code(function_response):
                logger.info(f"Verified code files: {code_files}")
                return code_files
            else:
                logger.error("Code verification failed after retries.")
                return None

        logger.error("No valid function call arguments found in the response")
        return None

    except Exception as e:
        logger.exception("An error occurred during code generation")
        raise

def get_final_sandbox_url(sandbox_id):
    """Retrieve the final sandbox URL using the sandbox_id."""
    if sandbox_id:
        final_url = f"https://codesandbox.io/s/{sandbox_id}"
        return final_url
    return None

def generate_code(prompt):
    files = generate_code_files(prompt)
    if files:
        sandbox_info = create_codesandbox(files)
        if sandbox_info:
            final_url = sandbox_info['final_url']
            print(f"Final URL: {final_url}")  # Print the final URL to the console
            return final_url
    return None
