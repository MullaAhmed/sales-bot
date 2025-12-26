from fastembed import TextEmbedding, SparseTextEmbedding
from app.config import get_settings


class EmbeddingService:
    """Generates dense and sparse embeddings using FastEmbed."""

    def __init__(self):
        settings = get_settings()
        self.dense_model = TextEmbedding(model_name=settings.dense_model)
        self.sparse_model = SparseTextEmbedding(model_name=settings.sparse_model)

    def embed_dense(self, texts: list[str]) -> list[list[float]]:
        embeddings = list(self.dense_model.embed(texts))
        return [e.tolist() for e in embeddings]

    def embed_sparse(self, texts: list[str]) -> list[dict]:
        embeddings = list(self.sparse_model.embed(texts))
        return [
            {"indices": e.indices.tolist(), "values": e.values.tolist()}
            for e in embeddings
        ]

    def embed_hybrid(self, texts: list[str]) -> list[dict]:
        dense = self.embed_dense(texts)
        sparse = self.embed_sparse(texts)
        return [
            {"dense": d, "sparse": s}
            for d, s in zip(dense, sparse)
        ]
