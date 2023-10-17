class VerbaComponent:
    """
    Base Class for Verba Readers, Chunkers, Embedders, Retrievers, and Generators
    """

    def __init__(self):
        self.requires_env = []
        self.requires_library = []
