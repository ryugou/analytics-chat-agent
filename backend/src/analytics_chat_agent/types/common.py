from typing import List, Dict, Any, Literal, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Intent:
    """
    ユーザーの意図を表す型定義
    """
    key: str  # 意図のキー
    description: str  # 意図の説明
    parameters: Dict[str, Any]  # 意図のパラメータ

@dataclass
class QueryResult:
    """
    BigQueryクエリ結果の型定義
    """
    # 柔軟に任意のキーを保持できるよう汎用構造に変更
    values: Dict[str, Any] = None

    def __post_init__(self):
        if self.values is None:
            self.values = {}

@dataclass
class Field:
    """
    フィールド情報の型定義
    """
    name: str  # フィールド名
    type: str  # フィールドの型

@dataclass
class FieldMappingResult:
    """
    フィールドマッピング結果の型定義
    """
    fields: List[Field]  # 解決されたフィールド情報のリスト
    description: str  # フィールドの説明
