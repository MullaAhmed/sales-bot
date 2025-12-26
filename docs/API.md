# Sales Bot API Documentation

Base URL: `http://localhost:8000/api`

## Overview

This API provides endpoints for a multi-company customer support chatbot. The backend manages conversation history, so the frontend only needs to track `conversation_id`.

---

## Endpoints

### Chat

#### Send Message

```
POST /chat
```

Send a message to the chatbot. Creates a new conversation if `conversation_id` is not provided.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_id` | string | Yes | Company identifier (UUID) |
| `message` | string | Yes | User's message |
| `conversation_id` | string | No | Existing conversation ID. If omitted, creates new conversation |

**Example Request:**

```json
{
  "company_id": "11111111-1111-1111-1111-111111111111",
  "message": "What is your return policy?",
  "conversation_id": null
}
```

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `conversation_id` | string | Conversation ID (save this for subsequent messages) |
| `response` | string | Bot's response text |
| `tool_calls` | array | Tools invoked during response (if any) |
| `sources` | array | RAG sources used (if any) |

**Example Response:**

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Our return policy allows returns within 30 days of purchase...",
  "tool_calls": [],
  "sources": [
    {"title": "Return Policy", "score": 0.85}
  ]
}
```

**Continuing a Conversation:**

```json
{
  "company_id": "11111111-1111-1111-1111-111111111111",
  "message": "Can I track my order?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Conversations

#### Get Conversation History

```
GET /conversations/{conversation_id}
```

Retrieve full message history for a conversation.

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `conversation_id` | string | Conversation ID |
| `company_id` | string | Tenant ID |
| `messages` | array | Array of message objects |

**Message Object:**

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | `"user"` or `"assistant"` |
| `content` | string | Message text |

**Example Response:**

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "company_id": "11111111-1111-1111-1111-111111111111",
  "messages": [
    {"role": "user", "content": "What is your return policy?"},
    {"role": "assistant", "content": "Our return policy allows..."},
    {"role": "user", "content": "Can I track my order?"},
    {"role": "assistant", "content": "Sure! Please provide your order ID..."}
  ]
}
```

---

### Document Ingestion

#### Ingest FAQ/Policy Documents

```
POST /ingest/documents
```

Add or update FAQ/policy documents for RAG retrieval.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_id` | string | Yes | Company identifier |
| `documents` | array | Yes | Array of document objects |

**Document Object:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique document ID |
| `text` | string | Yes | Document content |
| `title` | string | No | Document title |
| `metadata` | object | No | Additional metadata |

**Example Request:**

```json
{
  "company_id": "11111111-1111-1111-1111-111111111111",
  "documents": [
    {
      "id": "faq-returns",
      "title": "Return Policy",
      "text": "Items can be returned within 30 days of purchase. Items must be unused and in original packaging.",
      "metadata": {"category": "policy"}
    },
    {
      "id": "faq-shipping",
      "title": "Shipping Information",
      "text": "We offer free shipping on orders over $50. Standard delivery takes 3-5 business days.",
      "metadata": {"category": "shipping"}
    }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "count": 2
}
```

---

#### Ingest Product Descriptions

```
POST /ingest/products
```

Add or update product descriptions for semantic search.

**Request Body:** Same as `/ingest/documents`

**Example Request:**

```json
{
  "company_id": "11111111-1111-1111-1111-111111111111",
  "documents": [
    {
      "id": "prod-001",
      "title": "Wireless Mouse",
      "text": "Ergonomic wireless mouse with USB receiver. 2.4GHz connection, 1600 DPI, compatible with Windows and Mac.",
      "metadata": {"sku": "WM-001", "price": 29.99}
    }
  ]
}
```

---

### Health Check

```
GET /health
```

**Response:**

```json
{
  "status": "ok"
}
```

---

## Frontend Integration Guide

### Basic Chat Flow

```javascript
// State
let conversationId = null;

async function sendMessage(message) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      company_id: TENANT_ID,
      message: message,
      conversation_id: conversationId
    })
  });

  const data = await response.json();

  // Save conversation_id for subsequent messages
  conversationId = data.conversation_id;

  return data.response;
}
```

### Loading Conversation History

```javascript
async function loadHistory(convId) {
  const response = await fetch(`/api/conversations/${convId}`);
  const data = await response.json();

  // Render messages
  data.messages.forEach(msg => {
    renderMessage(msg.role, msg.content);
  });
}
```

### Starting New Conversation

```javascript
function startNewConversation() {
  conversationId = null;
  clearChatUI();
}
```

---

## Tool Calls

The chatbot can invoke these tools automatically:

| Tool | Description | Trigger Examples |
|------|-------------|------------------|
| `search_products` | Search products by name/SKU | "Do you have wireless mice?" |
| `get_product_details` | Get specific product info | "Tell me about product WM-001" |
| `track_package` | Track order/shipment | "Where is my order?" |
| `create_support_ticket` | Escalate to human | "I need to speak to someone" |

Tool results are included in `tool_calls` array in the response.

---

## Error Responses

| Status | Description |
|--------|-------------|
| 404 | Tenant or conversation not found |
| 422 | Validation error (missing required fields) |
| 500 | Server error |

**Example Error:**

```json
{
  "detail": "Tenant not found"
}
```

---

## Rate Limits

Currently no rate limits implemented. Consider adding based on your requirements.
