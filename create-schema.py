import weaviate
import os
import openai
from wasabi import msg
from dotenv import load_dotenv

load_dotenv()

msg.divider("Starting schema creation")

client = weaviate.Client(
    url=os.environ.get("WEAVIATE_URL"),
    auth_client_secret=weaviate.AuthApiKey(api_key=os.environ.get("WEAVIATE_API_KEY")),
    additional_headers={"X-OpenAI-Api-Key": openai.api_key},
)

schema = {
    "classes": [
        {
            "class": "BlogPost",
            "description": "Blog post from the Weaviate website.",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {"generative-openai": {"model": "gpt-3.5-turbo"}},
            "properties": [
                {
                    "name": "Content",
                    "dataType": ["text"],
                    "description": "Content from the blog post",
                }
            ],
        }
    ]
}

if client.schema.exists("BlogPost"):
    user_input = input(
        "BlogPost class already exists, do you want to delete it? (y/n): "
    )
    if user_input.strip().lower() == "y":
        client.schema.delete_class("BlogPost")
        client.schema.create(schema)
        msg.good("'BlogPost' schema created")
    else:
        msg.warn("Skipped deleting BlogPost, nothing changed")
else:
    client.schema.create(schema)
    msg.good("'BlogPost' schema created")

msg.info("Done")
