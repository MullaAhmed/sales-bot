import asyncio
import json
import time
from openai import AsyncOpenAI
from app.config import get_settings
from app.db import CompanyDB
from app.db.models import TTLCache
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

    # Class-level cache shared across all instances (TTL: 5 minutes)
    _history_cache = TTLCache(ttl=300)

    def __init__(self, rag: RAGService, tools: ToolService, db: CompanyDB):
        self.rag = rag
        self.tools = tools
        self.db = db
        self.client = AsyncOpenAI(api_key=get_settings().openai_api_key)
        self.model = get_settings().openai_model

    async def _get_history(self, conversation_id: str) -> list[dict]:
        """Get conversation history with caching."""
        cached = self._history_cache.get(conversation_id)
        if cached is not None:
            # Return a copy to avoid mutation issues
            return [msg.copy() for msg in cached]

        history = await self.db.get_messages(conversation_id)
        # Store a copy in cache
        self._history_cache.set(conversation_id, [msg.copy() for msg in history])
        return history

    async def _update_history_cache(self, conversation_id: str, role: str, content: str):
        """Update the history cache with new message."""
        cached = self._history_cache.get(conversation_id)
        if cached is None:
            cached = await self.db.get_messages(conversation_id)
        cached.append({"role": role, "content": content})
        self._history_cache.set(conversation_id, cached)

    async def _execute_tool(self, company_id: str, tool_call) -> dict:
        """Execute a single tool call and return the result."""
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        result = await self.tools.execute(company_id, func_name, func_args)
        return json.loads(result)


    async def chat(self, company_id: str, company_name: str, message: str, conversation_id: str) -> dict:
        """Send a chat message and get a response."""
        # Prepare context (RAG and history in parallel)
        rag_results, history = await asyncio.gather(
            self.rag.retrieve(company_id, message),
            self._get_history(conversation_id),
        )
        context = self.rag.format_context(rag_results)
        sources = [{"source": r.get("source"), "score": r.get("score")} for r in rag_results]

        # Build messages
        system = SYSTEM_PROMPT.format(company_name=company_name)
        messages = [{"role": "system", "content": system}]
        messages.extend(history)

        user_content = f"<context>\n{context}\n</context>\n\n{message}" if context else message
        messages.append({"role": "user", "content": user_content})

        # Update cache and fire-and-forget DB save
        await self._update_history_cache(conversation_id, "user", message)
        self.db.add_message_fire_and_forget(conversation_id, "user", message)

        tool_calls_made = []

        # Call OpenAI in a loop until no more tool calls
        while True:
            use_tools = len(tool_calls_made) == 0  # Only use tools on first call
            llm_start = time.perf_counter()
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=ToolService.TOOL_DEFINITIONS if use_tools else None,
                tool_choice="auto" if use_tools else None,
                service_tier="priority",
                reasoning_effort="minimal",
            )

            assistant_message = response.choices[0].message

            # If no tool calls, we're done
            if not assistant_message.tool_calls:
                break

            # Process tool calls
            messages.append({"role": "assistant", "content": None, "tool_calls": [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in assistant_message.tool_calls
            ]})

            # Execute all tool calls in parallel
            tool_results = await asyncio.gather(*[
                self._execute_tool(company_id, tc)
                for tc in assistant_message.tool_calls
            ])

            for tc, result in zip(assistant_message.tool_calls, tool_results):
                tool_calls_made.append({
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                    "result": result,
                })
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})

        # Update cache and fire-and-forget DB save
        await self._update_history_cache(conversation_id, "assistant", assistant_message.content or "")
        self.db.add_message_fire_and_forget(
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
        # Prepare context (RAG and history in parallel)
        rag_results, history = await asyncio.gather(
            self.rag.retrieve(company_id, message),
            self._get_history(conversation_id),
        )
        context = self.rag.format_context(rag_results)
        sources = [{"source": r.get("source"), "score": r.get("score")} for r in rag_results]

        # Build messages
        system = SYSTEM_PROMPT.format(company_name=company_name)
        user_content = f"<context>\n{context}\n</context>\n\n{message}" if context else message
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_content})

        # Update cache and fire-and-forget DB save
        await self._update_history_cache(conversation_id, "user", message)
        self.db.add_message_fire_and_forget(conversation_id, "user", message)

        # Send sources/metadata first
        yield f'8:{json.dumps([{"sources": sources, "conversation_id": conversation_id}])}\n'

        tool_calls_made = []
        full_response = ""

        # Stream loop - continues until no more tool calls
        while True:
            use_tools = len(tool_calls_made) == 0  # Only use tools on first call
            llm_start = time.perf_counter()
            first_token_time = None
            current_tool_calls = {}
            finish_reason = "stop"

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=ToolService.TOOL_DEFINITIONS if use_tools else None,
                tool_choice="auto" if use_tools else None,
                stream=True,
                service_tier="priority",
                reasoning_effort="minimal",
            )

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
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
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

            # If no tool calls, we're done
            if finish_reason != "tool_calls" or not current_tool_calls:
                break

            # Process tool calls
            messages.append({"role": "assistant", "content": None, "tool_calls": [
                {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["arguments"]}}
                for tc in current_tool_calls.values()
            ]})

            # Execute all tool calls in parallel
            sorted_indices = sorted(current_tool_calls.keys())
            tool_tasks = []
            for idx in sorted_indices:
                tc = current_tool_calls[idx]
                func_name = tc["name"]
                func_args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                tool_call_id = tc["id"]
                yield f'9:{json.dumps({"toolCallId": tool_call_id, "toolName": func_name, "args": func_args})}\n'
                tool_tasks.append(self.tools.execute(company_id, func_name, func_args))

            tool_results = await asyncio.gather(*tool_tasks)

            for idx, result in zip(sorted_indices, tool_results):
                tc = current_tool_calls[idx]
                func_name = tc["name"]
                func_args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                tool_call_id = tc["id"]
                result_json = json.loads(result)

                yield f'a:{json.dumps({"toolCallId": tool_call_id, "result": result_json})}\n'

                tool_calls_made.append({"name": func_name, "arguments": func_args, "result": result_json})
                messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": result})

        yield f'e:{json.dumps({"finishReason": "stop", "usage": {"promptTokens": 0, "completionTokens": 0}})}\n'

        # Update cache and fire-and-forget DB save
        await self._update_history_cache(conversation_id, "assistant", full_response)
        self.db.add_message_fire_and_forget(
            conversation_id, "assistant", full_response,
            tool_calls=tool_calls_made if tool_calls_made else None,
            sources=sources if sources else None,
        )
