"""
Analytics Chat Agentのコマンドラインインターフェース
"""

import logging
import sys
from pathlib import Path
import os

import click
from dotenv import load_dotenv

from .commands import analyze, version, import_ga4_schema

# .envファイルの読み込み
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# ロガーの設定
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """GA4の分析クエリを自然言語から生成・実行するCLIツール"""
    pass

# コマンドの登録
cli.add_command(analyze)
cli.add_command(version)
cli.add_command(import_ga4_schema)

if __name__ == "__main__":
    cli()