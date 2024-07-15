import base64
import json
from datetime import datetime
import io

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.components.types import FileData
from goldenverba.server.types import FileConfig

from goldenverba.server.ImportLogger import LoggerManager

try:
    from pypdf import PdfReader
except Exception:
    msg.warn("pypdf not installed, your base installation might be corrupted.")

try:
    import docx
except Exception:
    msg.warn("python-docx not installed, your base installation might be corrupted.")

class BasicReader(Reader):
    """
    The BasicReader reads .txt, .md, .mdx, .json, .pdf and .docx files.
    """

    def __init__(self):
        super().__init__()
        self.name = "Default"
        self.description = "Supports all text files (.txt, .md, .pdf, .docx, .json, .mdx)"
        self.requires_library = ["pypdf", "docx"]

    async def load(
        self, fileConfig: FileConfig
    ) -> list[Document]:

        document = None
    
        msg.info(f"Loading in {fileConfig.filename}")
        decoded_bytes = base64.b64decode(fileConfig.content)

        if fileConfig.extension in ["txt", "md", "mdx"]:
            try:
                original_text = decoded_bytes.decode("utf-8")
                document = Document(
                    title=fileConfig.filename,
                    content=original_text,
                    extension=fileConfig.extension,
                    labels=fileConfig.labels,
                    source=fileConfig.source,
                    meta={}
                )

            except Exception as e:
                msg.warn(f"Failed to load {fileConfig.filename} : {str(e)}")

        elif fileConfig.extension == "json":
            try:
                decoded_bytes = base64.b64decode(fileConfig.content)
                original_text = decoded_bytes.decode("utf-8")
                json_obj = json.loads(original_text)
                document = Document.from_json(json_obj)

            except Exception as e:
                msg.warn(f"Failed to load {fileConfig.filename} : {str(e)}")

        elif fileConfig.extension == "pdf":
            try:
                pdf_bytes = io.BytesIO(base64.b64decode(fileConfig.content))

                full_text = ""
                reader = PdfReader(pdf_bytes)

                for page in reader.pages:
                    full_text += page.extract_text() + "\n\n"

                document = Document(
                    title=fileConfig.filename,
                    content=full_text,
                    extension=fileConfig.extension,
                    labels=fileConfig.labels,
                    source=fileConfig.source,
                    meta={}
                )

            except Exception as e:
                msg.warn(f"Failed to load {fileConfig.filename} : {str(e)}")

        elif fileConfig.extension == "docx":
            try:
                docx_bytes = io.BytesIO(base64.b64decode(fileConfig.content))

                full_text = ""
                reader = docx.Document(docx_bytes)

                for paragraph in reader.paragraphs:
                    full_text += paragraph.text + "\n"
                
                document = Document(
                    title=fileConfig.filename,
                    content=full_text,
                    extension=fileConfig.extension,
                    labels=fileConfig.labels,
                    source=fileConfig.sourc,
                    meta={}
                )

            except Exception as e:
                msg.warn(f"Failed to load {fileConfig.filename} : {str(e)}")
        
        else:
            msg.warn(
                f"{fileConfig.filename} with extension {fileConfig.extension} not supported by BasicReader."
            )

        return document
