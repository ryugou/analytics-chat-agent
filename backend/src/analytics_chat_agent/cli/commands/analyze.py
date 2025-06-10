"""
分析コマンドの実装
"""

import logging
from typing import Dict, Any

import click
from rich.console import Console
from rich.table import Table

from ...core.analyzer.analysis_service import AnalysisService
from ...types import FieldMappingResult, QueryResult

# ロガーの設定
logger = logging.getLogger(__name__)

# Richコンソールの作成
console = Console()

@click.command()
@click.argument("query", type=str)
def analyze(query: str):
    """
    自然言語クエリを分析し、結果を表示する

    Args:
        query: 分析したい内容を自然言語で記述
    """
    try:
        # 分析サービスの初期化
        service = AnalysisService()

        # 分析の実行
        result = service.analyze(query)

        # 結果の表示
        console.print("\n[bold green]分析結果[/bold green]")
        console.print(f"クエリ: {result['query']}")

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
        field_mapping = result["fields"]
        field_table = Table(title="フィールドマッピング")
        field_table.add_column("フィールド")
        field_table.add_column("説明")
        field_table.add_column("型")
        for field in field_mapping["fields"]:
            field_table.add_row(
                field["name"],
                field_mapping["description"],
                field["type"]
            )
        console.print(field_table)

        # SQLの表示
        console.print("\n[bold]生成されたSQL[/bold]")
        console.print(result["sql"])

        # クエリ結果の表示
        if result["results"]:
            result_table = Table(title="クエリ結果")
            
            # 最初の行からカラム名を取得
            if result["results"]:
                columns = list(result["results"][0].keys())
                # カラムの追加
                for column in columns:
                    result_table.add_column(column)
                
                # データの追加
                for row in result["results"]:
                    result_table.add_row(
                        *[str(row.get(column, "")) for column in columns]
                    )
                console.print(result_table)
        else:
            console.print("[yellow]クエリ結果は空です[/yellow]")

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
        console.print(f"[red]エラーが発生しました: {str(e)}[/red]")
        raise click.Abort() 