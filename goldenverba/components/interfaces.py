from goldenverba.components.document import Document
from goldenverba.server.types import FileConfig
from goldenverba.components.types import InputConfig

from dotenv import load_dotenv

from wasabi import msg
from weaviate import Client

load_dotenv()


class VerbaComponent:
    """
    Base Class for Verba Readers, Chunkers, Embedders, Retrievers, and Generators.
    """

    def __init__(self):
        self.name = ""
        self.requires_env = []
        self.requires_library = []
        self.description = ""
        self.config = {}
        self.type = ""

    def get_meta(self, envs, libs) -> dict:

        if len(self.config) > 0:
            config = {_c: self.config[_c].model_dump() for _c in self.config}
        else:
            config = {}

        return {
            "name": self.name,
            "variables": self.requires_env,
            "library": self.requires_library,
            "description": self.description,
            "type": self.type,
            "config": config,
            "available": self.check_available(envs, libs),
        }

    def check_available(self, envs, libs) -> bool:
        if self.requires_env:
            for _env in self.requires_env:
                if _env not in envs or not envs.get(_env, False):
                    return False
        if self.requires_library:
            for _lib in self.requires_library:
                if _lib not in libs or not libs.get(_lib, False):
                    return False
        return True


class Reader(VerbaComponent):
    """
    Interface for Verba Readers.
    """

    def __init__(self):
        super().__init__()
        self.type = "FILE"  # "URL"
        self.extension = ["txt", "md", "mdx", "py", "ts", "tsx", "js", "go", "css"]

    async def load(self, config: dict, fileConfig: FileConfig) -> list[Document]:
        """Convert fileConfig into Verba Documents
        @parameter: fileConfig: FileConfig - FileConfiguration sent by the frontend
        @returns list[Document] - Verba documents
        """
        raise NotImplementedError("load method must be implemented by a subclass.")


class Embedding(VerbaComponent):
    """
    Interface for Verba Embedder Components.
    """

    def __init__(self):
        super().__init__()
        self.max_batch_size = 128

    async def vectorize(self, config: dict, content: list[str]) -> list[float]:
        """Embed verba documents and its chunks to Weaviate
        @parameter: config : dict - Embedder Configuration
        @parameter: content : list[str] - List of strings to embed
        @return: list[float] - List of embeddings
        """
        raise NotImplementedError("embed method must be implemented by a subclass.")


class Chunker(VerbaComponent):
    """
    Interface for Verba Chunking.
    """

    def __init__(self):
        super().__init__()
        self.config = {}

    async def chunk(
        self,
        config: dict,
        documents: list[Document],
        embedder: Embedding | None = None,
        embedder_config: dict | None = None,
    ) -> list[Document]:
        """Split Verba documents into chunks.
        @parameter: config : dict - Chunker Configuration
        @parameter: documents : list[Document] - List of Verba documents to chunk
        @parameter: embedder : Embedding | None - (Optional) Selected Embedder if the Chunker requires vectorization
        @parameter: embedder_config : dict | None - (Optional) Embedder Configuration
        @return: list[Documents]
        """
        raise NotImplementedError("chunk method must be implemented by a subclass.")


