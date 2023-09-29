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
