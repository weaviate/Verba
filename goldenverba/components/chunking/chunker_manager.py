"""
chunker_manager.py
==================
Chunker component registry and ChunkerManager.

To add a new Chunker:
  1. Implement it in this directory (goldenverba/components/chunking/)
  2. Import it below and add an instance to the `chunkers` list
"""

import asyncio

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Chunker, Embedding
from goldenverba.server.helpers import LoggerManager
from goldenverba.server.types import FileConfig, FileStatus

from goldenverba.components.chunking.TokenChunker import TokenChunker
from goldenverba.components.chunking.SentenceChunker import SentenceChunker
from goldenverba.components.chunking.RecursiveChunker import RecursiveChunker
from goldenverba.components.chunking.HTMLChunker import HTMLChunker
from goldenverba.components.chunking.MarkdownChunker import MarkdownChunker
from goldenverba.components.chunking.CodeChunker import CodeChunker
from goldenverba.components.chunking.JSONChunker import JSONChunker
from goldenverba.components.chunking.SemanticChunker import SemanticChunker

# All available chunkers — add new instances here
chunkers = [
    TokenChunker(),
    SentenceChunker(),
    RecursiveChunker(),
    SemanticChunker(),
    HTMLChunker(),
    MarkdownChunker(),
    CodeChunker(),
    JSONChunker(),
]


class ChunkerManager:
    """Dispatches chunk() calls to the correct Chunker implementation."""

    def __init__(self):
        self.chunkers: dict[str, Chunker] = {
            chunker.name: chunker for chunker in chunkers
        }

    async def chunk(
        self,
        chunker: str,
        fileConfig: FileConfig,
        documents: list[Document],
        embedder: Embedding,
        logger: LoggerManager,
    ) -> list[Document]:
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time()
            if chunker in self.chunkers:
                config = fileConfig.rag_config["Chunker"].components[chunker].config
                embedder_config = (
                    fileConfig.rag_config["Embedder"].components[embedder.name].config
                )
                chunked_documents = await self.chunkers[chunker].chunk(
                    config=config,
                    documents=documents,
                    embedder=embedder,
                    embedder_config=embedder_config,
                )
                for chunked_document in chunked_documents:
                    chunked_document.meta["Chunker"] = (
                        fileConfig.rag_config["Chunker"]
                        .components[chunker]
                        .model_dump()
                    )
                elapsed_time = round(loop.time() - start_time, 2)
                if len(documents) == 1:
                    await logger.send_report(
                        fileConfig.fileID,
                        FileStatus.CHUNKING,
                        f"Split {fileConfig.filename} into {len(chunked_documents[0].chunks)} chunks",
                        took=elapsed_time,
                    )
                else:
                    await logger.send_report(
                        fileConfig.fileID,
                        FileStatus.CHUNKING,
                        f"Chunked all {len(chunked_documents)} documents with a total of {sum([len(document.chunks) for document in chunked_documents])} chunks",
                        took=elapsed_time,
                    )

                await logger.send_report(
                    fileConfig.fileID, FileStatus.EMBEDDING, "", took=0
                )
                return chunked_documents
            else:
                raise Exception(f"{chunker} Chunker not found")
        except Exception as e:
            raise e
