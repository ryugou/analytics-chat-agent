import csv
import logging
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from ...config import get_settings

logger = logging.getLogger(__name__)

class SchemaImporter:
    """
    GA4スキーマをQdrantにインポートするクラス
    """
    def __init__(self):
        """
        SchemaImporterの初期化

        Raises:
            RuntimeError: 必要な設定が不足している場合
        """
        settings = get_settings()

        # モデルの初期化
        self.model = SentenceTransformer(settings["model"]["name"])

        # Qdrantクライアントの初期化
        try:
            self.qdrant_client = QdrantClient(
                url=settings["qdrant"]["url"],
                api_key=settings["qdrant"]["api_key"]
            )
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            raise RuntimeError("Failed to connect to Qdrant server.") from e

        # コレクション名
        self.collection_name = settings["qdrant"]["collection_name"]

    def import_schema(self, csv_path: Path, source: str = None) -> int:
        """
        CSVファイルからスキーマをインポートする

        Args:
            csv_path: スキーマCSVファイルのパス
            source: オプションの識別子（例: 'virtual'）

        Returns:
            int: インポートしたフィールド数

        Raises:
            FileNotFoundError: CSVファイルが見つからない場合
            RuntimeError: インポートに失敗した場合
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"CSVファイルが見つかりません: {csv_path}")

        try:
            self._create_collection_if_not_exists()
            fields = self._read_csv(csv_path)
            count = self._import_fields(fields, source)
            return count
        except Exception as e:
            logger.error(f"スキーマインポートエラー: {e}")
            raise RuntimeError("スキーマのインポートに失敗しました。") from e

    def _create_collection_if_not_exists(self):
        """
        コレクションが存在しない場合は作成する
        """
        try:
            collections = self.qdrant_client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.model.get_sentence_embedding_dimension(),
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"コレクション '{self.collection_name}' を作成しました。")

        except Exception as e:
            logger.error(f"コレクション作成エラー: {e}")
            raise RuntimeError("コレクションの作成に失敗しました。") from e

    def _read_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """
        CSVファイルを読み込む

        Args:
            csv_path: CSVファイルのパス

        Returns:
            List[Dict[str, str]]: フィールド情報のリスト
        """
        fields = []
        seen: set[tuple[str, str]] = set() 
        try:
            with csv_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name  = row["name"].strip()
                    desc  = row["description"].strip()
                    ftype = row.get("field_type") or row.get("expected_type", "STRING")
                    parent = row.get("parent_field", "").strip()

                    key = (name, ftype)
                    if key in seen:
                        continue                    # 同CSV内での重複行を除外
                    seen.add(key)

                    fields.append({
                        "name": name,
                        "description": desc,
                        "type": ftype,
                        "parent_field": parent
                    })
            return fields   

        except Exception as e:
            logger.error(f"CSV読み込みエラー: {e}")
            raise RuntimeError("CSVファイルの読み込みに失敗しました。") from e

    def _import_fields(self, fields: List[Dict[str, str]], source: str = None) -> int:
        """
        フィールドをQdrantにインポートする

        Args:
            fields: フィールド情報のリスト
            source: オプションの識別子（例: 'virtual'）

        Returns:
            int: インポートしたフィールド数
        """
        try:
            texts = [f"{f['description']} [{f['type']}] → {f['name']}" for f in fields]
            embeds = self.model.encode(texts)

            for rec, vec in zip(fields, embeds):
                # 🔑 name+source でハッシュ化して id をユニークに
                uid = abs(hash(f"{rec['name']}|{source or 'schema'}")) % (2**63)

                payload = {
                    "name": rec["name"],
                    "type": rec["type"],
                    "description": rec["description"],
                    "parent_field": rec["parent_field"],
                    "source": source or "schema",
                    "full_text":    f"{rec['description']} [{rec['type']}] → {rec['name']}",
                }
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=[models.PointStruct(id=uid, vector=vec.tolist(), payload=payload)]
                )
            return len(fields)

        except Exception as e:
            logger.error(f"フィールドインポートエラー: {e}")
            raise RuntimeError("フィールドのインポートに失敗しました。") from e
