import json
from datetime import datetime
import requests
import os
import re
import urllib

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig

from goldenverba.components.reader.BasicReader import BasicReader

from goldenverba.components.types import InputConfig


class GitLabReader(Reader):
    """
    The GitLabReader downloads files from GitLab and ingests them into Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "GitLab"
        self.type = "URL"
        self.description = "Downloads and ingests all files from a GitLab Repo."
        self.config = {
                    "Project ID": InputConfig(
                        type="text", value="gitlab-org/gitlab", description="Enter the project id", values=[]
                    ),
                    "Branch": InputConfig(
                        type="text", value="master", description="Enter the branch name", values=[]
                    ),
                    "Path": InputConfig(
                        type="text", value="data", description="Enter the path or leave it empty to import all", values=[]
                    ),
                    "GitLab Token": InputConfig(
                        type="password",
                        value="",
                        description="You can set your GitLab Token here if you haven't set it up as environment variable `GITLAB_TOKEN`", values=[]
                    ),
                }
    async def load(
        self, config:dict, fileConfig: FileConfig
    ) -> list[Document]:
        
        documents = []

        if config["GitLab Token"].value == "":
            TOKEN = os.environ.get("GITLAB_TOKEN")
            if TOKEN is None:
                raise Exception(f"No GitLab Token detected")
        else:
            TOKEN = config["GitLab Token"].value

        reader = BasicReader()

        ID = config["Project ID"].value
        PROJECT_PATH = urllib.parse.quote(ID, safe='')
        BRANCH = config["Branch"].value
        PATH = config["Path"].value

        FETCH_URL = f"https://gitlab.com/api/v4/projects/{PROJECT_PATH}/repository/tree?ref={BRANCH}&path={PATH}&per_page=100"



        docs = await self.fetch_docs(FETCH_URL, TOKEN)

        for _file in docs:
            try:
                content, link, size, extension = self.download_file(PROJECT_PATH, _file, BRANCH, TOKEN)
                if len(content) > 0:
                    newFileConfig = FileConfig(fileID=fileConfig.fileID, filename=_file, isURL=False, overwrite=fileConfig.overwrite, extension=extension, source=link, content=content, labels=fileConfig.labels, rag_config=fileConfig.rag_config, file_size=size, status=fileConfig.status, status_report=fileConfig.status_report)
                    document = await reader.load(config, newFileConfig)
                    documents.append(document[0])
                else:
                    continue

            except Exception as e:
                raise Exception(f"Couldn't load {_file}: {str(e)}")

        return documents


    async def fetch_docs(self, URL: str, token: str) -> list:
        try:
            url = URL
            headers = {
                "Authorization": f"Bearer {token}",
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            files = [
                item["path"]
                for item in response.json()
                if item["type"] == "blob"
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
            raise Exception(f"Failed to fetch doc from GitLab: {str(e)}")
    


    def download_file(self, ID: str, file_path: str, BRANCH:str, TOKEN:str) -> str:
        try:
            encoded_file_path = urllib.parse.quote(file_path, safe="")
            DOWNLOAD_URL = f"https://gitlab.com/api/v4/projects/{ID}/repository/files/{encoded_file_path}/raw?ref={BRANCH}"
            headers = {
                "Authorization": f"Bearer {TOKEN}",
            }
            response = requests.get(DOWNLOAD_URL, headers=headers)
            response.raise_for_status()

            print(response.json())

            content_b64 = response.json()["content"]
            link = f"https://gitlab.com/{ID}/-/blob/{BRANCH}/{file_path}"
            size = response.json()["size"]
            extension="txt"

            return (content_b64, link, size, extension)
        except Exception as e:
            raise Exception(f"Failed to download {DOWNLOAD_URL} : {str(e)}")
