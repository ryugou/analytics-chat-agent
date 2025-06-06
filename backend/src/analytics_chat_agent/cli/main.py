"""
Analytics Chat Agentのコマンドラインインターフェース
"""

import logging
import sys
from pathlib import Path
import os

import typer
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

# Typerアプリケーションの作成
app = typer.Typer(
    name="analytics-cli",
    help="GA4の分析クエリを自然言語から生成・実行するCLIツール",
    add_completion=False,
)

# コマンドの登録
app.command()(analyze)
app.command()(version)
app.command()(import_ga4_schema)

@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo("使い方: python -m analytics_chat_agent.cli.main [コマンド] [オプション] [引数]")
        typer.echo("例: python -m analytics_chat_agent.cli.main analyze '売上の推移を教えて'")
        raise typer.Exit()

if __name__ == "__main__":
    app()