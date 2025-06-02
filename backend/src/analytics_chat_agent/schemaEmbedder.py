import os
from typing import Dict, List

from dotenv import load_dotenv
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


def register_documents_to_qdrant(
    collection_name: str, texts: List[str], metadatas: List[Dict]
) -> Qdrant:
    """テキストとメタデータをQdrantベクトルデータベースに登録します。

    Args:
        collection_name (str): Qdrantのコレクション名。
        texts (List[str]): 登録するテキストのリスト。
        metadatas (List[Dict]): 各テキストに対応するメタデータのリスト。

    Returns:
        Qdrant: 初期化されたQdrantインスタンス。

    Raises:
        EnvironmentError: OPENAI_API_KEYが.envに設定されていない場合。
        ValueError: textsとmetadatasの長さが一致しない場合。

    Note:
        - .envファイルからOPENAI_API_KEYを読み込みます。
        - OpenAIEmbeddingsを使用してテキストをベクトル化します。
        - ベクトル化されたデータはQdrant（http://localhost:6333）に保存されます。
    """
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEYが.envに設定されていません")

    if len(texts) != len(metadatas):
        raise ValueError("textsとmetadatasの長さが一致しません")

    documents = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(texts, metadatas)
    ]
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

    vectordb = Qdrant.from_documents(
        documents,
        embeddings,
        url="http://localhost:6333",
        collection_name=collection_name,
        prefer_grpc=False,
    )
    return vectordb
