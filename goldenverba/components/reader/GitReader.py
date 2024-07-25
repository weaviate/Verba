import aiohttp
import os

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.util import get_environment

from goldenverba.components.types import InputConfig

class GitHubReader(Reader):
    """
    The GithubReader downloads files from Github and ingests them into Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "GitHub"
        self.type = "URL"
        self.description = "Downloads and ingests all files from a GitHub Repo."
        self.config = {
                    "Owner": InputConfig(
                        type="text", value="weaviate", description="Enter the repo owner", values=[]
                    ),
                    "Name": InputConfig(
                        type="text", value="Verba", description="Enter the repo name", values=[]
                    ),
                    "Branch": InputConfig(
                        type="text", value="main", description="Enter the branch name", values=[]
                    ),
                    "Path": InputConfig(
                        type="text", value="data", description="Enter the path or leave it empty to import all", values=[]
                    ),
                    "GitHub Token": InputConfig(
                        type="password",
                        value="",
                        description="You can set your GitHub Token here if you haven't set it up as environment variable `GITHUB_TOKEN`", values=[]
                    ),
                }

    async def load(
        self, config:dict, fileConfig: FileConfig
    ) -> list[Document]:
        
        documents = []
        token = get_environment(config["GitHub Token"].value, "GITHUB_TOKEN", "No GitHub Token detected")

        reader = BasicReader()

        owner = config["Owner"].value
        name = config["Name"].value
        branch = config["Branch"].value
        path = config["Path"].value
        fetch_url = f"https://api.github.com/repos/{owner}/{name}/git/trees/{branch}?recursive=1"

        docs = await self.fetch_docs(fetch_url, path, token, reader)
        msg.info(f"Fetched {len(docs)} document paths from {fetch_url}")

        for _file in docs:
            try:
                content, link, size, extension = await self.download_file(owner, name, _file, branch, token)
                if content:
                    new_file_config = FileConfig(
                        fileID=fileConfig.fileID, filename=_file, isURL=False, overwrite=fileConfig.overwrite,
                        extension=extension, source=link, content=content, labels=fileConfig.labels,
                        rag_config=fileConfig.rag_config, file_size=size, status=fileConfig.status,
                        status_report=fileConfig.status_report
                    )
                    document = await reader.load(config, new_file_config)
                    documents.append(document[0])
            except Exception as e:
                raise Exception(f"Couldn't load retrieve {_file}: {str(e)}")

        return documents

    async def fetch_docs(self, url: str, folder: str, token: str, reader: Reader) -> list[str]:
        """Fetch filenames from Github."""
        headers = self.get_headers(token)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return [
                    item["path"] for item in data["tree"]
                    if item["path"].startswith(folder) and any(item["path"].endswith(ext) for ext in reader.extension)
                ]

    async def download_file(self, owner: str, name: str, path: str, branch: str, token: str) -> tuple[str, str, int, str]:
        """Download files from Github based on filename."""
        url = f"https://api.github.com/repos/{owner}/{name}/contents/{path}?ref={branch}"
        headers = self.get_headers(token)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                content_b64 = data["content"]
                link = data["html_url"]
                size = data["size"]
                extension = os.path.splitext(path)[1][1:]
                return content_b64, link, size, extension
    
    def get_headers(self, token: str) -> dict:
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }