"""
GPTの呼び出し機能を提供するモジュール
"""

import logging
import os
from typing import Optional

from openai import OpenAI
from ...config import get_settings

logger = logging.getLogger(__name__)

def call_gpt(prompt: str, model: Optional[str] = None) -> str:
    """
    GPTを呼び出して応答を取得する

    Args:
        prompt: プロンプト
        model: モデル名（指定しない場合は設定ファイルの値を使用）

    Returns:
        str: GPTの応答
    """
    settings = get_settings()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEYが設定されていません")

    client = OpenAI(
        api_key=api_key
    )

    if model is None:
        model = settings["openai"]["model_name"]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは有能なAIアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # より決定論的な出力を得るため
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"GPTの呼び出し中にエラーが発生: {str(e)}")
        raise RuntimeError("GPTの呼び出しに失敗しました") from e 