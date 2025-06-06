import csv
import uuid
from pathlib import Path
from typing import List

import typer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

app = typer.Typer()

# === Config ===
COLLECTION_NAME = "ga4_fields"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CSV_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data"
    / "ga4_schema"
    / "ga4_schema.csv"
)


@app.command()
def import_schema(
    qdrant_url: str = typer.Option(..., help="Qdrant URL"),
    qdrant_api_key: str = typer.Option(..., help="Qdrant API Key"),
) -> None:
    """GA4スキーマCSVをQdrantにインポート"""

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSVファイルが見つかりません: {CSV_PATH}")

    # モデルとQdrant接続
    model = SentenceTransformer(MODEL_NAME)
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    # get_sentence_embedding_dimension() の戻り値をチェック
    vector_size = model.get_sentence_embedding_dimension()
    if vector_size is None:
        raise ValueError("モデルのベクトル次元が取得できません")

    # Qdrantのコレクション初期化
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,  
            distance=Distance.COSINE,
        ),
    )
    # CSV読み込み & ベクトル化
    points: List[PointStruct] = []
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            full_text = (
                f"{row['description']} [{row['field_type']}] → {row['name']}"
            )
            vector = model.encode(full_text).tolist()
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "id": row["id"],
                        "name": row["name"],
                        "type": row["field_type"],
                        "description": row["description"],
                        "full_text": full_text,
                    },
                )
            )

    # アップロード
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ {len(points)} 件のスキーマをQdrantに登録しました")
