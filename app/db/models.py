import json
import time
from typing import Any

from asyncpg import Pool


class TTLCache:
    """Simple in-memory cache with TTL."""

    def __init__(self, ttl: int = 300):
        self._cache: dict[str, tuple[float, Any]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Any | None:
        if key in self._cache:
            expires_at, value = self._cache[key]
            if time.time() < expires_at:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        self._cache[key] = (time.time() + self._ttl, value)


class CompanyDB:
    """Database operations for company data."""

    def __init__(self, pool: Pool):
        self.pool = pool
        self._company_cache = TTLCache(ttl=300)  # 5 min cache

    async def get_company(self, company_id: str) -> dict | None:
        # Check cache first
        cached = self._company_cache.get(company_id)
        if cached is not None:
            return cached

        row = await self.pool.fetchrow(
            "SELECT * FROM companies WHERE id = $1", company_id
        )
        company = dict(row) if row else None

        if company:
            self._company_cache.set(company_id, company)

        return company

    async def get_product(self, company_id: str, product_id: str) -> dict | None:
        row = await self.pool.fetchrow(
            """SELECT * FROM products
               WHERE company_id = $1 AND id = $2""",
            company_id, product_id
        )
        return dict(row) if row else None

    async def search_products(self, company_id: str, query: str) -> list[dict]:
        rows = await self.pool.fetch(
            """SELECT * FROM products
               WHERE company_id = $1
               AND (name ILIKE $2 OR sku ILIKE $2)
               LIMIT 10""",
            company_id, f"%{query}%"
        )
        return [dict(r) for r in rows]

    async def get_order(self, company_id: str, order_id: str) -> dict | None:
        row = await self.pool.fetchrow(
            """SELECT o.*,
                      s.carrier, s.tracking_number, s.status as shipping_status,
                      s.estimated_delivery
               FROM orders o
               LEFT JOIN shipments s ON s.order_id = o.id
               WHERE o.company_id = $1 AND o.id = $2""",
            company_id, order_id
        )
        return dict(row) if row else None

    async def get_order_by_tracking(self, company_id: str, tracking: str) -> dict | None:
        row = await self.pool.fetchrow(
            """SELECT o.*,
                      s.carrier, s.tracking_number, s.status as shipping_status,
                      s.estimated_delivery
               FROM orders o
               JOIN shipments s ON s.order_id = o.id
               WHERE o.company_id = $1 AND s.tracking_number = $2""",
            company_id, tracking
        )
        return dict(row) if row else None

    async def log_support_ticket(
        self, company_id: str, customer_email: str, subject: str, message: str
    ) -> str:
        ticket_id = await self.pool.fetchval(
            """INSERT INTO support_tickets (company_id, customer_email, subject, message)
               VALUES ($1, $2, $3, $4)
               RETURNING id""",
            company_id, customer_email, subject, message
        )
        return str(ticket_id)

    # Conversation methods

    async def create_conversation(self, company_id: str, customer_id: str | None = None) -> str:
        conv_id = await self.pool.fetchval(
            """INSERT INTO conversations (company_id, customer_id)
               VALUES ($1, $2)
               RETURNING id""",
            company_id, customer_id
        )
        return str(conv_id)

    async def get_conversation(self, conversation_id: str) -> dict | None:
        row = await self.pool.fetchrow(
            "SELECT * FROM conversations WHERE id = $1", conversation_id
        )
        return dict(row) if row else None

    async def get_messages(self, conversation_id: str, limit: int = 50) -> list[dict]:
        rows = await self.pool.fetch(
            """SELECT role, content FROM (
                   SELECT role, content, created_at FROM messages
                   WHERE conversation_id = $1
                   ORDER BY created_at DESC
                   LIMIT $2
               ) sub ORDER BY created_at ASC""",
            conversation_id, limit
        )
        return [{"role": r["role"], "content": r["content"]} for r in rows]

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: list | None = None,
        sources: list | None = None,
    ) -> str:
        msg_id = await self.pool.fetchval(
            """INSERT INTO messages (conversation_id, role, content, tool_calls, sources)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING id""",
            conversation_id,
            role,
            content,
            json.dumps(tool_calls) if tool_calls else None,
            json.dumps(sources) if sources else None,
        )
        # Update conversation timestamp
        await self.pool.execute(
            "UPDATE conversations SET updated_at = NOW() WHERE id = $1",
            conversation_id
        )
        return str(msg_id)

    # Document methods

    async def upsert_document(
        self,
        company_id: str,
        collection: str,
        doc_id: str,
        text: str,
        title: str | None = None,
        metadata: dict | None = None,
    ):
        await self.pool.execute(
            """INSERT INTO documents (id, company_id, collection, title, text, metadata)
               VALUES ($1, $2, $3, $4, $5, $6)
               ON CONFLICT (id) DO UPDATE SET
                   text = EXCLUDED.text,
                   title = EXCLUDED.title,
                   metadata = EXCLUDED.metadata,
                   updated_at = NOW()""",
            doc_id,
            company_id,
            collection,
            title,
            text,
            json.dumps(metadata) if metadata else None,
        )

    async def get_documents_by_ids(self, doc_ids: list[str]) -> dict[str, dict]:
        rows = await self.pool.fetch(
            """SELECT id, title, text, metadata FROM documents
               WHERE id = ANY($1) AND is_active = TRUE""",
            doc_ids,
        )
        return {
            r["id"]: {
                "title": r["title"],
                "text": r["text"],
                "metadata": json.loads(r["metadata"]) if r["metadata"] else {},
            }
            for r in rows
        }
