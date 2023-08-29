import os
from wasabi import msg  # type: ignore[import]

from verba_rag.ingestion.util import setup_client

from dotenv import load_dotenv

load_dotenv()


def init_suggestion():
    msg.divider("Creating Suggestion class")

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

    msg.info("Done")
