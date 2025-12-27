from app.dependencies import get_services


class EmbeddingService:
    """Generates dense embeddings using FastEmbed."""

    def __init__(self):
        self.model = get_services().embedding_model

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = list(self.model.embed(texts))
        return [e.tolist() for e in embeddings]
