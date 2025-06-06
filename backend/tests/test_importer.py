import pytest
import numpy as np
from pathlib import Path
from analytics_chat_agent.core.schema.importer import SchemaImporter

class DummyModel:
    def get_sentence_embedding_dimension(self):
        return 3
    def encode(self, text):
        return np.array([0.1, 0.2, 0.3])

class DummyQdrantClient:
    def __init__(self, url, api_key):
        self.recreated = False
        self.upserted = False
    def recreate_collection(self, **kwargs):
        self.recreated = True
    def upsert(self, **kwargs):
        self.upserted = True

@pytest.fixture
def dummy_csv(tmp_path):
    csv_path = tmp_path / "ga4_schema.csv"
    csv_path.write_text(
        "id,name,field_type,description\n"
        "1,field1,STRING,desc1\n"
        "2,field2,INTEGER,desc2\n"
    )
    return csv_path

def test_import_from_csv_success(monkeypatch, dummy_csv):
    monkeypatch.setattr(
        "analytics_chat_agent.core.schema.importer.SentenceTransformer",
        lambda name: DummyModel(),
    )
    monkeypatch.setattr(
        "analytics_chat_agent.core.schema.importer.QdrantClient",
        DummyQdrantClient,
    )
    importer = SchemaImporter()
    count = importer.import_from_csv(dummy_csv)
    assert count == 2

def test_import_from_csv_file_not_found():
    importer = SchemaImporter()
    with pytest.raises(FileNotFoundError):
        importer.import_from_csv(Path("non_existent.csv")) 