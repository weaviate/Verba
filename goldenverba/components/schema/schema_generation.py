import re

from wasabi import msg  # type: ignore[import]
from weaviate import Client


VECTORIZERS = set(
    ["text2vec-openai", "text2vec-cohere"]
)  # Needs to match with Weaviate modules
EMBEDDINGS = set(["MiniLM"])  # Custom Vectors


def strip_non_letters(s: str):
    return re.sub(r"[^a-zA-Z0-9]", "_", s)


def verify_vectorizer(
    schema: dict, vectorizer: str, skip_properties: list[str] = []
) -> dict:
    """Verifies if the vectorizer is available and adds it to a schema, also skips vectorization if list is provided
    @parameter schema : dict - Schema json
    @parameter vectorizer : str - Name of the vectorizer
    @parameter skip_properties: list[str] - List of property names that should not get vectorized
    @returns dict - Modified schema if vectorizer is available
    """
    modified_schema = schema.copy()
    # Verify Vectorizer
    if vectorizer in VECTORIZERS:
        modified_schema["classes"][0]["vectorizer"] = vectorizer

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
    elif vectorizer != None:
        msg.warn(f"Could not find matching vectorizer: {vectorizer}")

    return modified_schema


def add_suffix(schema: dict, vectorizer: str) -> tuple[dict, str]:
    """Adds the suffixof the vectorizer to the schema name
    @parameter schema : dict - Schema json
    @parameter vectorizer : str - Name of the vectorizer
    @returns dict - Modified schema if vectorizer is available
    """
    modified_schema = schema.copy()
    # Verify Vectorizer and add suffix
    modified_schema["classes"][0]["class"] = (
        modified_schema["classes"][0]["class"] + "_" + strip_non_letters(vectorizer)
    )
    return modified_schema, modified_schema["classes"][0]["class"]


def reset_schemas(
    client: Client = None,
    vectorizer: str = None,
):
    doc_name = "Document_" + strip_non_letters(vectorizer)
    chunk_name = "Chunk_" + strip_non_letters(vectorizer)
    cache_name = "Cache_" + strip_non_letters(vectorizer)

    client.schema.delete_class(doc_name)
    client.schema.delete_class(chunk_name)
    client.schema.delete_class(cache_name)


def init_schemas(
    client: Client = None,
    vectorizer: str = None,
    force: bool = False,
    check: bool = False,
) -> bool:
    """Initializes a weaviate client and initializes all required schemas
    @parameter client : Client - Weaviate Client
    @parameter vectorizer : str - Name of the vectorizer
    @parameter force : bool - Delete existing schema without user input
    @parameter check : bool - Only create if not exist
    @returns tuple[dict, dict] - Tuple of modified schemas
    """

    try:
        init_documents(client, vectorizer, force, check)
        init_cache(client, vectorizer, force, check)
        init_suggestion(client, vectorizer, force, check)
        return True
    except Exception as e:
        msg.fail(f"Schema initialization failed {str(e)}")
        return False


def init_documents(
    client: Client, vectorizer: str = None, force: bool = False, check: bool = False
) -> tuple[dict, dict]:
    """Initializes the Document and Chunk class
    @parameter client : Client - Weaviate client
    @parameter vectorizer : str - Name of the vectorizer
    @parameter force : bool - Delete existing schema without user input
    @parameter check : bool - Only create if not exist
    @returns tuple[dict, dict] - Tuple of modified schemas
    """

    SCHEMA_CHUNK = {
        "classes": [
            {
                "class": "Chunk",
                "description": "Chunks of Documentations",
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "Content of the document",
                    },
                    {
                        "name": "doc_name",
                        "dataType": ["text"],
                        "description": "Document name",
                    },
                    {
                        # Skip
                        "name": "doc_type",
                        "dataType": ["text"],
                        "description": "Document type",
                    },
                    {
                        # Skip
                        "name": "doc_uuid",
                        "dataType": ["text"],
                        "description": "Document UUID",
                    },
                    {
                        # Skip
                        "name": "chunk_id",
                        "dataType": ["number"],
                        "description": "Document chunk from the whole document",
                    },
                ],
            }
        ]
    }

    SCHEMA_DOCUMENT = {
        "classes": [
            {
                "class": "Document",
                "description": "Documentation",
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "Content of the document",
                    },
                    {
                        "name": "doc_name",
                        "dataType": ["text"],
                        "description": "Document name",
                    },
                    {
                        "name": "doc_type",
                        "dataType": ["text"],
                        "description": "Document type",
                    },
                    {
                        "name": "doc_link",
                        "dataType": ["text"],
                        "description": "Link to document",
                    },
                    {
                        "name": "timestamp",
                        "dataType": ["text"],
                        "description": "Timestamp of document",
                    },
                    {
                        "name": "chunk_count",
                        "dataType": ["number"],
                        "description": "Number of chunks",
                    },
                ],
            }
        ]
    }

    # Verify Vectorizer
    chunk_schema = verify_vectorizer(
        SCHEMA_CHUNK,
        vectorizer,
        ["doc_type", "doc_uuid", "chunk_id"],
    )

    # Add Suffix
    document_schema, document_name = add_suffix(SCHEMA_DOCUMENT, vectorizer)
    chunk_schema, chunk_name = add_suffix(chunk_schema, vectorizer)

    if client.schema.exists(document_name):
        if check:
            return document_schema, chunk_schema
        if not force:
            user_input = input(
                f"{document_name} class already exists, do you want to delete it? (y/n): "
            )
        else:
            user_input = "y"
        if user_input.strip().lower() == "y":
            client.schema.delete_class(document_name)
            client.schema.delete_class(chunk_name)
            client.schema.create(document_schema)
            client.schema.create(chunk_schema)
            msg.good(f"{document_name} and {chunk_name} schemas created")
        else:
            msg.warn(
                f"Skipped deleting {document_name} and {chunk_name} schema, nothing changed"
            )
    else:
        client.schema.create(document_schema)
        client.schema.create(chunk_schema)
        msg.good(f"{document_name} and {chunk_name} schemas created")

    # If Weaviate Embedded runs
    if client._connection.embedded_db:
        msg.info("Stopping Weaviate Embedded")
        client._connection.embedded_db.stop()

    return document_schema, chunk_schema


