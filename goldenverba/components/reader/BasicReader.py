import base64
import json
from datetime import datetime
import io

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.components.types import FileData

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
        self.name = "BasicReader"
        self.description = "Imports plain text, pdf, markdown, json and docx files."
        self.requires_library = ["pypdf", "docx"]

    def load(
        self, fileData: list[FileData], textValues: list[str], logging: list[dict]
    ) -> tuple[list[Document], list[str]]:

        documents = []
        
        for file in fileData:
            msg.info(f"Loading in {file.filename}")
            logging.append({"type": "INFO", "message": f"Importing {file.filename}"})

            decoded_bytes = base64.b64decode(file.content)

            if file.extension in ["txt", "md", "mdx"]:
                try:
                    original_text = decoded_bytes.decode("utf-8")
                    document = Document(
                        name=file.filename,
                        text=original_text,
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

            elif file.extension == "json":
                try:
                    decoded_bytes = base64.b64decode(file.content)
                    original_text = decoded_bytes.decode("utf-8")
                    json_obj = json.loads(original_text)
                    document = Document.from_json(json_obj)
                    documents.append(document)

                except Exception as e:
                    msg.warn(f"Failed to load {file.filename} : {str(e)}")
                    logging.append(
                        {
                            "type": "WARNING",
                            "message": f"Failed to load {file.filename} : {str(e)}",
                        }
                    )

            elif file.extension == "pdf":
                try:
                    pdf_bytes = io.BytesIO(base64.b64decode(file.content))

                    full_text = ""
                    reader = PdfReader(pdf_bytes)

                    for page in reader.pages:
                        full_text += page.extract_text() + "\n\n"

                    document = Document(
                        name=file.filename,
                        text=full_text,
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

            elif file.extension == "docx":
                try:
                    docx_bytes = io.BytesIO(base64.b64decode(file.content))

                    full_text = ""
                    reader = docx.Document(docx_bytes)

                    for paragraph in reader.paragraphs:
                        full_text += paragraph.text + "\n"
                    
                    document = Document(
                        name=file.filename,
                        text=full_text,
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

            else:
                msg.warn(
                    f"{file.filename} with extension {file.extension} not supported by BasicReader."
                )
                logging.append(
                    {
                        "type": "WARNING",
                        "message": f"{file.filename} with extension {file.extension} not supported by BasicReader.",
                    }
                )

        return documents, logging
