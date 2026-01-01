import asyncio

from app.db import CompanyDB, TTLCache
from app.vector import VectorStore

class RAGService:
    """Retrieval-Augmented Generation for FAQ and policy documents."""

    def __init__(self, vector_store: VectorStore, db: CompanyDB):
        self.vector_store = vector_store
        self.db = db
        self._rag_cache = TTLCache(ttl=600)  # 1 minute cache

    async def ingest_documents(
        self,
        company_id: str,
        collection: str,
        documents: list[dict],
    ):
        """
        Ingest documents.
        Each doc: {id, text, title (optional), metadata (optional)}
        """
        # Save to Supabase (source of truth)
        for doc in documents:
            await self.db.upsert_document(
                company_id=company_id,
                collection=collection,
                doc_id=doc["id"],
                text=doc["text"],
                title=doc.get("title"),
                metadata=doc.get("metadata"),
            )

        # Save embeddings + text to Qdrant
        await self.vector_store.upsert(
            company_id=company_id,
            collection=collection,
            documents=documents,
        )

    async def retrieve(
        self,
        company_id: str,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.35,
    ) -> list[dict]:
        """Retrieve relevant documents for a query with caching."""
        # Normalize query for cache key (lowercase, first 100 chars)
        cache_key = f"{company_id}:{query.lower().strip()[:100]}"

        # Check cache
        cached = self._rag_cache.get(cache_key)
        if cached is not None:
            return cached

        document_results = asyncio.create_task(self.vector_store.search(
            company_id=company_id,
            collection="documents",
            query=query,
            limit=limit,
            score_threshold=score_threshold,
        ))
        product_results = asyncio.create_task(self.vector_store.search(
            company_id=company_id,
            collection="products",
            query=query,
            limit=limit,
            score_threshold=score_threshold,
        ))
        results = asyncio.gather(document_results, product_results)
        results = await results
        results = results[0] + results[1]
        # Cache results
        self._rag_cache.set(cache_key, results)

        return results

    def format_context(self, results: list[dict]) -> str:
        """Format retrieved documents as context for the LLM."""
        if not results:
            return ""

        parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Document")
            text = r.get("text", "")
            parts.append(f"[{i}] {title}\n{text}")

        return "\n\n".join(parts)
