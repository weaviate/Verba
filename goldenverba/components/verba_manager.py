"""
verba_manager.py
================
Core pipeline orchestrator for Verba.

  VerbaManager — owns one instance of every component manager (Reader, Chunker,
                 Embedder, Retriever, Generator, Weaviate) and wires them together
                 for document import, retrieval, and generation.

                 One VerbaManager lives inside ClientManager (client_manager.py),
                 which handles connection pooling. api.py also keeps a module-level
                 VerbaManager singleton for config-only calls that don't need a
                 live Weaviate connection.

Adding a new pipeline component (e.g. a new Generator)?
  1. Implement it in goldenverba/components/generation/
  2. Register it in GeneratorManager (components/generation/generator_manager.py)
  3. Nothing else needs changing here.
"""

import os
import importlib
import math
import json

from dotenv import load_dotenv
from wasabi import msg
import asyncio

from copy import deepcopy
from goldenverba.server.helpers import LoggerManager

from goldenverba.components.document import Document
from goldenverba.server.types import (
    FileConfig,
    FileStatus,
    ChunkScore,
    Credentials,
)

from goldenverba.components.reader.reader_manager import ReaderManager
from goldenverba.components.chunking.chunker_manager import ChunkerManager
from goldenverba.components.embedding.embedding_manager import EmbeddingManager
from goldenverba.components.retriever.retriever_manager import RetrieverManager
from goldenverba.components.generation.generator_manager import GeneratorManager
from goldenverba.components.weaviate_manager import WeaviateManager

load_dotenv()


