import typer
import csv
import uuid
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer
import analytics_chat_agent.config.settings as settings

app = typer.Typer(help="GA4スキーマ関連コマンド")

@app.command("run")
def import_schema():
    """GA4スキーマCSVをQdrantにインポート"""

    csv_path = settings.get_ga4_schema_csv_path()
    if not csv_path.exists():
        print(f"CSVファイルが見つかりません: {csv_path}")
        raise typer.Exit(1)

    model = SentenceTransformer(settings.GA4_SCHEMA_MODEL_NAME)
    client = QdrantClient(
        url=settings.get_qdrant_url(),
        api_key=settings.get_qdrant_api_key()
    )

    vector_size = model.get_sentence_embedding_dimension()
    if vector_size is None:
        print("モデルのベクトル次元が取得できません")
        raise typer.Exit(1)

    client.recreate_collection(
        collection_name=settings.GA4_SCHEMA_COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    points: List[PointStruct] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            full_text = f"{row['description']} [{row['field_type']}] → {row['name']}"
            vector = model.encode(full_text).tolist()
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["field_type"],
                    "description": row["description"],
                    "full_text": full_text,
                },
            ))

    client.upsert(collection_name=settings.GA4_SCHEMA_COLLECTION_NAME, points=points)
    print(f"✅ {len(points)} 件のスキーマをQdrantに登録しました")
