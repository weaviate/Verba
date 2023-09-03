import hashlib
import ssl
import os

import openai
import weaviate  # type: ignore[import]
from weaviate import Client
from typing import Optional
from spacy.tokens import Doc

from weaviate.embedded import EmbeddedOptions

from wasabi import msg  # type: ignore[import]


def setup_client() -> Optional[Client]:
    """
    @returns Optional[Client] - The Weaviate Client
    """

    msg.info("Setting up client")

    openai_key = os.environ.get("OPENAI_API_KEY", "")
    weaviate_url = os.environ.get("VERBA_URL", "")
    weaviate_key = os.environ.get("VERBA_API_KEY", "")

    if openai_key == "":
        msg.fail("OPENAI_API_KEY environment variable not set")
        return None

    # Weaviate Embedded
    elif weaviate_url == "":
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        msg.info("VERBA_URL environment variable not set. Using Weaviate Embedded")
        client = weaviate.Client(
            additional_headers={"X-OpenAI-Api-Key": openai.api_key},
            embedded_options=EmbeddedOptions(
                persistence_data_path="./.verba/local/share/",
                binary_path="./.verba/cache/weaviate-embedded",
            ),
        )
        msg.good("Client connected to local Weaviate server")
        return client

    elif weaviate_key == "":
        msg.warn("VERBA_API_KEY environment variable not set")

    openai.api_key = openai_key
    url = weaviate_url
    auth_config = weaviate.AuthApiKey(api_key=weaviate_key)

    client = weaviate.Client(
        url=url,
        additional_headers={"X-OpenAI-Api-Key": openai.api_key},
        auth_client_secret=auth_config,
    )

    msg.good("Client connected to Weaviate Cluster")

    return client


def hash_string(text: str) -> str:
    """Hash a string
    @parameter text : str - The string to hash
    @returns str - Hashed string
    """
    # Create a new sha256 hash object
    sha256 = hashlib.sha256()

    # Update the hash object with the bytes-like object (filepath)
    sha256.update(text.encode())

    # Return the hexadecimal representation of the hash
    return str(sha256.hexdigest())


def import_documents(client: Client, documents: list[Doc]) -> dict:
    """Imports a list of document to the Weaviate Client and returns a list of UUID for the chunks to match
    @parameter client : Client - Weaviate Client
    @parameter documents : list[Document] - List of whole documents
    @returns dict - The UUID list
    """
    doc_uuid_map = {}

    with client.batch as batch:
        batch.batch_size = 100
        for i, d in enumerate(documents):
            msg.info(
                f"({i+1}/{len(documents)}) Importing document {d.user_data['doc_name']}"
            )

            properties = {
                "text": str(d.text),
                "doc_name": str(d.user_data["doc_name"]),
                "doc_type": str(d.user_data["doc_type"]),
                "doc_link": str(d.user_data["doc_link"]),
            }

            uuid = client.batch.add_data_object(properties, "Document")
            uuid_key = str(d.user_data["doc_hash"]).strip().lower()
            doc_uuid_map[uuid_key] = uuid

    msg.good("Imported all docs")
    return doc_uuid_map


def import_chunks(client: Client, chunks: list[Doc], doc_uuid_map: dict) -> None:
    """Imports a list of chunks to the Weaviate Client and uses a list of UUID for the chunks to match
    @parameter client : Client - Weaviate Client
    @parameter chunks : list[Document] - List of chunks of documents
    @parameter doc_uuid_map : dict  UUID list of documents the chunks belong to
    @returns None
    """
    with client.batch as batch:
        batch.batch_size = 100
        for i, d in enumerate(chunks):
            msg.info(
                f"({i+1}/{len(chunks)}) Importing chunk of {d.user_data['doc_name']} ({d.user_data['_split_id']})"
            )

            uuid_key = str(d.user_data["doc_hash"]).strip().lower()
            uuid = doc_uuid_map[uuid_key]

            properties = {
                "text": str(d.text),
                "doc_name": str(d.user_data["doc_name"]),
                "doc_uuid": uuid,
                "doc_type": str(d.user_data["doc_type"]),
                "chunk_id": int(d.user_data["_split_id"]),
            }

            client.batch.add_data_object(properties, "Chunk")

    msg.good("Imported all chunks")


def import_suggestions(client: Client, suggestions: list[str]) -> None:
    """Imports a list of strings as suggestions to the Weaviate Client
    @parameter client : Client - Weaviate Client
    @parameter suggestions : list[str] - List of strings
    @returns None
    """
    with client.batch as batch:
        batch.batch_size = 100
        for i, d in enumerate(suggestions):
            msg.info(f"({i+1}/{len(suggestions)}) Importing suggestion")
            properties = {
                "suggestion": d,
            }

            client.batch.add_data_object(properties, "Suggestion")

    msg.good("Imported all suggestions")


