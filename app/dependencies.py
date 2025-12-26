"""Singleton services - initialized once at startup."""

import asyncpg
from qdrant_client import AsyncQdrantClient
from fastembed import TextEmbedding, SparseTextEmbedding

from app.config import get_settings


class Services:
    """Container for singleton services."""

    _instance: "Services | None" = None

    def __init__(self):
        self.db_pool: asyncpg.Pool | None = None
        self.qdrant: AsyncQdrantClient | None = None
        self.dense_model: TextEmbedding | None = None
        self.sparse_model: SparseTextEmbedding | None = None

    @classmethod
    def get(cls) -> "Services":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def init(self):
        """Initialize all services. Call once at startup."""
        settings = get_settings()

        # Database pool
        print("Initializing database pool...")
        self.db_pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=2,
            max_size=10,
        )

        # Qdrant async client
        print("Initializing Qdrant client...")
        self.qdrant = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        # Embedding models (slow - loads on first use)
        print("Loading embedding models...")
        self.dense_model = TextEmbedding(model_name=settings.dense_model)
        self.sparse_model = SparseTextEmbedding(model_name=settings.sparse_model)

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
