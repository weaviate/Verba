import click
import uvicorn
import gunicorn
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
@click.option(
    "--workers",
    default=4,
    help="Workers to run Verba",
)
def start(port, host, prod, workers):
    """
    Run the FastAPI application.
    """
    uvicorn.run("goldenverba.server.api:app", host=host, port=port, reload=(not prod), workers=workers)
    

if __name__ == "__main__":
    cli()
