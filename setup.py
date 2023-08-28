from setuptools import setup, find_packages

setup(
    name="verba",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "verba=verba.server.cli_start:cli",
        ],
    },
    install_requires=[
        "weaviate-client",
        "python-dotenv",
        "openai",
        "black",
        "wasabi",
        "typer",
        "farm-haystack",
        "nltk",
        "fastapi",
        "uvicorn",
        "pytest",
        "mypy",
        "click",
    ],
)
