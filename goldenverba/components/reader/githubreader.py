import base64
import json
from datetime import datetime
import time
import requests
import os

from wasabi import msg

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.components.types import FileData


class GitHubReader(Reader):
    """
    The GithubReader downloads files from Github and ingests them into Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "GitHubReader"
        self.requires_env = ["GITHUB_TOKEN"]
        self.description = "Retrieves all text files (.txt, .md, .mdx, .json) from a GitHub Repository and imports them into Verba. Use this format {owner}/{repo}/{branch}/{folder}"

    def load(
        self,
        fileData: list[FileData],
    ) -> tuple[list[Document], list[str]]:

        start_time = time.time()  # Start timing
        documents = []
        logging = []
        logging.append(["INFO",f"Starting loading in {len(fileData)} files"])

        data = fileData[0]
        docs = self.fetch_docs(data.content)

        for _file in docs:
            try:
                logging.append(["INFO",f"Downloading in {_file}"])
                content, link, _path = self.download_file(data.content, _file)
                if ".json" in _file:
                    json_obj = json.loads(str(content))
                    try:
                        document = Document.from_json(json_obj)
                    except Exception as e:
                        raise Exception(f"Loading JSON failed {e}")

                else:
                    document = Document(
                        text=content,
                        type=self.config["document_type"],
                        name=_file,
                        link=link,
                        path=_path,
                        timestamp=str(
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ),
                        reader=self.name,
                    )

                documents.append(document)

            except Exception as e:
                msg.warn(f"Couldn't load, skipping {_file}: {str(e)}")
                continue

        elapsed_time = round(time.time() - start_time , 2) # Calculate elapsed time
        msg.good(f"Loaded {len(documents)} documents in {elapsed_time}s")
        logging.append(["SUCCESS",f"Loaded {len(documents)} documents in {elapsed_time}s"])



    def fetch_docs(self, path: str) -> list:
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
