"""フィールド名の解決を行うモジュール。"""

import os
from pathlib import Path
from typing import List, Optional
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

from ..config import get_settings
from ..types import FieldMappingResult, Field

# 設定の読み込み
settings = get_settings()
GA4_SCHEMA_MODEL_NAME = settings["model"]["name"]
GA4_SCHEMA_VECTOR_SIZE = 384  # all-MiniLM-L6-v2のベクトルサイズ

# キャッシュディレクトリの設定
CACHE_DIR = Path(".cache/sentence_transformers")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# モデルのキャッシュ
_model_cache = {}

def _create_session_with_retry():
    """リトライ付きのセッションを作成する"""
    session = requests.Session()
    retry = Retry(
        total=5,  # 最大5回リトライ
        backoff_factor=1,  # リトライ間隔を指数関数的に増加
        status_forcelist=[500, 502, 503, 504]  # これらのステータスコードでリトライ
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_cached_model():
    """キャッシュされたモデルを取得する。キャッシュがない場合は新しくダウンロードする。"""
    global _model_cache
    if GA4_SCHEMA_MODEL_NAME not in _model_cache:
        # カスタムセッションを使用してモデルを初期化
        session = _create_session_with_retry()
        _model_cache[GA4_SCHEMA_MODEL_NAME] = SentenceTransformer(
            GA4_SCHEMA_MODEL_NAME,
            cache_folder=str(CACHE_DIR),
            device="cpu"  # MPSデバイスでの問題を回避
        )
    return _model_cache[GA4_SCHEMA_MODEL_NAME]

class FieldResolver:
    """フィールド名の解決を行うクラス。"""

    def __init__(self, collection_name: str = "ga4_schema"):
        """初期化。

        Args:
            collection_name: Qdrantのコレクション名
        """
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=settings["qdrant"]["url"],
            api_key=settings["qdrant"]["api_key"],
        )
        
        # モデルの初期化（キャッシュを使用）
        self.model = get_cached_model()
        
        # ベクトルサイズのチェック
        if self.model.get_sentence_embedding_dimension() is None:
            raise ValueError("モデルのベクトルサイズが不正です")

    def resolve_fields(self, query: str, limit: int = 5) -> FieldMappingResult:
        """自然言語のクエリからフィールド名を解決する。

        Args:
            query: 自然言語のクエリ
            limit: 取得するフィールドの最大数

        Returns:
            FieldMappingResult: 解決されたフィールド情報
        """
        # クエリをベクトル化
        query_vector = self.model.encode(query).tolist()
        
        # Qdrantで検索
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,  # Vectorクラスのインスタンス化を避け、直接ベクトルを渡す
            limit=limit,
            search_params=models.SearchParams(
                hnsw_ef=128,  # HNSWインデックスの探索パラメータ
                exact=False,  # 近似検索を使用
            ),
        )
        
        # 結果を整形
        fields: List[Field] = []
        description = ""
        for result in search_result:
            field = Field(
                name=result.payload["name"],
                type="string"  # 固定の文字列を使用
            )
            fields.append(field)
            if not description:
                description = result.payload["description"]
        
        return FieldMappingResult(
            fields=fields,
            description=description
        ) 