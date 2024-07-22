import base64
import json
import requests
import os

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.reader.BasicReader import BasicReader

from goldenverba.components.types import InputConfig

try:
    import markdownify
    from markdownify import markdownify as md
except Exception as e:
    pass

class HTMLReader(Reader):
    """
    The GithubReader downloads files from Github and ingests them into Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "HTML"
        self.type = "URL"
        self.requires_library=["markdownify"]
        self.description = "Downloads and ingests HTML from a URL."
        self.config = {
                    "URL": InputConfig(
                        type="text", value="https://weaviate.io/", description="Enter the URL to scrape the HTML", values=[]
                    ),
                    "Convert To Markdown": InputConfig(
                        type="bool", value=True, description="Should the HTML be converted into markdown?", values=[]
                    ),
                }

    async def load(
        self, config:dict, fileConfig: FileConfig
    ) -> list[Document]:
        

        reader = BasicReader()

        URL = config["URL"].value
        TO_MARKDOWN = bool(config["Convert To Markdown"].value)


        content, size = self.fetch_html_and_convert_to_markdown(URL, TO_MARKDOWN)

        newFileConfig = FileConfig(fileID=fileConfig.fileID, filename=URL, isURL=False, overwrite=fileConfig.overwrite, extension="md", source=URL, content=content, labels=fileConfig.labels, rag_config=fileConfig.rag_config, file_size=size, status=fileConfig.status, status_report=fileConfig.status_report)
        document = await reader.load(config, newFileConfig)

        return document

    
    def fetch_html_and_convert_to_markdown(self, url: str, markdown: bool) -> str:
        """
        Fetches the full HTML content of the given URL and converts it to Markdown.

        :param url: The URL of the web page to fetch.
        :return: A string containing the converted Markdown content.
        """
        try:
            # Fetch the HTML content of the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            html_content = response.text

            if markdown:
                content = md(html_content).encode('utf-8')
            else:
                content = html_content.encode('utf-8')

            base64_content = base64.b64encode(content).decode('utf-8')

            return (base64_content, len(content))
                


        except requests.RequestException as e:
            raise Exception(f"Failed to fetch HTML content from URL: {str(e)}")