def init_cache(
    client: Client, vectorizer: str = None, force: bool = False, check: bool = False
) -> dict:
    """Initializes the Cache
    @parameter client : Client - Weaviate client
    @parameter vectorizer : str - Name of the vectorizer
    @parameter force : bool - Delete existing schema without user input
    @parameter check : bool - Only create if not exist
    @returns dict - Modified schema
    """

    SCHEMA_CACHE = {
        "classes": [
            {
                "class": "Cache",
                "description": "Cache of Documentations and their queries",
                "properties": [
                    {
                        "name": "query",
                        "dataType": ["text"],
                        "description": "Query",
                    },
                    {
                        # Skip
                        "name": "system",
                        "dataType": ["text"],
                        "description": "System message",
                    },
                ],
            }
        ]
    }

    # Verify Vectorizer
    cache_schema = verify_vectorizer(
        SCHEMA_CACHE,
        vectorizer,
        ["system", "results"],
    )

    # Add Suffix
    cache_schema, cache_name = add_suffix(cache_schema, vectorizer)

    if client.schema.exists(cache_name):
        if check:
            return cache_schema
        if not force:
            user_input = input(
                f"{cache_name} class already exists, do you want to delete it? (y/n): "
            )
        else:
            user_input = "y"
        if user_input.strip().lower() == "y":
            client.schema.delete_class(cache_name)
            client.schema.create(cache_schema)
            msg.good(f"{cache_name} schema created")
        else:
            msg.warn(f"Skipped deleting {cache_name} schema, nothing changed")
    else:
        client.schema.create(cache_schema)
        msg.good(f"{cache_name} schema created")

    # If Weaviate Embedded runs
    if client._connection.embedded_db:
        msg.info("Stopping Weaviate Embedded")
        client._connection.embedded_db.stop()

    return cache_schema


def init_suggestion(
    client: Client, vectorizer: str = None, force: bool = False, check: bool = False
) -> dict:
    """Initializes the Suggestion schema
    @parameter client : Client - Weaviate client
    @parameter vectorizer : str - Name of the vectorizer
    @parameter force : bool - Delete existing schema without user input
    @parameter check : bool - Only create if not exist
    @returns dict - Modified schema
    """

    SCHEMA_SUGGESTION = {
        "classes": [
            {
                "class": "Suggestion",
                "description": "List of possible prompts",
                "properties": [
                    {
                        "name": "suggestion",
                        "dataType": ["text"],
                        "description": "Query",
                    },
                ],
            }
        ]
    }

    suggestion_schema = SCHEMA_SUGGESTION
    suggestion_name = "Suggestion"

    if client.schema.exists(suggestion_name):
        if check:
            return suggestion_schema
        if not force:
            user_input = input(
                f"{suggestion_name} class already exists, do you want to delete it? (y/n): "
            )
        else:
            user_input = "y"
        if user_input.strip().lower() == "y":
            client.schema.delete_class(suggestion_name)
            client.schema.create(suggestion_schema)
            msg.good(f"{suggestion_name} schema created")
        else:
            msg.warn(f"Skipped deleting {suggestion_name} schema, nothing changed")
    else:
        client.schema.create(suggestion_schema)
        msg.good(f"{suggestion_name} schema created")

    # If Weaviate Embedded runs
    if client._connection.embedded_db:
        msg.info("Stopping Weaviate Embedded")
        client._connection.embedded_db.stop()

    return suggestion_schema
