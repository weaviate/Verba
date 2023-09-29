03. EMBEDDER

The task of the Embedder is to embed verba documents into Weaviate and also to retrieve them. It handles teh currentlu selected vectorizer or embedding mode ()e.g sentence transformer, openai)

You can create different Embedders that embed and retrieve the data to Weaviate with different techniques, api and more. The EmbeddingManager handles all embedders.

How to create a new Embedder
1. Create a new python file within the embedding folder
2. Create a class that inherits the Embedder class
3. Implement it's methods (e.g. embed(), retrieve())
4. Add your new EmbedderClass to the EmbeddingManager
5. Add unit tests and usage examples in the embedder/tests folder with example data