"""
フィールド解決モジュール
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import logging
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from ..types.common import FieldMappingResult
from ..core.llm.gemini import call_gemini

logger = logging.getLogger(__name__)

def get_settings():
    """設定ファイルを読み込む"""
    settings_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(settings_path) as f:
        return json.load(f)

class FieldResolver:
    """
    フィールド解決を行うクラス
    """
    def __init__(self):
        """
        FieldResolverの初期化

        Raises:
            RuntimeError: 必要な設定が不足している場合
        """
        self.settings = get_settings()
        self.model_name = self.settings["model"]["name"]
        
        # モデルの初期化
        self.model = SentenceTransformer(self.model_name)
        
        # Qdrantクライアントの初期化
        try:
            self.qdrant_client = QdrantClient(
                url=self.settings["qdrant"]["url"],
                api_key=self.settings["qdrant"]["api_key"]
            )
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            raise RuntimeError("Failed to connect to Qdrant server.") from e
        
        # コレクション名
        self.collection_name = self.settings["qdrant"]["collection_name"]

    def resolve_fields(self, queries: List[str]) -> FieldMappingResult:
        """
        クエリからフィールドを解決する

        Args:
            queries: 解決対象のクエリリスト

        Returns:
            FieldMappingResult: フィールド解決結果
        """
        try:
            # プロンプトの構築
            prompt = self._build_prompt(queries)
            logger.debug(f"プロンプト: {prompt}")
            
            # Gemini APIを呼び出し
            response = call_gemini(prompt)
            logger.debug(f"Gemini APIレスポンス: {response}")
            
            # レスポンスの解析
            return self._parse_response(response)
            
        except Exception as e:
            logger.error(f"フィールド解決エラー: {e}")
            raise RuntimeError("フィールド解決に失敗しました。") from e

    def _build_prompt(self, queries: List[str]) -> str:
        """
        プロンプトを構築する

        Args:
            queries: 解決対象のクエリリスト

        Returns:
            str: 構築されたプロンプト
        """
        return f"""
        以下のクエリから必要なGA4のフィールド名を抽出してください。
        クエリ: {queries}
        
        必ず以下の形式でJSONを返してください。他の説明やテキストは含めないでください。
        また、JSONの前後に余分な文字や改行を入れないでください：
        {{
            "fields": ["フィールド1", "フィールド2", ...],
            "description": "フィールドの説明"
        }}
        
        例：
        {{
            "fields": ["event_date", "event_name", "user_pseudo_id"],
            "description": "ユーザー数の分析に必要なフィールド"
        }}
        
        注意：
        1. 必ず有効なJSON形式で返してください
        2. 前後に余分な文字や改行を入れないでください
        3. 他の説明やテキストは含めないでください
        4. 必ず"fields"と"description"の両方を含めてください
        5. フィールド名は必ずGA4の実際のフィールド名を使用してください（例：event_date, event_name, event_value, user_pseudo_id など）
        6. 日本語のフィールド名は使用せず、必ず英語のフィールド名を使用してください
        """

    def _parse_response(self, response: str) -> FieldMappingResult:
        """
        レスポンスを解析する

        Args:
            response: Gemini APIからのレスポンス

        Returns:
            FieldMappingResult: 解析結果
        """
        try:
            # JSONとして解析
            result = json.loads(response)
            
            # 型チェック
            if not isinstance(result, dict):
                raise ValueError("レスポンスが辞書形式ではありません")
            
            if "fields" not in result:
                raise ValueError("'fields'キーが存在しません")
            
            if not isinstance(result["fields"], list):
                raise ValueError("'fields'がリスト形式ではありません")
            
            return FieldMappingResult(
                fields=result["fields"],
                description=result.get("description", "")
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}")
            raise ValueError("レスポンスのJSON解析に失敗しました。") from e
        except Exception as e:
            logger.error(f"レスポンス解析エラー: {e}")
            raise RuntimeError("レスポンスの解析に失敗しました。") from e 