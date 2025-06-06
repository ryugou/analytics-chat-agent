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

    def import_schema(self, csv_path: Path) -> int:
        """
        CSVファイルからスキーマをインポートする

        Args:
            csv_path: スキーマCSVファイルのパス

        Returns:
            int: インポートしたフィールド数

        Raises:
            FileNotFoundError: CSVファイルが見つからない場合
            RuntimeError: インポートに失敗した場合
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"CSVファイルが見つかりません: {csv_path}")

        try:
            # コレクションの作成（既に存在する場合はスキップ）
            self._create_collection_if_not_exists()
            
            # CSVファイルの読み込み
            fields = self._read_csv(csv_path)
            
            # フィールドのインポート
            count = self._import_fields(fields)
            
            logger.info(f"{count}件のフィールドをインポートしました。")
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
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fields.append({
                        'name': row['name'],
                        'description': row['description']
                    })
            return fields
            
        except Exception as e:
            logger.error(f"CSV読み込みエラー: {e}")
            raise RuntimeError("CSVファイルの読み込みに失敗しました。") from e

    def _import_fields(self, fields: List[Dict[str, str]]) -> int:
        """
        フィールドをQdrantにインポートする

        Args:
            fields: フィールド情報のリスト

        Returns:
            int: インポートしたフィールド数
        """
        try:
            # フィールドの説明をエンベディング
            texts = [f"{field['name']} {field['description']}" for field in fields]
            embeddings = self.model.encode(texts)
            
            # バッチサイズ
            batch_size = 100
            
            # バッチ処理
            for i in range(0, len(fields), batch_size):
                batch_fields = fields[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]
                
                # ポイントの作成
                points = [
                    models.PointStruct(
                        id=i + j,
                        vector=embedding.tolist(),
                        payload=field
                    )
                    for j, (field, embedding) in enumerate(zip(batch_fields, batch_embeddings))
                ]
                
                # バッチのアップロード
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
            return len(fields)
            
        except Exception as e:
            logger.error(f"フィールドインポートエラー: {e}")
            raise RuntimeError("フィールドのインポートに失敗しました。") from e 