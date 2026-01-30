"""
Reset script - Deletes ALL data from Qdrant and Supabase.
Use with caution!
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from qdrant_client import AsyncQdrantClient
from app.config import get_settings


async def reset_qdrant(client: AsyncQdrantClient):
    """Delete all collections from Qdrant."""
    print("\n--- Qdrant ---")

    collections = await client.get_collections()
    collection_names = [c.name for c in collections.collections]

    if not collection_names:
        print("No collections found.")
        return

    print(f"Found collections: {collection_names}")

    for name in collection_names:
        await client.delete_collection(name)
        print(f"  Deleted collection: {name}")

    print("All Qdrant collections deleted.")


async def reset_supabase(pool: asyncpg.Pool):
    """Truncate all application tables in Supabase."""
    print("\n--- Supabase ---")

    # Order matters due to foreign key constraints
    tables = [
        "messages",
        "conversations",
        "support_tickets",
        "documents",
        "shipments",
        "orders",
        "products",
        "companies",
    ]

    for table in tables:
        try:
            result = await pool.execute(f"TRUNCATE TABLE {table} CASCADE")
            print(f"  Truncated: {table}")
        except Exception as e:
            print(f"  Skipped {table}: {e}")

    print("All Supabase tables truncated.")


async def main():
    settings = get_settings()

    print("=" * 50)
    print("  DATABASE RESET SCRIPT")
    print("=" * 50)
    print("\nThis will DELETE ALL DATA from:")
    print("  - Qdrant: All collections")
    print("  - Supabase: All table data")
    print("\nThis action is IRREVERSIBLE!")
    print()

    confirm = input("Type 'DELETE EVERYTHING' to confirm: ")
    if confirm != "DELETE EVERYTHING":
        print("Aborted.")
        return

    print("\nConnecting to services...")

    # Connect to Qdrant
    qdrant = AsyncQdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    # Connect to Supabase
    pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=1,
        max_size=2,
        statement_cache_size=0,
    )

    try:
        await reset_qdrant(qdrant)
        await reset_supabase(pool)
        print("\n" + "=" * 50)
        print("  RESET COMPLETE")
        print("=" * 50)
    finally:
        await qdrant.close()
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
