import pytest
import numpy as np
from pathlib import Path
from analytics_chat_agent.core.importer.import_ga4_schema import SchemaImporter

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

def test_import_schema_success(monkeypatch, dummy_csv):
    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.SentenceTransformer",
        lambda name: DummyModel(),
    )
    monkeypatch.setattr(
        "analytics_chat_agent.core.importer.import_ga4_schema.QdrantClient",
        DummyQdrantClient,
    )
    importer = SchemaImporter()
    count = importer.import_schema(dummy_csv)
    assert count == 2

def test_import_schema_file_not_found():
    importer = SchemaImporter()
    with pytest.raises(FileNotFoundError):
        importer.import_schema(Path("non_existent.csv"))

def test_schema_importer():
    importer = SchemaImporter()
    csv_path = Path("data/ga4_schema/ga4_schema.csv")
    count = importer.import_schema(csv_path)
    assert count > 0 