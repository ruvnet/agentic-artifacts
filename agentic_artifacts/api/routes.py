import logging
from typing import Dict, Any
from litestar import Litestar, get, Request
from litestar.response import Template
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.static_files import StaticFilesConfig
from litestar.template import TemplateConfig
from agentic_artifacts.services.code_generator import generate_code
from agentic_artifacts.services.sandbox_manager import create_codesandbox

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@get("/", template_name="index.html")
async def home(request: Request) -> Template:
    return Template(template_name="index.html", context={"message": "Welcome to Agentic Artifacts"})

@get("/generate")
async def generate_artifact(request: Request) -> Dict[str, Any]:
    try:
        prompt = request.query_params.get("prompt")
        logger.info(f"Received prompt: {prompt}")
        if not prompt:
            logger.error("No prompt provided")
            return {"error": "No prompt provided"}

        code_files = generate_code(prompt)
        if not code_files:
            logger.error(f"Failed to generate code for prompt: {prompt}")
            return {"error": "Failed to generate code"}

        logger.info(f"Generated code files: {code_files}")

        sandbox_url = create_codesandbox(code_files)
        if not sandbox_url:
            logger.error("Failed to create sandbox")
            return {"error": "Failed to create sandbox"}

        logger.info(f"Generated sandbox URL: {sandbox_url}")
        return {"preview_url": sandbox_url}
    except Exception as e:
        logger.exception("An error occurred during artifact generation")
        return {"error": str(e)}

app = Litestar(
    route_handlers=[home, generate_artifact],
    template_config=TemplateConfig(
        directory="agentic_artifacts/ui/templates",
        engine=JinjaTemplateEngine
    ),
    static_files_config=[
        StaticFilesConfig(directories=["agentic_artifacts/ui/static"], path="/static")
    ],
)
