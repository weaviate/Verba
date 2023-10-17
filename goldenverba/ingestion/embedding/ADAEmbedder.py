from weaviate import Client
from wasabi import msg

from goldenverba.ingestion.embedding.interface import Embedder
from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.reader.interface import InputForm
from goldenverba.ingestion.schema.schema_generation import (
    VECTORIZERS,
    EMBEDDINGS,
    strip_non_letters,
)


class ADAEmbedder(Embedder):
    """
    ADAEmbedder for Verba
    """

    def __init__(self):
        super().__init__()
        self.name = "ADAEmbedder"
        self.requires_env = ["OPENAI_API_KEY"]
        self.requires_library = ["openai"]
        self.description = "Embeds and retrieves objects using OpenAI's ADA model"
        self.vectorizer = "text2vec-openai"

    def embed(
        self,
        documents: list[Document],
        client: Client,
    ) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful
        """
        try:
            if self.vectorizer not in VECTORIZERS and self.vectorizer not in EMBEDDINGS:
                msg.fail(f"Vectorizer of {self.name} not found")
                return False

            for i, document in enumerate(documents):
                batches = []
                uuid = ""
                temp_batch = []
                token_counter = 0
                for chunk in document.chunks:
                    if token_counter + chunk.tokens <= 4000:
                        token_counter += chunk.tokens
                        temp_batch.append(chunk)
                    else:
                        batches.append(temp_batch.copy())
                        token_counter = 0
                        temp_batch = []
                if len(temp_batch) > 0:
                    batches.append(temp_batch.copy())
                    token_counter = 0
                    temp_batch = []

                msg.info(
                    f"({i+1}/{len(documents)}) Importing document {document.name} with {len(batches)} batches"
                )

                with client.batch as batch:
                    batch.batch_size = 1
                    properties = {
                        "text": str(document.text),
                        "doc_name": str(document.name),
                        "doc_type": str(document.type),
                        "doc_link": str(document.link),
                        "chunk_count": len(document.chunks),
                        "timestamp": str(document.timestamp),
                    }

                    class_name = "Document_" + strip_non_letters(self.vectorizer)
                    uuid = client.batch.add_data_object(properties, class_name)

                    for chunk in document.chunks:
                        chunk.set_uuid(uuid)

                for batch_id, chunk_batch in enumerate(batches):
                    with client.batch as batch:
                        batch.batch_size = len(chunk_batch)
                        for i, chunk in enumerate(chunk_batch):
                            msg.info(
                                f"({i+1}/{len(document.chunks)} of batch ({batch_id+1})) Importing chunk of {document.name}"
                            )

                            properties = {
                                "text": chunk.text,
                                "doc_name": str(document.name),
                                "doc_uuid": chunk.doc_uuid,
                                "doc_type": chunk.doc_type,
                                "chunk_id": chunk.chunk_id,
                            }
                            class_name = "Chunk_" + strip_non_letters(self.vectorizer)
                            client.batch.add_data_object(properties, class_name)

                self.check_document_status(
                    client,
                    uuid,
                    document.name,
                    "Document_" + strip_non_letters(self.vectorizer),
                    "Chunk_" + strip_non_letters(self.vectorizer),
                    len(document.chunks),
                )

            return True
        except Exception as e:
            raise Exception(e)
