from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
import weaviate

# connect to your weaviate instance
client = weaviate.Client("https://verba-demo-q86cpjhs.weaviate.network")

# load the blogs in using the reader
blogs = SimpleDirectoryReader('./data').load_data()

# chunk up the blog posts into nodes 
parser = SimpleNodeParser()
nodes = parser.get_nodes_from_documents(blogs)