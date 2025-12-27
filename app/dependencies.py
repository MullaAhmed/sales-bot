"""Singleton services - initialized once at startup."""

import asyncpg
from qdrant_client import AsyncQdrantClient
from fastembed import TextEmbedding

from app.config import get_settings


class Services:
    """Container for singleton services."""

    _instance: "Services | None" = None

    def __init__(self):
        self.db_pool: asyncpg.Pool | None = None
        self.qdrant: AsyncQdrantClient | None = None
        self.embedding_model: TextEmbedding | None = None

    @classmethod
    def get(cls) -> "Services":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def init(self):
        """Initialize all services. Call once at startup."""
        settings = get_settings()

        # Database pool
        # statement_cache_size=0 required for Supabase/pgbouncer compatibility
        print("Initializing database pool...")
        self.db_pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=2,
            max_size=10,
            statement_cache_size=0,
        )

        # Qdrant async client
        print("Initializing Qdrant client...")
        self.qdrant = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        # Embedding model (all-MiniLM-L6-v2 is small and fast)
        print("Loading embedding model...")
        self.embedding_model = TextEmbedding(model_name=settings.embedding_model)

        print("All services initialized.")

    async def close(self):
        """Cleanup services. Call on shutdown."""
        if self.qdrant:
            await self.qdrant.close()
            self.qdrant = None
        if self.db_pool:
            await self.db_pool.close()
            self.db_pool = None


def get_services() -> Services:
    """Get the singleton services instance."""
    return Services.get()
