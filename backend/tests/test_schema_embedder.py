"""
Tests for the embedder module.
"""
import pytest
from unittest.mock import patch, MagicMock
from analytics_chat_agent.schema.embedder import register_documents_to_qdrant


@pytest.fixture(autouse=True)
def mock_env():
    """Mock environment variables for all tests."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'dummy-key'}):
        yield


@pytest.fixture
def mock_qdrant():
    """Mock Qdrant instance."""
    with patch('analytics_chat_agent.schema.embedder.Qdrant') as mock:
        mock.from_documents.return_value = MagicMock()
        yield mock


def test_mismatched_lengths():
    """Test that ValueError is raised when texts and metadatas lengths don't match."""
    with pytest.raises(ValueError):
        register_documents_to_qdrant("test", ["text1"], [{"meta": 1}, {"meta": 2}])


def test_successful_registration(mock_qdrant):
    """Test successful document registration."""
    texts = ["test document"]
    metadatas = [{"source": "test"}]
    
    result = register_documents_to_qdrant("test", texts, metadatas)
    
    assert result is not None
    mock_qdrant.from_documents.assert_called_once() 