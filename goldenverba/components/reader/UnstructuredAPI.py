import base64
import io
import os

import requests
from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.util import get_environment

from goldenverba.components.types import InputConfig

try:
    import spacy
except Exception:
    msg.warn("spacy not installed, your base installation might be corrupted.")

class UnstructuredReader(Reader):
    """
    Unstructured API Reader
    """

    def __init__(self):
        super().__init__()
        self.requires_env = ["UNSTRUCTURED_API_KEY"]
        self.name = "Unstructured IO"
        self.description = "Uses the Unstructured API to import multiple file types such as plain text and documents"

        self.nlp = spacy.blank("en")
        config = {"punct_chars": None}
        self.nlp.add_pipe("sentencizer", config=config)

        self.config = {
            "Strategy": InputConfig(
                type="dropdown",
                value="auto",
                description="Set the extraction strategy", values=["auto", "hi_res", "ocr_only", "fast"]
            )
        }

        if os.getenv("UNSTRUCTURED_API_KEY") is None:
            self.config["API Key"] = InputConfig(type="password", value="", description="Set your Unstructured API Key here or set it as an environment variable `UNSTRUCTURED_API_KEY` ", values=[])
        if os.getenv("UNSTRUCTURED_API_URL") is None:
            self.config["API URL"] = InputConfig(type="text",value="https://api.unstructured.io/general/v0/general",description="Set the base URL to the Unstructured API or set it as an environment variable `UNSTRUCTURED_API_URL`", values=[])



    async def load(
        self, config: dict,  fileConfig: FileConfig
    ) -> list[Document]:

        token = get_environment(config,"API Key", "UNSTRUCTURED_API_KEY", "No Unstructured API Key detected")
        api_url = get_environment(config,"API URL", "UNSTRUCTURED_API_URL", "No Unstructured URL detected")

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
            
            fileContent = "".join(chunk.get("text","") for chunk in json_response)

            doc = self.nlp(fileContent)

            document = Document(
                title=fileConfig.filename,
                content=fileContent,
                extension=fileConfig.extension,
                labels=fileConfig.labels,
                source=fileConfig.source,
                fileSize=fileConfig.file_size,
                spacy_doc=doc,
                meta={}
            )

            return [document]

        except Exception as e:
            raise Exception(f"Unstructed API failed to load {fileConfig.filename} : {str(e)}")
    