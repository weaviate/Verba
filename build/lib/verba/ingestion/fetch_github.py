import requests
import base64

from dotenv import load_dotenv

load_dotenv()


def fetch_docs(owner, repo, folder_path, token=None) -> list:
    """Fetch filenames from Github
    @parameter owner : str - Repo owner
    @parameter repo : str - Repo name
    @parameter folder_path : str - Directory in repo to fetch from
    @parameter token : str - Github token
    @returns list - List of document names
    """

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
    """Download files from Github based on filename
    @parameter owner : str - Repo owner
    @parameter repo : str - Repo name
    @parameter file_path : str - Path of the file in repo
    @parameter token : str - Github token
    @returns str - Content of the file
    """
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


def is_link_working(url: str) -> bool:
    """Validates whether a link is working
    @parameter url : str - The URL
    @returns bool - Whether it is a valid url
    """
    try:
        response = requests.get(url, timeout=10)  # Adjust the timeout as needed
        # Checking if the status code is in the range 200-299 (all success codes)
        return 200 <= response.status_code < 300
    except requests.RequestException:
        return False
