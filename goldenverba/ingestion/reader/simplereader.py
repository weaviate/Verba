from datetime import datetime
import glob
import base64

from wasabi import msg
from pathlib import Path

from goldenverba.ingestion.reader.interface import Reader, InputForm
from goldenverba.ingestion.reader.document import Document


class SimpleReader(Reader):
    """
    SimpleReader that receives a list of strings, it's used to receive loaded documents directly from the frontend
    """

    def __init__(self):
        super().__init__()
        self.file_types = [".txt", ".md", ".mdx"]
        self.name = "SimpleReader"
        self.description = "Reads text and markdown files"
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
        @returns list[str] - List of strings
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
                    decoded_bytes = base64.b64decode(byte)
                    try:
                        original_text = decoded_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        msg.fail(
                            f"Error decoding text for file {fileName}. The file might not be a text file."
                        )
                        continue

                    document = Document(
                        name=fileName,
                        text=original_text,
                        type=document_type,
                        timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        reader=self.name,
                    )
                    documents.append(document)

        # If content exist
        if len(contents) > 0:
            if len(bytes) == len(fileNames):
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

    def load_file(self, file_path: Path, document_type: str) -> list[Document]:
        """Loads text file
        @param dir_path : Path - Path to directory
        @param document_type : str - Document Type
        @returns list[Document] - Lists of documents
        """
        documents = []

        if file_path.suffix not in self.file_types:
            msg.warn(f"{file_path.suffix} not supported")
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            msg.info(f"Reading {str(file_path)}")
            document = Document(
                text=f.read(),
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
        """Loads text files from a directory and its subdirectories.

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
                    document = Document(
                        text=f.read(),
                        type=document_type,
                        name=str(file),
                        link=str(file),
                        timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        reader=self.name,
                    )

                    documents.append(document)

        msg.good(f"Loaded {len(documents)} documents")
        return documents
