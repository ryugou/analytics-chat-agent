import types
import pytest
from typer.testing import CliRunner
from analytics_chat_agent.cli.import_ga4_schema import app
from pathlib import Path
import numpy as np

runner = CliRunner()

def test_import_schema_file_not_found(monkeypatch):
    # 存在しないパスを強制する
    monkeypatch.setattr(
        "analytics_chat_agent.cli.import_ga4_schema.CSV_PATH",
        Path("non_existent_file.csv")
    )
    result = runner.invoke(app, ["--qdrant-url", "http://localhost:6333", "--qdrant-api-key", "dummy"])
    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
    assert "CSVファイルが見つかりません: non_existent_file.csv" in str(result.exception)

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
        "analytics_chat_agent.cli.import_ga4_schema.CSV_PATH",
        csv_path
    )
    # モデルのモック
    class DummyModel:
        def get_sentence_embedding_dimension(self):
            return None
        def encode(self, text):
            return np.array([0.1, 0.2, 0.3])
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.SentenceTransformer", lambda name: DummyModel())
    # QdrantClientのモック
    class DummyQdrantClient:
        def __init__(self, url, api_key): pass
        def recreate_collection(self, **kwargs): pass
        def upsert(self, **kwargs): pass
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.QdrantClient", DummyQdrantClient)
    # VectorParams, Distance, PointStructのモック
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.VectorParams", lambda size, distance: None)
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.Distance", types.SimpleNamespace(COSINE="cosine"))
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.PointStruct", lambda id, vector, payload: None)

    result = runner.invoke(app, ["--qdrant-url", "http://localhost:6333", "--qdrant-api-key", "dummy"])
    assert result.exit_code != 0
    assert isinstance(result.exception, ValueError)
    assert "モデルのベクトル次元が取得できません" in str(result.exception)

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
        "analytics_chat_agent.cli.import_ga4_schema.CSV_PATH",
        csv_path
    )
    # モデルのモック
    class DummyModel:
        def get_sentence_embedding_dimension(self):
            return 3
        def encode(self, text):
            return np.array([0.1, 0.2, 0.3])
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.SentenceTransformer", lambda name: DummyModel())
    # QdrantClientのモック
    class DummyQdrantClient:
        def __init__(self, url, api_key): pass
        def recreate_collection(self, **kwargs): pass
        def upsert(self, **kwargs): pass
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.QdrantClient", DummyQdrantClient)
    # VectorParams, Distance, PointStructのモック
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.VectorParams", lambda size, distance: None)
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.Distance", types.SimpleNamespace(COSINE="cosine"))
    monkeypatch.setattr("analytics_chat_agent.cli.import_ga4_schema.PointStruct", lambda id, vector, payload: None)

    result = runner.invoke(app, ["--qdrant-url", "http://localhost:6333", "--qdrant-api-key", "dummy"])
    assert result.exit_code == 0
    assert "スキーマをQdrantに登録しました" in result.output 