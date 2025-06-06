from typing import List, TypedDict, Any
import os
import json
import logging
from pathlib import Path
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)

def get_settings():
    """設定ファイルを読み込む"""
    settings_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(settings_path) as f:
        return json.load(f)

class QueryResult(TypedDict, total=False):
    """
    BigQueryクエリ結果の型定義
    注: 実際のスキーマに応じて、より具体的な型定義に更新してください
    """
    # 例: 一般的なGA4のフィールド
    event_date: str
    event_name: str
    user_pseudo_id: str
    # その他のフィールドは動的に追加される可能性があるため、Any型を使用
    __annotations__: dict[str, Any]

def run_bigquery_query(query: str) -> List[QueryResult]:
    """
    指定されたSQLクエリをBigQueryに投げ、結果を返す

    Args:
        query: 実行するSQL文字列（データセットIDは自動的に追加されます）

    Returns:
        クエリ結果のリスト（辞書形式）

    Raises:
        RuntimeError: 実行に失敗した場合
    """
    settings = get_settings()
    project_id = settings["bigquery"]["project_id"]
    dataset_id = settings["bigquery"]["dataset_id"]
    credentials_path = settings["bigquery"]["credentials_path"]

    if not project_id:
        raise RuntimeError("BigQueryのプロジェクトIDが設定されていません。")

    if not dataset_id:
        raise RuntimeError("BigQueryのデータセットIDが設定されていません。")

    if not credentials_path or not os.path.exists(credentials_path):
        raise RuntimeError("BigQueryのクレデンシャルが未設定または存在しません。")

    try:
        # クエリにデータセットIDを追加
        if not query.strip().lower().startswith("select"):
            raise RuntimeError("クエリはSELECT文で始まる必要があります。")
        
        # クエリにデータセットIDが含まれていない場合のみ追加
        if f"{project_id}.{dataset_id}" not in query:
            query = query.replace("FROM ", f"FROM {project_id}.{dataset_id}.")
            query = query.replace("from ", f"FROM {project_id}.{dataset_id}.")

        client = bigquery.Client(project=project_id)
        query_job = client.query(query)
        results = query_job.result()

        # 結果をTypedDictに変換
        return [dict(row.items()) for row in results]

    except GoogleAPIError as e:
        logger.error(f"BigQuery実行エラー: {e}")
        raise RuntimeError("BigQueryクエリの実行に失敗しました。") from e 