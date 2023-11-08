import glob
import base64
import os
import requests

from wasabi import msg
from pathlib import Path
from datetime import datetime

from goldenverba.components.reader.interface import Reader, InputForm
from goldenverba.components.reader.document import Document


class PDFReader(Reader):
    """
    The PDFReader reads .pdf files using Unstructured.
    """

    def __init__(self):
        super().__init__()
        self.file_types = [".pdf"]
        self.requires_env = ["UNSTRUCTURED_API_KEY"]
        self.name = "PDFReader"
        self.description = "Reads PDF files powered by unstructured.io"
        self.input_form = InputForm.UPLOAD.value

    def load(
        self,
        bytes: list[str] = [],
        contents: list[str] = [],
        paths: list[str] = [],
        fileNames: list[str] = [],
        document_type: str = "Documentation",
    ) -> list[Document]:
        """Ingest data into Weaviate
        @parameter: bytes : list[str] - List of bytes
        @parameter: contents : list[str] - List of string content
        @parameter: paths : list[str] - List of paths to files
        @parameter: fileNames : list[str] - List of file names
        @parameter: document_type : str - Document type
        @returns list[Document] - Lists of documents
        """

        documents = []

        # If paths exist
        if len(paths) > 0:
            for path in paths:
                if path != "":
                    data_path = Path(path)
                    if data_path.exists():
                        if data_path.is_file():
                            documents += self.load_file(data_path, document_type)
                        else:
                            documents += self.load_directory(data_path, document_type)
                    else:
                        msg.warn(f"Path {data_path} does not exist")

        # If bytes exist
        if len(bytes) > 0:
            if len(bytes) == len(fileNames):
                for byte, fileName in zip(bytes, fileNames):
                    documents += self.load_bytes(byte, fileName, document_type)

        # If content exist
        if len(contents) > 0:
            if len(contents) == len(fileNames):
                for content, fileName in zip(contents, fileNames):
                    document = Document(
                        name=fileName,
                        text=content,
                        type=document_type,
                        timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        reader=self.name,
                    )
                    documents.append(document)

        msg.good(f"Loaded {len(documents)} documents")
        return documents

    def load_bytes(self, bytes_string, fileName, document_type: str) -> list[Document]:
        """Loads a pdf bytes file
        @param bytes_string : str - PDF File bytes coming from the frontend
        @param fileName : str - Filename
        @param document_type : str - Document Type
        @returns list[Document] - Lists of documents
        """
        documents = []

        url = "https://api.unstructured.io/general/v0/general"

        headers = {
            "accept": "application/json",
            "unstructured-api-key": os.environ.get("UNSTRUCTURED_API_KEY", ""),
        }

        data = {
            "strategy": "auto",
        }

        decoded_bytes = base64.b64decode(bytes_string)
        with open("reconstructed.pdf", "wb") as file:
            file.write(decoded_bytes)

        file_data = {"files": open("reconstructed.pdf", "rb")}

        response = requests.post(url, headers=headers, data=data, files=file_data)

        json_response = response.json()

        full_content = ""

        for chunk in json_response:
            if "text" in chunk:
                text = chunk["text"]
                full_content += text + " "

        document = Document(
            text=full_content,
            type=document_type,
            name=str(fileName),
            link=str(fileName),
            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            reader=self.name,
        )
        documents.append(document)
        msg.good(f"Loaded {str(fileName)}")
        os.remove("reconstructed.pdf")
        return documents

    def load_file(self, file_path: Path, document_type: str) -> list[Document]:
        """Loads .pdf file
        @param file_path : Path - Path to file
        @param document_type : str - Document Type
        @returns list[Document] - Lists of documents
        """
        documents = []

        if file_path.suffix not in self.file_types:
            msg.warn(f"{file_path.suffix} not supported")
            return []

        url = "https://api.unstructured.io/general/v0/general"

        headers = {
            "accept": "application/json",
            "unstructured-api-key": os.environ.get("UNSTRUCTURED_API_KEY", ""),
        }

        data = {
            "strategy": "auto",
        }

        file_data = {"files": open(file_path, "rb")}

        response = requests.post(url, headers=headers, data=data, files=file_data)

        file_data["files"].close()

        json_response = response.json()

        full_content = ""

        for chunk in json_response:
            if "text" in chunk:
                text = chunk["text"]
                full_content += text + " "

        document = Document(
            text=full_content,
            type=document_type,
            name=str(file_path),
            link=str(file_path),
            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            reader=self.name,
        )
        documents.append(document)
        msg.good(f"Loaded {str(file_path)}")
        return documents

    def load_directory(self, dir_path: Path, document_type: str) -> list[Document]:
        """Loads .pdf files from a directory and its subdirectories.

        @param dir_path : Path - Path to directory
        @param document_type : str - Document Type
        @returns list[Document] - List of documents
        """
        # Initialize an empty dictionary to store the file contents
        documents = []

        # Convert dir_path to string, in case it's a Path object
        dir_path_str = str(dir_path)

        # Loop through each file type
        for file_type in self.file_types:
            # Use glob to find all the files in dir_path and its subdirectories matching the current file_type
            files = glob.glob(f"{dir_path_str}/**/*{file_type}", recursive=True)

            # Loop through each file
            for file in files:
                msg.info(f"Reading {str(file)}")
                with open(file, "r", encoding="utf-8") as f:
                    documents += self.load_file(file, document_type=document_type)

        msg.good(f"Loaded {len(documents)} documents")
        return documents
