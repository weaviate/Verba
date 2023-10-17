import glob
from datetime import datetime

from pathlib import Path
from wasabi import msg

from goldenverba.ingestion.reader.interface import Reader, InputForm
from goldenverba.ingestion.reader.document import Document


class PathReader(Reader):
    """
    PathReader for Verba
    """

    def __init__(self):
        super().__init__()
        self.file_types = [".txt", ".md", ".mdx"]
        self.name = "PathReader"
        self.requires_library = ["unstructured"]
        self.description = "Imports text files and directories from a path."
        self.input_form = InputForm.INPUT.value

    def load(
        self,
        contents: list[str] = [],
        document_type: str = "Documentation",
    ) -> list[Document]:
        """Load data from text sources
        @parameter: contents : list[str] - List of absolute paths to a file or a directory
        @parameter: document_type : str - Document type
        @returns list[Document] - List of Documents
        """

        documents = []

        for path_str in contents:
            if path_str != "":
                data_path = Path(path_str)
                if data_path.exists():
                    if data_path.is_file():
                        documents += self.load_file(data_path, document_type)
                    else:
                        documents += self.load_directory(data_path, document_type)
                else:
                    msg.warn(f"Path {data_path} does not exist")

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
