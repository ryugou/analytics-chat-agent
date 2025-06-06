"""GA4スキーマをインポートするCLIコマンド。"""

import typer

from analytics_chat_agent.config.settings import get_ga4_schema_csv_path
from analytics_chat_agent.core.schema.importer import SchemaImporter


def import_schema() -> None:
    """GA4スキーマのCSVファイルをQdrantにインポートする。

    設定ファイルで指定されたCSVファイルからスキーマをインポートします。
    """
    try:
        csv_path = get_ga4_schema_csv_path()
        importer = SchemaImporter()
        count = importer.import_from_csv(csv_path)
        typer.echo(f"Imported {count} schemas to Qdrant.")
    except FileNotFoundError as e:
        typer.echo(str(e))
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"エラー: {e}")
        raise typer.Exit(1)
