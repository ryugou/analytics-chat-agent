from typing import List, TypedDict

class FieldMappingResult(TypedDict):
    """
    フィールドマッピング結果の型定義
    """
    fields: List[str]  # 解決されたフィールド名のリスト
    description: str   # フィールドの説明 