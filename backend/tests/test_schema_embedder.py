import pytest
from unittest.mock import patch
from schemaEmbedder import register_documents_to_qdrant


@pytest.fixture(autouse=True)
def mock_env():
    """Mock environment variables for all tests."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'dummy-key'}):
        yield


def test_mismatched_lengths():
    """Test that ValueError is raised when texts and metadatas lengths don't match."""
    with pytest.raises(ValueError):
        register_documents_to_qdrant("test", ["text1"], [{"meta": 1}, {"meta": 2}]) 