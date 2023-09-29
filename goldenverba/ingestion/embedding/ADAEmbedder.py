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
        self.name = "ADAEmbedder"
        self.requires_env = ["OPENAI_API_KEY"]
        self.requires_library = ["openai"]
        self.description = "Embeds and retrieves objects using OpenAI's ADA model"
        self.input_form = InputForm.TEXT.value
        self.vectorizer = "text2vec-openai"

    def embed(
        self, documents: list[Document], client: Client, batch_size: int = 100
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

            with client.batch as batch:
                batch.batch_size = batch_size
                for i, d in enumerate(documents):
                    msg.info(f"({i+1}/{len(documents)}) Importing document {d.name}")

                    properties = {
                        "text": str(d.text),
                        "doc_name": str(d.name),
                        "doc_type": str(d.type),
                        "doc_link": str(d.link),
                        "timestamp": str(d.timestamp),
                    }

                    class_name = "Document_" + strip_non_letters(self.vectorizer)
                    uuid = client.batch.add_data_object(properties, class_name)

                    for chunk in d.chunks:
                        chunk.set_uuid(uuid)

            with client.batch as batch:
                batch.batch_size = batch_size
                for d in documents:
                    for i, chunk in enumerate(d.chunks):
                        msg.info(f"({i+1}/{len(d.chunks)}) Importing chunk of {d.name}")

                        properties = {
                            "text": chunk.text,
                            "doc_name": str(d.name),
                            "doc_uuid": chunk.doc_uuid,
                            "doc_type": chunk.doc_type,
                            "chunk_id": chunk.chunk_id,
                        }
                        class_name = "Chunk_" + strip_non_letters(self.vectorizer)
                        client.batch.add_data_object(properties, class_name)

            return True
        except Exception as e:
            msg.fail(f"Something went wrong {str(e)}")
            return False
