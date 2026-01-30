# Sales Bot

Multi-company customer support chatbot with RAG and tool calling.

## Features

- **Multi-company**: Single deployment serves multiple companies
- **RAG**: Dense vector search for FAQ/policy documents
- **Tool Calling**: Product details lookup
- **Conversation History**: Backend-managed chat sessions
- **Priority Flow**: High → Medium → Low query handling

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Vector Store**: Qdrant
- **Embeddings**: FastEmbed (all-MiniLM-L6-v2)
- **Database**: Supabase/PostgreSQL (asyncpg)
- **LLM**: OpenAI gpt-5-nano

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
uv run python app/main.py
```

Server runs at `http://localhost:8000`

## Project Structure

```
sales-bot/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── dependencies.py      # Dependency injection
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── schemas.py       # Request/response models
│   ├── db/
│   │   ├── postgres.py      # Connection pool
│   │   ├── repository.py    # Database operations
│   │   └── cache.py         # Caching layer
│   ├── vector/
│   │   ├── qdrant.py        # Vector store
│   │   ├── embeddings.py    # FastEmbed
│   │   └── chunker.py       # Document chunking
│   └── services/
│       ├── chatbot.py       # Chat logic + priority flow
│       ├── rag.py           # Document retrieval
│       └── tools.py         # Tool definitions
├── scripts/
│   ├── create_tables.sql    # Database schema
│   ├── seed_data.sql        # Seed data
│   ├── setup_supabase.py    # DB setup script
│   ├── setup_qdrant.py      # Vector store setup
│   ├── seed_supabase.py     # Seed database
│   ├── seed_qdrant.py       # Seed vector store
│   ├── reset_db.py          # Reset database
│   └── create_data.py       # Generate test data
├── frontend/                 # Frontend application
├── docs/
│   └── API.md               # API documentation
├── .env.example
├── pyproject.toml
└── README.md
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Supabase PostgreSQL connection string (pooler, port 5432) |
| `QDRANT_URL` | Qdrant server URL |
| `QDRANT_API_KEY` | Qdrant API key (optional for local) |
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | Model name (default: gpt-5-nano) |

## Adding a New Tenant

1. Insert company into Supabase:
```sql
INSERT INTO companies (id, name) VALUES ('company-slug', 'Company Name');
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
