from weaviate import Client

from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.reader.interface import InputForm
from goldenverba.ingestion.component import VerbaComponent

from wasabi import msg


class Embedder(VerbaComponent):
    """
    Interface for Verba Embedding
    """

    def __init__(self):
        super().__init__()
        self.name = ""
        self.input_form = InputForm.TEXT.value  # Default for all Embedders
        self.description = ""
        self.vectorizer = "text2vec-openai"

    def embed(documents: list[Document], client: Client, batch_size: int = 100) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful
        """
        raise NotImplementedError("embed method must be implemented by a subclass.")

    def check_document_status(
        self,
        client: Client,
        doc_uuid: str,
        doc_name: str,
        doc_class_name: str,
        chunk_class_name: str,
        chunk_count: int,
    ):
        """Verifies that imported documents and its chunks exist in the database, if not, remove everything that was added and rollback
        @parameter: client : Client - Weaviate Client
        @parameter: doc_uuid : str - Document UUID
        @parameter: doc_name : str - Document name
        @parameter: doc_class_name : str - Class name of Document
        @parameter: chunk_class_name : str - Class name of Chunks
        @parameter: chunk_count : int - Number of expected chunks
        @returns Optional[Exception] - Raises Exceptions if imported fail, will be catched by the manager
        """
        document = client.data_object.get_by_id(
            doc_uuid,
            class_name=doc_class_name,
        )

        if document != None:
            results = (
                client.query.get(
                    class_name=chunk_class_name,
                    properties=[
                        "doc_name",
                    ],
                )
                .with_where(
                    {
                        "path": ["doc_uuid"],
                        "operator": "Equal",
                        "valueText": doc_uuid,
                    }
                )
                .with_limit(chunk_count)
                .do()
            )

            if len(results["data"]["Get"][chunk_class_name]) != chunk_count:
                # Rollback if fails
                self.remove_document(client, doc_name, doc_class_name, chunk_class_name)
                raise Exception(
                    f"Chunk mismatch for {doc_uuid} {len(results['data']['Get'])} != {chunk_count}"
                )
        else:
            raise Exception(f"Document {doc_uuid} not found {document}")

    def remove_document(
        self, client: Client, doc_name: str, doc_class_name: str, chunk_class_name: str
    ) -> None:
        """Deletes documents and its chunks
        @parameter: client : Client - Weaviate Client
        @parameter: doc_name : str - Document name
        @parameter: doc_class_name : str - Class name of Document
        @parameter: chunk_class_name : str - Class name of Chunks
        """
        client.batch.delete_objects(
            class_name=doc_class_name,
            where={"path": ["doc_name"], "operator": "Equal", "valueText": doc_name},
        )

        client.batch.delete_objects(
            class_name=chunk_class_name,
            where={"path": ["doc_name"], "operator": "Equal", "valueText": doc_name},
        )

        msg.warn(f"Deleted document {doc_name} and its chunks")
