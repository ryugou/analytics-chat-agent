import typer
from .commands.import_ga4_schema import import_schema as do_import_schema

cli = typer.Typer(help="Analytics Chat Agent CLI")

@cli.command()
def import_schema():
    """GA4スキーマCSVをQdrantにインポート"""
    do_import_schema()

if __name__ == "__main__":
    cli()