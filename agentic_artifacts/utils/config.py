import os
from dotenv import load_dotenv

def check_environment():
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY", "CODESANDBOX_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return False
    
    return True