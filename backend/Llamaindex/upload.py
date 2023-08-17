from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
import weaviate
import os
from dotenv import load_dotenv

load_dotenv()

client = weaviate.Client(
    url=os.environ.get("WEAVIATE_URL"),
    auth_client_secret=weaviate.AuthApiKey(api_key=os.environ.get("WEAVIATE_API_KEY")),
)

# load the blogs in using the reader
blogs = SimpleDirectoryReader("./data/test").load_data()

# chunk up the blog posts into nodes
parser = SimpleNodeParser()
nodes = parser.get_nodes_from_documents(blogs)

print(len(nodes))
print(type(nodes[0]))
