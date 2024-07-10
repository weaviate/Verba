import base64
import json
from datetime import datetime
import requests
import os
import re

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.components.types import FileData

from goldenverba.server.ImportLogger import LoggerManager


class GitHubReader(Reader):
    """
    The GithubReader downloads files from Github and ingests them into Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "GitHub"
        self.type = "URL"
        self.requires_env = ["GITHUB_TOKEN"]
        self.description = "Retrieves all text files (.txt, .md, .mdx, .json) from a GitHub Repository and imports them into Verba. Use this format {owner}/{repo}/{branch}/{folder}"

    async def load(
        self, fileData: list[FileData], textValues: list[str], logger: LoggerManager
    ) -> list[Document]:

        if len(textValues) <= 0:
            await logger.send_error(f"No GitHub Link detected")
            return []
        elif textValues[0] == "":
            await logger.send_error(f"Empty GitHub URL")
            return []

        github_link = textValues[0]

        if not self.is_valid_github_path(github_link):
            await logger.send_error(f"GitHub URL {github_link} not matching pattern: owner/repo/branch/folder")
            return []

        documents = []
        docs = await self.fetch_docs(github_link, await logger)

        for _file in docs:
            try:
                await logger.send_info(f"Downloading {_file}")
                content, link, _path = self.download_file(github_link, _file)
                if ".json" in _file:
                    json_obj = json.loads(str(content))
                    try:
                        document = Document.from_json(json_obj)
                    except Exception as e:
                        raise Exception(f"Loading JSON failed {e}")

                elif ".txt" in _file or ".md" in _file or ".mdx" in _file:
                    document = Document(
                        text=content,
                        type=self.config["document_type"].text,
                        name=_file,
                        link=link,
                        path=_path,
                        timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        reader=self.name,
                    )

                documents.append(document)

            except Exception as e:
                msg.warn(f"Couldn't load, skipping {_file}: {str(e)}")
                await logger.send_warning(f"Couldn't load, skipping {_file}: {str(e)}")
                continue

        return documents, 

    async def fetch_docs(self, path: str, logger: LoggerManager) -> list:
        """Fetch filenames from Github
        @parameter path : str - Path to a GitHub repository
        @returns list - List of document names.
        """
        split = path.split("/")
        owner = split[0]
        repo = split[1]
        branch = split[2] if len(split) > 2 else "main"
        folder_path = "/".join(split[3:]) if len(split) > 3 else ""

        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        headers = {
            "Authorization": f"token {os.environ.get('GITHUB_TOKEN', '')}",
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
            )
        ]
        msg.info(
            f"Fetched {len(files)} filenames from {url} (checking folder {folder_path})"
        )
        await logger.send_success(f"Fetched {len(files)} filenames from {url} (checking folder {folder_path})")

        return files

    def download_file(self, path: str, file_path: str) -> str:
        """Download files from Github based on filename
        @parameter path : str - Path to a GitHub repository
        @parameter file_path : str - Path of the file in repo
        @returns str - Content of the file.
        """
        split = path.split("/")
        owner = split[0]
        repo = split[1]
        branch = split[2] if len(split) > 2 else "main"

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
        headers = {
            "Authorization": f"token {os.environ.get('GITHUB_TOKEN', '')}",
            "Accept": "application/vnd.github.v3+json",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        content_b64 = response.json()["content"]
        link = response.json()["html_url"]
        path = response.json()["path"]
        content = base64.b64decode(content_b64).decode("utf-8")
        msg.info(f"Downloaded {url}")
        return (content, link, path)

    def is_valid_github_path(self, path):
        # Regex pattern to match {owner}/{repo}/{branch}/{folder}
        # {folder} is optional and can include subfolders
        pattern = r"^([^/]+)/([^/]+)/([^/]+)(/[^/]*)*$"

        # Match the pattern with the provided path
        match = re.match(pattern, path)

        # Return True if the pattern matches, False otherwise
        return bool(match)
