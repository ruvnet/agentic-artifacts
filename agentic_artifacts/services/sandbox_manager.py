import json
import logging
from lzstring import LZString
from urllib.parse import quote

logger = logging.getLogger(__name__)

def create_codesandbox(files):
    try:
        # Wrap the files dictionary in the expected structure
        parameters = {
            "files": files
        }

        # Convert the parameters to a JSON string
        parameters_json = json.dumps(parameters)

        # Compress the JSON string
        lz = LZString()
        compressed_parameters = lz.compressToBase64(parameters_json)

        # Encode the compressed string for the URL
        encoded_compressed_parameters = quote(compressed_parameters)

        # Construct the URL
        sandbox_url = f"https://codesandbox.io/embed/new?view=preview&hidenavigation=1&parameters={encoded_compressed_parameters}"
        return sandbox_url

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
