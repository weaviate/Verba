import os
from wasabi import msg  # type: ignore[import]

from util import setup_client

from dotenv import load_dotenv

load_dotenv()

msg.divider("Starting Suggestion schema creation")


client = setup_client(
    openai_key=os.environ.get("OPENAI_API_KEY", ""),
    weaviate_url=os.environ.get("WEAVIATE_URL", ""),
    weaviate_key=os.environ.get("WEAVIATE_API_KEY", ""),
)

suggestion_schema = {
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

if client.schema.exists("Suggestion"):
    user_input = input(
        "Suggestion class already exists, do you want to overwrite it? (y/n): "
    )
    if user_input.strip().lower() == "y":
        client.schema.delete_class("Suggestion")
        client.schema.create(suggestion_schema)
        msg.good("'Suggestion' schema created")
    else:
        msg.warn("Skipped deleting Suggestion schema, nothing changed")
else:
    client.schema.create(suggestion_schema)
    msg.good("'Suggestion' schema created")


suggestion_list = [
    "What is a vector database?",
    "What is Weaviate?",
    "What is Semantic Search?",
    "What is Multi Tenancy?",
    "What is a Generative Feedback Loop?",
    "What is Healthsearch?",
    "What is Hybrid Search?",
    "What are you using vector databases for?",
    "How to setup the Weaviate client in Python?",
    "How to setup the Weaviate client in Typescript?",
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
]

with client.batch as batch:
    batch.batch_size = 100
    for i, d in enumerate(suggestion_list):
        msg.info(f"({i+1}/{len(suggestion_list)}) Importing suggestion)")
        properties = {
            "suggestion": d,
        }

        client.batch.add_data_object(properties, "Suggestion")

msg.info("Done")
