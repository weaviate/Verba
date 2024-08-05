import aiohttp
import os
import urllib
import base64

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.util import get_environment

from goldenverba.components.types import InputConfig


class GitReader(Reader):
    """
    The GitReader downloads files from GitHub or GitLab and ingests them into Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "Git"
        self.type = "URL"
        self.description = (
            "Downloads and ingests all files from a GitHub or GitLab Repo."
        )
        self.config = {
            "Platform": InputConfig(
                type="dropdown",
                value="GitHub",
                description="Select the Git platform",
                values=["GitHub", "GitLab"],
            ),
            "Owner": InputConfig(
                type="text",
                value="",
                description="Enter the repo owner (GitHub) or group/user (GitLab)",
                values=[],
            ),
            "Name": InputConfig(
                type="text",
                value="",
                description="Enter the repo name",
                values=[],
            ),
            "Branch": InputConfig(
                type="text",
                value="main",
                description="Enter the branch name",
                values=[],
            ),
            "Path": InputConfig(
                type="text",
                value="",
                description="Enter the path or leave it empty to import all",
                values=[],
            ),
        }

        if os.getenv("GITHUB_TOKEN") is None and os.getenv("GITLAB_TOKEN") is None:
            self.config["Git Token"] = InputConfig(
                type="password",
                value="",
                description="You can set your GitHub/GitLab Token here if you haven't set it up as environment variable `GITHUB_TOKEN` or `GITLAB_TOKEN`",
                values=[],
            )

    async def load(self, config: dict, fileConfig: FileConfig) -> list[Document]:
        documents = []
        platform = config["Platform"].value
        token = self.get_token(config, platform)

        reader = BasicReader()

        if platform == "GitHub":
            owner = config["Owner"].value
            name = config["Name"].value
            branch = config["Branch"].value
            path = config["Path"].value
            fetch_url = f"https://api.github.com/repos/{owner}/{name}/git/trees/{branch}?recursive=1"
            docs = await self.fetch_docs_github(fetch_url, path, token, reader)
        else:  # GitLab
            owner = config["Owner"].value
            name = config["Name"].value
            project_id = urllib.parse.quote(f"{owner}/{name}", safe="")
            branch = config["Branch"].value
            path = config["Path"].value
            fetch_url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/tree?ref={branch}&path={path}&per_page=100"
            docs = await self.fetch_docs_gitlab(fetch_url, token, reader)

        msg.info(f"Fetched {len(docs)} document paths from {fetch_url}")

        for _file in docs:
            try:
                if platform == "GitHub":
                    content, link, size, extension = await self.download_file_github(
                        owner, name, _file, branch, token
                    )
                else:
                    content, link, size, extension = await self.download_file_gitlab(
                        owner, name, _file, branch, token
                    )

                if content:
                    new_file_config = FileConfig(
                        fileID=fileConfig.fileID,
                        filename=_file,
                        isURL=False,
                        overwrite=fileConfig.overwrite,
                        extension=extension,
                        source=link,
                        content=content,
                        labels=fileConfig.labels,
                        rag_config=fileConfig.rag_config,
                        file_size=size,
                        status=fileConfig.status,
                        status_report=fileConfig.status_report,
                    )
                    document = await reader.load(config, new_file_config)
                    documents.append(document[0])
            except Exception as e:
                raise Exception(f"Couldn't load retrieve {_file}: {str(e)}")

        return documents

    def get_token(self, config: dict, platform: str) -> str:
        env_var = "GITHUB_TOKEN" if platform == "GitHub" else "GITLAB_TOKEN"
        return get_environment(
            config, "Git Token", env_var, f"No {platform} Token detected"
        )

    async def fetch_docs_github(
        self, url: str, folder: str, token: str, reader: Reader
    ) -> list[str]:
        headers = self.get_headers(token, "GitHub")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return [
                    item["path"]
                    for item in data["tree"]
                    if item["path"].startswith(folder)
                    and any(item["path"].endswith(ext) for ext in reader.extension)
                ]

    async def fetch_docs_gitlab(self, url: str, token: str, reader: Reader) -> list:
        headers = self.get_headers(token, "GitLab")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return [
                    item["path"]
                    for item in data
                    if item["type"] == "blob"
                    and any(item["path"].endswith(ext) for ext in reader.extension)
                ]

    async def download_file_github(
        self, owner: str, name: str, path: str, branch: str, token: str
    ) -> tuple[str, str, int, str]:
        url = (
            f"https://api.github.com/repos/{owner}/{name}/contents/{path}?ref={branch}"
        )
        headers = self.get_headers(token, "GitHub")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                content_b64 = data["content"]
                link = data["html_url"]
                size = data["size"]
                extension = os.path.splitext(path)[1][1:]
                return content_b64, link, size, extension

    async def download_file_gitlab(
        self, owner: str, name: str, file_path: str, branch: str, token: str
    ) -> tuple[str, str, int, str]:
        project_id = urllib.parse.quote(f"{owner}/{name}", safe="")
        url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/{urllib.parse.quote(file_path, safe='')}/raw?ref={branch}"
        headers = {"PRIVATE-TOKEN": token}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    content = await response.read()
                    content_b64 = base64.b64encode(content).decode("utf-8")
                    size = len(content)
                    extension = os.path.splitext(file_path)[1][1:]
                    link = (
                        f"https://gitlab.com/{owner}/{name}/-/blob/{branch}/{file_path}"
                    )
                    return content_b64, link, size, extension
                else:
                    raise Exception(
                        f"Failed to download file: {response.status} {await response.text()}"
                    )

    def get_headers(self, token: str, platform: str) -> dict:
        if platform == "GitHub":
            return {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }
        else:  # GitLab
            return {
                "Authorization": f"Bearer {token}",
            }
