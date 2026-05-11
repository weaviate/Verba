"""
reader_manager.py
=================
Reader component registry and ReaderManager.

To add a new Reader:
  1. Implement it in this directory (goldenverba/components/reader/)
  2. Import it below and add an instance to the `readers` list
"""

import asyncio

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Reader
from goldenverba.server.helpers import LoggerManager
from goldenverba.server.types import FileConfig, FileStatus

from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.reader.GitReader import GitReader
from goldenverba.components.reader.UnstructuredAPI import UnstructuredReader
from goldenverba.components.reader.HTMLReader import HTMLReader
from goldenverba.components.reader.WhisperReader import WhisperReader

# All available readers — add new instances here
readers = [
    BasicReader(),
    HTMLReader(),
    GitReader(),
    UnstructuredReader(),
    WhisperReader(),
]


class ReaderManager:
    """Dispatches load() calls to the correct Reader implementation."""

    def __init__(self):
        self.readers: dict[str, Reader] = {reader.name: reader for reader in readers}

    async def load(
        self, reader: str, fileConfig: FileConfig, logger: LoggerManager
    ) -> list[Document]:
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time()
            if reader in self.readers:
                config = fileConfig.rag_config["Reader"].components[reader].config
                documents: list[Document] = await self.readers[reader].load(
                    config, fileConfig
                )
                for document in documents:
                    document.meta["Reader"] = (
                        fileConfig.rag_config["Reader"].components[reader].model_dump()
                    )
                elapsed_time = round(loop.time() - start_time, 2)
                if len(documents) == 1:
                    await logger.send_report(
                        fileConfig.fileID,
                        FileStatus.LOADING,
                        f"Loaded {fileConfig.filename}",
                        took=elapsed_time,
                    )
                else:
                    await logger.send_report(
                        fileConfig.fileID,
                        FileStatus.LOADING,
                        f"Loaded {fileConfig.filename} with {len(documents)} documents",
                        took=elapsed_time,
                    )
                await logger.send_report(
                    fileConfig.fileID, FileStatus.CHUNKING, "", took=0
                )
                return documents
            else:
                raise Exception(f"{reader} Reader not found")

        except Exception as e:
            raise Exception(f"Reader {reader} failed with: {str(e)}")
