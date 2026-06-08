"""
embedding_manager.py
====================
Embedder component registry and EmbeddingManager.

To add a new Embedder:
  1. Implement it in this directory (goldenverba/components/embedding/)
  2. Import it below and add an instance to the embedders list

VERBA_PRODUCTION env var
------------------------
When set to "Production", local-only embedders (Ollama, SentenceTransformers) are
excluded. This is used for hosted deployments where those services aren't available.
"""

import os
import asyncio

from wasabi import msg
from sklearn.decomposition import PCA

from goldenverba.components.document import Document
from goldenverba.components.interfaces import Embedding
from goldenverba.server.helpers import LoggerManager
from goldenverba.server.types import FileConfig, FileStatus

from goldenverba.components.embedding.OpenAIEmbedder import OpenAIEmbedder
from goldenverba.components.embedding.CohereEmbedder import CohereEmbedder
from goldenverba.components.embedding.OllamaEmbedder import OllamaEmbedder
from goldenverba.components.embedding.UpstageEmbedder import UpstageEmbedder
from goldenverba.components.embedding.WeaviateEmbedder import WeaviateEmbedder
from goldenverba.components.embedding.VoyageAIEmbedder import VoyageAIEmbedder
from goldenverba.components.embedding.SentenceTransformersEmbedder import (
    SentenceTransformersEmbedder,
)
from goldenverba.components.embedding.LMStudioEmbedder import LMStudioEmbedder

# Local-only embedders are excluded in Production mode (hosted deployments)
_is_production = os.getenv("VERBA_PRODUCTION") == "Production"

embedders = [
    e for e in [
        OllamaEmbedder(),
        SentenceTransformersEmbedder(),
        WeaviateEmbedder(),
        UpstageEmbedder(),
        VoyageAIEmbedder(),
        CohereEmbedder(),
        OpenAIEmbedder(),
        LMStudioEmbedder(),
    ]
    # OllamaEmbedder and SentenceTransformersEmbedder require local services
    if not _is_production or e.name not in {"Ollama", "SentenceTransformers"}
]


class EmbeddingManager:
    """Dispatches vectorize() calls to the correct Embedder implementation."""

    def __init__(self):
        self.embedders: dict[str, Embedding] = {
            embedder.name: embedder for embedder in embedders
        }

    async def vectorize(
        self,
        embedder: str,
        fileConfig: FileConfig,
        documents: list[Document],
        logger: LoggerManager,
    ) -> list[Document]:
        """Vectorizes chunks in batches
        @parameter: documents : Document - Verba document
        @returns Document - Document with vectorized chunks
        """
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time()
            if embedder in self.embedders:
                config = fileConfig.rag_config["Embedder"].components[embedder].config

                for document in documents:
                    content = [
                        document.metadata + "\n" + chunk.content
                        for chunk in document.chunks
                    ]
                    embeddings = await self.batch_vectorize(embedder, config, content)

                    if len(embeddings) >= 3:
                        pca = PCA(n_components=3)
                        generated_pca_embeddings = pca.fit_transform(embeddings)
                        pca_embeddings = [
                            pca_.tolist() for pca_ in generated_pca_embeddings
                        ]
                    else:
                        pca_embeddings = [embedding[0:3] for embedding in embeddings]

                    for vector, chunk, pca_ in zip(
                        embeddings, document.chunks, pca_embeddings
                    ):
                        chunk.vector = vector
                        chunk.pca = pca_

                    document.meta["Embedder"] = (
                        fileConfig.rag_config["Embedder"]
                        .components[embedder]
                        .model_dump()
                    )

                elapsed_time = round(loop.time() - start_time, 2)
                await logger.send_report(
                    fileConfig.fileID,
                    FileStatus.EMBEDDING,
                    f"Vectorized all chunks",
                    took=elapsed_time,
                )
                await logger.send_report(
                    fileConfig.fileID, FileStatus.INGESTING, "", took=0
                )
                return documents
            else:
                raise Exception(f"{embedder} Embedder not found")
        except Exception as e:
            raise e

    async def batch_vectorize(
        self, embedder: str, config: dict, content: list[str]
    ) -> list[list[float]]:
        """Vectorize content in batches"""
        try:
            batches = [
                content[i : i + self.embedders[embedder].max_batch_size]
                for i in range(0, len(content), self.embedders[embedder].max_batch_size)
            ]
            msg.info(f"Vectorizing {len(content)} chunks in {len(batches)} batches")
            tasks = [
                self.embedders[embedder].vectorize(config, batch) for batch in batches
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check if all tasks were successful
            errors = [r for r in results if isinstance(r, Exception)]
            if errors:
                error_messages = [str(e) for e in errors]
                raise Exception(
                    f"Vectorization failed for some batches: {', '.join(error_messages)}"
                )

            # Flatten the results
            flattened_results = [item for sublist in results for item in sublist]

            # Verify the number of vectors matches the input content
            if len(flattened_results) != len(content):
                raise Exception(
                    f"Mismatch in vectorization results: expected {len(content)} vectors, got {len(flattened_results)}"
                )

            return flattened_results
        except Exception as e:
            raise Exception(f"Batch vectorization failed: {str(e)}")

    async def vectorize_query(
        self, embedder: str, content: str, rag_config: dict
    ) -> list[float]:
        try:
            if embedder in self.embedders:
                config = rag_config["Embedder"].components[embedder].config
                embeddings = await self.embedders[embedder].vectorize(config, [content])
                return embeddings[0]
            else:
                raise Exception(f"{embedder} Embedder not found")
        except Exception as e:
            raise e
