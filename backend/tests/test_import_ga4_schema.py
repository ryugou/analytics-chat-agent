import types
import pytest
from pathlib import Path
import numpy as np
from typer.testing import CliRunner
from analytics_chat_agent.cli.main import cli
from analytics_chat_agent.config.settings import get_ga4_schema_csv_path

runner = CliRunner()

def test_import_schema_file_not_found(monkeypatch):
    non_existent_path = Path("non_existent_file.csv")
    monkeypatch.setattr(
        "analytics_chat_agent.config.settings.get_ga4_schema_csv_path",
        lambda: non_existent_path
    )
    monkeypatch.setattr(Path, "exists", lambda self: False)
    result = runner.invoke(cli)
    assert result.exit_code != 0
    assert "CSV file not found" in result.output or "CSVファイルが存在しない" in result.output

def test_import_schema_vector_size_none(monkeypatch, tmp_path):
    # ダミーCSVの作成
    csv_path = tmp_path / "ga4_schema.csv"
    csv_path.write_text(
        "id,name,field_type,description\n"
        "1,field1,STRING,desc1\n"
        "2,field2,INTEGER,desc2\n"
    )

    # モックの設定
    def mock_get_csv_path():
        return csv_path

    monkeypatch.setattr(
        "analytics_chat_agent.config.settings.get_ga4_schema_csv_path",
        mock_get_csv_path
    )
    monkeypatch.setattr(Path, "exists", lambda self: True)

    class DummyModel:
        def get_sentence_embedding_dimension(self):
            return None
        def encode(self, text):
            return np.array([0.1, 0.2, 0.3])

    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.SentenceTransformer",
        lambda name: DummyModel(),
    )

    class DummyQdrantClient:
        def __init__(self, url, api_key):
            pass
        def recreate_collection(self, **kwargs):
            pass
        def upsert(self, **kwargs):
            pass

    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.QdrantClient",
        DummyQdrantClient,
    )
    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.models.VectorParams",
        lambda size, distance: None,
    )
    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.models.Distance",
        types.SimpleNamespace(COSINE="cosine"),
    )
    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.models.PointStruct",
        lambda id, vector, payload: None,
    )

    result = runner.invoke(cli)
    assert result.exit_code != 0
    assert "モデルのベクトルサイズが不正です" in result.output

def test_import_schema_success(monkeypatch, tmp_path):
    # ダミーCSVの作成
    csv_path = tmp_path / "ga4_schema.csv"
    csv_path.write_text(
        "id,name,field_type,description\n"
        "1,field1,STRING,desc1\n"
        "2,field2,INTEGER,desc2\n"
    )

    # モックの設定
    def mock_get_csv_path():
        return csv_path

    monkeypatch.setattr(
        "analytics_chat_agent.config.settings.get_ga4_schema_csv_path",
        mock_get_csv_path
    )
    monkeypatch.setattr(Path, "exists", lambda self: True)

    class DummyModel:
        def get_sentence_embedding_dimension(self):
            return 3
        def encode(self, text):
            return np.array([0.1, 0.2, 0.3])

    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.SentenceTransformer",
        lambda name: DummyModel(),
    )

    class DummyQdrantClient:
        def __init__(self, url, api_key):
            pass
        def recreate_collection(self, **kwargs):
            pass
        def upsert(self, **kwargs):
            pass

    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.QdrantClient",
        DummyQdrantClient,
    )
    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.models.VectorParams",
        lambda size, distance: None,
    )
    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.models.Distance",
        types.SimpleNamespace(COSINE="cosine"),
    )
    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.models.PointStruct",
        lambda id, vector, payload: None,
    )

    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert "Imported 187 schemas to Qdrant." in result.output
