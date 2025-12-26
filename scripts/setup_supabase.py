"""Initial setup script for Supabase/PostgreSQL."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from app.config import get_settings


async def setup():
    settings = get_settings()

    print("Connecting to database...")
    conn = await asyncpg.connect(settings.database_url)

    try:
        print("Creating tables and indexes...")

        with open(Path(__file__).parent / "create_tables.sql") as f:
            sql = f.read()

        await conn.execute(sql)
        print("Done!")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(setup())
