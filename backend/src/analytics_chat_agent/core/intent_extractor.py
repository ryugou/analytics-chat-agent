import ast
from typing import Dict, List, Union

from analytics_chat_agent.llm import call_gemini


def extract_intent(question: str) -> Dict[str, Union[str, List[str]]]:
    """
    自然言語の質問から意図を抽出する関数

    Args:
        question (str): 自然言語での質問文

    Returns:
        Dict[str, Union[str, List[str]]]: 抽出された意図を含む辞書
        {
            "目的": str,
            "対象": str,
            "条件": List[str]
        }
    """
    prompt = f"""次の質問の意図を抽出してください：
「{question}」

出力形式（Pythonの辞書形式）：
{{
  "目的": "...",
  "対象": "...",
  "条件": ["...", "..."]
}}"""

    try:
        response = call_gemini(prompt)
        result = ast.literal_eval(response)

        # 必要なキーが存在することを確認
        if not all(key in result for key in ["目的", "対象", "条件"]):
            return {"目的": "", "対象": "", "条件": []}

        # 条件の型チェック
        if not isinstance(result["条件"], list) or not all(
            isinstance(c, str) for c in result["条件"]
        ):
            return {"目的": "", "対象": "", "条件": []}

        return result
    except (SyntaxError, ValueError, TypeError):
        # 不正な形式の場合は空テンプレートを返す
        return {"目的": "", "対象": "", "条件": []}
