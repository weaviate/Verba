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
    default="localhost",
    help="FastAPI Host",
)
@click.option(
    "--prod/--no-prod",
    default=False,
    help="Run in production mode.",
)
def start(port, host, prod):
    """
    Run the FastAPI application.
    """
    uvicorn.run("goldenverba.server.api:app", host=host, port=port, reload=(not prod))

if __name__ == "__main__":
    cli()
