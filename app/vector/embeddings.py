import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.dependencies import get_services


class EmbeddingService:
    """Generates dense embeddings using FastEmbed."""

    _executor = ThreadPoolExecutor(max_workers=2)

    def __init__(self):
        self.model = get_services().embedding_model

    def _embed_sync(self, texts: list[str]) -> list[list[float]]:
        """Synchronous embedding generation."""
        embeddings = list(self.model.embed(texts))
        return [e.tolist() for e in embeddings]

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts (sync)."""
        return self._embed_sync(texts)

    async def embed_async(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings asynchronously using thread executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._embed_sync,
            texts,
        )
