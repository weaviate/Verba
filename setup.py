from setuptools import setup, find_packages

setup(
    name="verba",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "verba=verba.server.cli:cli",
            "verba-ingest=verba.ingestion.cli:cli",
        ],
    },
    install_requires=[
        "weaviate-client>=3.23.1",
        "python-dotenv>=1.0.0",
        "openai>=0.27.9",
        "black>=23.7.0",
        "wasabi>=1.1.2",
        "farm-haystack>=1.19.0",
        "nltk>=3.8.1",
        "fastapi>=0.102.0",
        "uvicorn[standard]",
        "click>= 8.1.7",
    ],
)
