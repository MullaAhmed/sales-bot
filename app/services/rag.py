from app.db import CompanyDB
from app.vector import VectorStore


class RAGService:
    """Retrieval-Augmented Generation for FAQ and policy documents."""

    def __init__(self, vector_store: VectorStore, db: CompanyDB):
        self.vector_store = vector_store
        self.db = db

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
        limit: int = 3,
    ) -> list[dict]:
        """Retrieve relevant documents for a query."""
        return await self.vector_store.hybrid_search(
            company_id=company_id,
            collection="documents",
            query=query,
            limit=limit,
        )

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
