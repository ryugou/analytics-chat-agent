"""GA4スキーマのインポート処理を行うモジュール。"""

import csv
from pathlib import Path
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

from analytics_chat_agent.config.settings import (
    get_qdrant_url,
    get_qdrant_api_key,
    GA4_SCHEMA_MODEL_NAME,
    GA4_SCHEMA_VECTOR_SIZE,
)


class SchemaImporter:
    """GA4スキーマをQdrantにインポートするクラス。"""

    def __init__(self, collection_name: str = "ga4_schema"):
        """初期化。

        Args:
            collection_name: Qdrantのコレクション名
        """
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=get_qdrant_url(),
            api_key=get_qdrant_api_key(),
        )
        self.model = SentenceTransformer(GA4_SCHEMA_MODEL_NAME)
        # ベクトルサイズのチェック
        if self.model.get_sentence_embedding_dimension() is None:
            raise ValueError("モデルのベクトルサイズが不正です")

    def import_from_csv(self, csv_path: Path) -> int:
        """CSVファイルからスキーマをインポートする。

        Args:
            csv_path: インポートするCSVファイルのパス

        Returns:
            インポートされたスキーマの数

        Raises:
            FileNotFoundError: CSVファイルが存在しない場合
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # コレクションの再作成
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=GA4_SCHEMA_VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )

        # CSVファイルの読み込み
        schemas = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # テキストの生成
                full_text = f"{row['description']} [{row['field_type']}] → {row['name']}"
                # ベクトルの生成
                vector = self.model.encode(full_text).tolist()
                
                # パラメータ名をハッシュ化してIDとして使用（符号なし整数に変換）
                point_id = abs(hash(row["name"])) % (2**63)  # 63ビットの符号なし整数に収める
                
                schemas.append(
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "id": row["id"],
                            "name": row["name"],
                            "type": row["field_type"],
                            "description": row["description"],
                            "full_text": full_text,
                        },
                    )
                )

        # スキーマの一括登録
        self.client.upsert(
            collection_name=self.collection_name,
            points=schemas,
        )

        return len(schemas) 