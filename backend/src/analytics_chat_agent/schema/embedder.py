"""
Document embedding and vector storage functionality.
"""
from typing import List, Dict
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from ..config.settings import get_openai_api_key, get_qdrant_url

def register_documents_to_qdrant(
    collection_name: str,
    texts: List[str],
    metadatas: List[Dict]
) -> Qdrant:
    """
    Register documents to Qdrant vector store.

    Args:
        collection_name: Name of the collection to store vectors
        texts: List of text documents
        metadatas: List of metadata dictionaries for each document

    Returns:
        Qdrant: Initialized Qdrant instance

    Raises:
        ValueError: If lengths of texts and metadatas don't match
    """
    if len(texts) != len(metadatas):
        raise ValueError("Length of texts and metadatas must match")

    # Create documents
    documents = [
        Document(page_content=text, metadata=metadata)
        for text, metadata in zip(texts, metadatas)
    ]

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        openai_api_key=get_openai_api_key()
    )

    # Register documents in Qdrant
    qdrant = Qdrant.from_documents(
        documents=documents,
        embedding=embeddings,
        url=get_qdrant_url(),
        collection_name=collection_name,
        prefer_grpc=False
    )

    return qdrant 