from typing import Dict, List, Union, TypedDict, Any
import logging

from .field_resolver import FieldResolver
from ..types import Intent, FieldMappingResult

logger = logging.getLogger(__name__)

class GA4FieldMapper:
    def __init__(self):
        self.field_resolver = FieldResolver()

    def resolve_all_fields(self, intent: Intent) -> FieldMappingResult:
        """
        intentからGA4フィールド名へのマッピングを実行する

        Args:
            intent: intent_extractor.pyで返された意図データ
                  {
                      "key": str,
                      "description": str,
                      "parameters": Dict[str, Any]
                  }

        Returns:
            GA4フィールド名のマッピング結果
            {
                "fields": List[Dict[str, str]]
            }
        """
        result: FieldMappingResult = {
            "fields": []
        }

        # 対象のフィールド解決
        target = intent.get("parameters", {}).get("target", "")
        if target and isinstance(target, str):
            logger.debug(f"Resolving target field: {target}")
            resolved_fields = self.field_resolver.resolve_fields([target])
            for field in resolved_fields:
                result["fields"].append({
                    "name": field,
                    "type": "target"
                })
            logger.debug(f"Resolved target fields: {resolved_fields}")

        # 条件のフィールド解決
        conditions = intent.get("parameters", {}).get("conditions", [])
        if conditions and isinstance(conditions, list):
            logger.debug(f"Resolving condition fields: {conditions}")
            resolved_fields = self.field_resolver.resolve_fields(conditions)
            for field in resolved_fields:
                result["fields"].append({
                    "name": field,
                    "type": "condition"
                })
            logger.debug(f"Resolved condition fields: {resolved_fields}")

        return result 