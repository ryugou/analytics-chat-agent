import types
import pytest
from pathlib import Path

import numpy as np
from typer.testing import CliRunner
from analytics_chat_agent.config.settings import get_ga4_schema_csv_path

from analytics_chat_agent.cli.commands.import_ga4_schema import app

runner = CliRunner()


def test_import_schema_file_not_found(monkeypatch):
    # 存在しないパスを強制する
    non_existent_path = Path("non_existent_file.csv")
    monkeypatch.setattr(
        "analytics_chat_agent.config.settings.get_ga4_schema_csv_path",
        lambda: non_existent_path
    )
    # Path.exists()をモック
    monkeypatch.setattr(Path, "exists", lambda self: False)
    
    result = runner.invoke(app, catch_exceptions=False)
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)


def test_import_schema_vector_size_none(monkeypatch, tmp_path):
    # ダミーCSV作成
    csv_path = tmp_path / "ga4_schema.csv"
    csv_path.write_text(
        "id,name,field_type,description\n"
        "1,field1,STRING,desc1\n"
        "2,field2,INTEGER,desc2\n"
    )
    # CSV_PATHを差し替え
    monkeypatch.setattr(
        "analytics_chat_agent.config.settings.get_ga4_schema_csv_path",
        lambda: csv_path
    )
    # Path.exists()をモック
    monkeypatch.setattr(Path, "exists", lambda self: True)

    # モデルのモック
    class DummyModel:
        def get_sentence_embedding_dimension(self):
            return None

        def encode(self, text):
            return np.array([0.1, 0.2, 0.3])

    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.SentenceTransformer",
        lambda name: DummyModel(),
    )

    # QdrantClientのモック
    class DummyQdrantClient:
        def __init__(self, url, api_key):
            pass

        def recreate_collection(self, **kwargs):
            pass

        def upsert(self, **kwargs):
            pass

    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.QdrantClient",
        DummyQdrantClient,
    )
    # VectorParams, Distance, PointStructのモック
    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.VectorParams",
        lambda size, distance: None,
    )
    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.Distance",
        types.SimpleNamespace(COSINE="cosine"),
    )
    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.PointStruct",
        lambda id, vector, payload: None,
    )

    result = runner.invoke(app, catch_exceptions=False)
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)


def test_import_schema_success(monkeypatch, tmp_path):
    # ダミーCSV作成
    csv_path = tmp_path / "ga4_schema.csv"
    csv_path.write_text(
        "id,name,field_type,description\n"
        "1,field1,STRING,desc1\n"
        "2,field2,INTEGER,desc2\n"
    )
    # CSV_PATHを差し替え
    monkeypatch.setattr(
        "analytics_chat_agent.config.settings.get_ga4_schema_csv_path",
        lambda: csv_path
    )
    # Path.exists()をモック
    monkeypatch.setattr(Path, "exists", lambda self: True)

    # モデルのモック
    class DummyModel:
        def get_sentence_embedding_dimension(self):
            return 3

        def encode(self, text):
            return np.array([0.1, 0.2, 0.3])

    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.SentenceTransformer",
        lambda name: DummyModel(),
    )

    # QdrantClientのモック
    class DummyQdrantClient:
        def __init__(self, url, api_key):
            pass

        def recreate_collection(self, **kwargs):
            pass

        def upsert(self, **kwargs):
            pass

    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.QdrantClient",
        DummyQdrantClient,
    )
    # VectorParams, Distance, PointStructのモック
    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.VectorParams",
        lambda size, distance: None,
    )
    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.Distance",
        types.SimpleNamespace(COSINE="cosine"),
    )
    monkeypatch.setattr(
        "analytics_chat_agent.cli.commands.import_ga4_schema.PointStruct",
        lambda id, vector, payload: None,
    )

    result = runner.invoke(app, catch_exceptions=False)
    assert result.exit_code == 0
    assert "スキーマをQdrantに登録しました" in result.output
