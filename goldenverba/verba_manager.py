import os
import ssl

import weaviate

from typing import Optional
from weaviate import Client
from weaviate.embedded import EmbeddedOptions
from wasabi import msg

from goldenverba.ingestion.reader.manager import ReaderManager
from goldenverba.ingestion.chunking.manager import ChunkerManager
from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.reader.interface import Reader
from goldenverba.ingestion.chunking.interface import Chunker

import goldenverba.ingestion.schema.schema_generation as schema


class VerbaManager:
    """Manages all Verba Components"""

    def __init__(self) -> None:
        self.reader_manager = ReaderManager()
        self.chunker_manager = ChunkerManager()
        self.environment_variables = {}
        self.current_embedding = ""
        self.client = self.setup_client()
        # Check if all schemas exist for all possible vectorizers
        for vectorizer in schema.VECTORIZERS + schema.EMBEDDINGS:
            schema.init_schemas(self.client, vectorizer, False, True)

    def import_data(
        self,
        contents: list[str] = [],
        document_type: str = "Documentation",
        units: int = 100,
        overlap: int = 50,
    ) -> list[Document]:
        loaded_documents = self.reader_load(contents, document_type)
        modified_documents = self.chunker_chunk(loaded_documents, units, overlap)

        return modified_documents

    def reader_load(
        self,
        contents: list[str] = [],
        document_type: str = "Documentation",
    ) -> list[Document]:
        return self.reader_manager.load(contents, document_type)

    def chunker_chunk(
        self, documents: list[Document], units: int, overlap: int
    ) -> list[Document]:
        return self.chunker_manager.chunk(documents, units, overlap)

    def reader_set_reader(self, reader: str) -> bool:
        return self.reader_manager.set_reader(reader)

    def reader_get_readers(self) -> dict[str, Reader]:
        return self.reader_manager.get_readers()

    def chunker_set_chunker(self, chunker: str) -> bool:
        return self.chunker_manager.set_chunker(chunker)

    def chunker_get_chunker(self) -> dict[str, Chunker]:
        return self.chunker_manager.get_chunkers()

    def setup_client(self) -> Optional[Client]:
        """
        @returns Optional[Client] - The Weaviate Client
        """

        msg.info("Setting up client")

        additional_header = {}
        client = None

        # Check OpenAI ENV KEY
        try:
            import openai

            openai_key = os.environ.get("OPENAI_API_KEY", "")
            if openai_key != "":
                additional_header["X-OpenAI-Api-Key"] = openai_key
                self.environment_variables["OPENAI_API_KEY"] = True
                openai.api_key = openai_key
                msg.info("OpenAI API key detected")
            else:
                self.environment_variables["OPENAI_API_KEY"] = False
        except Exception as e:
            self.environment_variables["OPENAI_API_KEY"] = False

        # Check Verba URL ENV
        weaviate_url = os.environ.get("VERBA_URL", "")
        if weaviate_url != "":
            weaviate_key = os.environ.get("VERBA_API_KEY", "")
            self.environment_variables["VERBA_URL"] = True

            auth_config = weaviate.AuthApiKey(api_key=weaviate_key)
            client = weaviate.Client(
                url=weaviate_url,
                additional_headers=additional_header,
                auth_client_secret=auth_config,
            )
        # Use Weaviate Embedded
        else:
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context

            msg.info("Using Weaviate Embedded")
            client = weaviate.Client(
                additional_headers={"X-OpenAI-Api-Key": openai.api_key},
                embedded_options=EmbeddedOptions(
                    persistence_data_path="./.verba/local/share/",
                    binary_path="./.verba/cache/weaviate-embedded",
                ),
            )

        if client != None:
            msg.good("Connected to Weaviate")
        else:
            msg.fail("Connection to Weaviate failed")

        return client
