"""
分析サービスの実装
"""

import logging
import json
from typing import Dict, Any

from ..field_resolver import FieldResolver
from ..sql_generator import generate_sql
from ..sql_executor import run_bigquery_query
from ..llm import call_gemini
from ...types import Intent, FieldMappingResult

logger = logging.getLogger(__name__)

class AnalysisService:
    """分析サービス"""

    def __init__(self):
        self.field_resolver = FieldResolver()

    def _extract_intent(self, query: str) -> Intent:
        """
        クエリから意図を抽出する

        Args:
            query: 自然言語クエリ

        Returns:
            Intent: 抽出された意図
        """
        prompt = f"""
        以下のクエリから分析意図を抽出してください。
        クエリ: {query}

        必ず以下の形式でJSONを返してください。他の説明やテキストは含めないでください：
        {{
            "key": "分析タイプのキー",
            "description": "分析の説明",
            "parameters": {{
                "time_range": "時間範囲（例：7d, 30d, 1y）",
                "other_params": "その他のパラメータ"
            }}
        }}

        分析タイプのキーは以下のいずれかを使用してください：
        - user_count: ユーザー数分析
        - sales_trend: 売上推移分析
        - conversion_rate: コンバージョン率分析
        - retention: リテンション分析
        - custom: その他の分析

        注意：
        1. 必ず有効なJSON形式で返してください
        2. 前後に余分な文字や改行を入れないでください
        3. 他の説明やテキストは含めないでください
        """

        response = call_gemini(prompt)
        logger.debug(f"意図抽出のレスポンス: {response}")
        
        try:
            intent = json.loads(response)
            return intent
        except json.JSONDecodeError as e:
            logger.error(f"意図抽出のレスポンスをJSONとしてパースできませんでした: {e}")
            raise RuntimeError("意図抽出のレスポンスが不正な形式です")

    def analyze(self, query: str) -> Dict[str, Any]:
        """
        自然言語クエリを分析し、結果を返す

        Args:
            query: 自然言語クエリ

        Returns:
            Dict[str, Any]: 分析結果
        """
        try:
            # 意図の抽出
            intent = self._extract_intent(query)
            logger.info(f"意図を抽出: {intent}")

            # フィールドの解決
            field_mapping = self.field_resolver.resolve_fields([query])
            logger.info(f"フィールドを解決: {field_mapping}")

            # SQLの生成
            sql = generate_sql(field_mapping)
            logger.info(f"SQLを生成: {sql}")

            # クエリの実行
            results = run_bigquery_query(sql)
            logger.info(f"クエリを実行: {len(results)}件の結果")

            return {
                "query": query,
                "intent": intent,
                "field_mapping": dict(field_mapping),
                "sql": sql,
                "results": results
            }

        except Exception as e:
            logger.error(f"分析中にエラーが発生: {str(e)}")
            raise 