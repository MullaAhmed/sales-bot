from app.dependencies import get_services


class EmbeddingService:
    """Generates dense and sparse embeddings using FastEmbed."""

    def __init__(self):
        services = get_services()
        self.dense_model = services.dense_model
        self.sparse_model = services.sparse_model

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
