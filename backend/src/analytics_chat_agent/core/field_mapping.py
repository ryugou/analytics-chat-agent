from typing import Dict, List, Union, TypedDict, Any
import logging

from .field_resolver import FieldResolver
from ..types import Intent, FieldMappingResult, Field

logger = logging.getLogger(__name__)

class GA4FieldMapper:
    def __init__(self):
        self.field_resolver = FieldResolver()

    def resolve_all_fields(self, intent: Intent) -> FieldMappingResult:
        """
        intentからGA4フィールド名へのマッピングを実行する

        Args:
            intent: intent_extractor.pyで返された意図データ

        Returns:
            GA4フィールド名のマッピング結果
        """
        fields: List[Field] = []

        # 対象のフィールド解決
        target = intent.parameters.get("target", "")
        if target and isinstance(target, str):
            logger.debug(f"Resolving target field: {target}")
            resolved_fields = self.field_resolver.resolve_fields(target)
            fields.extend(resolved_fields.fields)
            logger.debug(f"Resolved target fields: {resolved_fields}")

        # 条件のフィールド解決
        conditions = intent.parameters.get("conditions", [])
        if conditions and isinstance(conditions, list):
            logger.debug(f"Resolving condition fields: {conditions}")
            for condition in conditions:
                if isinstance(condition, str):
                    resolved_fields = self.field_resolver.resolve_fields(condition)
                    for field in resolved_fields.fields:
                        # 新しいFieldオブジェクトを作成
                        fields.append(Field(
                            name=field.name,
                            type="condition"
                        ))
            logger.debug(f"Resolved condition fields: {fields}")

        return FieldMappingResult(
            fields=fields,
            description=""
        ) 