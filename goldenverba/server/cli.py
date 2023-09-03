import click
import uvicorn
import os

from goldenverba.ingestion.cli import init as init_ingest
from goldenverba.ingestion.cli import clear_cache_command as clear_cache
from goldenverba.ingestion.cli import clear_all_command as clear_all
from goldenverba.ingestion.cli import import_data_command as import_data
from goldenverba.ingestion.cli import import_weaviate_command as import_weaviate


@click.group()
def cli():
    """Main command group for verba."""
    pass


@cli.command()
@click.option(
    "--model",
    default="gpt-3.5-turbo",
    help="Generative OpenAI model",
)
def start(model):
    """
    Run the FastAPI application.
    """
    os.environ["VERBA_MODEL"] = model
    uvicorn.run("goldenverba.server.api:app", host="0.0.0.0", port=8000, reload=True)


cli.add_command(init_ingest, name="init")
cli.add_command(import_data, name="import")
cli.add_command(import_weaviate, name="weaviate")
cli.add_command(clear_cache, name="clear_cache")
cli.add_command(clear_all, name="clear")

if __name__ == "__main__":
    cli()
