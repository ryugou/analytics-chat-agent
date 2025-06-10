import logging
import click
from pathlib import Path
from ...config import get_settings
from ...core.importer.import_ga4_schema import SchemaImporter

logger = logging.getLogger(__name__)

def get_ga4_schema_csv_path() -> Path:
    settings = get_settings()
    return Path(settings["ga4_schema"]["csv_path"])

def get_ga4_virtual_csv_path() -> Path:
    settings = get_settings()
    return Path(settings["ga4_schema"]["virtual_csv_path"])

@click.command()
def import_ga4_schema():
    """
    GA4のスキーマと仮想キーをQdrantにインポートする
    """
    try:
        importer = SchemaImporter()

        # メインスキーマ
        csv_path = get_ga4_schema_csv_path()
        if not csv_path.exists():
            raise FileNotFoundError(f"スキーマCSVファイルが見つかりません: {csv_path}")
        count = importer.import_schema(csv_path, source="schema")
        click.echo(f"{count}件のGA4スキーマをインポートしました。")

        # 仮想キー（オプション扱い）
        virtual_csv_path = get_ga4_virtual_csv_path()
        if virtual_csv_path.exists():
            count_virtual = importer.import_schema(virtual_csv_path, source="virtual")
            click.echo(f"{count_virtual}件の仮想キーをインポートしました。")
        else:
            click.echo(f"仮想キーCSVファイルが見つかりません（スキップ）: {virtual_csv_path}")

    except Exception as e:
        logger.error(f"スキーマインポートエラー: {e}")
        click.echo(f"エラー: {str(e)}")
        raise click.Abort()
