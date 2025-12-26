from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas import (
    ChatRequest, ChatResponse, ConversationResponse,
    IngestRequest, IngestResponse,
)
from app.db import get_pool, TenantDB
from app.vector import VectorStore
from app.services import RAGService, ToolService, ChatbotService

router = APIRouter()


async def get_services():
    """Dependency to get initialized services."""
    pool = await get_pool()
    db = TenantDB(pool)
    vector_store = VectorStore()
    rag = RAGService(vector_store, db)
    tools = ToolService(db)
    chatbot = ChatbotService(rag, tools, db)
    return {"db": db, "rag": rag, "chatbot": chatbot, "vector_store": vector_store}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, services: dict = Depends(get_services)):
    """Send a message to the chatbot."""
    db: TenantDB = services["db"]
    chatbot: ChatbotService = services["chatbot"]

    # Verify tenant exists
    tenant = await db.get_tenant(request.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get or create conversation
    conversation_id = request.conversation_id
    if conversation_id:
        conv = await db.get_conversation(conversation_id)
        if not conv or str(conv["tenant_id"]) != request.tenant_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation_id = await db.create_conversation(request.tenant_id)

    result = await chatbot.chat(
        tenant_id=request.tenant_id,
        company_name=tenant["name"],
        message=request.message,
        conversation_id=conversation_id,
    )

    return ChatResponse(conversation_id=conversation_id, **result)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, services: dict = Depends(get_services)):
    """Get conversation history."""
    db: TenantDB = services["db"]

    conv = await db.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await db.get_messages(conversation_id)

    return ConversationResponse(
        conversation_id=conversation_id,
        tenant_id=str(conv["tenant_id"]),
        messages=messages,
    )


@router.post("/ingest/documents", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest, services: dict = Depends(get_services)):
    """Ingest FAQ/policy documents for a tenant."""
    db: TenantDB = services["db"]
    rag: RAGService = services["rag"]

    tenant = await db.get_tenant(request.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    documents = [
        {"id": d.id, "text": d.text, "title": d.title or "", "metadata": d.metadata or {}}
        for d in request.documents
    ]

    await rag.ingest_documents(request.tenant_id, "documents", documents)

    return IngestResponse(success=True, count=len(documents))


@router.post("/ingest/products", response_model=IngestResponse)
async def ingest_products(request: IngestRequest, services: dict = Depends(get_services)):
    """Ingest product descriptions for semantic search."""
    db: TenantDB = services["db"]
    rag: RAGService = services["rag"]

    tenant = await db.get_tenant(request.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    documents = [
        {"id": d.id, "text": d.text, "title": d.title or "", "metadata": d.metadata or {}}
        for d in request.documents
    ]

    await rag.ingest_documents(request.tenant_id, "products", documents)

    return IngestResponse(success=True, count=len(documents))


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
