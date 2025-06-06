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
    """OpenAIのAPIキーを取得します。"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEYが設定されていません")
    return api_key


def get_qdrant_url() -> str:
    """QdrantのURLを取得します。"""
    return os.getenv("QDRANT_URL", "http://localhost:6333")


def get_qdrant_api_key() -> str:
    """QdrantのAPIキーを取得します。"""
    return os.getenv("QDRANT_API_KEY", "")


def get_bigquery_credentials_path() -> str:
    """BigQueryの認証情報ファイルのパスを取得します。"""
    return os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")


# === GA4 Schema Settings ===
GA4_SCHEMA_COLLECTION_NAME = "ga4_schema"
GA4_SCHEMA_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def get_ga4_schema_csv_path() -> Path:
    """GA4スキーマCSVファイルのパスを返す"""
    # backend/data/ga4_schema.csv を返す
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    return base_dir / "data" / "ga4_schema" / "ga4_schema.csv"
