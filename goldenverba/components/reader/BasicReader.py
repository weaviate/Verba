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
        self, config:dict, fileConfig: FileConfig
    ) -> list[Document]:

        document = None
    
        msg.info(f"Loading in {fileConfig.filename}")
        decoded_bytes = base64.b64decode(fileConfig.content)
        fileContent = ""

        if fileConfig.extension in ["txt", "md", "mdx"]:
            try:
                fileContent = decoded_bytes.decode("utf-8")
            except Exception as e:
                raise Exception(f"Failed to load {fileConfig.filename} : {str(e)}")

        elif fileConfig.extension == "json":
            try:
                decoded_bytes = base64.b64decode(fileConfig.content)
                original_text = decoded_bytes.decode("utf-8")
                json_obj = json.loads(original_text)
                document = Document.from_json(json_obj)

                if document is not None:
                    return [document]
            
                else:
                    fileContent = original_text

            except Exception as e:
                raise Exception(f"Failed to load {fileConfig.filename} : {str(e)}")
            
        elif fileConfig.extension == "pdf":
            try:
                pdf_bytes = io.BytesIO(base64.b64decode(fileConfig.content))

                full_text = ""
                reader = PdfReader(pdf_bytes)

                for page in reader.pages:
                    full_text += page.extract_text() + "\n\n"

                fileContent = full_text

            except Exception as e:
                raise Exception(f"Failed to load {fileConfig.filename} : {str(e)}")

        elif fileConfig.extension == "docx":
            try:
                docx_bytes = io.BytesIO(base64.b64decode(fileConfig.content))

                full_text = ""
                reader = docx.Document(docx_bytes)

                for paragraph in reader.paragraphs:
                    full_text += paragraph.text + "\n"

                fileContent = full_text

            except Exception as e:
                raise Exception(f"Failed to load {fileConfig.filename} : {str(e)}")
        
        else:
            raise Exception(f"{fileConfig.filename} with extension {fileConfig.extension} not supported by BasicReader.")

        document = Document(
            title=fileConfig.filename,
            content=fileContent,
            extension=fileConfig.extension,
            labels=fileConfig.labels,
            source=fileConfig.source,
            fileSize=fileConfig.file_size,
            meta={}
        )

        return [document]