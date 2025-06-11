"""
BigQuery接続管理
"""

from typing import Any, Dict, Optional
from google.cloud import bigquery
from google.oauth2 import service_account

from .base import DatabaseConnection

class BigQueryConnection(DatabaseConnection):
    """BigQuery接続管理クラス"""

    def _connect(self) -> bigquery.Client:
        """
        BigQueryに接続

        Returns:
            bigquery.Client: BigQueryクライアント
        """
        credentials = service_account.Credentials.from_service_account_file(
            self.settings["credentials_path"]
        )
        return bigquery.Client(
            project=self.settings["project_id"],
            credentials=credentials
        )

    def close(self) -> None:
        """BigQuery接続を閉じる"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute_query(self, query: str) -> Any:
        """
        SQLクエリを実行

        Args:
            query: 実行するSQLクエリ

        Returns:
            Any: クエリ結果
        """
        return self.connection.query(query).result() 