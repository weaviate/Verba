import re
import os
from dotenv import load_dotenv
from wasabi import msg  # type: ignore[import]
from weaviate import (
    WeaviateClient,
)
from weaviate.collections.collections import Collection
from weaviate.collections.classes.types import WeaviateProperties
import weaviate.classes.config as wvc
from typing import TypedDict, List, Union
from dataclasses import dataclass
from verba_types import VectorizerType, EmbeddingType, VectorizerOrEmbeddingType


load_dotenv()


VECTORIZERS: List[VectorizerType] = [
    VectorizerType(
        name="text2vecopenai", config_class=wvc.Configure.NamedVectors.text2vec_openai
    ),
    VectorizerType(
        name="text2veccohere", config_class=wvc.Configure.NamedVectors.text2vec_cohere
    ),
]  # Needs to match with Weaviate modules
EMBEDDINGS: List[EmbeddingType] = [EmbeddingType(name="MiniLM")]  # Custom Vectors


def strip_non_letters(s: str):
    return re.sub(r"[^a-zA-Z0-9]", "_", s)


# TODO: not used anymore, recreate checks
def verify_vectorizer(
    schema: dict, vectorizer: str, skip_properties: list[str] = []
) -> dict:
    """Verifies if the vectorizer is available and adds it to a schema, also skips vectorization if list is provided
    @parameter schema : dict - Schema json
    @parameter vectorizer : str - Name of the vectorizer
    @parameter skip_properties: list[str] - List of property names that should not get vectorized
    @returns dict - Modified schema if vectorizer is available.
    """
    if skip_properties is None:
        skip_properties = []
    modified_schema = schema.copy()

    # adding specific config for Azure OpenAI
    vectorizer_config = None
    if os.getenv("OPENAI_API_TYPE") == "azure" and vectorizer == "text2vec-openai":
        resourceName = os.getenv("AZURE_OPENAI_RESOURCE_NAME")
        model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
        if resourceName is None or model is None:
            raise Exception(
                "AZURE_OPENAI_RESOURCE_NAME and AZURE_OPENAI_EMBEDDING_MODEL should be set when OPENAI_API_TYPE is azure. Resource name is XXX in http://XXX.openai.azure.com"
            )
        vectorizer_config = {
            "text2vec-openai": {"deploymentId": model, "resourceName": resourceName}
        }

    # Verify Vectorizer
    if vectorizer in VECTORIZERS:
        modified_schema["classes"][0]["vectorizer"] = vectorizer
        if vectorizer_config is not None:
            modified_schema["classes"][0]["moduleConfig"] = vectorizer_config
        for property in modified_schema["classes"][0]["properties"]:
            if property["name"] in skip_properties:
                moduleConfig = {
                    vectorizer: {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                }
                property["moduleConfig"] = moduleConfig
    elif vectorizer in EMBEDDINGS:
        pass
    elif vectorizer is not None:
        msg.warn(f"Could not find matching vectorizer: {vectorizer}")

    return modified_schema


def reset_schemas(client: WeaviateClient):
    client.collections._delete("Document")
    client.collections._delete("Chunk")
    client.collections._delete("Cache")


def init_schemas(
    client: WeaviateClient,
    force: bool = False,
    check: bool = False,
) -> bool:
    """Initializes a weaviate client and initializes all required schemas
    @parameter client : Client - Weaviate Client
    @parameter vectorizer : str - Name of the vectorizer
    @parameter force : bool - Delete existing schema without user input
    @parameter check : bool - Only create if not exist
    @returns tuple[dict, dict] - Tuple of modified schemas.
    """
    try:

        init_documents(client, force, check)
        init_cache(client, force, check)
        init_suggestion(client, force, check)
        return True
    except Exception as e:
        msg.fail(f"Schema initialization failed {str(e)}")
        return False


def init_documents(
    client: WeaviateClient, force: bool = False, check: bool = False
) -> tuple[Collection[WeaviateProperties, None], Collection[WeaviateProperties, None]]:
    """Initializes the Document and Chunk class
    @parameter client : Client - Weaviate client
    @parameter vectorizer : str - Name of the vectorizer
    @parameter force : bool - Delete existing schema without user input
    @parameter check : bool - Only create if not exist
    @returns tuple[dict, dict] - Tuple of modified schemas.
    """

    chunk_properties = [
        wvc.Property(
            name="text",
            data_type=wvc.DataType.TEXT,
            description="Content of the document",
        ),
        wvc.Property(
            name="doc_name",
            data_type=wvc.DataType.TEXT,
            description="Document name",
        ),
        wvc.Property(
            name="doc_type",
            data_type=wvc.DataType.TEXT,
            description="Document type",
        ),
        wvc.Property(
            name="doc_uuid",
            data_type=wvc.DataType.TEXT,
            description="Document UUID",
        ),
        wvc.Property(
            name="chunk_id",
            data_type=wvc.DataType.NUMBER,
            description="Document chunk from the whole document",
        ),
    ]

    document_properties = [
        wvc.Property(
            name="text",
            data_type=wvc.DataType.TEXT,
            description="Content of the document",
        ),
        wvc.Property(
            name="doc_name",
            data_type=wvc.DataType.TEXT,
            description="Document name",
        ),
        wvc.Property(
            name="doc_type",
            data_type=wvc.DataType.TEXT,
            description="Document type",
        ),
        wvc.Property(
            name="doc_link",
            data_type=wvc.DataType.TEXT,
            description="Link to document",
        ),
        wvc.Property(
            name="timestamp",
            data_type=wvc.DataType.TEXT,
            description="Timestamp of document",
        ),
        wvc.Property(
            name="chunk_count",
            data_type=wvc.DataType.NUMBER,
            description="Number of chunks",
        ),
    ]

    vectorizer_config = [
        vectorizer.config_class(name=vectorizer.name) for vectorizer in VECTORIZERS
    ]

    vectorizer_config.extend(
        [
            wvc.Configure.NamedVectors.none(name=embedding.name)
            for embedding in EMBEDDINGS
        ]
    )

    document_name = "Document"
    chunk_name = "Chunk"

    if client.collections.exists("Document"):
        if check:
            return client.collections.get("Document"), client.collections.get("Chunk")
        if not force:
            user_input = input(
                f"Document class already exists, do you want to delete it? (y/n): "
            )
        else:
            user_input = "y"
        if user_input.strip().lower() == "y":
            client.collections.delete("Document")
            client.collections.delete("Chunk")
            client.collections.create(
                "Document",
                properties=document_properties,
                vectorizer_config=vectorizer_config,
            )
            client.collections.create(
                "Chunk",
                properties=chunk_properties,
                vectorizer_config=vectorizer_config,
            )
            msg.good(f"Document and Chunk schemas created")
        else:
            msg.warn(
                f"Skipped deleting {document_name} and {chunk_name} schema, nothing changed"
            )
    else:
        client.collections.create(
            "Document",
            properties=document_properties,
            vectorizer_config=vectorizer_config,
        )
        client.collections.create(
            "Chunk",
            properties=chunk_properties,
            vectorizer_config=vectorizer_config,
        )
        msg.good(f"{document_name} and {chunk_name} schemas created")

    return client.collections.get("Document"), client.collections.get("Chunk")


def init_cache(
    client: WeaviateClient, force: bool = False, check: bool = False
) -> Collection[WeaviateProperties, None]:
    """Initializes the Cache
    @parameter client : Client - Weaviate client
    @parameter vectorizer : str - Name of the vectorizer
    @parameter force : bool - Delete existing schema without user input
    @parameter check : bool - Only create if not exist
    @returns dict - Modified schema.
    """

    cache_schema = [
        wvc.Property(
            name="query",
            data_type=wvc.DataType.TEXT,
            description="Query",
        ),
        wvc.Property(
            name="system",
            data_type=wvc.DataType.TEXT,
            description="System message",
        ),
    ]

    vectorizer_config = [
        vectorizer.config_class(name=vectorizer.name) for vectorizer in VECTORIZERS
    ]

    vectorizer_config.extend(
        [
            wvc.Configure.NamedVectors.none(name=embedding.name)
            for embedding in EMBEDDINGS
        ]
    )

    cache_name = "Cache"

    if client.collections.exists("Cache"):
        if check:
            return client.collections.get("Cache")
        if not force:
            user_input = input(
                f"Cache class already exists, do you want to delete it? (y/n): "
            )
        else:
            user_input = "y"
        if user_input.strip().lower() == "y":
            client.collections.delete("Cache")
            client.collections.create(
                "Cache",
                properties=cache_schema,
                vectorizer_config=vectorizer_config,
            )
            msg.good(f"Cache schema created")
        else:
            msg.warn(f"Skipped deleting Cache schema, nothing changed")
    else:
        client.collections.create(
            "Cache",
            properties=cache_schema,
            vectorizer_config=vectorizer_config,
        )
        msg.good(f"Cache schema created")

    return client.collections.get("Cache")


def init_suggestion(
    client: WeaviateClient, force: bool = False, check: bool = False
) -> Collection[WeaviateProperties, None]:
    """Initializes the Suggestion schema
    @parameter client : Client - Weaviate client
    @parameter vectorizer : str - Name of the vectorizer
    @parameter force : bool - Delete existing schema without user input
    @parameter check : bool - Only create if not exist
    @returns dict - Modified schema.
    """

    suggestion_schema = [
        wvc.Property(
            name="suggestion",
            data_type=wvc.DataType.TEXT,
            description="Query",
        ),
    ]

    vectorizer_config = [
        vectorizer.config_class(name=vectorizer.name) for vectorizer in VECTORIZERS
    ]

    vectorizer_config.extend(
        [
            wvc.Configure.NamedVectors.none(name=embedding.name)
            for embedding in EMBEDDINGS
        ]
    )

    suggestion_name = "Suggestion"

    if client.collections.exists("Suggestion"):
        if check:
            return client.collections.get("Suggestion")
        if not force:
            user_input = input(
                f"Suggestion class already exists, do you want to delete it? (y/n): "
            )
        else:
            user_input = "y"
        if user_input.strip().lower() == "y":
            client.collections.delete("Suggestion")
            client.collections.create(
                "Suggestion",
                properties=suggestion_schema,
                vectorizer_config=vectorizer_config,
            )
            msg.good(f"Suggestion schema created")
        else:
            msg.warn(f"Skipped deleting Suggestion schema, nothing changed")
    else:
        client.collections.create(
            "Suggestion",
            properties=suggestion_schema,
            vectorizer_config=vectorizer_config,
        )
        msg.good(f"Suggestion schema created")

    return client.collections.get("Suggestion")
