from datetime import datetime, timezone
from qdrant_client import QdrantClient, models
from app.config import get_settings
from app.vector.embeddings import EmbeddingService


class VectorStore:
    """Qdrant vector store with hybrid search support."""

    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.embeddings = EmbeddingService()

    async def upsert(
        self,
        tenant_id: str,
        collection: str,
        documents: list[dict],
    ):
        """
        Upsert documents with hybrid embeddings.
        Each doc: {id, text, title (optional)}
        Text is stored in Supabase, only metadata in Qdrant.
        """
        texts = [d["text"] for d in documents]
        embeddings = self.embeddings.embed_hybrid(texts)
        now = datetime.now(timezone.utc).isoformat()

        points = [
            models.PointStruct(
                id=doc["id"],
                vector={
                    "dense": emb["dense"],
                    "sparse": models.SparseVector(**emb["sparse"]),
                },
                payload={
                    "tenant_id": tenant_id,
                    "title": doc.get("title", ""),
                    "text": doc["text"],
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            for doc, emb in zip(documents, embeddings)
        ]

        self.client.upsert(collection_name=collection, points=points)

    async def hybrid_search(
        self,
        tenant_id: str,
        collection: str,
        query: str,
        limit: int = 5,
    ) -> list[dict]:
        """Hybrid search using RRF fusion of dense and sparse results."""
        dense = self.embeddings.embed_dense([query])[0]
        sparse = self.embeddings.embed_sparse([query])[0]

        tenant_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="tenant_id",
                    match=models.MatchValue(value=tenant_id),
                ),
                models.FieldCondition(
                    key="is_active",
                    match=models.MatchValue(value=True),
                ),
            ]
        )

        results = self.client.query_points(
            collection_name=collection,
            prefetch=[
                models.Prefetch(
                    query=dense,
                    using="dense",
                    limit=limit * 2,
                    filter=tenant_filter,
                ),
                models.Prefetch(
                    query=models.SparseVector(**sparse),
                    using="sparse",
                    limit=limit * 2,
                    filter=tenant_filter,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
        )

        return [
            {"id": p.id, "score": p.score, **p.payload}
            for p in results.points
        ]

    async def deactivate(self, collection: str, doc_id: str):
        """Soft delete by setting is_active to False."""
        self.client.set_payload(
            collection_name=collection,
            payload={"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()},
            points=[doc_id],
        )
