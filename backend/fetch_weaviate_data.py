import requests
import base64
import os

from dotenv import load_dotenv

load_dotenv()


def fetch_docs(owner, repo, folder_path, token=None) -> list:
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    headers = {
        "Authorization": f"token {token}" if token else None,
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    md_files = [
        item["path"]
        for item in response.json()["tree"]
        if item["path"].startswith(folder_path)
        and (item["path"].endswith(".md") or item["path"].endswith(".mdx"))
    ]
    return md_files


def download_file(owner, repo, file_path, token=None) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}" if token else None,
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    content_b64 = response.json()["content"]
    link = response.json()["html_url"]
    path = response.json()["path"]
    content = base64.b64decode(content_b64).decode("utf-8")

    return (content, link, path)
