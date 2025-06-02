import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


def register_documents_to_qdrant(collection_name: str, texts: List[str], metadatas: List[Dict]) -> Qdrant:
    """
    .envからOPENAI_API_KEYを読み込み、OpenAIEmbeddingsでベクトル化し、
    Qdrant(http://localhost:6333)にcollection_nameで登録する
    :param collection_name: コレクション名
    :param texts: テキストのリスト
    :param metadatas: メタデータのリスト（各要素はdict）
    :return: Qdrantインスタンス
    """
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEYが.envに設定されていません")

    if len(texts) != len(metadatas):
        raise ValueError("textsとmetadatasの長さが一致しません")

    documents = [Document(page_content=text, metadata=meta) for text, meta in zip(texts, metadatas)]
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

    vectordb = Qdrant.from_documents(
        documents,
        embeddings,
        url="http://localhost:6333",
        collection_name=collection_name,
        prefer_grpc=False,
    )
    return vectordb 