import asyncpg
from app.dependencies import get_services


def get_pool() -> asyncpg.Pool:
    """Get the singleton database pool."""
    return get_services().db_pool
