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


class UpstageDocumentParseReader(Reader):
    """
    Upstage Document Parse API Reader for converting documents to structured HTML format.
    """

    def __init__(self):
        super().__init__()
        self.requires_env = ["UPSTAGE_API_KEY"]
        self.name = "Upstage Parser"
        self.description = "Uses the Upstage Document Parse API to convert documents into structured HTML format"

        if os.getenv("UPSTAGE_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="Set your Upstage API Key here or set it as an environment variable `UPSTAGE_API_KEY`",
                values=[],
            )

        if os.getenv("UPSTAGE_API_URL") is None:
            self.config["API URL"] = InputConfig(
                type="text",
                value="https://api.upstage.ai/v1/document-ai/document-parse",
                description="Set the base URL to the Upstage API",
                values=[],
            )

    async def load(
        self, config: dict[str, InputConfig], fileConfig: FileConfig
    ) -> list[Document]:
        """
        Load and process a file using the Upstage Document Parse API.
        """
        # Get API credentials
        token = get_environment(
            config,
            "API Key",
            "UPSTAGE_API_KEY",
            "No Upstage API Key detected",
        )
        api_url = get_environment(
            config, "API URL", "UPSTAGE_API_URL", "No Upstage API URL detected"
        )

        headers = {
            "Authorization": f"Bearer {token}",
        }

        msg.info(f"Loading {fileConfig.filename}")

        file_data = aiohttp.FormData()
        file_bytes = io.BytesIO(base64.b64decode(fileConfig.content))
        file_data.add_field(
            "document",
            file_bytes,
            filename=f"{fileConfig.filename}.{fileConfig.extension}",
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url, headers=headers, data=file_data
                ) as response:
                    response.raise_for_status()
                    json_response = await response.json()

                    if "content" not in json_response:
                        raise ValueError(f"API error: Invalid response format")

                    # Extract text content from HTML
                    html_content = json_response["content"]["html"]
                    # You might want to add HTML to text conversion here
                    # For now, we'll use the HTML content directly
                    return [create_document(html_content, fileConfig)]

        except aiohttp.ClientError as e:
            raise Exception(
                f"Upstage API request failed for {fileConfig.filename}: {str(e)}"
            )
        except Exception as e:
            raise Exception(f"Failed to process {fileConfig.filename}: {str(e)}")
