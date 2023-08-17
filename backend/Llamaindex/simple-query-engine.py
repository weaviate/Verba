import weaviate
from llama_index.vector_stores import WeaviateVectorStore
from llama_index import VectorStoreIndex, StorageContext
from llama_index.storage.storage_context import StorageContext
import os
from dotenv import load_dotenv

load_dotenv()

client = weaviate.Client(
    url=os.environ.get("WEAVIATE_URL"),
    auth_client_secret=weaviate.AuthApiKey(api_key=os.environ.get("WEAVIATE_API_KEY")),
)


# construct vector store
vector_store = WeaviateVectorStore(
    weaviate_client=client, index_name="BlogPost", text_key="content"
)

# setting up the storage for the embeddings
storage_context = StorageContext.from_defaults(vector_store=vector_store)

from upload import nodes

# set up the index
index = VectorStoreIndex(nodes, storage_context=storage_context)

# and now query 🚀
query_engine = index.as_query_engine()

query = input("Please enter your query: ")

response = query_engine.query(query)
