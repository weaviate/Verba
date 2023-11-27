import json
import os

from wasabi import msg


class Config:
    def __init__(
        self, reader: str, chunker: str, embedder: str, retriever: str, generator: str
    ):
        self.reader = reader
        self.chunker = chunker
        self.embedder = embedder
        self.retriever = retriever
        self.generator = generator

    def initalized(self) -> bool:
        return (
            self.reader == ""
            or self.chunker == ""
            or self.embedder == ""
            or self.retriever == ""
            or self.generator == ""
        )


class ConfigManager:
    def __init__(
        self,
        filename="verba_config.json",
    ):
        self.filename = filename
        self.config: Config = None
        # Load the config if exists or create one if not
        if os.path.exists(self.filename):
            self.load_config()
        else:
            self.default_config()
            self.save_config()

    def default_config(self):
        """Create a default config."""
        msg.info("New Config initialized")
        self.config = Config(
            reader="",
            chunker="",
            embedder="",
            retriever="",
            generator="",
        )

    def load_config(self):
        """Load config from file."""
        msg.good("Config loaded")
        with open(self.filename) as file:
            json_obj = json.load(file)
            self.config = Config(
                reader=json_obj["reader"],
                chunker=json_obj["chunker"],
                embedder=json_obj["embedder"],
                retriever=json_obj["retriever"],
                generator=json_obj["generator"],
            )

    def save_config(self):
        """Save config to file."""
        msg.good("Saved Config")
        with open(self.filename, "w") as file:
            json_obj = {
                "reader": self.config.reader,
                "chunker": self.config.chunker,
                "embedder": self.config.embedder,
                "retriever": self.config.retriever,
                "generator": self.config.generator,
            }
            json.dump(json_obj, file, indent=4)

    def set_reader(self, reader: str):
        self.config.reader = reader

    def get_reader(self):
        return self.config.reader

    def set_chunker(self, chunker: str):
        self.config.chunker = chunker

    def get_chunker(self):
        return self.config.chunker

    def set_embedder(self, embedder: str):
        self.config.embedder = embedder

    def get_embedder(self):
        return self.config.embedder

    def set_retriever(self, retriever: str):
        self.config.retriever = retriever

    def get_retriever(self):
        return self.config.retriever

    def set_generator(self, generator: str):
        self.config.generator = generator

    def get_generator(self):
        return self.config.generator

    def initialized(self) -> bool:
        if self.config is not None:
            return self.config.initalized()
        else:
            return False

    def get_config(self):
        return self.config
