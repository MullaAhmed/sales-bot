from datetime import datetime, timezone
from qdrant_client import models
from app.dependencies import get_services
from app.vector.embeddings import EmbeddingService


class VectorStore:
    """Qdrant vector store with hybrid search support."""

    def __init__(self):
        self.client = get_services().qdrant
        self.embeddings = EmbeddingService()

    async def upsert(
        self,
        company_id: str,
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
                    "company_id": company_id,
                    "title": doc.get("title", ""),
                    "text": doc["text"],
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            for doc, emb in zip(documents, embeddings)
        ]

        await self.client.upsert(collection_name=collection, points=points)

    async def hybrid_search(
        self,
        company_id: str,
        collection: str,
        query: str,
        limit: int = 5,
    ) -> list[dict]:
        """Hybrid search using RRF fusion of dense and sparse results."""
        dense = self.embeddings.embed_dense([query])[0]
        sparse = self.embeddings.embed_sparse([query])[0]

        company_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="company_id",
                    match=models.MatchValue(value=company_id),
                ),
                models.FieldCondition(
                    key="is_active",
                    match=models.MatchValue(value=True),
                ),
            ]
        )

        results = await self.client.query_points(
            collection_name=collection,
            prefetch=[
                models.Prefetch(
                    query=dense,
                    using="dense",
                    limit=limit * 2,
                    filter=company_filter,
                ),
                models.Prefetch(
                    query=models.SparseVector(**sparse),
                    using="sparse",
                    limit=limit * 2,
                    filter=company_filter,
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
        await self.client.set_payload(
            collection_name=collection,
            payload={"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()},
            points=[doc_id],
        )
