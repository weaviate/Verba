import base64
import os
from datetime import datetime
import io

import requests
from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig

from goldenverba.server.ImportLogger import LoggerManager
from goldenverba.components.types import InputConfig


class UnstructuredReader(Reader):
    """
    Unstructured API Reader
    """

    def __init__(self):
        super().__init__()
        self.file_types = [".pdf"]
        self.requires_env = ["UNSTRUCTURED_API_KEY"]
        self.name = "Unstructured"
        self.description = "Uses the Unstructured API to import multiple file types such as plain text and documents (.pdf, .csv). Requires an Unstructured API Key"
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

        document = None

        if config["API Key"].value == "":
            API_KEY = os.environ.get("UNSTRUCTURED_API_KEY")
            if API_KEY is None:
                raise Exception(f"No Unstructured API Key detected")
        else:
            API_KEY = config["API Key"].value

        API_URL = config["API URL"].value
        STRATEGY = config["Strategy"].value

        headers = {
            "accept": "application/json",
            "unstructured-api-key": API_KEY,
        }

        data = {
            "strategy": STRATEGY,
        }

        msg.info(f"Loading in {fileConfig.filename}")
        file_bytes = io.BytesIO(base64.b64decode(fileConfig.content))
        file_data = {"files": (f"{fileConfig.filename}.{fileConfig.extension}", file_bytes)}

        try:
            response = requests.post(
                API_URL, headers=headers, data=data, files=file_data
            )
            json_response = response.json()
            
            if "detail" in json_response:
                raise Exception(f"Failed to read {fileConfig.filename} : {json_response['detail']}")

            full_content = ""
            for chunk in json_response:
                if "text" in chunk:
                    text = str(chunk["text"])
                    full_content += text + " "

            document = Document(
                title=fileConfig.filename,
                content=full_content,
                extension=fileConfig.extension,
                labels=fileConfig.labels,
                source=fileConfig.source,
                fileSize=fileConfig.file_size,
                meta={}
            )

            return document

        except Exception as e:
            raise Exception(f"Failed to load {fileConfig.filename} : {str(e)}")