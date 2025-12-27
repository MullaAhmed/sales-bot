"""One-time setup script for Qdrant collections."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient, models
from app.config import get_settings


def setup():
    """Create Qdrant collections with indexes."""
    settings = get_settings()

    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    collections = ["documents", "products"]

    for name in collections:
        if client.collection_exists(name):
            print(f"Collection '{name}' already exists, skipping...")
            continue

        client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(
                size=384,  # all-MiniLM-L6-v2
                distance=models.Distance.COSINE,
            ),
        )
        print(f"Created collection '{name}'")

        # Create payload indexes for filtering
        client.create_payload_index(
            collection_name=name,
            field_name="company_id",
            field_schema=models.KeywordIndexParams(
                type=models.KeywordIndexType.KEYWORD,
                is_tenant=True,
            ),
        )
        client.create_payload_index(
            collection_name=name,
            field_name="is_active",
            field_schema=models.PayloadSchemaType.BOOL,
        )
        client.create_payload_index(
            collection_name=name,
            field_name="created_at",
            field_schema=models.PayloadSchemaType.DATETIME,
        )
        client.create_payload_index(
            collection_name=name,
            field_name="updated_at",
            field_schema=models.PayloadSchemaType.DATETIME,
        )
        print(f"Created indexes for '{name}'")

    print("Qdrant setup complete!")


if __name__ == "__main__":
    setup()