def import_weaviate_suggestions(client: Client) -> None:
    suggestion_list = [
        "What is a vector database?",
        "What is a database?",
        "What is a vector?",
        "What is Weaviate?",
        "What is Semantic Search?",
        "What is Multi Tenancy?",
        "What is a Generative Feedback Loop?",
        "What is Healthsearch?",
        "What is Hybrid Search?",
        "What are you using vector databases for?",
        "How to setup the Weaviate client in Python?",
        "How to setup the Weaviate client in Typescript?",
        "How to use nearText?",
        "How to use nearText in Python?",
        "How to use nearText in Typescript?",
        "How to use nearVector in Python?",
        "How to use nearVector in Typescript?",
        "How to use GraphQL to retrieve objects?",
        "How to can I retrieve objects from Weaviate in Python?",
        "How to can I retrieve objects from Weaviate in Typescript?",
        "Why would I use Weaviate as my vector database?",
        "What is the difference between Weaviate and for example Elasticsearch?",
        "Do you offer Weaviate as a managed service?",
        "How to deploy Weaviate?",
        "How should I configure the size of my instance?",
        "Do I need to know about Docker (Compose) to use Weaviate?",
        "What happens when the Weaviate Docker container restarts? Is my data in the Weaviate database lost?",
        "Are there any 'best practices' or guidelines to consider when designing a schema?",
        "Should I use references in my schema?",
        "Is it possible to create one-to-many relationships in the schema?",
        "What is the difference between text and string and valueText and valueString?"
        "Do Weaviate classes have namespaces?",
        "Are there restrictions on UUID formatting? Do I have to adhere to any standards?",
        "If I do not specify a UUID during adding data objects, will Weaviate create one automatically?",
        "Can I use Weaviate to create a traditional knowledge graph?",
        "Why does Weaviate have a schema and not an ontology?",
        "What is the difference between a Weaviate data schema, ontologies and taxonomies?",
        "How to deal with custom terminology?",
        "How can you index data near-realtime without losing semantic meaning?",
        "Why isn't there a text2vec-contextionary in my language?",
        "How do you deal with words that have multiple meanings?",
        "Is there support to multiple versions of the query/document embedding models to co-exist at a given time? (helps with live experiments of new model versions)",
        "How can I retrieve the total object count in a class?",
        "How do I get the cosine similarity from Weaviate's certainty?",
        "The quality of my search results change depending on the specified limit. Why? How can I fix this?"
        "Why GraphQL instead of SPARQL?",
        "What is the best way to iterate through objects? Can I do paginated API calls?",
        "What is best practice for updating data?",
        "Can I connect my own module?",
        "Can I train my own text2vec-contextionary vectorizer module?",
        "Does Weaviate use Hnswlib?",
        "Are all ANN algorithms potential candidates to become an indexation plugin in Weaviate?",
        "Does Weaviate use pre- or post-filtering ANN index search?",
        "How does Weaviate's vector and scalar filtering work?",
        "What is the maximum number of vector dimensions for embeddings?",
        "What would you say is more important for query speed in Weaviate: More CPU power, or more RAM?",
        "Data import takes long / is slow (slower than before v1.0.0), what is causing this and what can I do?",
        "How can slow queries be optimized?",
        "When scalar and vector search are combined, will the scalar filter happen before or after the nearest neighbor (vector) search?",
        "Regarding 'filtered vector search': Since this is a two-phase pipeline, how big can that list of IDs get? Do you know how that size might affect query performance?",
        "My Weaviate setup is using more memory than what I think is reasonable. How can I debug this?",
        "How can I print a stack trace of Weaviate?",
        "Can I request a feature in Weaviate?",
        "What is Weaviate's consistency model in a distributed setup?",
        "With your aggregations I could not see how to do time buckets, is this possible?",
        "How can I run the latest master branch with Docker Compose?",
        "Give me an code example of nearText",
        "Give me an code example of nearVector",
        "Give me an code example of using filters",
        "Give me an code example of setting up the weaviate client",
        "Give me an code example of adding objects to weaviate",
        "Give me an code example of removing objects from weaviate",
        "Give me an code example of updating objects in weaviate",
        "Give me an code example of searching objects in weaviate",
        "How to retrieve all objects from weaviate?",
    ]
    import_suggestions(client, suggestion_list)
