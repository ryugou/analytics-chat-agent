"""
SQL生成モジュール
"""

import logging
from typing import List

from .llm import call_gpt
from ..types import FieldMappingResult

logger = logging.getLogger(__name__)

def generate_sql(field_mapping: FieldMappingResult) -> str:
    """
    フィールドマッピング結果からSQLを生成する

    Args:
        field_mapping: フィールドマッピング結果（fieldsとdescriptionを含む）

    Returns:
        str: 生成されたSQL
    """
    # フィールド情報を文字列に変換
    fields_info = "\n".join([
        f"- {field.name} ({field.type}): {field_mapping.description}"
        for field in field_mapping.fields
    ])

    prompt = f"""あなたはBigQueryとGA4構造に精通したSQLエキスパートです。

        以下のフィールド情報をもとに、Google Analytics 4（GA4）のBigQuery連携テーブルから目的に沿ったSQLクエリを正確に生成してください。

        # 要件（必ず厳守）
        1. 使用テーブルは `events_*`
        2. クエリは **必ず `SELECT` 文から開始**
        3. 日付フィルターは `_TABLE_SUFFIX` を使うこと
        4. 結果は **時系列（例：`event_timestamp`昇順）でソート**
        5. テーブル名は必ず `ungift.analytics_336047273.events_*` をフルパスで指定してください。 ※以下のような仮名の形式（例：`project_id.dataset_id.events_*`）は**絶対に使用しないでください**
        6. **ネストされた構造（例：`event_params`や`user_properties`）は正確に展開すること**
        7. **SQL文のみを出力。解説・コメント・装飾（コードブロックなど）一切不要**
        8. 日付フィルターは、_TABLE_SUFFIX を用いて 現在日付からの相対期間（例：過去30日間、過去1年間など）を正確に動的指定すること。固定値（例：'20230101'）は使用禁止。
        9. 日付条件は動的に変化させること。

        # GA4構造に関する特別な注意点（必ず遵守）

        - `event_params` と `user_properties` はどちらも **REPEATED RECORD型**です。以下のように展開してください：
            - UNNEST対象: `event_params` または `user_properties`
            - 抽出方法: `key = 'XXX'` でフィルター後、`value.string_value` や `value.int_value` 等を取得

        - `items` は `event_params` 内にある key で、その `value.string_value` は **JSON配列形式の文字列**です。
            - `JSON_EXTRACT_ARRAY(...)` を用いて配列に変換した上で `UNNEST()` してください
            - さらに `JSON_EXTRACT_SCALAR(item, '$.price')` のように各プロパティを抽出してください

        - `geo`, `app_info`, `device` などのサブフィールド（例：`geo.city`）は RECORD型です。
            - フラットに `geo.city`, `app_info.version` のようにアクセスしてください
            - 不要な `UNNEST()` や `SELECT ... FROM ... WHERE` のネスト構造は使わないでください

        【重要】SQL文のみを返してください。説明やコメント、コードブロック（```sql など）は不要です。

        # フィールド情報:
        {fields_info}
        """

    response = call_gpt(prompt)

    return response 