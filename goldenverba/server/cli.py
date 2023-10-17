import click
import uvicorn
import os

from goldenverba.verba_manager import VerbaManager

from wasabi import msg
from dotenv import load_dotenv

load_dotenv()


@click.group()
def cli():
    """Main command group for verba."""
    pass


@cli.command()
@click.option(
    "--port",
    default=8000,
    help="FastAPI Port",
)
def start(port):
    """
    Run the FastAPI application.
    """
    uvicorn.run("goldenverba.server.api:app", host="0.0.0.0", port=port, reload=True)


@cli.command()
@click.option(
    "--reader",
    default="SimpleReader",
    help="Reader",
)
@click.option(
    "--type",
    default="Documentation",
    help="Document Type",
)
@click.option(
    "--chunker",
    default="WordChunker",
    help="Chunker",
)
@click.option(
    "--units",
    default=100,
    help="Units per chunk",
)
@click.option(
    "--overlap",
    default=50,
    help="Overlap of units per chunk",
)
@click.option(
    "--embedder",
    default="ADAEmbedder",
    help="Embedder",
)
@click.option(
    "--path",
    help="Path to data",
)
def load(reader, type, chunker, units, overlap, embedder, path):
    """
    Run the FastAPI application.
    """
    manager = VerbaManager()
    manager.reader_set_reader(reader)
    manager.chunker_set_chunker(chunker)
    manager.embedder_set_embedder(embedder)

    manager.import_data(
        bytes=[],
        contents=[],
        paths=[path],
        fileNames=[path],
        document_type=type,
        units=units,
        overlap=overlap,
    )


@cli.command()
def reset():
    """
    Delete all schemas
    """
    manager = VerbaManager()
    manager.reset()
    msg.warn("Verba Resetted")


if __name__ == "__main__":
    cli()
