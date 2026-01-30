"""
Seed Qdrant with products and documents from JSON files.
Run create_data.py first to generate the JSON files.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

SCRIPTS_DIR = Path(__file__).parent
PRODUCTS_PATH = SCRIPTS_DIR / "products.json"
DOCUMENTS_PATH = SCRIPTS_DIR / "documents.json"
API_BASE_URL = "http://localhost:8000/api"
COMPANY_ID = "winston"


async def check_health(client: httpx.AsyncClient) -> bool:
    """Check if API is running."""
    try:
        response = await client.get(f"{API_BASE_URL}/health")
        return response.status_code == 200
    except httpx.ConnectError:
        return False


async def seed_products(client: httpx.AsyncClient) -> bool:
    """Ingest products from products.json."""
    if not PRODUCTS_PATH.exists():
        print(f"  Error: {PRODUCTS_PATH} not found. Run create_data.py first.")
        return False

    with open(PRODUCTS_PATH, encoding="utf-8") as f:
        products = json.load(f)

    # Transform to Qdrant format: {id, text, title, metadata}
    documents = [
        {
            "id": p["id"],
            "title": p["title"],
            "text": p["text"],
            "metadata": {
                "product_id": p["id"],
                "handle": p.get("handle"),
                "sku": p.get("sku"),
                "price": p.get("price"),
                "image_url": p.get("image_url"),
            },
        }
        for p in products
    ]

    print(f"Ingesting {len(documents)} products...")

    response = await client.post(
        f"{API_BASE_URL}/ingest/products",
        json={"company_id": COMPANY_ID, "documents": documents},
    )

    if response.status_code == 200:
        result = response.json()
        print(f"  Success: {result['count']} products ingested")
        return True
    else:
        print(f"  Error: {response.status_code} - {response.text}")
        return False


async def seed_documents(client: httpx.AsyncClient) -> bool:
    """Ingest documents from documents.json."""
    if not DOCUMENTS_PATH.exists():
        print(f"  Error: {DOCUMENTS_PATH} not found. Run create_data.py first.")
        return False

    with open(DOCUMENTS_PATH, encoding="utf-8") as f:
        documents = json.load(f)

    print(f"Ingesting {len(documents)} documents...")

    response = await client.post(
        f"{API_BASE_URL}/ingest/documents",
        json={"company_id": COMPANY_ID, "documents": documents},
    )

    if response.status_code == 200:
        result = response.json()
        print(f"  Success: {result['count']} documents ingested")
        return True
    else:
        print(f"  Error: {response.status_code} - {response.text}")
        return False


async def main():
    print("=" * 50)
    print("  SEED QDRANT")
    print("=" * 50)
    print(f"\nCompany ID: {COMPANY_ID}")
    print("-" * 40)

    async with httpx.AsyncClient(timeout=120.0) as client:
        print("Checking API health...")
        if not await check_health(client):
            print("Error: API is not running. Start the server first:")
            print("  uvicorn app.main:app --reload")
            return

        print("  API is healthy\n")

        products_ok = await seed_products(client)
        documents_ok = await seed_documents(client)

        print()
        if products_ok and documents_ok:
            print("Seeding completed successfully!")
        else:
            print("Seeding completed with errors.")


if __name__ == "__main__":
    asyncio.run(main())
