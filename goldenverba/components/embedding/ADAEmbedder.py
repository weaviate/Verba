from goldenverba.components.embedding.OpenAIEmbedder import OpenAIEmbedder

class ADAEmbedder(OpenAIEmbedder):
    """
    ADAEmbedder for Verba.
    """

    def __init__(self):
        super().__init__()
        self.name = "ADAEmbedder"
        self.description = "Embeds and retrieves objects using OpenAI's ADA model"
        self.model = "text-embedding-ada-002"
