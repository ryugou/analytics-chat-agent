from typing import List
import os
import json
import logging
from pathlib import Path
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

from ..types import QueryResult

logger = logging.getLogger(__name__)

def get_settings():
    """設定ファイルを読み込む"""
    settings_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(settings_path) as f:
        return json.load(f)

def run_bigquery_query(query: str) -> List[QueryResult]:
    """
    指定されたSQLクエリをBigQueryに投げ、結果を返す

    Args:
        query: 実行するSQL文字列（フルパスでテーブルが指定されている前提）

    Returns:
        クエリ結果のリスト（QueryResultオブジェクトのリスト）

    Raises:
        RuntimeError: 実行に失敗した場合
    """
    settings = get_settings()
    project_id = settings["bigquery"]["project_id"]
    credentials_path = settings["bigquery"]["credentials_path"]

    if not project_id:
        raise RuntimeError("BigQueryのプロジェクトIDが設定されていません。")

    if not credentials_path or not os.path.exists(credentials_path):
        raise RuntimeError("BigQueryのクレデンシャルが未設定または存在しません。")

    try:
        # SQL文の先頭が SELECT であるかチェック
        cleaned_query = query.lstrip().splitlines()[0]
        if not cleaned_query.upper().startswith("SELECT"):
            logger.error(f"SQLヘッダの内容: {repr(cleaned_query)}")
            raise RuntimeError("クエリはSELECT文で始まる必要があります。")

        client = bigquery.Client(project=project_id)
        query_job = client.query(query)
        results = query_job.result()

        # 結果をQueryResultオブジェクトに変換
        query_results = []
        for row in results:
            row_dict = dict(row.items())
            query_result = QueryResult(values=row_dict)
            query_results.append(query_result)

        return query_results

    except GoogleAPIError as e:
        logger.error(f"BigQuery実行エラー: {e}")
        raise RuntimeError("BigQueryクエリの実行に失敗しました。") from e