class Embedder(VerbaComponent):
    """
    Interface for Verba Embedding.
    """

    def __init__(self):
        super().__init__()
        self.vectorizer = ""

    def embed(
        documents: list[Document],
        client: Client,
        logging: list[dict],
        batch_size: int = 100,
    ) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        raise NotImplementedError("embed method must be implemented by a subclass.")

    def remove_document(
        self, client: Client, doc_name: str, doc_class_name: str, chunk_class_name: str
    ) -> None:
        """Deletes documents and its chunks
        @parameter: client : Client - Weaviate Client
        @parameter: doc_name : str - Document name
        @parameter: doc_class_name : str - Class name of Document
        @parameter: chunk_class_name : str - Class name of Chunks.
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

    def remove_document_by_id(self, client: Client, doc_id: str):
        doc_class_name = "VERBA_Document_" + strip_non_letters(self.vectorizer)
        chunk_class_name = "VERBA_Chunk_" + strip_non_letters(self.vectorizer)

        client.data_object.delete(uuid=doc_id, class_name=doc_class_name)

        client.batch.delete_objects(
            class_name=chunk_class_name,
            where={"path": ["doc_uuid"], "operator": "Equal", "valueText": doc_id},
        )

        msg.warn(f"Deleted document {doc_id} and its chunks")

    def get_document_class(self) -> str:
        return "VERBA_Document_" + strip_non_letters(self.vectorizer)

    def get_chunk_class(self) -> str:
        return "VERBA_Chunk_" + strip_non_letters(self.vectorizer)

    def get_cache_class(self) -> str:
        return "VERBA_Cache_" + strip_non_letters(self.vectorizer)

    def search_documents(
        self, client: Client, query: str, doc_type: str, page: int, pageSize: int
    ) -> list:
        """Search for documents from Weaviate
        @parameter query_string : str - Search query
        @returns list - Document list.
        """
        doc_class_name = "VERBA_Document_" + strip_non_letters(self.vectorizer)
        offset = pageSize * (page - 1)

        if doc_type == "" or doc_type is None:
            query_results = (
                client.query.get(
                    class_name=doc_class_name,
                    properties=["doc_name", "doc_type", "doc_link"],
                )
                .with_bm25(query, properties=["doc_name"])
                .with_additional(properties=["id"])
                .with_limit(pageSize)
                .with_offset(offset)
                .do()
            )
        else:
            query_results = (
                client.query.get(
                    class_name=doc_class_name,
                    properties=["doc_name", "doc_type", "doc_link"],
                )
                .with_bm25(query, properties=["doc_name"])
                .with_where(
                    {
                        "path": ["doc_type"],
                        "operator": "Equal",
                        "valueText": doc_type,
                    }
                )
                .with_offset(offset)
                .with_additional(properties=["id"])
                .with_limit(100)
                .do()
            )

        # TODO Better Error Handling, what if error occur?
        results = query_results["data"]["Get"][doc_class_name]
        return results

    def get_need_vectorization(self) -> bool:
        if self.vectorizer in EMBEDDINGS:
            return True
        return False

    def vectorize_query(self, query: str):
        raise NotImplementedError(
            "vectorize_query method must be implemented by a subclass."
        )

    def conversation_to_query(self, queries: list[str], conversation: dict) -> str:
        query = ""

        if len(conversation) > 1:
            if conversation[-1].type == "system":
                query += conversation[-1].content + " "
            elif conversation[-2].type == "system":
                query += conversation[-2].content + " "

        for _query in queries:
            query += _query + " "

        return query.lower()

    def retrieve_semantic_cache(
        self, client: Client, query: str, dist: float = 0.04
    ) -> str:
        """Retrieve results from semantic cache based on query and distance threshold
        @parameter query - str - User query
        @parameter dist - float - Distance threshold
        @returns Optional[dict] - List of results or None.
        """
        needs_vectorization = self.get_need_vectorization()

        match_results = (
            client.query.get(
                class_name=self.get_cache_class(),
                properties=["query", "system"],
            )
            .with_where(
                {
                    "path": ["query"],
                    "operator": "Equal",
                    "valueText": query,
                }
            )
            .with_limit(1)
        ).do()

        if (
            "data" in match_results
            and len(match_results["data"]["Get"][self.get_cache_class()]) > 0
            and (
                query
                == match_results["data"]["Get"][self.get_cache_class()][0]["query"]
            )
        ):
            msg.good("Direct match from cache")
            return (
                match_results["data"]["Get"][self.get_cache_class()][0]["system"],
                0.0,
            )

        query_results = (
            client.query.get(
                class_name=self.get_cache_class(),
                properties=["query", "system"],
            )
            .with_additional(properties=["distance"])
            .with_limit(1)
        )

        if needs_vectorization:
            vector = self.vectorize_query(query)
            query_results = query_results.with_near_vector(
                content={"vector": vector},
            ).do()

        else:
            query_results = query_results.with_near_text(
                content={"concepts": [query]},
            ).do()

        if "data" not in query_results:
            msg.warn(query_results)
            return None, None

        results = query_results["data"]["Get"][self.get_cache_class()]

        if not results:
            return None, None

        result = results[0]

        if float(result["_additional"]["distance"]) <= dist:
            msg.good("Retrieved similar from cache")
            return result["system"], float(result["_additional"]["distance"])

        else:
            return None, None

    def add_to_semantic_cache(self, client: Client, query: str, system: str):
        """Add results to semantic cache
        @parameter query : str - User query
        @parameter results : list[dict] - Results from Weaviate
        @parameter system : str - System message
        @returns None.
        """
        needs_vectorization = self.get_need_vectorization()

        with client.batch as batch:
            batch.batch_size = 1
            properties = {
                "query": str(query),
                "system": system,
            }
            msg.good("Saved to cache")

            if needs_vectorization:
                vector = self.vectorize_query(query)
                client.batch.add_data_object(
                    properties, self.get_cache_class(), vector=vector
                )
            else:
                client.batch.add_data_object(properties, self.get_cache_class())


class Retriever(VerbaComponent):
    """
    Interface for Verba Retrievers.
    """

    def __init__(self):
        super().__init__()
        self.config["Suggestion"] = InputConfig(
            type="bool",
            value=True,
            description="Enable Autocomplete Suggestions",
            values=[],
        )

    async def retrieve(
        self,
        client,
        query,
        vector,
        config,
        weaviate_manager,
        embedder,
        labels,
        document_uuids,
    ):

        raise NotImplementedError("retrieve method must be implemented by a subclass.")


class Generator(VerbaComponent):
    """
    Interface for Verba Generators.
    """

    def __init__(self):
        super().__init__()
        self.context_window = 5000
        self.config["System Message"] = InputConfig(
            type="text",
            value="You are Verba, a chatbot for Retrieval Augmented Generation (RAG). You will receive a user query and context pieces that have a semantic similarity to that query. Please answer these user queries only with the provided context. Mention documents you used from the context if you use them to reduce hallucination. If the provided documentation does not provide enough information, say so. If the user asks questions about you as a chatbot specifially, answer them naturally. If the answer requires code examples encapsulate them with ```programming-language-name ```. Don't do pseudo-code.",
            description="System Message",
            values=[],
        )

    async def generate_stream(
        self,
        queries: list[str],
        context: list[str],
        conversation: dict = None,
    ):
        """Generate a stream of response dicts based on a list of queries and list of contexts, and includes conversational context
        @parameter: queries : list[str] - List of queries
        @parameter: context : list[str] - List of contexts
        @parameter: conversation : dict - Conversational context
        @returns Iterator[dict] - Token response generated by the Generator in this format {system:TOKEN, finish_reason:stop or empty}.
        """
        if conversation is None:
            conversation = {}
        raise NotImplementedError(
            "generate_stream method must be implemented by a subclass."
        )

    def prepare_messages(
        self, queries: list[str], context: list[str], conversation: dict[str, str]
    ) -> any:
        """
        Prepares a list of messages formatted for a Retrieval Augmented Generation chatbot system, including system instructions, previous conversation, and a new user query with context.

        @parameter queries: A list of strings representing the user queries to be answered.
        @parameter context: A list of strings representing the context information provided for the queries.
        @parameter conversation: A list of previous conversation messages that include the role and content.

        @returns A list or of message dictionaries or whole prompts formatted for the chatbot. This includes an initial system message, the previous conversation messages, and the new user query encapsulated with the provided context.

        Each message in the list is a dictionary with 'role' and 'content' keys, where 'role' is either 'system' or 'user', and 'content' contains the relevant text. This will depend on the LLM used.
        """
        raise NotImplementedError(
            "prepare_messages method must be implemented by a subclass."
        )
