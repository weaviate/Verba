import base64
import io

import requests
from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.util import get_environment

from goldenverba.components.types import InputConfig


class UnstructuredReader(Reader):
    """
    Unstructured API Reader
    """

    def __init__(self):
        super().__init__()
        self.requires_env = ["UNSTRUCTURED_API_KEY"]
        self.name = "Unstructured IO"
        self.description = "Uses the Unstructured API to import multiple file types such as plain text and documents"
        self.config = {
            "API Key": InputConfig(
                type="password", value="", description="You can set your Unstructured API Key here, it will overwrite the environment variable: UNSTRUCTURED_API_KEY", values=[]
            ),
            "Strategy": InputConfig(
                type="dropdown",
                value="auto",
                description="Set the extraction strategy", values=["auto", "hi_res", "ocr_only", "fast"]
            ),
            "API URL": InputConfig(
                type="text",
                value="https://api.unstructured.io/general/v0/general",
                description="Set the URL to the API", values=[]
            ),
        }

    async def load(
        self, config: dict,  fileConfig: FileConfig
    ) -> list[Document]:

        token = get_environment(config["API Key"].value, "UNSTRUCTURED_API_KEY", "No Unstructured API Key detected")
        api_url = config["API URL"].value
        strategy = config["Strategy"].value

        headers = {
            "accept": "application/json",
            "unstructured-api-key": token,
        }

        data = {
            "strategy": strategy,
        }

        msg.info(f"Loading in {fileConfig.filename}")

        file_bytes = io.BytesIO(base64.b64decode(fileConfig.content))
        file_data = {"files": (f"{fileConfig.filename}.{fileConfig.extension}", file_bytes)}

        try:
            response = requests.post(
                api_url, headers=headers, data=data, files=file_data
            )
            json_response = response.json()
            
            if "detail" in json_response:
                raise Exception(f"Failed to read {fileConfig.filename} : {json_response['detail']}")

            document = Document(
                title=fileConfig.filename,
                content="".join(chunk.get("text","") for chunk in json_response),
                extension=fileConfig.extension,
                labels=fileConfig.labels,
                source=fileConfig.source,
                fileSize=fileConfig.file_size,
                meta={}
            )

            return [document]

        except Exception as e:
            raise Exception(f"Unstructed API failed to load {fileConfig.filename} : {str(e)}")
    