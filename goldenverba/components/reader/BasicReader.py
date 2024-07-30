import base64
import json
import io

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig

try:
    from pypdf import PdfReader
except Exception:
    msg.warn("pypdf not installed, your base installation might be corrupted.")

try:
    import spacy
except Exception:
    msg.warn("spacy not installed, your base installation might be corrupted.")

try:
    import docx
except Exception:
    msg.warn("python-docx not installed, your base installation might be corrupted.")

class BasicReader(Reader):
    """
    The BasicReader reads text and code files
    """

    def __init__(self):
        super().__init__()
        self.name = "Default"
        self.description = "Ingests all text and code files"
        self.requires_library = ["pypdf", "docx", "spacy"]

        self.nlp = spacy.blank("en")
        config = {"punct_chars": None}
        self.nlp.add_pipe("sentencizer", config=config)
        

    async def load(
        self, config:dict, fileConfig: FileConfig
    ) -> list[Document]:

        msg.info(f"Loading in {fileConfig.filename}")
        decoded_bytes = base64.b64decode(fileConfig.content)

        if fileConfig.extension in self.extension:
            fileContent = self.load_text_file(decoded_bytes, fileConfig)
        elif fileConfig.extension == "json":
            return self.load_json_file(decoded_bytes, fileConfig)
        elif fileConfig.extension == "pdf":
            fileContent = self.load_pdf_file(decoded_bytes, fileConfig)
        elif fileConfig.extension == "docx":
            fileContent = self.load_docx_file(decoded_bytes, fileConfig)
        else:
            raise Exception(f"{fileConfig.filename} with extension {fileConfig.extension} is not supported by BasicReader.")
        
        doc = self.nlp(fileContent)
    
        document = Document(
            title=fileConfig.filename,
            content=fileContent,
            extension=fileConfig.extension,
            labels=fileConfig.labels,
            source=fileConfig.source,
            fileSize=fileConfig.file_size,
            spacy_doc = doc,
            meta={}
        )

        return [document]
    
    def load_text_file(self, decoded_bytes: bytes, fileConfig: FileConfig) -> str:
        try:
            return decoded_bytes.decode("utf-8")
        except Exception as e:
            raise Exception(f"Failed to load {fileConfig.filename}: {str(e)}")

    def load_json_file(self, decoded_bytes: bytes, fileConfig: FileConfig) -> list[Document]:
        try:
            original_text = decoded_bytes.decode("utf-8")
            json_obj = json.loads(original_text)
            document = Document.from_json(json_obj)
            if document is not None:
                return [document]
            else:
                return [Document(
                    title=fileConfig.filename,
                    content=original_text,
                    extension=fileConfig.extension,
                    labels=fileConfig.labels,
                    source=fileConfig.source,
                    fileSize=fileConfig.file_size,
                    meta={}
                )]
        except Exception as e:
            raise Exception(f"Failed to load {fileConfig.filename}: {str(e)}")

    def load_pdf_file(self, decoded_bytes: bytes, fileConfig: FileConfig) -> str:
        try:
            pdf_bytes = io.BytesIO(decoded_bytes)
            reader = PdfReader(pdf_bytes)
            full_text = "\n\n".join(page.extract_text() for page in reader.pages)
            return full_text
        except Exception as e:
            raise Exception(f"Failed to load {fileConfig.filename}: {str(e)}")

    def load_docx_file(self, decoded_bytes: bytes, fileConfig: FileConfig) -> str:
        try:
            docx_bytes = io.BytesIO(decoded_bytes)
            reader = docx.Document(docx_bytes)
            full_text = "\n".join(paragraph.text for paragraph in reader.paragraphs)
            return full_text
        except Exception as e:
            raise Exception(f"Failed to load {fileConfig.filename}: {str(e)}")