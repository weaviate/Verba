from setuptools import setup, find_packages

setup(
    name="verba_rag",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "verba=verba_rag.server.cli:cli",
            "verba-ingest=verba.ingestion.cli:cli",
        ],
    },
    author="Weaviate",
    author_email="edward@weaviate.io",
    description="Verba is an open-source RAG application which offers an interface for importing and querying custom data.",
    url="https://github.com/weaviate/Verba",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
        "weaviate-client>=3.23.1",
        "python-dotenv>=1.0.0",
        "openai>=0.27.9",
        "wasabi>=1.1.2",
        "spacy",
        "fastapi>=0.102.0",
        "uvicorn[standard]",
        "click>= 8.1.7",
    ],
)
