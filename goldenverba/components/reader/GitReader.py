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

        if config["GitHub Token"].value == "":
            TOKEN = os.environ.get("GITHUB_TOKEN")
            if TOKEN is None:
                raise Exception(f"No GitHub Token detected")
        else:
            TOKEN = config["GitHub Token"].value

        reader = BasicReader()

        OWNER = config["Owner"].value
        NAME = config["Name"].value
        BRANCH = config["Branch"].value
        PATH = config["Path"].value

        FETCH_URL = f"https://api.github.com/repos/{OWNER}/{NAME}/git/trees/{BRANCH}?recursive=1"

        docs = await self.fetch_docs(FETCH_URL, PATH, TOKEN)

        for _file in docs:
            try:
                content, link, size, extension = self.download_file(OWNER, NAME, _file, BRANCH, TOKEN)
                if len(content) > 0:
                    newFileConfig = FileConfig(fileID=fileConfig.fileID, filename=_file, isURL=False, overwrite=fileConfig.overwrite, extension=extension, source=link, content=content, labels=fileConfig.labels, rag_config=fileConfig.rag_config, file_size=size, status=fileConfig.status, status_report=fileConfig.status_report)
                    document = await reader.load(config, newFileConfig)
                    documents.append(document[0])
                else:
                    continue

            except Exception as e:
                raise Exception(f"Couldn't load retrieve {_file}: {str(e)}")

        return documents

    async def fetch_docs(self, URL: str, FOLDER: str, TOKEN: str) -> list:
        """Fetch filenames from Github
        @parameter path : str - Path to a GitHub repository
        @returns list - List of document names.
        """
        try:
            folder_path = FOLDER
            url = URL
            headers = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            files = [
                item["path"]
                for item in response.json()["tree"]
                if item["path"].startswith(folder_path)
                and (
                    item["path"].endswith(".md")
                    or item["path"].endswith(".mdx")
                    or item["path"].endswith(".txt")
                    or item["path"].endswith(".json")
                    or item["path"].endswith(".pdf")
                    or item["path"].endswith(".docx")
                )
            ]

            return files
        
        except Exception as e:
            raise Exception (f"Failed to fetch docs from GitHub: {str(e)}")

    def download_file(self, OWNER: str, NAME: str, PATH: str, BRANCH: str, TOKEN: str) -> str:
        """Download files from Github based on filename
        @parameter OWNER: str - Owner of the GitHub repository
        @parameter NAME: str - Name of the GitHub repository
        @parameter PATH: str - Path of the file in the repo
        @parameter BRANCH: str - Branch of the repository
        @parameter TOKEN: str - GitHub token for authentication
        @returns tuple: Content of the file (as a byte string), link to the file, size in bytes, and file extension.
        """
        try:
            DOWNLOAD_URL = f"https://api.github.com/repos/{OWNER}/{NAME}/contents/{PATH}?ref={BRANCH}"
            headers = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            response = requests.get(DOWNLOAD_URL, headers=headers)
            response.raise_for_status()

            content_b64 = response.json()["content"]
            link = response.json()["html_url"]
            size = response.json()["size"]
            extension = os.path.splitext(PATH)[1][1:]

        except Exception as e:
            raise Exception(f"Couldn't download {DOWNLOAD_URL}: {str(e)}")

        return (content_b64, link, size, extension)
