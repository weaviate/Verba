import click
import uvicorn


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


if __name__ == "__main__":
    cli()
