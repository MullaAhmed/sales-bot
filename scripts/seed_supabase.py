"""
Seed Supabase with company and products from products.json.
Run create_data.py first to generate the JSON files.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from app.config import get_settings

SCRIPTS_DIR = Path(__file__).parent
PRODUCTS_PATH = SCRIPTS_DIR / "products.json"
COMPANY_ID = "winston"
COMPANY_NAME = "Winston Electronics"


async def seed_company(conn: asyncpg.Connection):
    """Ensure company exists."""
    await conn.execute(
        """
        INSERT INTO companies (id, name) VALUES ($1, $2)
        ON CONFLICT (id) DO UPDATE SET name = $2
        """,
        COMPANY_ID, COMPANY_NAME
    )
    print(f"  Company '{COMPANY_NAME}' ensured")


async def seed_products(conn: asyncpg.Connection):
    """Seed products from products.json."""
    if not PRODUCTS_PATH.exists():
        print(f"  Error: {PRODUCTS_PATH} not found. Run create_data.py first.")
        return 0

    with open(PRODUCTS_PATH, encoding="utf-8") as f:
        products = json.load(f)

    print(f"  Seeding {len(products)} products...")

    inserted = 0
    for prod in products:
        try:
            await conn.execute(
                """
                INSERT INTO products (
                    company_id, handle, name, sku, description, short_description,
                    price, compare_at_price, stock, image_url, images, variants
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (company_id, handle) DO UPDATE SET
                    name = EXCLUDED.name,
                    sku = EXCLUDED.sku,
                    description = EXCLUDED.description,
                    short_description = EXCLUDED.short_description,
                    price = EXCLUDED.price,
                    compare_at_price = EXCLUDED.compare_at_price,
                    stock = EXCLUDED.stock,
                    image_url = EXCLUDED.image_url,
                    images = EXCLUDED.images,
                    variants = EXCLUDED.variants
                """,
                COMPANY_ID,
                prod["handle"],
                prod["title"],
                prod["sku"],
                prod.get("description", "")[:2000],
                prod.get("short_description", ""),
                prod["price"],
                prod.get("compare_at_price"),
                prod.get("stock", 0),
                prod.get("image_url", ""),
                json.dumps(prod.get("images", [])),
                json.dumps(prod.get("variants", [])),
            )
            inserted += 1
        except Exception as e:
            print(f"    Error inserting {prod.get('handle')}: {e}")

    print(f"  Inserted/updated {inserted} products")
    return inserted


async def seed_sample_order(conn: asyncpg.Connection):
    """Seed a sample order for testing."""
    await conn.execute(
        """
        INSERT INTO orders (id, company_id, customer_email, status, total)
        VALUES ('22222222-2222-2222-2222-222222222222', $1, 'customer@example.com', 'shipped', 3799.00)
        ON CONFLICT (id) DO NOTHING
        """,
        COMPANY_ID
    )

    await conn.execute(
        """
        INSERT INTO shipments (order_id, carrier, tracking_number, status, estimated_delivery)
        VALUES ('22222222-2222-2222-2222-222222222222', 'BlueDart', 'BD123456789', 'in_transit', CURRENT_DATE + INTERVAL '3 days')
        ON CONFLICT DO NOTHING
        """
    )
    print("  Sample order created")


async def main():
    print("=" * 50)
    print("  SEED SUPABASE")
    print("=" * 50)

    settings = get_settings()

    print("\nConnecting to database...")
    conn = await asyncpg.connect(settings.database_url, statement_cache_size=0)

    try:
        print("\n--- Seeding Data ---")
        await seed_company(conn)
        await seed_products(conn)
        await seed_sample_order(conn)

        print("\n" + "=" * 50)
        print("  SEEDING COMPLETE")
        print("=" * 50)
        print("\nNext: python scripts/seed_qdrant.py")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
