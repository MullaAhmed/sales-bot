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
- Use the provided context from documents to answer policy/FAQ questions
- Use tools to look up real-time data (products, orders, tracking)
- If you cannot help, offer to create a support ticket
- Never make up information - use tools or say you don't know
- For order/tracking queries, always ask for order ID or tracking number if not provided

## Available Context:
{context}
"""


class ChatbotService:
    """Main chatbot service with RAG and tool calling."""

    def __init__(self, rag: RAGService, tools: ToolService, db: CompanyDB):
        self.rag = rag
        self.tools = tools
        self.db = db
        self.client = AsyncOpenAI(api_key=get_settings().openai_api_key)
        self.model = get_settings().openai_model

    async def chat(
        self,
        company_id: str,
        company_name: str,
        message: str,
        conversation_id: str,
    ) -> dict:
        """
        Process a chat message with RAG context and tool calling.

        Returns: {response: str, tool_calls: list, sources: list}
        """
        # 1. Fetch RAG context and history in parallel
        rag_results, history = await asyncio.gather(
            self.rag.retrieve(company_id, message),
            self.db.get_messages(conversation_id),
        )
        context = self.rag.format_context(rag_results)

        # 2. Build messages
        system = SYSTEM_PROMPT.format(
            company_name=company_name,
            context=context if context else "No relevant documents found.",
        )

        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        # 3. Save user message to DB
        await self.db.add_message(conversation_id, "user", message)

        # 4. Call LLM with tools
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=ToolService.TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message
        tool_calls_made = []

        # 5. Handle tool calls (loop until no more tool calls)
        while assistant_message.tool_calls:
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                result = await self.tools.execute(company_id, func_name, func_args)
                tool_calls_made.append({
                    "name": func_name,
                    "arguments": func_args,
                    "result": json.loads(result),
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            # Get next response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=ToolService.TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message

        sources = [
            {"source": r.get("source"), "score": r.get("score")}
            for r in rag_results
        ]

        # 6. Save assistant response to DB
        await self.db.add_message(
            conversation_id,
            "assistant",
            assistant_message.content,
            tool_calls=tool_calls_made if tool_calls_made else None,
            sources=sources if sources else None,
        )

        return {
            "response": assistant_message.content,
            "tool_calls": tool_calls_made,
            "sources": sources,
        }
