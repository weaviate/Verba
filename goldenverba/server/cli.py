import click
import uvicorn
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
@click.option(
    "--host",
    default="0.0.0.0",
    help="FastAPI Host",
)
def start(port, host):
    """
    Run the FastAPI application.
    """
    uvicorn.run("goldenverba.server.api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    cli()
