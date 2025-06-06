"""
GA4スキーマをインポートするCLIコマンド。
"""

import logging
import typer
from pathlib import Path
from ...config import get_settings
from ...core.importer.import_ga4_schema import SchemaImporter

logger = logging.getLogger(__name__)

def get_ga4_schema_csv_path() -> Path:
    """GA4スキーマCSVファイルのパスを取得"""
    settings = get_settings()
    return Path(settings["ga4_schema"]["csv_path"])

def import_ga4_schema() -> None:
    """
    GA4のスキーマをインポートする
    """
    try:
        # スキーマCSVファイルのパスを取得
        csv_path = get_ga4_schema_csv_path()
        
        if not csv_path.exists():
            raise FileNotFoundError(f"スキーマCSVファイルが見つかりません: {csv_path}")
        
        # スキーマのインポート
        importer = SchemaImporter()
        count = importer.import_schema(csv_path)
        
        typer.echo(f"{count}件のスキーマをインポートしました。")
        
    except Exception as e:
        logger.error(f"スキーマインポートエラー: {e}")
        typer.echo(f"エラー: {str(e)}")
        raise typer.Exit(1)
