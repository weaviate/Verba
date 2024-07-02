from goldenverba.components.embedding.SentenceTransformersEmbedder import (
    SentenceTransformersEmbedder,
)


class AllMPNetEmbedder(SentenceTransformersEmbedder):
    """
    AllMPNetEmbedder for Verba.
    """

    def __init__(self):
        super().__init__(vectorizer="all-mpnet-base-v2")
