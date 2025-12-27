import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.api.schemas import (
    ChatRequest, ChatResponse, ConversationResponse,
    IngestRequest, IngestResponse, ChatRequest,
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


@router.post("/chat")
async def chat(request: ChatRequest):
    """Send a message to the chatbot. Supports Vercel AI SDK format."""
    # Extract the last user message
    user_messages = [m for m in request.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")

    message = user_messages[-1].content

    company = await _db.get_company(request.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    conversation_id = request.conversation_id
    if conversation_id:
        conv = await _db.get_conversation(conversation_id)
        if not conv or str(conv["company_id"]) != request.company_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation_id = await _db.create_conversation(request.company_id)

    result = await _chatbot.chat(
        company_id=request.company_id,
        company_name=company["name"],
        message=message,
        conversation_id=conversation_id,
    )

    # Return in AI SDK Data Stream Protocol format
    async def generate():
        # Text content (format: 0:"text"\n)
        response_text = result.get("response", "")
        yield f'0:{json.dumps(response_text)}\n'

        # Tool calls if any (format: 9:{...}\n for invocation, a:{...}\n for result)
        tool_calls = result.get("tool_calls", [])
        for i, tool_call in enumerate(tool_calls):
            tool_call_id = f"call_{conversation_id}_{i}"
            # Tool invocation
            invocation = {
                "toolCallId": tool_call_id,
                "toolName": tool_call.get("name", "unknown"),
                "args": tool_call.get("args", {}),
            }
            yield f'9:{json.dumps(invocation)}\n'
            # Tool result
            tool_result = {
                "toolCallId": tool_call_id,
                "result": tool_call.get("result", {}),
            }
            yield f'a:{json.dumps(tool_result)}\n'

        # Message annotations with sources (format: 8:[{...}]\n)
        sources = result.get("sources", [])
        if sources or conversation_id:
            annotation = {
                "sources": sources,
                "conversation_id": conversation_id,
            }
            yield f'8:{json.dumps([annotation])}\n'

        # Finish event (format: e:{...}\n)
        finish = {
            "finishReason": "stop",
            "usage": {"promptTokens": 0, "completionTokens": 0},
        }
        yield f'e:{json.dumps(finish)}\n'

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={"X-Conversation-Id": conversation_id},
    )


@router.post("/chat/simple", response_model=ChatResponse)
async def chat_simple(request: ChatRequest):
    """Send a message to the chatbot. Simple JSON format."""
    company = await _db.get_company(request.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    conversation_id = request.conversation_id
    if conversation_id:
        conv = await _db.get_conversation(conversation_id)
        if not conv or str(conv["company_id"]) != request.company_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation_id = await _db.create_conversation(request.company_id)

    result = await _chatbot.chat(
        company_id=request.company_id,
        company_name=company["name"],
        message=request.message,
        conversation_id=conversation_id,
    )

    return ChatResponse(conversation_id=conversation_id, **result)


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
