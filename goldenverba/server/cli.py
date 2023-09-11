import click
import uvicorn
import os


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


if __name__ == "__main__":
    cli()
