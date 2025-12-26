from pydantic import BaseModel


class ChatRequest(BaseModel):
    company_id: str
    message: str
    conversation_id: str | None = None  # If None, creates new conversation


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: list[dict]
    sources: list[dict]


class ConversationResponse(BaseModel):
    conversation_id: str
    company_id: str
    messages: list[dict]


class DocumentInput(BaseModel):
    id: str
    text: str
    title: str | None = None
    metadata: dict | None = None


class IngestRequest(BaseModel):
    company_id: str
    documents: list[DocumentInput]


class IngestResponse(BaseModel):
    success: bool
    count: int
