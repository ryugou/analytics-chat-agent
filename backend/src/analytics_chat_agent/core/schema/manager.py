"""
スキーマ管理クラス
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from ..database import PostgresConnection

logger = logging.getLogger(__name__)

class SchemaManager:
    """スキーマ管理クラス"""

    def __init__(self, pg_conn: PostgresConnection):
        """
        Args:
            pg_conn: PostgreSQL接続
        """
        self.pg_conn = pg_conn

    def get_table_columns(self, table_name: str) -> List[str]:
        """
        テーブルのカラム一覧を取得

        Args:
            table_name: テーブル名

        Returns:
            List[str]: カラム名のリスト
        """
        query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %(table_name)s
        """
        result = self.pg_conn.execute_query(query, {"table_name": table_name})
        return [row["column_name"] for row in result]

    def get_virtual_keys(self) -> List[Dict[str, Any]]:
        """
        仮想キーの一覧を取得

        Returns:
            List[Dict[str, Any]]: 仮想キーのリスト
        """
        query = "SELECT * FROM virtual_keys"
        return self.pg_conn.execute_query(query)

    def add_virtual_column(self, key: str, value: Any) -> None:
        """
        仮想カラムを追加

        Args:
            key: カラム名
            value: 値（型推定に使用）
        """
        # 型の推定
        field_type = self._infer_field_type(value)
        column_name = f"bq_column_{key}"

        # トランザクション開始
        with self.pg_conn.connection:
            try:
                # カラムが存在するか確認
                query = """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'events'
                    AND column_name = %(column_name)s
                """
                result = self.pg_conn.execute_query(query, {"column_name": column_name})
                if result:
                    logger.info(f"カラム {column_name} はすでに存在します")
                    return

                # virtual_keys テーブルに追加
                self._add_virtual_key(key, field_type)

                # events テーブルにカラム追加
                self._add_column_to_events(column_name, field_type)

                # コミットを確実に行う
                self.pg_conn.connection.commit()

                # カラムが追加されたことを確認
                result = self.pg_conn.execute_query(query, {"column_name": column_name})
                if not result:
                    raise Exception(f"カラム {column_name} の追加に失敗しました")
            except Exception as e:
                # エラーが発生した場合はロールバック
                self.pg_conn.connection.rollback()
                logger.error(f"カラム {column_name} の追加中にエラーが発生しました: {e}")
                raise

    def _infer_field_type(self, value: Any) -> str:
        """
        値から型を推定

        Args:
            value: 型を推定する値

        Returns:
            str: 推定された型（STRING, INTEGER, BIGINT, FLOAT, BOOLEAN）
        """
        if isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            # 整数値の範囲に基づいて型を決定
            if value > 2147483647 or value < -2147483648:
                return "BIGINT"
            return "INTEGER"
        elif isinstance(value, float):
            return "FLOAT"
        else:
            return "STRING"

    def _add_virtual_key(self, key: str, field_type: str) -> None:
        """
        virtual_keys テーブルにキーを追加

        Args:
            key: キー名
            field_type: フィールド型
        """
        query = """
            INSERT INTO virtual_keys (name, parent_field, field_type)
            VALUES (%(name)s, 'event_params.key', %(field_type)s)
            ON CONFLICT (name) DO NOTHING
        """
        self.pg_conn.execute_query(query, {
            "name": key,
            "field_type": field_type
        })

    def _add_column_to_events(self, column_name: str, field_type: str) -> None:
        """
        events テーブルにカラムを追加

        Args:
            column_name: カラム名
            field_type: フィールド型
        """
        # PostgreSQLの型に変換
        pg_type = {
            "STRING": "TEXT",
            "INTEGER": "INTEGER",
            "BIGINT": "BIGINT",
            "FLOAT": "FLOAT",
            "BOOLEAN": "BOOLEAN"
        }[field_type]

        # カラムが存在するか確認
        query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'events'
            AND column_name = %(column_name)s
        """
        result = self.pg_conn.execute_query(query, {"column_name": column_name})
        
        # カラムが存在しない場合のみ追加
        if not result:
            query = f"""
                ALTER TABLE events
                ADD COLUMN {column_name} {pg_type} DEFAULT NULL
            """
            self.pg_conn.execute_query(query)
            logger.info(f"カラム {column_name} を追加しました")

            # カラムが追加されたことを確認
            result = self.pg_conn.execute_query(query, {"column_name": column_name})
            if not result:
                raise Exception(f"カラム {column_name} の追加に失敗しました") 