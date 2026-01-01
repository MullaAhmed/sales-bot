from pydantic import BaseModel
from typing import Any


class MessagePart(BaseModel):
    type: str
    text: str | None = None


class Message(BaseModel):
    role: str
    content: str
    parts: list[MessagePart] | None = None


class ChatRequest(BaseModel):
    """Request format from Vercel AI SDK useChat hook."""
    messages: list[Message]
    company_id: str = "acme-store"
    conversation_id: str


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
