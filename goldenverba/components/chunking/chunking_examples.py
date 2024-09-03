from goldenverba.components.chunking.TokenChunker import TokenChunker
from goldenverba.components.document import Document
import asyncio


async def run_token_chunker():
    chunker = TokenChunker()

    document = Document(content="This is a test document.")

    config = chunker.config
    config["Tokens"].value = 1
    config["Overlap"].value = 0
    chunked_documents = await chunker.chunk(config, [document])

    for doc in chunked_documents:
        print(f"Document content: {doc.content}")
        print("Chunks:")
        for i, chunk in enumerate(doc.chunks, 1):
            print(f"  Chunk {i}: {chunk.content}")
        print()  # Add a blank line between documents¬


asyncio.run(run_token_chunker())
