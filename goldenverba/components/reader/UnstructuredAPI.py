import base64
import os
from datetime import datetime
import io

import requests
from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.components.types import FileData


class UnstructuredReader(Reader):
    """
    Unstructured API Reader
    """

    def __init__(self):
        super().__init__()
        self.file_types = [".pdf"]
        self.requires_env = ["UNSTRUCTURED_API_KEY"]
        self.name = "UnstructuredAPI"
        self.description = "Uses the Unstructured API to import multiple file types such as plain text and documents (.pdf, .csv). Requires an Unstructured API Key"

    def load(
        self, fileData: list[FileData], textValues: list[str], logging: list[dict]
    ) -> tuple[list[Document], list[str]]:

        documents = []

        url = os.environ.get(
            "UNSTRUCTURED_API_URL", "https://api.unstructured.io/general/v0/general"
        )
        api_key = os.environ.get("UNSTRUCTURED_API_KEY", "")

        if api_key == "":
            logging.append(
                {"type": "ERROR", "message": f"No Unstructed API Key detected"}
            )
            msg.warn(f"No Unstructed API Key detected")
            return documents, logging

        headers = {
            "accept": "application/json",
            "unstructured-api-key": api_key,
        }

        data = {
            "strategy": "auto",
        }

        for file in fileData:
            msg.info(f"Loading in {file.filename}")
            logging.append({"type": "INFO", "message": f"Importing {file.filename}"})

            file_bytes = io.BytesIO(base64.b64decode(file.content))
            file_data = {"files": (file.filename, file_bytes)}

            try:
                response = requests.post(
                    url, headers=headers, data=data, files=file_data
                )
                json_response = response.json()
                
                if "detail" in json_response:
                    msg.warn(
                        f"Failed to load {file.filename} : {json_response['detail']}"
                    )
                    logging.append(
                        {
                            "type": "ERROR",
                            "message": f"Failed to load {file.filename} : {json_response['detail']}",
                        }
                    )
                    continue

                full_content = ""
                for chunk in json_response:
                    if "text" in chunk:
                        text = str(chunk["text"])
                        full_content += text + " "

                if full_content == "":
                    msg.warn(f"Empty Text for {file.filename}")
                    logging.append(
                        {
                            "type": "WARNING",
                            "message": f"Empty Text for {file.filename}",
                        }
                    )
                    continue

                document = Document(
                    name=file.filename,
                    text=full_content,
                    type=self.config["document_type"].text,
                    timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    reader=self.name,
                )
                documents.append(document)

            except Exception as e:
                msg.warn(f"Failed to load {file.filename} : {str(e)}")
                logging.append(
                    {
                        "type": "WARNING",
                        "message": f"Failed to load {file.filename} : {str(e)}",
                    }
                )

        return documents, logging
