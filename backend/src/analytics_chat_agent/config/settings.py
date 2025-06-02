"""
Environment variable and configuration management.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the project root
env_path = Path(__file__).parents[3] / '.env'
load_dotenv(env_path)

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment variables."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in environment variables")
    return api_key

def get_qdrant_url() -> str:
    """Get Qdrant URL from environment variables."""
    return os.getenv('QDRANT_URL', 'http://localhost:6333')

def get_bigquery_credentials_path() -> str:
    """Get BigQuery credentials file path from environment variables."""
    return os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '') 