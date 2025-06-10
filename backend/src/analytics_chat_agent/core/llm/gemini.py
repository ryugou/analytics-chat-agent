import logging
import os
import google.generativeai as genai
from ...config import get_settings

logger = logging.getLogger(__name__)

def call_gemini(prompt: str) -> str:
    """
    Gemini APIを呼び出し、応答を返す

    Args:
        prompt: プロンプト文字列

    Returns:
        str: Gemini APIからの応答

    Raises:
        RuntimeError: APIキーが未設定の場合
    """
    settings = get_settings()
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = settings["gemini"]["model_name"]

    if not api_key:
        raise RuntimeError("Gemini APIキーが設定されていません。")

    try:
        # APIキーの設定
        genai.configure(api_key=api_key)
        logger.info(f"使用するモデル: {model_name}")
        
        # モデルの初期化
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.0,  # より決定論的な出力のために0に設定
                "top_p": 1.0,
                "top_k": 1,
            }
        )
        
        # プロンプトの送信と応答の取得
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.0,
                "top_p": 1.0,
                "top_k": 1,
            }
        )
        
        if not response.text:
            raise RuntimeError("Gemini APIからの応答が空です。")
            
        return response.text

    except Exception as e:
        logger.error(f"Gemini API呼び出しエラー: {str(e)}")
        raise RuntimeError(f"Gemini APIの呼び出しに失敗しました: {e}") 