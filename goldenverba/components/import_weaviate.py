import os

from wasabi import msg  # type: ignore[import]
import spacy

from goldenverba.components.util import (
    setup_client,
    import_documents,
    import_chunks,
    import_weaviate_suggestions,
)
from goldenverba.components.preprocess_weaviate import (
    retrieve_documentation,
    retrieve_blogs,
)

from dotenv import load_dotenv

load_dotenv()


def import_weaviate() -> None:
    msg.divider("Starting data import")

    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    # Setup Client
    client = setup_client()

    if not client:
        return

    # Download and preprocess data
    weaviate_blog, chunked_weaviate_blog = retrieve_blogs(nlp)
    weaviate_documentation, chunked_weaviate_documentation = retrieve_documentation(nlp)

    weaviate_data = weaviate_documentation + weaviate_blog
    chunked_weaviate_data = chunked_weaviate_blog + chunked_weaviate_documentation

    # Import data
    doc_uuid_map = import_documents(client, weaviate_data)
    import_chunks(client, chunked_weaviate_data, doc_uuid_map)
    import_weaviate_suggestions(client)
