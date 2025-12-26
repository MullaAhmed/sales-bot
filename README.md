# Sales Bot

Multi-company customer support chatbot with RAG and tool calling.

## Features

- **Multi-company**: Single deployment serves multiple companies
- **RAG**: Hybrid search (dense + sparse) for FAQ/policy documents
- **Tool Calling**: Product search, order tracking, support ticket creation
- **Conversation History**: Backend-managed chat sessions
- **Priority Flow**: Urgent → High → Medium → Low query handling

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Vector Store**: Qdrant (hybrid search with RRF fusion)
- **Embeddings**: FastEmbed (Jina + BM42)
- **Database**: Supabase/PostgreSQL (asyncpg)
- **LLM**: OpenAI GPT-4o-mini

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Start Services

```bash
# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Or use Qdrant Cloud
```

### 4. Run Setup Scripts

```bash
# Create Supabase tables
uv run python scripts/setup_supabase.py

# Create Qdrant collections
uv run python scripts/setup_qdrant.py <company_id>
```

### 5. Start Server

```bash
uv run python main.py
```

Server runs at `http://localhost:8000`

## Project Structure

```
sales-bot/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── schemas.py       # Request/response models
│   ├── db/
│   │   ├── postgres.py      # Connection pool
│   │   └── models.py        # Database operations
│   ├── vector/
│   │   ├── qdrant.py        # Vector store
│   │   └── embeddings.py    # FastEmbed
│   └── services/
│       ├── chatbot.py       # Chat logic + priority flow
│       ├── rag.py           # Document retrieval
│       └── tools.py         # Tool definitions
├── scripts/
│   ├── create_tables.sql    # Database schema
│   ├── setup_supabase.py    # DB setup script
│   └── setup_qdrant.py      # Vector store setup
├── docs/
│   └── API.md               # API documentation
├── .env.example
├── pyproject.toml
└── README.md
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Supabase PostgreSQL connection string (use port 5432) |
| `QDRANT_URL` | Qdrant server URL |
| `QDRANT_API_KEY` | Qdrant API key (optional for local) |
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | Model name (default: gpt-4o-mini) |
| `DENSE_MODEL` | Dense embedding model |
| `SPARSE_MODEL` | Sparse embedding model |

## Adding a New Tenant

1. Insert company into Supabase:
```sql
INSERT INTO companys (id, name) VALUES ('uuid-here', 'Company Name');
```

2. Create Qdrant collections:
```bash
uv run python scripts/setup_qdrant.py <company_id>
```

3. Ingest documents via API:
```bash
curl -X POST http://localhost:8000/api/ingest/documents \
  -H "Content-Type: application/json" \
  -d '{"company_id": "uuid", "documents": [{"id": "1", "text": "...", "title": "FAQ"}]}'
```

## API Documentation

See [docs/API.md](docs/API.md) for full API reference.
