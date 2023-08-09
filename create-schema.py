import weaviate
import os
from dotenv import load_dotenv

load_dotenv() 

client = weaviate.Client(
    url=os.environ.get("WEAVIATE_URL"),
    auth_client_secret=weaviate.AuthApiKey(api_key=os.environ.get("WEAVIATE_API_KEY"))
)

schema = {
   "classes": [
       {
           "class": "BlogPost",
           "description": "Blog post from the Weaviate website.",
           "vectorizer": "text2vec-openai",
           "moduleConfig": {
               "generative-openai": { 
                    "model": "gpt-3.5-turbo"
                }
           },
           "properties": [
               {
                  "name": "Content",
                  "dataType": ["text"],
                  "description": "Content from the blog post",
               }
            ]
        }
    ]
}

client.schema.delete_all()

client.schema.create(schema)

print("Schema was created.")