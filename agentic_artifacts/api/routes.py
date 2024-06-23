# routes.py file that contains the route handlers for the API. The handlers are defined using the @get decorator from Litestar. The handlers are then passed to the Litestar app along with the template and static files configuration.

import logging
from typing import Dict, Any
from litestar import Litestar, get, Request
from litestar.response import Template
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.static_files import StaticFilesConfig
from litestar.template import TemplateConfig
from agentic_artifacts.services.code_generator import generate_react_code, determine_sandbox_environment
from agentic_artifacts.services.sandbox_manager import create_codesandbox, check_sandbox_errors, fix_code_errors

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
        if not prompt:
            logger.error("No prompt provided")
            return {"error": "No prompt provided"}

        code = generate_react_code(prompt)
        if not code:
            logger.error("Failed to generate code")
            return {"error": "Failed to generate code"}

        environment = determine_sandbox_environment(prompt)
        sandbox_id = create_codesandbox(code, environment)
        if not sandbox_id:
            logger.error("Failed to create sandbox")
            return {"error": "Failed to create sandbox"}

        error = check_sandbox_errors(sandbox_id)
        while error:
            fixed_code = fix_code_errors(code, error)
            if not fixed_code:
                logger.error("Failed to fix code errors")
                return {"error": "Failed to fix code errors"}
            
            sandbox_id = create_codesandbox(fixed_code, environment)
            if not sandbox_id:
                logger.error("Failed to create sandbox with fixed code")
                return {"error": "Failed to create sandbox with fixed code"}
            
            error = check_sandbox_errors(sandbox_id)

        preview_url = f"https://codesandbox.io/embed/{sandbox_id}?view=preview&hidenavigation=1"
        return {"preview_url": preview_url}
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
