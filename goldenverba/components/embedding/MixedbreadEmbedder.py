from goldenverba.components.embedding.SentenceTransformersEmbedder import (
    SentenceTransformersEmbedder,
)


class MixedbreadEmbedder(SentenceTransformersEmbedder):
    """
    MixedbreadEmbedder for Verba.
    """

    def __init__(self):
        super().__init__(vectorizer="mixedbread-ai/mxbai-embed-large-v1")
