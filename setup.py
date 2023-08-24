from setuptools import setup, find_packages

setup(
    name="verba",
    version="0.1",
    packages=find_packages(),
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
    ],
)
