import os
from wasabi import msg  # type: ignore[import]

from util import setup_client

from dotenv import load_dotenv

load_dotenv()

msg.divider("Starting cache schema creation")


client = setup_client(
    openai_key=os.environ.get("OPENAI_API_KEY", ""),
    weaviate_url=os.environ.get("WEAVIATE_URL", ""),
    weaviate_key=os.environ.get("WEAVIATE_API_KEY", ""),
)

cache_schema = {
    "classes": [
        {
            "class": "Cache",
            "description": "Cache of Documentations and their queries",
            "vectorizer": "text2vec-openai",
            "properties": [
                {
                    "name": "query",
                    "dataType": ["text"],
                    "description": "Query",
                },
                {
                    "name": "system",
                    "dataType": ["text"],
                    "description": "System message",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": True,
                            "vectorizePropertyName": False,
                        }
                    },
                },
                {
                    "name": "results",
                    "dataType": ["text"],
                    "description": "List of results",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": True,
                            "vectorizePropertyName": False,
                        }
                    },
                },
            ],
        }
    ]
}

if client.schema.exists("Cache"):
    user_input = input(
        "Cache class already exists, do you want to overwrite it? (y/n): "
    )
    if user_input.strip().lower() == "y":
        client.schema.delete_class("Cache")
        client.schema.create(cache_schema)
        msg.good("'Cache' schema created")
    else:
        msg.warn("Skipped deleting Cacheschema, nothing changed")
else:
    client.schema.create(cache_schema)
    msg.good("'Cache' schema created")

msg.info("Done")
