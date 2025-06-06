"""
分析コマンドの実装
"""

import logging
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ...core.analyzer.analysis_service import AnalysisService

# ロガーの設定
logger = logging.getLogger(__name__)

# Richコンソールの作成
console = Console()

def setup_logging(verbose: bool = False):
    """ロギングの設定"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def analyze(
    query: str = typer.Argument(None, help="分析したい内容を自然言語で入力"),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="詳細なログを出力"
    )
):
    """自然言語クエリを分析し、結果を表示"""
    if query is None:
        typer.echo("エラー: クエリ（QUERY）引数が必要です。\n'--help'で使い方を確認できます。", err=True)
        raise typer.Exit(1)

    setup_logging(verbose)
    
    try:
        service = AnalysisService()
        result = service.analyze(query)
        
        # 結果の表示
        console.print("\n[bold green]分析結果:[/bold green]")
        
        # 意図の表示
        intent_table = Table(title="意図")
        intent_table.add_column("キー")
        intent_table.add_column("説明")
        intent_table.add_column("パラメータ")
        intent_table.add_row(
            result["intent"]["key"],
            result["intent"]["description"],
            str(result["intent"]["parameters"])
        )
        console.print(intent_table)
        
        # フィールドマッピングの表示
        field_table = Table(title="フィールドマッピング")
        field_table.add_column("フィールド")
        field_table.add_column("説明")
        field_table.add_column("型")
        for field in result["field_mapping"]["fields"]:
            field_table.add_row(
                field["name"],
                field["description"],
                field["type"]
            )
        console.print(field_table)
        
        # SQLの表示
        console.print("\n[bold]生成されたSQL:[/bold]")
        console.print(result["sql"])
        
        # クエリ結果の表示
        if result["results"]:
            results_table = Table(title="クエリ結果")
            # カラムの追加
            for key in result["results"][0].keys():
                results_table.add_column(key)
            # データの追加
            for row in result["results"]:
                results_table.add_row(*[str(value) for value in row.values()])
            console.print(results_table)
        else:
            console.print("[yellow]結果がありません[/yellow]")
            
    except Exception as e:
        console.print(f"[bold red]エラーが発生しました:[/bold red] {str(e)}")
        raise typer.Exit(1) 