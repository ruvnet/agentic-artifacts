import logging
import os
import sys
import uvicorn
import threading
import webbrowser
from typing import Dict
from dotenv import load_dotenv
from litestar import Litestar, get
from litestar.response import Template
from litestar.static_files import StaticFilesConfig
from litestar.template import TemplateConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from agentic_artifacts.utils.config import check_environment
from agentic_artifacts.api.routes import home, generate_artifact, plan_artifact, overview_artifact

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def display_banner():
    print(r"""
   _                    _   _        _        _   _  __            _       
  /_\   __ _  ___ _ __ | |_(_) ___  /_\  _ __| |_(_)/ _| __ _  ___| |_ ___ 
 //_\\ / _` |/ _ \ '_ \| __| |/ __|//_\\| '__| __| | |_ / _` |/ __| __/ __|
/  _  | (_| |  __| | | | |_| | (__/  _  | |  | |_| |  _| (_| | (__| |_\__ \
\_/ \_/\__, |\___|_| |_|\__|_|\___\_/ \_|_|   \__|_|_|  \__,_|\___|\__|___/
       |___/                                                               
    """)

@get("/")
async def root() -> Template:
    return Template(template_name="index.html", context={"message": "Welcome to Agentic Artifacts"})

app = Litestar(
    route_handlers=[home, plan_artifact, overview_artifact, generate_artifact],
    template_config=TemplateConfig(
        directory="agentic_artifacts/ui/templates",
        engine=JinjaTemplateEngine
    ),
    static_files_config=[
        StaticFilesConfig(directories=["agentic_artifacts/ui/static"], path="/static")
    ]
)

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def open_browser():
    webbrowser.open("http://localhost:8000")

def main():
    load_dotenv()
    display_banner()
    
    print("Checking environment...")
    if not check_environment():
        print("Environment setup failed. Exiting.")
        sys.exit(1)
    
    print("Environment check passed.")
    
    print("Starting Litestar UI...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give the server a moment to start
    import time
    time.sleep(2)
    
    print("\nLitestar UI is now running.")
    print("Access the UI at: http://localhost:8000")
    print("To access from other devices on your network, use: http://<your-ip-address>:8000")
    
    open_browser()
    
    print("\nPress Ctrl+C to stop the server and exit.")
    
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\nExiting Agentic Artifacts. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
