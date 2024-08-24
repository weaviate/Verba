import base64
import aiohttp
import asyncio
import os
from typing import List, Tuple

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.util import get_environment
from goldenverba.components.types import InputConfig


class FirecrawlReader(Reader):
    """
    FirecrawlReader uses the Firecrawl API to scrape or crawl websites and ingest them into Verba.
    """

    def __init__(self):
        super().__init__()
        self.name = "Firecrawl"
        self.type = "URL"
        self.description = "Use Firecrawl to scrape websites and ingest them into Verba"
        self.config = {
            "Mode": InputConfig(
                type="dropdown",
                value="Scrape",
                description="Switch between scraping and crawling. Note that crawling can take some time.",
                values=["Crawl", "Scrape"],
            ),
            "URLs": InputConfig(
                type="multi",
                value="",
                description="Add URLs to retrieve data from",
                values=[],
            ),
        }

        if os.getenv("FIRECRAWL_API_KEY") is None:
            self.config["Firecrawl API Key"] = InputConfig(
                type="password",
                value="",
                description="You can set your Firecrawl API Key or set it as environment variable `FIRECRAWL_API_KEY`",
                values=[],
            )

    async def load(self, config: dict, fileConfig: FileConfig) -> List[Document]:
        """
        Load documents from URLs using Firecrawl API.
        """
        reader = BasicReader()
        urls = config["URLs"].values
        mode = config["Mode"].value
        token = get_environment(
            config,
            "Firecrawl API Key",
            "FIRECRAWL_API_KEY",
            "No Firecrawl API Key detected",
        )

        raw_documents = await self.firecrawl(mode, urls, token)
        documents = []

        for title, content, source_url in raw_documents:
            content_bytes = content.encode("utf-8")
            base64_content = base64.b64encode(content_bytes).decode("utf-8")

            new_file_config = FileConfig(
                fileID=fileConfig.fileID,
                filename=title,
                isURL=False,
                overwrite=fileConfig.overwrite,
                extension="md",
                source=source_url,
                content=base64_content,
                labels=fileConfig.labels,
                rag_config=fileConfig.rag_config,
                file_size=len(content_bytes),
                status=fileConfig.status,
                status_report=fileConfig.status_report,
            )
            document = await reader.load(config, new_file_config)
            documents.append(document[0])

        return documents

    async def handle_response(self, response: aiohttp.ClientResponse) -> dict:
        """
        Handle the API response and raise an exception if the status is not 200.
        """
        if response.status != 200:
            text = await response.text()
            raise Exception(f"Firecrawl Error: {response.status}, {text}")
        return await response.json()

    async def firecrawl(
        self, mode: str, urls: List[str], token: str
    ) -> List[Tuple[str, str, str]]:
        """
        Perform scraping or crawling using Firecrawl API.
        """
        crawl_url = "https://api.firecrawl.dev/v0/crawl"
        scrape_url = "https://api.firecrawl.dev/v0/scrape"
        documents = []

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                request_data = {"url": url}
                if mode == "Scrape":
                    task = self.scrape_url(session, scrape_url, headers, request_data)
                else:
                    task = self.handle_crawl(session, crawl_url, headers, request_data)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    msg.warn(f"Failed to process URL: {str(result)}")
                else:
                    documents.extend(result)

        if not documents:
            raise Exception(
                "Firecrawl was not able to load any documents, please check your API Key and settings"
            )

        return documents

    async def scrape_url(
        self,
        session: aiohttp.ClientSession,
        scrape_url: str,
        headers: dict,
        request_data: dict,
    ) -> List[Tuple[str, str, str]]:
        """
        Scrape a single URL using Firecrawl API.
        """
        async with session.post(
            scrape_url, headers=headers, json=request_data
        ) as response:
            response_data = await self.handle_response(response)
            if "data" in response_data and response_data.get("success", False):
                return [
                    (
                        response_data["data"]["metadata"]["title"],
                        response_data["data"]["markdown"],
                        request_data["url"],
                    )
                ]
        return []

    async def handle_crawl(
        self,
        session: aiohttp.ClientSession,
        crawl_url: str,
        headers: dict,
        request_data: dict,
    ) -> List[Tuple[str, str, str]]:
        """
        Handle the crawling process for a single URL.
        """
        documents = []
        start_time = asyncio.get_event_loop().time()

        async with session.post(
            crawl_url, headers=headers, json=request_data
        ) as response:
            data = await self.handle_response(response)
            job_id = data.get("jobId")
            msg.info(f"Creating Firecrawl Job {job_id}")

            if job_id:
                documents = await self.poll_job_status(
                    session, crawl_url, headers, job_id, start_time
                )

        return documents

    async def poll_job_status(
        self,
        session: aiohttp.ClientSession,
        crawl_url: str,
        headers: dict,
        job_id: str,
        start_time: float,
    ) -> List[Tuple[str, str, str]]:
        """
        Poll the job status and retrieve results when completed.
        """
        max_retries = 60
        wait_time = 10
        documents = []

        for attempt in range(max_retries):
            elapsed_time = round(asyncio.get_event_loop().time() - start_time, 2)
            msg.info(
                f"Checking Firecrawl Job Status for {job_id} (Try: {attempt + 1}) ({elapsed_time}s)"
            )

            async with session.get(
                f"{crawl_url}/status/{job_id}", headers=headers
            ) as response:
                data = await self.handle_response(response)
                status = data.get("status")
                msg.info(f"Firecrawl Job Status: {status}")

                files = data.get("data", [])
                if files:
                    msg.info(f"{len(files)} Files scraped")

                if status == "completed":
                    msg.good("Firecrawl Job successful")
                    documents.extend(
                        (
                            file["metadata"]["title"],
                            file["markdown"],
                            file["metadata"]["sourceURL"],
                        )
                        for file in files
                    )
                    break

                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)

        return documents
