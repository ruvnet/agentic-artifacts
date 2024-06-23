import json
import logging
from litellm import completion
from lzstring import LZString
from urllib.parse import quote

logger = logging.getLogger(__name__)

def is_valid_verification(response):
    """Check if the verification response is valid."""
    try:
        message_content = response.choices[0].message['content'].strip().upper()
        return "VALID" in message_content
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing verification response: {e}")
        return False

def compress_and_encode(json_data):
    """Compress and encode JSON data for embedding in URL."""
    lz = LZString()
    compressed = lz.compressToBase64(json_data)
    return quote(compressed)

def generate_code(prompt, max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        try:
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
                    attempt += 1
                    continue

                # Verify the generated code with a council of experts approach
                verification_prompt = (
                    "Please verify that the following code files are correct and functional. "
                    "Respond with 'VALID' if the code is correct or 'INVALID' if there are issues. "
                    "Here are the code files: "
                    f"{function_response}"
                )

                logger.info(f"Verification prompt: {verification_prompt}")

                valid_count = 0
                for _ in range(3):  # Use 3 verifications
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

                if valid_count >= 2:  # At least 2 out of 3 verifications must be valid
                    # Convert the verified response to JSON
                    code_files = json.loads(function_response)
                    logger.info(f"Verified code files: {code_files}")

                    # Wrap the files dictionary in the expected structure
                    parameters = {
                        "files": code_files
                    }

                    # Convert the parameters to a JSON string
                    parameters_json = json.dumps(parameters)

                    # Compress and encode the JSON string
                    encoded_compressed_parameters = compress_and_encode(parameters_json)

                    # Construct the URL
                    sandbox_url = f"https://codesandbox.io/embed/new?view=preview&hidenavigation=1&parameters={encoded_compressed_parameters}"
                    logger.info(f"Generated sandbox URL: {sandbox_url}")

                    return sandbox_url

            logger.error("No valid function call arguments found in the response")

        except Exception as e:
            logger.error(f"Error generating code on attempt {attempt + 1}: {e}")
            attempt += 1

    logger.error("Exceeded maximum attempts to generate code")
    return None

# Example usage
prompt = "Create a simple React application that displays a 'Hello World' button. When the button is clicked, it should show an alert saying 'Hello, World!'."
generated_sandbox_url = generate_code(prompt)
print(generated_sandbox_url)
