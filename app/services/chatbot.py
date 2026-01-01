import asyncio
import json
from openai import AsyncOpenAI
from app.config import get_settings
from app.db import CompanyDB
from app.services.rag import RAGService
from app.services.tools import ToolService


SYSTEM_PROMPT = """You are a helpful customer support assistant for {company_name}.

## Priority Flow (handle in this order):
0. Always answer from the provided context first
1. URGENT: Shipping issues, order problems, payment failures - escalate if needed
2. HIGH: Product availability, pricing questions
3. MEDIUM: General product inquiries, policy questions
4. LOW: General FAQs, company information

## Guidelines:
- Be friendly, professional, and concise
- Answer from the provided context when available
- Use tools to look up real-time data (products, orders, tracking)
- If you cannot help, offer to create a support ticket
- Never make up information - use tools or say you don't know
- For order/tracking queries, always ask for order ID or tracking number if not provided
"""


class ChatbotService:
    """Main chatbot service with RAG and tool calling."""

    def __init__(self, rag: RAGService, tools: ToolService, db: CompanyDB):
        self.rag = rag
        self.tools = tools
        self.db = db
        self.client = AsyncOpenAI(api_key=get_settings().openai_api_key)
        self.model = get_settings().openai_model

    async def chat(self, company_id: str, company_name: str, message: str, conversation_id: str) -> dict:
        """Send a chat message and get a response."""
        # Prepare context
        rag_results, history = await asyncio.gather(
            self.rag.retrieve(company_id, message),
            self.db.get_messages(conversation_id),
        )
        context = self.rag.format_context(rag_results)
        sources = [{"source": r.get("source"), "score": r.get("score")} for r in rag_results]

        # Build messages
        system = SYSTEM_PROMPT.format(company_name=company_name)
        user_content = f"<context>\n{context}\n</context>\n\n{message}" if context else message
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_content})

        await self.db.add_message(conversation_id, "user", message)

        # Call OpenAI
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=ToolService.TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message
        tool_calls_made = []

        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                result = await self.tools.execute(company_id, func_name, func_args)
                tool_calls_made.append({
                    "name": func_name,
                    "arguments": func_args,
                    "result": json.loads(result),
                })

        await self.db.add_message(
            conversation_id, "assistant", assistant_message.content or "",
            tool_calls=tool_calls_made if tool_calls_made else None,
            sources=sources if sources else None,
        )

        return {
            "response": assistant_message.content or "",
            "tool_calls": tool_calls_made,
            "sources": sources,
        }

    async def chat_stream(self, company_id: str, company_name: str, message: str, conversation_id: str):
        """Send a chat message and stream the response."""
        # Prepare context
        rag_results, history = await asyncio.gather(
            self.rag.retrieve(company_id, message),
            self.db.get_messages(conversation_id),
        )
        context = self.rag.format_context(rag_results)
        sources = [{"source": r.get("source"), "score": r.get("score")} for r in rag_results]

        # Build messages
        system = SYSTEM_PROMPT.format(company_name=company_name)
        user_content = f"<context>\n{context}\n</context>\n\n{message}" if context else message
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_content})

        await self.db.add_message(conversation_id, "user", message)

        # Send sources/metadata first
        yield f'8:{json.dumps([{"sources": sources, "conversation_id": conversation_id}])}\n'

        # Call OpenAI with streaming
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=ToolService.TOOL_DEFINITIONS,
            tool_choice="auto",
            stream=True,
        )

        tool_calls_made = []
        full_response = ""
        finish_reason = "stop"
        current_tool_calls = {}

        async for chunk in response:
            choice = chunk.choices[0] if chunk.choices else None
            if not choice:
                continue

            if choice.finish_reason:
                finish_reason = choice.finish_reason

            delta = choice.delta
            if not delta:
                continue

            if delta.content:
                full_response += delta.content
                yield f'0:{json.dumps(delta.content)}\n'

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in current_tool_calls:
                        current_tool_calls[idx] = {"id": tc.id or "", "name": "", "arguments": ""}
                    if tc.id:
                        current_tool_calls[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            current_tool_calls[idx]["name"] = tc.function.name
                        if tc.function.arguments:
                            current_tool_calls[idx]["arguments"] += tc.function.arguments

        # Execute tool calls and emit results
        if finish_reason == "tool_calls" and current_tool_calls:
            for idx in sorted(current_tool_calls.keys()):
                tc = current_tool_calls[idx]
                func_name = tc["name"]
                func_args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                tool_call_id = tc["id"]

                yield f'9:{json.dumps({"toolCallId": tool_call_id, "toolName": func_name, "args": func_args})}\n'

                result = await self.tools.execute(company_id, func_name, func_args)
                result_json = json.loads(result)
                yield f'a:{json.dumps({"toolCallId": tool_call_id, "result": result_json})}\n'

                tool_calls_made.append({"name": func_name, "arguments": func_args, "result": result_json})

        yield f'e:{json.dumps({"finishReason": finish_reason.replace("_", "-"), "usage": {"promptTokens": 0, "completionTokens": 0}})}\n'

        await self.db.add_message(
            conversation_id, "assistant", full_response,
            tool_calls=tool_calls_made if tool_calls_made else None,
            sources=sources if sources else None,
        )
