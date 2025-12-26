from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import router
from app.db import close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await close_pool()


app = FastAPI(
    title="Sales Bot API",
    description="Multi-tenant chatbot with RAG and tool calling",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
