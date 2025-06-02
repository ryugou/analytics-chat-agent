"""環境変数と設定の管理モジュール。

このモジュールは、アプリケーション全体で使用される環境変数と設定を管理します。
.envファイルから設定を読み込み、必要な環境変数が設定されているかを確認します。
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from the project root
env_path = Path(__file__).parents[3] / ".env"
load_dotenv(env_path)


def get_openai_api_key() -> str:
    """OpenAI APIキーを環境変数から取得します。

    Returns:
        str: OpenAI APIキー。

    Raises:
        ValueError: OPENAI_API_KEYが環境変数に設定されていない場合。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in environment variables")
    return api_key


def get_qdrant_url() -> str:
    """QdrantのURLを環境変数から取得します。

    Returns:
        str: QdrantのURL。環境変数が設定されていない場合は'http://localhost:6333'を返します。
    """
    return os.getenv("QDRANT_URL", "http://localhost:6333")


def get_bigquery_credentials_path() -> str:
    """BigQueryの認証情報ファイルのパスを環境変数から取得します。

    Returns:
        str: BigQueryの認証情報ファイルのパス。環境変数が設定されていない場合は空文字列を返します。
    """
    return os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
