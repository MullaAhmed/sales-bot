from datetime import datetime, timezone
from qdrant_client import models
from app.dependencies import get_services
from app.vector.embeddings import EmbeddingService


class VectorStore:
    """Qdrant vector store with dense search."""

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
        Upsert documents with embeddings.
        Each doc: {id, text, title (optional)}
        """
        texts = [d["text"] for d in documents]
        embeddings = self.embeddings.embed(texts)
        now = datetime.now(timezone.utc).isoformat()

        points = [
            models.PointStruct(
                id=doc["id"],
                vector=emb,
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

    async def search(
        self,
        company_id: str,
        collection: str,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.0,
    ) -> list[dict]:
        """Dense vector search with optional score filtering."""
        query_embedding = await self.embeddings.embed_async([query])
        query_embedding = query_embedding[0]

        results = await self.client.query_points(
            collection_name=collection,
            query=query_embedding,
            query_filter=models.Filter(
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
            ),
            limit=limit,
            score_threshold=score_threshold if score_threshold > 0 else None,
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
