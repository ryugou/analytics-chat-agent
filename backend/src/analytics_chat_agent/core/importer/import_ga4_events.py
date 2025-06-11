"""
GA4イベントデータの移行処理
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..database import BigQueryConnection, PostgresConnection
from ..schema import SchemaManager
from ...qdrant.importer import import_events_to_qdrant
from ...config import get_settings
from qdrant_client import QdrantClient
import json

logger = logging.getLogger(__name__)

class EventsImporter:
    """GA4イベントデータの移行処理クラス"""

    def __init__(self, bq_conn: BigQueryConnection, pg_conn: PostgresConnection):
        """
        Args:
            bq_conn: BigQuery接続
            pg_conn: PostgreSQL接続
        """
        self.bq_conn = bq_conn
        self.pg_conn = pg_conn
        self.schema_manager = SchemaManager(pg_conn)
        self.virtual_keys = {vk["name"]: vk for vk in self.schema_manager.get_virtual_keys()}

    def import_all_events(self) -> int:
        """
        全期間のイベントデータをインポート

        Returns:
            int: インポートしたレコード数
        """
        # 全データを削除
        self._delete_all_events()
        
        # 全期間のデータを取得してインポート
        query = self._build_base_query()
        return self._import_events(query)

    def import_events_by_date(self, target_date: str) -> int:
        """
        指定日付のイベントデータをインポート

        Args:
            target_date: 対象日付 (YYYY-MM-DD)

        Returns:
            int: インポートしたレコード数
        """
        # 指定日付のデータを削除
        self._delete_events_by_date(target_date)
        
        # 指定日付のデータを取得してインポート
        query = self._build_base_query(target_date)
        return self._import_events(query)

    def _delete_all_events(self) -> None:
        """全イベントデータを削除"""
        query = "TRUNCATE events CASCADE"
        self.pg_conn.execute_query(query)

    def _delete_events_by_date(self, target_date: str) -> None:
        """
        指定日付のイベントデータを削除

        Args:
            target_date: 対象日付 (YYYY-MM-DD)
        """
        query = """
            DELETE FROM events
            WHERE DATE(event_timestamp) = %(target_date)s
        """
        self.pg_conn.execute_query(query, {"target_date": target_date})

    def _build_base_query(self, target_date: Optional[str] = None) -> str:
        """
        基本クエリを構築

        Args:
            target_date: 対象日付 (YYYY-MM-DD)

        Returns:
            str: SQLクエリ
        """
        date_filter = f"AND _TABLE_SUFFIX = '{target_date.replace('-', '')}'" if target_date else ""
        
        # virtual_keysからキー名のリストを取得
        keys = list(self.virtual_keys.keys())
        if keys:
            keys_str = ", ".join([f"'{key}'" for key in keys])
            key_filter = f"AND param.key IN ({keys_str})"
        else:
            key_filter = ""
        
        return f"""
            SELECT 
                event_bundle_sequence_id,
                event_timestamp,
                event_name,
                param.key as param_key,
                param.value as param_value
            FROM `ungift.analytics_336047273.events_*`,
            UNNEST(event_params) as param
            WHERE 1=1 {date_filter}
            {key_filter}
        """

    def _import_events(self, query: str) -> int:
        """
        イベントデータをインポート

        Args:
            query: 実行するSQLクエリ

        Returns:
            int: インポートしたレコード数
        """
        # BigQueryからデータを取得
        rows = list(self.bq_conn.execute_query(query))
        
        # デバッグ用：最初の数行のデータを出力
        logger.debug("BigQueryから取得したデータの最初の5行:")
        for i, row in enumerate(rows[:5]):
            logger.debug(f"行 {i+1}: {row}")
        
        # イベントデータを正規化
        events = self._normalize_events(rows)
        
        # PostgreSQLに挿入
        count = self._insert_events(events)

        # Qdrantにイベント構造を登録
        settings = get_settings()
        qdrant_client = QdrantClient(
            url=settings["qdrant"]["url"],
            api_key=settings["qdrant"]["api_key"]
        )
        import_events_to_qdrant(self.pg_conn, qdrant_client)
        logger.info("イベント構造をQdrantに登録しました")

        return count

    def _normalize_events(self, rows: List[Any]) -> List[Dict[str, Any]]:
        """
        イベントデータを正規化

        Args:
            rows: BigQueryから取得した行データ

        Returns:
            List[Dict[str, Any]]: 正規化されたイベントデータ
        """
        events = {}
        new_keys = set()  # 新しいキーを記録

        # 最初のパス：新しいキーを検出
        for row in rows:
            if row.param_key not in self.virtual_keys:
                new_keys.add(row.param_key)

        # 新しいキーを一括で追加
        if new_keys:
            # サンプルの値を取得
            key_samples = {}
            for key in new_keys:
                for row in rows:
                    if row.param_key == key:
                        param_value = row.param_value
                        if param_value.get('string_value') is not None:
                            key_samples[key] = param_value['string_value']
                        elif param_value.get('int_value') is not None:
                            key_samples[key] = param_value['int_value']
                        elif param_value.get('float_value') is not None:
                            key_samples[key] = param_value['float_value']
                        elif param_value.get('double_value') is not None:
                            key_samples[key] = param_value['double_value']
                        break

            # カラムを一括で追加
            try:
                for key, sample_value in key_samples.items():
                    self.schema_manager.add_virtual_column(key, sample_value)
                    logger.info(f"新しいキー {key} を追加しました")
            except Exception as e:
                logger.error(f"キーの追加に失敗しました: {e}")
                raise

            # virtual_keysを更新
            self.virtual_keys = {vk['name']: vk for vk in self.schema_manager.get_virtual_keys()}

        # 2番目のパス：データを正規化
        for row in rows:
            event_id = row.event_bundle_sequence_id
            if event_id not in events:
                events[event_id] = {
                    "event_bundle_sequence_id": event_id,
                    "event_dimensions": json.dumps({
                        "event_name": row.event_name
                    })
                }

            # パラメータの値を取得
            param_value = row.param_value
            value = None
            if param_value.get('string_value') is not None:
                value = param_value['string_value']
            elif param_value.get('int_value') is not None:
                value = param_value['int_value']
            elif param_value.get('float_value') is not None:
                value = param_value['float_value']
            elif param_value.get('double_value') is not None:
                value = param_value['double_value']

            # カラム名を生成
            column_name = f"bq_column_{row.param_key}"
            events[event_id][column_name] = value

        return list(events.values())

    def _insert_events(self, events: List[Dict[str, Any]]) -> int:
        """
        イベントデータをPostgreSQLに挿入

        Args:
            events: 挿入するイベントデータ

        Returns:
            int: 挿入したレコード数
        """
        if not events:
            return 0
        
        # カラム名を取得
        columns = list(events[0].keys())
        
        # プレースホルダーを生成
        placeholders = ", ".join([f"%({col})s" for col in columns])
        
        # クエリを構築
        query = f"""
            INSERT INTO events ({", ".join(columns)})
            VALUES ({placeholders})
        """
        
        # データを挿入
        self.pg_conn.execute_many(query, events)
        return len(events)

    def _insert_app_infos(self, app_infos: List[Dict[str, Any]]) -> None:
        """
        app_infoデータをPostgreSQLに挿入

        Args:
            app_infos: 挿入するapp_infoデータ
        """
        if not app_infos:
            return
        
        # カラム名を取得
        columns = list(app_infos[0].keys())
        
        # プレースホルダーを生成
        placeholders = ", ".join([f"%({col})s" for col in columns])
        
        # クエリを構築
        query = f"""
            INSERT INTO app_info ({", ".join(columns)})
            VALUES ({placeholders})
        """
        
        # データを挿入
        self.pg_conn.execute_many(query, app_infos)

    def _insert_devices(self, devices: List[Dict[str, Any]]) -> None:
        """
        deviceデータをPostgreSQLに挿入

        Args:
            devices: 挿入するdeviceデータ
        """
        if not devices:
            return
        
        # カラム名を取得
        columns = list(devices[0].keys())
        
        # プレースホルダーを生成
        placeholders = ", ".join([f"%({col})s" for col in columns])
        
        # クエリを構築
        query = f"""
            INSERT INTO device ({", ".join(columns)})
            VALUES ({placeholders})
        """
        
        # データを挿入
        self.pg_conn.execute_many(query, devices)

    def _insert_ecommerces(self, ecommerces: List[Dict[str, Any]]) -> None:
        """
        ecommerceデータをPostgreSQLに挿入

        Args:
            ecommerces: 挿入するecommerceデータ
        """
        if not ecommerces:
            return
        
        # カラム名を取得
        columns = list(ecommerces[0].keys())
        
        # プレースホルダーを生成
        placeholders = ", ".join([f"%({col})s" for col in columns])
        
        # クエリを構築
        query = f"""
            INSERT INTO ecommerce ({", ".join(columns)})
            VALUES ({placeholders})
        """
        
        # データを挿入
        self.pg_conn.execute_many(query, ecommerces)

    def _insert_items(self, items: List[Dict[str, Any]]) -> None:
        """
        itemsデータをPostgreSQLに挿入

        Args:
            items: 挿入するitemsデータ
        """
        if not items:
            return
        
        # カラム名を取得
        columns = list(items[0].keys())
        
        # プレースホルダーを生成
        placeholders = ", ".join([f"%({col})s" for col in columns])
        
        # クエリを構築
        query = f"""
            INSERT INTO items ({", ".join(columns)})
            VALUES ({placeholders})
        """
        
        # データを挿入
        self.pg_conn.execute_many(query, items) 