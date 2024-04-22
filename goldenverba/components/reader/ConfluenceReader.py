import os
from datetime import datetime

from dotenv import load_dotenv

from goldenverba.components.connector.ConfluenceConnector import ConfluenceConnector
from goldenverba.components.reader.document import Document
from goldenverba.components.reader.interface import Reader, InputForm

load_dotenv()


class ConfluenceReader(Reader):
    """
    The ConfluenceReader downloads pages from Confluence and ingests them into Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "ConfluenceReader"
        self.requires_env = ["ATLASSIAN_URL", "CONFLUENCE_TOKEN"]
        self.description = "Downloads pages from a Confluence and ingests it into Verba."
        self.input_form = InputForm.INPUT.value

        url = os.getenv('ATLASSIAN_URL')
        access_token = os.getenv('CONFLUENCE_TOKEN')
        self.confluence_connector = ConfluenceConnector(url, access_token)

    def load(
            self,
            bytes: list[str] = None,
            contents: list[str] = None,
            paths: list[str] = None,
            fileNames: list[str] = None,
            document_type: str = "Documentation",
    ) -> list[Document]:
        """Ingest data into Weaviate
        @parameter: bytes : list[str] - List of bytes
        @parameter: contents : list[str] - List of string content
        @parameter: paths : list[str] - List of paths to files
        @parameter: fileNames : list[str] - List of file names
        @parameter: document_type : str - Document type
        @returns list[Document] - Lists of documents.
        """

        space = 'SCO'  # FIXME: from parameters

        documents = []

        space_data = self.confluence_connector.getSpace(space)

        homepage_link: str = space_data.get("_expandable").get("homepage")
        homepage_id = homepage_link.split("/")[-1]

        # TODO keep arborescence for path build (breadcrumb)
        pending_page_ids = [homepage_id]
        explored_page_ids = []

        while len(pending_page_ids) > 0:
            page_id = pending_page_ids.pop()
            explored_page_ids.append(page_id)
            print('Exploring page:', page_id)

            page_data = self.confluence_connector.getPage(page_id, params={"expand": "body.storage"})
            children = self.confluence_connector.getChildren(page_id)

            content = page_data.get("body").get("storage").get("value")
            print('Content:', content[:100] + '...')
            if content != "":
                documents.append(self.build_document(page_data, document_type))

            for child_page in children:
                child_page_id = child_page.get("id")
                print('Child page:', child_page_id)
                if (
                        child_page_id not in explored_page_ids
                        and child_page_id not in pending_page_ids
                ):
                    pending_page_ids.append(child_page_id)

        return documents

    def build_document(self, page_data, document_type):
        page_content = page_data.get("body").get("storage").get("value")
        page_title = page_data.get("title")
        print('Page title:', page_title)
        page_path = page_data.get('_links').get('webui')
        print('Page path:', page_path)
        document = Document(
            text=page_content,
            type=document_type,
            name=page_title,
            link=f"{self.confluence_connector.url}{page_path}",
            path=f"",
            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            reader=self.name,
        )
        return document