class VerbaManager:
    """
    Orchestrates the full Verba pipeline.

    Holds one instance of each component manager and exposes high-level
    async methods used by the FastAPI layer (api.py) and ClientManager.
    Does not manage Weaviate connections directly — that is ClientManager's job.
    """

    def __init__(self) -> None:
        # One instance of each component manager; each manager holds the full
        # registry of available implementations (e.g. all Generator subclasses).
        self.reader_manager = ReaderManager()
        self.chunker_manager = ChunkerManager()
        self.embedder_manager = EmbeddingManager()
        self.retriever_manager = RetrieverManager()
        self.generator_manager = GeneratorManager()
        self.weaviate_manager = WeaviateManager()

        # Fixed UUIDs for the three config documents stored in Weaviate.
        # These never change so that configs survive restarts.
        self.rag_config_uuid = "e0adcc12-9bad-4588-8a1e-bab0af6ed485"
        self.theme_config_uuid = "baab38a7-cb51-4108-acd8-6edeca222820"
        self.user_config_uuid = "f53f7738-08be-4d5a-b003-13eb4bf03ac7"

        # Populated at startup; passed to components so they can mark themselves
        # available/unavailable in the UI without attempting live calls.
        self.environment_variables: dict[str, bool] = {}
        self.installed_libraries: dict[str, bool] = {}

        self.verify_installed_libraries()
        self.verify_variables()

    # -------------------------------------------------------------------------
    # Connection
    # -------------------------------------------------------------------------

    async def connect(self, credentials: Credentials, port: str = "8080"):
        """Open a Weaviate client and ensure the config collection exists."""
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        client = await self.weaviate_manager.connect(
            credentials.deployment, credentials.url, credentials.key, port
        )
        if client:
            initialized = await self.weaviate_manager.verify_collection(
                client, self.weaviate_manager.config_collection_name
            )
            if initialized:
                msg.info(f"Connection time: {loop.time() - start_time:.2f} seconds")
                return client
            raise Exception(
                "Connected to Weaviate but failed to verify configuration collection"
            )
        raise Exception("Weaviate client could not be created")

    async def disconnect(self, client):
        """Close a Weaviate client connection."""
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        result = await self.weaviate_manager.disconnect(client)
        msg.info(f"Disconnection time: {loop.time() - start_time:.2f} seconds")
        return result

    async def get_deployments(self):
        """Return Weaviate connection env vars so the frontend can pre-fill them."""
        return {
            "WEAVIATE_URL_VERBA": os.getenv("WEAVIATE_URL_VERBA") or "",
            "WEAVIATE_API_KEY_VERBA": os.getenv("WEAVIATE_API_KEY_VERBA") or "",
        }

    # -------------------------------------------------------------------------
    # Import pipeline
    # -------------------------------------------------------------------------

    async def import_document(
        self, client, fileConfig: FileConfig, logger: LoggerManager = None
    ):
        """
        Entry point for ingesting one file/URL.

        Flow: duplicate check → Reader.load() → process_single_document() per doc.
        All per-document tasks run concurrently via asyncio.gather().
        Progress is streamed back to the caller via `logger` (a WebSocket wrapper).
        """
        if logger is None:
            logger = LoggerManager()
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time()

            # Check for an existing document with the same name.
            duplicate_uuid = await self.weaviate_manager.exist_document_name(
                client, fileConfig.filename
            )
            if duplicate_uuid is not None and not fileConfig.overwrite:
                raise Exception(f"{fileConfig.filename} already exists in Verba")
            elif duplicate_uuid is not None and fileConfig.overwrite:
                await self.weaviate_manager.delete_document(client, duplicate_uuid)
                await logger.send_report(
                    fileConfig.fileID,
                    status=FileStatus.STARTING,
                    message=f"Overwriting {fileConfig.filename}",
                    took=0,
                )
            else:
                await logger.send_report(
                    fileConfig.fileID,
                    status=FileStatus.STARTING,
                    message="Starting Import",
                    took=0,
                )

            # Reader turns the raw file/URL into one or more Document objects.
            documents = await self.reader_manager.load(
                fileConfig.rag_config["Reader"].selected, fileConfig, logger
            )

            # Process all documents concurrently; collect exceptions instead of failing fast.
            tasks = [
                self.process_single_document(client, doc, fileConfig, logger)
                for doc in documents
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_tasks = sum(
                1 for result in results if not isinstance(result, Exception)
            )

            # Report outcome: multi-doc (e.g. URL with multiple pages), single doc, or failure.
            if successful_tasks > 1:
                await logger.send_report(
                    fileConfig.fileID,
                    status=FileStatus.INGESTING,
                    message=f"Imported {fileConfig.filename} and it's {successful_tasks} documents into Weaviate",
                    took=round(loop.time() - start_time, 2),
                )
            elif successful_tasks == 1:
                await logger.send_report(
                    fileConfig.fileID,
                    status=FileStatus.INGESTING,
                    message=f"Imported {fileConfig.filename} and {len(documents[0].chunks)} chunks into Weaviate",
                    took=round(loop.time() - start_time, 2),
                )
            elif (
                successful_tasks == 0
                and len(results) == 1
                and isinstance(results[0], Exception)
            ):
                msg.fail(
                    f"No documents imported {successful_tasks} of {len(results)} succesful tasks"
                )
                raise results[0]
            else:
                raise Exception(
                    f"No documents imported {successful_tasks} of {len(results)} succesful tasks"
                )

            await logger.send_report(
                fileConfig.fileID,
                status=FileStatus.DONE,
                message=f"Import for {fileConfig.filename} completed successfully",
                took=round(loop.time() - start_time, 2),
            )

        except Exception as e:
            await logger.send_report(
                fileConfig.fileID,
                status=FileStatus.ERROR,
                message=f"Import for {fileConfig.filename} failed: {str(e)}",
                took=0,
            )
            return

    async def process_single_document(
        self,
        client,
        document: Document,
        fileConfig: FileConfig,
        logger: LoggerManager,
    ):
        """
        Chunk → embed → store one Document in Weaviate.

        For URL imports a single FileConfig can expand into multiple Documents
        (e.g. one per page). Each gets its own derived fileID so the frontend
        can track them independently.
        """
        loop = asyncio.get_running_loop()
        start_time = loop.time()

        # URL imports: each extracted document gets its own config and logger entry.
        if fileConfig.isURL:
            currentFileConfig = deepcopy(fileConfig)
            currentFileConfig.fileID = fileConfig.fileID + document.title
            currentFileConfig.isURL = False
            currentFileConfig.filename = document.title
            await logger.create_new_document(
                fileConfig.fileID + document.title,
                document.title,
                fileConfig.fileID,
            )
        else:
            currentFileConfig = fileConfig

        try:
            duplicate_uuid = await self.weaviate_manager.exist_document_name(
                client, document.title
            )
            if duplicate_uuid is not None and not currentFileConfig.overwrite:
                raise Exception(f"{document.title} already exists in Verba")
            elif duplicate_uuid is not None and currentFileConfig.overwrite:
                await self.weaviate_manager.delete_document(client, duplicate_uuid)

            # Chunker splits the document into overlapping text windows.
            chunked_documents = await self.chunker_manager.chunk(
                currentFileConfig.rag_config["Chunker"].selected,
                currentFileConfig,
                [document],
                self.embedder_manager.embedders[
                    currentFileConfig.rag_config["Embedder"].selected
                ],
                logger,
            )

            # Embedder turns each chunk into a vector; may batch-call an external API.
            vectorized_documents = await self.embedder_manager.vectorize(
                currentFileConfig.rag_config["Embedder"].selected,
                currentFileConfig,
                chunked_documents,
                logger,
            )

            # Write each vectorized document (and its chunks) to Weaviate.
            for document in vectorized_documents:
                await self.weaviate_manager.import_document(
                    client,
                    document,
                    currentFileConfig.rag_config["Embedder"]
                    .components[fileConfig.rag_config["Embedder"].selected]
                    .config["Model"]
                    .value,
                )

            await logger.send_report(
                currentFileConfig.fileID,
                status=FileStatus.INGESTING,
                message=f"Imported {currentFileConfig.filename} into Weaviate",
                took=round(loop.time() - start_time, 2),
            )

            await logger.send_report(
                currentFileConfig.fileID,
                status=FileStatus.DONE,
                message=f"Import for {currentFileConfig.filename} completed successfully",
                took=round(loop.time() - start_time, 2),
            )
        except Exception as e:
            await logger.send_report(
                currentFileConfig.fileID,
                status=FileStatus.ERROR,
                message=f"Import for {fileConfig.filename} failed: {str(e)}",
                took=round(loop.time() - start_time, 2),
            )
            raise Exception(f"Import for {fileConfig.filename} failed: {str(e)}")

    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------

    def _build_category_config(self, components: dict) -> dict:
        """
        Build the config payload for one pipeline category (e.g. "Reader").

        Returns {"components": {name: meta, ...}, "selected": first_component_name}.
        `get_meta()` on each component includes env/library availability so the
        frontend knows which components are usable without an extra round-trip.
        """
        return {
            "components": {
                k: v.get_meta(self.environment_variables, self.installed_libraries)
                for k, v in components.items()
            },
            "selected": next(iter(components.values())).name,
        }

    def create_config(self) -> dict:
        """
        Build a fresh RAG config from the currently registered components.

        Called on every load_rag_config() to compare against the stored config
        and detect schema drift (added/removed components or config keys).
        """
        return {
            "Reader": self._build_category_config(self.reader_manager.readers),
            "Chunker": self._build_category_config(self.chunker_manager.chunkers),
            "Embedder": self._build_category_config(self.embedder_manager.embedders),
            "Retriever": self._build_category_config(self.retriever_manager.retrievers),
            "Generator": self._build_category_config(self.generator_manager.generators),
        }

    def create_user_config(self) -> dict:
        """Default user config returned when no stored config exists yet."""
        return {"getting_started": False}

    # Thin pass-throughs — config storage lives in Weaviate, not in memory.
    async def set_theme_config(self, client, config: dict):
        await self.weaviate_manager.set_config(client, self.theme_config_uuid, config)

    async def set_rag_config(self, client, config: dict):
        await self.weaviate_manager.set_config(client, self.rag_config_uuid, config)

    async def set_user_config(self, client, config: dict):
        await self.weaviate_manager.set_config(client, self.user_config_uuid, config)

    async def load_rag_config(self, client):
        """
        Return a valid RAG config, preferring the stored one.

        If the stored config is missing or fails verify_config() (schema drift),
        fall back to a freshly generated config and persist it.
        """
        loaded_config = await self.weaviate_manager.get_config(
            client, self.rag_config_uuid
        )
        new_config = self.create_config()
        if loaded_config is not None:
            if self.verify_config(loaded_config, new_config):
                msg.info("Using Existing RAG Configuration")
                return loaded_config
            else:
                msg.info("Using New RAG Configuration")
                await self.set_rag_config(client, new_config)
                return new_config
        else:
            msg.info("Using New RAG Configuration")
            return new_config

    async def load_theme_config(self, client):
        """Return (theme, themes) from Weaviate, or (None, None) if not set."""
        loaded_config = await self.weaviate_manager.get_config(
            client, self.theme_config_uuid
        )
        if loaded_config is None:
            return None, None
        return loaded_config["theme"], loaded_config["themes"]

    async def load_user_config(self, client):
        """Return the stored user config, or a fresh default if none exists."""
        loaded_config = await self.weaviate_manager.get_config(
            client, self.user_config_uuid
        )
        if loaded_config is None:
            return self.create_user_config()
        return loaded_config

    @staticmethod
    def _keys_match(a: dict, b: dict, label: str) -> bool:
        """Return True if both dicts have identical key sets; log and return False otherwise."""
        if set(a.keys()) == set(b.keys()):
            return True
        msg.fail(f"Config Validation Failed, {label}: {set(a.keys())} != {set(b.keys())}")
        return False

    def verify_config(self, a: dict, b: dict) -> bool:
        """
        Compare stored config `a` against authoritative config `b` (4 levels deep).

        Walks categories → components → config keys → setting fields.
        Returns False on the first mismatch so the caller knows to regenerate.
        In Demo mode, always returns True to avoid overwriting a shared config.
        """
        try:
            if os.getenv("VERBA_PRODUCTION") == "Demo":
                return True

            if not self._keys_match(a, b, "category mismatch"):
                return False

            for category_key in b:
                a_components = a[category_key]["components"]
                b_components = b[category_key]["components"]
                if not self._keys_match(a_components, b_components, f"{category_key} component mismatch"):
                    return False

                for component_key in b_components:
                    a_config = a_components[component_key]["config"]
                    b_config = b_components[component_key]["config"]
                    if not self._keys_match(a_config, b_config, f"{component_key} config key mismatch"):
                        return False

                    for config_key in b_config:
                        a_s, b_s = a_config[config_key], b_config[config_key]
                        if a_s["description"] != b_s["description"]:
                            msg.fail(f"Config Validation Failed, description mismatch: {a_s['description']} != {b_s['description']}")
                            return False
                        if sorted(a_s["values"]) != sorted(b_s["values"]):
                            msg.fail(f"Config Validation Failed, values mismatch: {a_s['values']} != {b_s['values']}")
                            return False

            return True

        except Exception as e:
            msg.fail(f"Config Validation failed: {str(e)}")
            return False

    async def reset_rag_config(self, client):
        msg.info("Resetting RAG Configuration")
        await self.weaviate_manager.reset_config(client, self.rag_config_uuid)

    async def reset_theme_config(self, client):
        msg.info("Resetting Theme Configuration")
        await self.weaviate_manager.reset_config(client, self.theme_config_uuid)

    async def reset_user_config(self, client):
        msg.info("Resetting User Configuration")
        await self.weaviate_manager.reset_config(client, self.user_config_uuid)

    # -------------------------------------------------------------------------
    # Environment and library introspection
    # -------------------------------------------------------------------------

    def _collect_from_managers(self, attr: str) -> set[str]:
        """
        Union of `attr` (e.g. 'requires_library') across every registered component.

        Used to build the availability maps shown in the status page without
        duplicating component iteration logic in each verify_* method.
        """
        managers = [
            (self.reader_manager, "readers"),
            (self.chunker_manager, "chunkers"),
            (self.embedder_manager, "embedders"),
            (self.retriever_manager, "retrievers"),
            (self.generator_manager, "generators"),
        ]
        return {
            item
            for mgr, collection_attr in managers
            for component in getattr(mgr, collection_attr).values()
            for item in getattr(component, attr)
        }

    def verify_installed_libraries(self) -> None:
        """
        Attempt to import every library declared by any component.
        Populates self.installed_libraries {lib_name: bool}.
        """
        for lib in self._collect_from_managers("requires_library"):
            try:
                importlib.import_module(lib)
                self.installed_libraries[lib] = True
            except Exception:
                self.installed_libraries[lib] = False

    def verify_variables(self) -> None:
        """
        Check which env vars declared by any component are actually set.
        Populates self.environment_variables {var_name: bool}.
        """
        for env in self._collect_from_managers("requires_env"):
            self.environment_variables[env] = os.environ.get(env) is not None

    # -------------------------------------------------------------------------
    # Document content retrieval
    # -------------------------------------------------------------------------

    async def get_content(
        self,
        client,
        uuid: str,
        page: int,
        chunkScores: list[ChunkScore],
    ):
        """
        Return paginated document content for the Document Explorer.

        Two modes:
          chunkScores present — RAG mode. Shows the matched chunk plus up to 5
            surrounding chunks for context. Three Weaviate fetches run in parallel.
          chunkScores empty   — Browse mode. Returns one page of sequential chunks
            and the total page count (chunk count + chunk count run in parallel).

        Returns: (content_pieces, total_batches)
          content_pieces: list of {"content", "chunk_id", "score", "type"} dicts
          total_batches:  total number of pages/scores available
        """
        chunks_per_page = 10
        content_pieces = []
        total_batches = 0

        if len(chunkScores) > 0:
            # RAG mode: show the matched chunk with surrounding context window.
            if page > len(chunkScores):
                page = 0

            total_batches = len(chunkScores)
            score = chunkScores[page]
            half = chunks_per_page // 2

            before_ids = list(range(max(0, score.chunk_id - half), score.chunk_id))
            after_ids = list(range(score.chunk_id + 1, score.chunk_id + half))

            async def _empty():
                return []

            # Fetch target + before/after context in a single round-trip.
            chunk, chunks_before, chunks_after = await asyncio.gather(
                self.weaviate_manager.get_chunk(client, score.uuid, score.embedder),
                self.weaviate_manager.get_chunk_by_ids(client, score.embedder, uuid, before_ids)
                if before_ids
                else _empty(),
                self.weaviate_manager.get_chunk_by_ids(client, score.embedder, uuid, after_ids)
                if after_ids
                else _empty(),
            )

            before_content = "".join(
                c.properties["content_without_overlap"] for c in (chunks_before or [])
            )
            after_content = "".join(
                c.properties["content_without_overlap"] for c in (chunks_after or [])
            )

            content_pieces.append({"content": before_content, "chunk_id": 0, "score": 0, "type": "text"})
            content_pieces.append({"content": chunk["content_without_overlap"] if chunk else "", "chunk_id": score.chunk_id, "score": score.score, "type": "extract"})
            content_pieces.append({"content": after_content, "chunk_id": 0, "score": 0, "type": "text"})

        else:
            # Browse mode: return one sequential page of chunks.
            document = await self.weaviate_manager.get_document(
                client, uuid, properties=["meta"]
            )
            if not document or not document.get("meta"):
                return (content_pieces, total_batches)

            config = json.loads(document["meta"])
            embedder = config["Embedder"]["config"]["Model"]["value"]
            request_chunk_ids = list(range(chunks_per_page * page, chunks_per_page * (page + 1)))

            # Fetch the page content and total count in parallel.
            chunks, total_chunks = await asyncio.gather(
                self.weaviate_manager.get_chunk_by_ids(client, embedder, uuid, request_chunk_ids),
                self.weaviate_manager.get_chunk_count(client, embedder, uuid),
            )
            total_batches = int(math.ceil(total_chunks / chunks_per_page))
            content = "".join(chunk.properties["content_without_overlap"] for chunk in chunks)
            content_pieces.append({"content": content, "chunk_id": 0, "score": 0, "type": "text"})

        return (content_pieces, total_batches)

    # -------------------------------------------------------------------------
    # RAG pipeline
    # -------------------------------------------------------------------------

    async def retrieve_chunks(
        self,
        client,
        query: str,
        rag_config: dict,
        labels: list[str] | None = None,
        document_uuids: list[str] | None = None,
    ):
        """
        Embed the query and retrieve relevant chunks via the selected Retriever.

        Also writes the query as an autocomplete suggestion (skipped for very
        short queries to avoid polluting suggestions with partial keystrokes).

        Returns: (documents, context_string)
        """
        labels = labels or []
        document_uuids = document_uuids or []

        retriever = rag_config["Retriever"].selected
        embedder = rag_config["Embedder"].selected

        # Only persist as a suggestion if the query is meaningful.
        if query and len(query.strip()) >= 3:
            await self.weaviate_manager.add_suggestion(client, query)

        vector = await self.embedder_manager.vectorize_query(embedder, query, rag_config)
        documents, context = await self.retriever_manager.retrieve(
            client, retriever, query, vector, rag_config,
            self.weaviate_manager, labels, document_uuids,
        )

        return (documents, context)

    async def generate_stream_answer(
        self,
        rag_config: dict,
        query: str,
        context: str,
        conversation: list[dict],
    ):
        """
        Async generator that streams token chunks from the selected Generator.

        Accumulates tokens into full_text_parts and attaches full_text to the
        final "stop" chunk so the caller gets the complete answer in one place.
        Yields each result dict directly to the WebSocket handler in api.py.
        """
        full_text_parts: list[str] = []
        async for result in self.generator_manager.generate_stream(
            rag_config, query, context, conversation
        ):
            full_text_parts.append(result["message"])
            if result.get("finish_reason") == "stop":
                result["full_text"] = "".join(full_text_parts)
            yield result
