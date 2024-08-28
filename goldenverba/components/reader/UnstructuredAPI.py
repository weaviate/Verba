import base64
import io
import os

import requests
from wasabi import msg
import aiohttp

from goldenverba.components.document import Document, create_document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.util import get_environment
from goldenverba.components.types import InputConfig


class UnstructuredReader(Reader):
    """
    Unstructured API Reader for importing multiple file types using the Unstructured.io API.
    """

    def __init__(self):
        super().__init__()
        self.requires_env = ["UNSTRUCTURED_API_KEY"]
        self.name = "Unstructured IO"
        self.description = "Uses the Unstructured API to import multiple file types such as plain text and documents"

        # Define configuration options
        self.config = {
            "Strategy": InputConfig(
                type="dropdown",
                value="auto",
                description="Set the extraction strategy",
                values=["auto", "hi_res", "ocr_only", "fast"],
            )
        }

        if os.getenv("UNSTRUCTURED_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="Set your Unstructured API Key here or set it as an environment variable `UNSTRUCTURED_API_KEY`",
                values=[],
            )

        if os.getenv("UNSTRUCTURED_API_URL") is None:
            self.config["API URL"] = InputConfig(
                type="text",
                value="https://api.unstructured.io/general/v0/general",
                description="Set the base URL to the Unstructured API or set it as an environment variable `UNSTRUCTURED_API_URL`",
                values=[],
            )

    async def load(
        self, config: dict[str, InputConfig], fileConfig: FileConfig
    ) -> list[Document]:
        """
        Load and process a file using the Unstructured API.
        """
        # Validate and get API credentials
        token = get_environment(
            config,
            "API Key",
            "UNSTRUCTURED_API_KEY",
            "No Unstructured API Key detected",
        )
        api_url = get_environment(
            config, "API URL", "UNSTRUCTURED_API_URL", "No Unstructured URL detected"
        )

        # Validate strategy
        strategy = config["Strategy"].value
        if strategy not in ["auto", "hi_res", "ocr_only", "fast"]:
            raise ValueError(f"Invalid strategy: {strategy}")

        headers = {
            "accept": "application/json",
            "unstructured-api-key": token,
        }

        msg.info(f"Loading {fileConfig.filename}")

        file_data = aiohttp.FormData()
        file_data.add_field("strategy", strategy)
        file_bytes = io.BytesIO(base64.b64decode(fileConfig.content))
        file_data.add_field(
            "files",
            file_bytes,
            filename=f"{fileConfig.filename}.{fileConfig.extension}",
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url, headers=headers, data=file_data
                ) as response:
                    response.raise_for_status()  # Raise an exception for bad status codes
                    json_response = await response.json()

                    if "detail" in json_response:
                        raise ValueError(f"API error: {json_response['detail']}")

                    file_content = "".join(
                        chunk.get("text", "") for chunk in json_response
                    )

                    return [create_document(file_content, fileConfig)]

        except requests.RequestException as e:
            raise Exception(
                f"Unstructured API request failed for {fileConfig.filename}: {str(e)}"
            )
        except Exception as e:
            raise Exception(f"Failed to process {fileConfig.filename}: {str(e)}")
