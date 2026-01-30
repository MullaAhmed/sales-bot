from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.api.schemas import (
    ChatRequest, ChatResponse, ConversationResponse,
    IngestRequest, IngestResponse,
)
from app.db import get_pool, CompanyDB
from app.vector import VectorStore
from app.services import RAGService, ToolService, ChatbotService

router = APIRouter()

# Singleton service instances (initialized after app startup)
_db: CompanyDB | None = None
_rag: RAGService | None = None
_chatbot: ChatbotService | None = None


def init_services():
    """Initialize service instances. Called after app startup."""
    global _db, _rag, _chatbot
    pool = get_pool()
    _db = CompanyDB(pool)
    vector_store = VectorStore()
    _rag = RAGService(vector_store, _db)
    tools = ToolService(_db)
    _chatbot = ChatbotService(_rag, tools, _db)


async def _get_company_and_conversation(request: ChatRequest):
    """Helper to validate company and get/create conversation."""
    # Extract the last user message
    user_messages = [m for m in request.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")
    message = user_messages[-1].content

    # Convert frontend messages to history format (exclude the last user message)
    history = [{"role": m.role, "content": m.content} for m in request.messages[:-1]]

    company = await _db.get_company(request.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get or create conversation
    conversation_id = request.conversation_id
    conv = await _db.get_conversation(conversation_id)
    if not conv:
        await _db.create_conversation(request.company_id, conversation_id)

    return message, company, conversation_id, history


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the chatbot. Returns JSON response."""
    message, company, conversation_id, history = await _get_company_and_conversation(request)

    result = await _chatbot.chat(
        company_id=request.company_id,
        company_name=company["name"],
        message=message,
        conversation_id=conversation_id,
        history=history,
    )

    return ChatResponse(conversation_id=conversation_id, **result)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Send a message to the chatbot with streaming. Supports Vercel AI SDK format."""
    message, company, conversation_id, history = await _get_company_and_conversation(request)

    async def generate():
        async for event in _chatbot.chat_stream(
            company_id=request.company_id,
            company_name=company["name"],
            message=message,
            conversation_id=conversation_id,
            history=history,
        ):
            yield event

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={"X-Conversation-Id": conversation_id},
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    conv = await _db.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await _db.get_messages(conversation_id)

    return ConversationResponse(
        conversation_id=conversation_id,
        company_id=str(conv["company_id"]),
        messages=messages,
    )


@router.post("/ingest/documents", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """Ingest FAQ/policy documents for a company."""
    company = await _db.get_company(request.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    documents = [
        {"id": d.id, "text": d.text, "title": d.title or "", "metadata": d.metadata or {}}
        for d in request.documents
    ]

    await _rag.ingest_documents(request.company_id, "documents", documents)

    return IngestResponse(success=True, count=len(documents))


@router.post("/ingest/products", response_model=IngestResponse)
async def ingest_products(request: IngestRequest):
    """Ingest product descriptions for semantic search."""
    company = await _db.get_company(request.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    documents = [
        {"id": d.id, "text": d.text, "title": d.title or "", "metadata": d.metadata or {}}
        for d in request.documents
    ]

    await _rag.ingest_documents(request.company_id, "products", documents)

    return IngestResponse(success=True, count=len(documents))


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
