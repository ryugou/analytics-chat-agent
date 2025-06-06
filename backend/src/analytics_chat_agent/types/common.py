from typing import List, TypedDict, Dict, Any

class Intent(TypedDict):
    """
    ユーザーの意図を表す型定義
    """
    key: str  # 意図のキー
    description: str  # 意図の説明
    parameters: Dict[str, Any]  # 意図のパラメータ

class QueryResult(TypedDict, total=False):
    """
    BigQueryクエリ結果の型定義
    """
    event_date: str
    event_name: str
    user_pseudo_id: str
    __annotations__: dict[str, Any]

class FieldMappingResult(TypedDict):
    """
    フィールドマッピング結果の型定義
    """
    fields: List[str]  # 解決されたフィールド名のリスト
    description: str   # フィールドの説明 