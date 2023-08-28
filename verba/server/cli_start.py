import click
import uvicorn
from verba.ingestion.cli import init as init_ingest
from verba.ingestion.cli import import_data_command as import_data
from verba.ingestion.cli import import_weaviate_command as import_weaviate


@click.group()
def cli():
    """Main command group for verba."""
    pass


@cli.command()
def start():
    """
    Run the FastAPI application.
    """
    uvicorn.run("verba.server.api:app", host="0.0.0.0", port=8000, reload=True)


cli.add_command(init_ingest, name="init")
cli.add_command(import_data, name="import")
cli.add_command(import_weaviate, name="weaviate")

if __name__ == "__main__":
    cli()
