"""
PostgreSQL接続管理
"""

import os
import logging
from typing import Any, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

from .base import DatabaseConnection

logger = logging.getLogger(__name__)

class PostgresConnection(DatabaseConnection):
    """PostgreSQL接続管理クラス"""

    def _connect(self) -> psycopg2.extensions.connection:
        """
        PostgreSQLに接続

        Returns:
            psycopg2.extensions.connection: PostgreSQL接続
        """
        return psycopg2.connect(
            host=self.settings["host"],
            port=self.settings["port"],
            dbname=self.settings["database"],
            user=self.settings["user"],
            password=os.getenv("POSTGRES_PASSWORD"),
            cursor_factory=RealDictCursor
        )

    def close(self) -> None:
        """PostgreSQL接続を閉じる"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        SQLクエリを実行

        Args:
            query: 実行するSQLクエリ
            params: クエリパラメータ

        Returns:
            Any: クエリ結果

        Raises:
            psycopg2.Error: PostgreSQLエラーが発生した場合
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:  # SELECT文の場合
                    return cursor.fetchall()
                self.connection.commit()
                return None
        except psycopg2.Error as e:
            # エラー情報をログに出力
            logger.error("PostgreSQLエラーが発生しました:")
            logger.error(f"エラー: {str(e)}")
            logger.error(f"エラーコード: {e.pgcode}")
            logger.error(f"エラーメッセージ: {e.pgerror}")
            logger.error(f"クエリ: {query}")
            if params:
                logger.error(f"パラメータ: {params}")
            # エラーをそのまま伝播
            raise

    def execute_many(self, query: str, params_list: list[Dict[str, Any]]) -> None:
        """
        複数のSQLクエリを実行

        Args:
            query: 実行するSQLクエリ
            params_list: クエリパラメータのリスト

        Raises:
            psycopg2.Error: PostgreSQLエラーが発生した場合
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(query, params_list)
                self.connection.commit()
        except psycopg2.Error as e:
            # エラー情報をログに出力
            logger.error("PostgreSQLエラーが発生しました:")
            logger.error(f"エラー: {str(e)}")
            logger.error(f"エラーコード: {e.pgcode}")
            logger.error(f"エラーメッセージ: {e.pgerror}")
            logger.error(f"クエリ: {query}")
            if params_list:
                logger.error(f"パラメータ: {params_list[0]}")  # 最初のパラメータのみ出力
            # エラーをそのまま伝播
            raise 