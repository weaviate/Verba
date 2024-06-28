import base64
import json
import os
from datetime import datetime
import urllib.parse

import requests
from wasabi import msg

from goldenverba.components.reader.document import Document
from goldenverba.components.reader.interface import InputForm, Reader


class GitLabReader(Reader):
    """
    The GitLabReader downloads files from GitLab and ingests them into Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "GitLabReader"
        self.requires_env = ["GITLAB_TOKEN"]
        self.description = "Downloads only text files from a GitLab repository and ingests it into Verba. Use this format {project_id}/{branch}/{folder}"
        self.input_form = InputForm.INPUT.value

    def load(
        self,
        bytes: list[str] = None,
        contents: list[str] = None,
        paths: list[str] = None,
        fileNames: list[str] = None,
        document_type: str = "Documentation",
    ) -> list[Document]:
        documents = []
        if paths:
            for path in paths:
                files = self.fetch_docs(path)

                for _file in files:
                    try:
                        content, link, _path = self.download_file(path, _file)
                    except Exception as e:
                        msg.warn(f"Couldn't load, skipping {_file}: {str(e)}")
                        continue

                    if ".json" in _file:
                        json_obj = json.loads(content)
                        document = Document.from_json(json_obj)
                    else:
                        document = Document(
                            text=content,
                            type=document_type,
                            name=_file,
                            link=link,
                            path=_path,
                            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                            reader=self.name,
                        )
                    documents.append(document)

        msg.good(f"Loaded {len(documents)} documents")
        return documents

    def fetch_docs(self, path: str) -> list:
        split = path.split("/")
        project_id = split[0]
        branch = split[1]
        folder_path = "/".join(split[2:]) if len(split) > 2 else ""

        url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/tree?ref={branch}&path={folder_path}&per_page=100"
        headers = {
            "Authorization": f"Bearer {os.environ.get('GITLAB_TOKEN', '')}",
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
            )
        ]
        msg.info(
            f"Fetched {len(files)} filenames from {url} (checking folder {folder_path})"
        )
        return files

    def download_file(self, path: str, file_path: str) -> str:
        split = path.split("/")
        project_id = split[0]
        branch = split[1]
        encoded_file_path = urllib.parse.quote(file_path, safe="")

        url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/{encoded_file_path}/raw?ref={branch}"
        headers = {
            "Authorization": f"Bearer {os.environ.get('GITLAB_TOKEN', '')}",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        content = response.text
        link = f"https://gitlab.com/{project_id}/-/blob/{branch}/{file_path}"
        msg.info(f"Downloaded {url}")
        return (content, link, file_path)
