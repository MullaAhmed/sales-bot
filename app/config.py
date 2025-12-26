from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database (Supabase PostgreSQL - use direct connection port 5432)
    database_url: str = "postgresql://user:pass@db.supabase.co:5432/postgres"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Embedding models (FastEmbed)
    dense_model: str = "jinaai/jina-embeddings-v2-base-en"
    sparse_model: str = "Qdrant/bm42-all-minilm-l6-v2-attentions"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
