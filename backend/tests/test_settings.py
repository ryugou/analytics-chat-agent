import os
import pytest

from analytics_chat_agent.config import settings


def test_get_openai_api_key_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    assert settings.get_openai_api_key() == "test-key"


def test_get_openai_api_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        settings.get_openai_api_key()


def test_get_qdrant_url_default(monkeypatch):
    monkeypatch.delenv("QDRANT_URL", raising=False)
    assert settings.get_qdrant_url() == "http://localhost:6333"


def test_get_qdrant_url_env(monkeypatch):
    monkeypatch.setenv("QDRANT_URL", "http://test-qdrant:1234")
    assert settings.get_qdrant_url() == "http://test-qdrant:1234"


def test_get_bigquery_credentials_path_default(monkeypatch):
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    assert settings.get_bigquery_credentials_path() == ""


def test_get_bigquery_credentials_path_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/path/to/creds.json")
    assert settings.get_bigquery_credentials_path() == "/path/to/creds.json"


def test_get_qdrant_api_key_default():
    """Qdrant API Keyが設定されていない場合のテスト"""
    if "QDRANT_API_KEY" in os.environ:
        del os.environ["QDRANT_API_KEY"]
    assert settings.get_qdrant_api_key() == ""


def test_get_qdrant_api_key_env():
    """Qdrant API Keyが環境変数で設定されている場合のテスト"""
    os.environ["QDRANT_API_KEY"] = "test-api-key"
    assert settings.get_qdrant_api_key() == "test-api-key"


def test_get_bigquery_credentials_path_default():
    """BigQuery認証情報のパスが設定されていない場合のテスト"""
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    assert settings.get_bigquery_credentials_path() == ""


def test_get_bigquery_credentials_path_env():
    """BigQuery認証情報のパスが環境変数で設定されている場合のテスト"""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/credentials.json"
    assert settings.get_bigquery_credentials_path() == "/path/to/credentials.json"
