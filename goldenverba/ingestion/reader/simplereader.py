from datetime import datetime

from wasabi import msg

from goldenverba.ingestion.reader.interface import Reader, InputForm
from goldenverba.ingestion.reader.document import Document


class SimpleReader(Reader):
    """
    SimpleReader that receives a list of strings, it's used to receive loaded documents directly from the frontend
    """

    def __init__(self):
        self.file_types = [".txt", ".md", ".mdx"]
        self.name = "SimpleReader"
        self.requires_env = (
            []
        )  # The SimpleReader does not require any environment variables to work
        self.description = "Reads text files directly from the frontend."
        self.input_form = InputForm.UPLOAD.value

    def load(
        self,
        contents: list[str] = [],
        document_type: str = "Documentation",
    ) -> list[Document]:
        """Load data from text sources
        @parameter: contents : list[str] - List of text uploaded thorugh the frontend
        @parameter: document_type : str - Document type
        @returns list[Document] - List of Documents
        """

        documents = []

        for content in contents:
            split = content.split("<VERBASPLIT>")

            document = Document(
                name=split[0],
                text=split[1],
                type=document_type,
                timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                reader=self.name,
            )
            documents.append(document)

        msg.good(f"Loaded {len(documents)} documents")
        return documents
