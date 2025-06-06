import os
import pytest
from analytics_chat_agent.config import settings
from pathlib import Path


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


def test_get_qdrant_api_key_default(monkeypatch):
    monkeypatch.delenv("QDRANT_API_KEY", raising=False)
    assert settings.get_qdrant_api_key() == ""


def test_get_qdrant_api_key_env(monkeypatch):
    monkeypatch.setenv("QDRANT_API_KEY", "test-api-key")
    assert settings.get_qdrant_api_key() == "test-api-key"


def test_get_ga4_schema_csv_path(monkeypatch):
    # デフォルト値のテスト
    monkeypatch.delenv("GA4_SCHEMA_CSV_PATH", raising=False)
    path = settings.get_ga4_schema_csv_path()
    expected = str(Path.cwd() / "data/ga4_schema/ga4_schema.csv")
    assert str(path) == expected

    # 環境変数で上書きした場合のテスト
    test_path = "/tmp/test.csv"
    monkeypatch.setenv("GA4_SCHEMA_CSV_PATH", test_path)
    path2 = settings.get_ga4_schema_csv_path()
    assert str(path2) == test_path
