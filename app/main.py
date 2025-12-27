from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.api import router
from app.api.routes import init_services
from app.dependencies import get_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - initialize all singleton services
    services = get_services()
    await services.init()
    init_services()

    yield

    # Shutdown
    await services.close()


app = FastAPI(
    title="Sales Bot API",
    description="Multi-company chatbot with RAG and tool calling",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
