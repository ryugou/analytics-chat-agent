"""
SQL生成モジュール
"""

from typing import List, Dict, Any

from .llm import call_gemini
from ..types import FieldMappingResult

def generate_sql(field_mapping: FieldMappingResult) -> str:
    """
    フィールドマッピングからSQLを生成する

    Args:
        field_mapping: フィールドマッピング結果

    Returns:
        str: 生成されたSQL
    """
    # TODO: より高度なSQL生成ロジックの実装
    fields = ", ".join([f"'{field}'" for field in field_mapping["fields"]])
    return f"SELECT {fields} FROM analytics_987654321.events_*" 