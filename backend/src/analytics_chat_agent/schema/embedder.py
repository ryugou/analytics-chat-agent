"""ドキュメントの埋め込みとベクトルストレージ機能を提供するモジュール。

このモジュールは、テキストドキュメントをベクトル化し、Qdrantベクトルデータベースに
保存するための機能を提供します。OpenAIの埋め込みモデルを使用してテキストをベクトル化し、
メタデータと共にQdrantに保存します。
"""
from typing import Dict, List

from langchain.schema import Document
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings

from ..config.settings import get_openai_api_key, get_qdrant_url


def register_documents_to_qdrant(
    collection_name: str, texts: List[str], metadatas: List[Dict]
) -> Qdrant:
    """ドキュメントをQdrantベクトルストアに登録します。

    Args:
        collection_name (str): ベクトルを保存するコレクション名。
        texts (List[str]): 登録するテキストドキュメントのリスト。
        metadatas (List[Dict]): 各ドキュメントに対応するメタデータの辞書のリスト。

    Returns:
        Qdrant: 初期化されたQdrantインスタンス。

    Raises:
        ValueError: textsとmetadatasの長さが一致しない場合。

    Note:
        - OpenAIの埋め込みモデルを使用してテキストをベクトル化します。
        - ベクトル化されたデータはQdrantに保存されます。
        - 各ドキュメントは、テキストコンテンツとメタデータのペアとして保存されます。
    """
    if len(texts) != len(metadatas):
        raise ValueError("Length of texts and metadatas must match")

    # Create documents
    documents = [
        Document(page_content=text, metadata=metadata)
        for text, metadata in zip(texts, metadatas)
    ]

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(api_key=get_openai_api_key())

    # Register documents in Qdrant
    qdrant = Qdrant.from_documents(
        documents=documents,
        embedding=embeddings,
        url=get_qdrant_url(),
        collection_name=collection_name,
        prefer_grpc=False,
    )

    return qdrant
