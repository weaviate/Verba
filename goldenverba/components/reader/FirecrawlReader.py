import base64
import json
import requests
import os
import asyncio

from wasabi import msg
import httpx

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.reader.BasicReader import BasicReader

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

        URLs = config["URLs"].values
        Mode = config["Mode"].value
        JobID = config["JobID"].value

        if config["Firecrawl API Key"].value == "":
            TOKEN = os.environ.get("FIRECRAWL_API_KEY")
            if TOKEN is None:
                raise Exception(f"No Firecrawl API Key detected")
        else:
            TOKEN = config["Firecrawl API Key"].value

        raw_documents = await self.firecrawl(Mode, URLs, TOKEN, JobID)
        documents = []
        for raw_document in raw_documents:
            content = raw_document[1].encode('utf-8')
            base64_content = base64.b64encode(content).decode('utf-8')

            newFileConfig = FileConfig(fileID=fileConfig.fileID, filename=raw_document[0], isURL=False, overwrite=fileConfig.overwrite, extension="md", source=raw_document[2], content=base64_content, labels=fileConfig.labels, rag_config=fileConfig.rag_config, file_size=len(content), status=fileConfig.status, status_report=fileConfig.status_report)
            document = await reader.load(config, newFileConfig)
            documents.append(document[0])

        return documents
    

    async def firecrawl(self, mode: str, urls: list[str], token: str, _jobID: str) -> list[str]:
         
        crawl_url = "https://api.firecrawl.dev/v0/crawl"
        scrape_url = "https://api.firecrawl.dev/v0/scrape"

        documents = []

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        for _url in urls:

            request_data = {
                "url":_url
            }

            if mode == "Scrape":
                async with httpx.AsyncClient() as client:
                    response = await client.post(scrape_url, headers=headers, content=json.dumps(request_data))
                    if response.status_code == 200:
                        data = response.json()
                        if "data" in data and data.get("success", False):
                            documents.append((data["data"]["metadata"]["title"],data["data"]["markdown"],_url))
                        else:
                            raise Exception(f"Firecrawl call was not successful: {data}")
                    else:
                        raise Exception(f"Error: {response.status_code}, {response.text}")
            else:
                try:

                    loop = asyncio.get_running_loop()
                    start_time = loop.time() 

                    if _jobID != "":
                        jobID = _jobID
                        msg.info(f"Continuing Firecrawl Job {jobID}")
                    else:
                        response = requests.post(crawl_url, headers=headers, data=json.dumps(request_data))
                        data = response.json()
                        jobID = data["jobId", ""]
                        msg.info(f"Creating Firecrawl Job {jobID}")

                    if jobID != "":
                        max_loop_retries = 60
                        wait_time = 10

                        for _ in range(max_loop_retries):
                            msg.info(f"Checking Firecrawl Job Status for {jobID} (Try: {_}) ({round(loop.time() - start_time, 2)}s)")
                            response = requests.get(f"{crawl_url}/status/{jobID}", headers=headers)
                            if response.status_code == 200:
                                data = response.json()
                                status = data.get("status")
                                msg.info(f"Firecrawl Job Status: {status}")
                                files = data.get("data",[])
                                if files is not None:
                                    msg.info(f"{len(files)} Files scraped")
                                if status == "completed":
                                    msg.good(f"Firecrawl Job successful")
                                    files = data.get("data",[])
                                    for file in files:
                                        documents.append((file["metadata"]["title"], file["markdown"], file["metadata"]["sourceURL"]))
                                    break  # Exit loop when job is completed

                                await asyncio.sleep(wait_time)
                except Exception as e:
                    raise Exception(f"Firecrawl Crawl failed with: {str(e)}")

        if len(documents) == 0:
            raise Exception("Firecrawl was not able to load any documents, please check your API Key and settings")

        return documents



    
