import base64
import aiohttp
from typing import Tuple, List
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.types import InputConfig

try:
    from markdownify import markdownify as md
except ImportError:
    md = None


class HTMLReader(Reader):
    """
    The HTMLReader downloads HTML content from URLs and ingests it into Weaviate.
    It can optionally fetch linked pages recursively.
    """

    def __init__(self):
        super().__init__()
        self.name = "HTML"
        self.type = "URL"
        self.requires_library = ["markdownify", "beautifulsoup4"]
        self.description = (
            "Downloads and ingests HTML from a URL, with optional recursive fetching."
        )
        self.config = {
            "URLs": InputConfig(
                type="multi",
                value="",
                description="Add URLs to retrieve data from",
                values=[],
            ),
            "Convert To Markdown": InputConfig(
                type="bool",
                value=False,
                description="Should the HTML be converted into markdown?",
                values=[],
            ),
            "Recursive": InputConfig(
                type="bool",
                value=False,
                description="Fetch linked pages recursively",
                values=[],
            ),
            "Max Depth": InputConfig(
                type="number",
                value=3,
                description="Maximum depth for recursive fetching",
                values=[],
            ),
        }

    async def load(self, config: dict, fileConfig: FileConfig) -> list[Document]:
        reader = BasicReader()
        urls = config["URLs"].values
        to_markdown = config["Convert To Markdown"].value
        recursive = config["Recursive"].value
        max_depth = int(config["Max Depth"].value)

        documents = []
        processed_urls = set()

        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    await self.process_url(
                        url,
                        to_markdown,
                        recursive,
                        max_depth,
                        0,
                        session,
                        reader,
                        fileConfig,
                        documents,
                        processed_urls,
                    )
                except Exception as e:
                    msg.warn(f"Failed to process URL {url}: {str(e)}")

        return documents

    async def process_url(
        self,
        url: str,
        to_markdown: bool,
        recursive: bool,
        max_depth: int,
        current_depth: int,
        session: aiohttp.ClientSession,
        reader: BasicReader,
        fileConfig: FileConfig,
        documents: List[Document],
        processed_urls: set,
    ):
        if url in processed_urls or current_depth > max_depth:
            return

        processed_urls.add(url)

        try:
            content, size, _html = await self.fetch_html_and_convert(
                session, url, to_markdown
            )
            new_file_config = FileConfig(
                fileID=fileConfig.fileID,
                filename=url,
                isURL=False,
                overwrite=fileConfig.overwrite,
                extension="md" if to_markdown else "html",
                source=url,
                content=content,
                labels=fileConfig.labels,
                rag_config=fileConfig.rag_config,
                file_size=size,
                status=fileConfig.status,
                status_report=fileConfig.status_report,
                metadata=fileConfig.metadata,
            )
            document = await reader.load(self.config, new_file_config)
            documents.extend(document)

            if recursive and current_depth < max_depth:
                linked_urls = self.extract_links(_html, url)
                for linked_url in linked_urls:
                    await self.process_url(
                        linked_url,
                        to_markdown,
                        recursive,
                        max_depth,
                        current_depth + 1,
                        session,
                        reader,
                        fileConfig,
                        documents,
                        processed_urls,
                    )
        except Exception as e:
            msg.warn(f"Failed to process URL {url}: {str(e)}")

    async def fetch_html_and_convert(
        self, session: aiohttp.ClientSession, url: str, to_markdown: bool
    ) -> Tuple[str, int, str]:
        """
        Fetches the HTML content of the given URL and optionally converts it to Markdown.

        :param session: The aiohttp ClientSession to use for the request.
        :param url: The URL of the web page to fetch.
        :param to_markdown: Whether to convert the HTML to Markdown.
        :return: A tuple containing the base64-encoded content and its size.
        """
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                html_content = await response.text()

            if to_markdown:
                if md is None:
                    raise ImportError("markdownify is required for Markdown conversion")
                content = md(html_content).encode("utf-8")
            else:
                content = html_content.encode("utf-8")

            base64_content = base64.b64encode(content).decode("utf-8")
            return base64_content, len(content), html_content

        except aiohttp.ClientError as e:
            raise Exception(f"Failed to fetch HTML content from URL: {str(e)}")
        except ImportError as e:
            raise Exception(f"Markdown conversion failed: {str(e)}")

    def extract_links(self, html_content: str, base_url: str) -> List[str]:
        """
        Extracts links from the HTML content and returns absolute URLs.

        :param html_content: The HTML content to parse.
        :param base_url: The base URL to resolve relative links.
        :return: A list of absolute URLs found in the HTML content.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            absolute_url = urljoin(base_url, href)
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                links.append(absolute_url)
        return links
