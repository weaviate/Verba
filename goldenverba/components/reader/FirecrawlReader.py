import base64
import json
import requests
import aiohttp
import asyncio

from wasabi import msg
import httpx

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.util import get_environment

from goldenverba.components.types import InputConfig

class FirecrawlReader(Reader):
    """
    The FirecrawlReader downloads files from Github and ingests them into Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "Firecrawl"
        self.type = "URL"
        self.description = "Use Firecrawl to scrape websites and ingest them into Verba"
        self.config = {
                    "Firecrawl API Key": InputConfig(
                        type="password",
                        value="",
                        description="You can set your Firecrawl API Key or set it as environment variable `FIRECRAWL_API_KEY`", values=[]
                    ),
                    "Mode": InputConfig(
                        type="dropdown", value="Scrape", description="Switch between scraping and crawling. Note that crawling can take some time.", values=["Crawl","Scrape"]
                    ),
                    "URLs": InputConfig(
                        type="multi", value="", description="Add URLs to retrieve data from", values=[]
                    )
                }

    async def load(
        self, config:dict, fileConfig: FileConfig
    ) -> list[Document]:
        
        reader = BasicReader()

        urls = config["URLs"].values
        mode = config["Mode"].value
        token = get_environment(config["Firecrawl API Key"].value,"FIRECRAWL_API_KEY","No Firecrawl API Key detected")


        raw_documents = await self.firecrawl(mode, urls, token)
        documents = []

        for raw_document in raw_documents:
            content = raw_document[1].encode('utf-8')
            base64_content = base64.b64encode(content).decode('utf-8')

            newFileConfig = FileConfig(fileID=fileConfig.fileID, filename=raw_document[0], isURL=False, overwrite=fileConfig.overwrite, extension="md", source=raw_document[2], content=base64_content, labels=fileConfig.labels, rag_config=fileConfig.rag_config, file_size=len(content), status=fileConfig.status, status_report=fileConfig.status_report)
            document = await reader.load(config, newFileConfig)
            documents.append(document[0])

        return documents
    
    async def handle_response(self, response: aiohttp.ClientResponse) -> dict:
        if response.status != 200:
            text = await response.text()
            raise Exception(f"Firecrawl Error: {response.status}, {text}")
        return await response.json()
    

    async def firecrawl(self, mode: str, urls: list[str], token: str) -> list[tuple[str, str, str]]:

        crawl_url = "https://api.firecrawl.dev/v0/crawl"
        scrape_url = "https://api.firecrawl.dev/v0/scrape"
        documents = []

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        async with aiohttp.ClientSession() as session:
            for url in urls:
                request_data = {"url": url}
                if mode == "Scrape":
                    async with session.post(scrape_url, headers=headers, json=request_data) as response:
                        response_data = await self.handle_response(response)
                        if "data" in response_data and response_data.get("success", False):
                            documents.append((
                                response_data["data"]["metadata"]["title"],
                                response_data["data"]["markdown"],
                                url
                            ))
                else:
                    documents.extend(await self.handle_crawl(session, crawl_url, headers, request_data))

        if not documents:
            raise Exception("Firecrawl was not able to load any documents, please check your API Key and settings")

        return documents
    
    async def handle_crawl(self, session: aiohttp.ClientSession, crawl_url: str, headers: dict, request_data: dict) -> list[tuple[str, str, str]]:
        documents = []
        loop = asyncio.get_running_loop()
        start_time = loop.time()

        async with session.post(crawl_url, headers=headers, json=request_data) as response:
            data = await self.handle_response(response)
            job_id = data.get("jobId")
            msg.info(f"Creating Firecrawl Job {job_id}")

            if job_id:
                max_retries = 60
                wait_time = 10

                for _ in range(max_retries):
                    msg.info(f"Checking Firecrawl Job Status for {job_id} (Try: {_}) ({round(loop.time() - start_time, 2)}s)")
                    async with session.get(f"{crawl_url}/status/{job_id}", headers=headers) as response:
                        data = await self.handle_response(response)
                        status = data.get("status")
                        msg.info(f"Firecrawl Job Status: {status}")
                        files = data.get("data", [])
                        if files:
                            msg.info(f"{len(files)} Files scraped")
                        if status == "completed":
                            msg.good("Firecrawl Job successful")
                            documents.extend((file["metadata"]["title"], file["markdown"], file["metadata"]["sourceURL"]) for file in files)
                            break
                        await asyncio.sleep(wait_time)

        return documents
