"""CLIのメインモジュール。"""

import typer

from .commands.import_ga4_schema import import_schema

cli = typer.Typer(help="Analytics Chat Agent CLI")

# メインコマンドとして登録
cli.command()(import_schema)


if __name__ == "__main__":
    cli()