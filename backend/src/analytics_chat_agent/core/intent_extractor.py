import ast
from typing import Dict, List, Union, Any

from .llm import call_gemini
from ..types import Intent


def extract_intent(question: str) -> Intent:
    """
    自然言語の質問から意図を抽出する関数

    Args:
        question (str): 自然言語での質問文

    Returns:
        Intent: 抽出された意図を含むオブジェクト
    """
    prompt = f"""次の質問の意図を抽出してください：
「{question}」

出力形式（Pythonの辞書形式）：
{{
  "key": "分析の種類（例：user_count, page_view, event_count等）",
  "description": "分析の目的の説明",
  "parameters": {{
    "target": "分析対象",
    "conditions": ["条件1", "条件2", ...],
    "time_range": "時間範囲（例：7d, 30d等）"
  }}
}}"""

    try:
        response = call_gemini(prompt)
        result = ast.literal_eval(response)

        # 必要なキーが存在することを確認
        if not all(key in result for key in ["key", "description", "parameters"]):
            return Intent(
                key="",
                description="",
                parameters={}
            )

        # parametersの型チェック
        if not isinstance(result["parameters"], dict):
            return Intent(
                key="",
                description="",
                parameters={}
            )

        return Intent(
            key=result["key"],
            description=result["description"],
            parameters=result["parameters"]
        )
    except (SyntaxError, ValueError, TypeError):
        # 不正な形式の場合は空テンプレートを返す
        return Intent(
            key="",
            description="",
            parameters={}
        )
