from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os
load_dotenv(override=True)


class Settings(BaseSettings):
    # Database (Supabase PostgreSQL - use direct connection port 5432)
    database_url: str = os.getenv("DATABASE_URL")

    # Qdrant
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: str | None = os.getenv("QDRANT_API_KEY")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    # Embedding models (FastEmbed)
    dense_model: str = "jinaai/jina-embeddings-v2-base-en"
    sparse_model: str = "Qdrant/bm42-all-minilm-l6-v2-attentions"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
