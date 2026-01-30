import json
from app.db import CompanyDB


class ToolService:
    """Tool implementations for the chatbot."""

    def __init__(self, db: CompanyDB):
        self.db = db

    # Tool definitions for OpenAI function calling
    TOOL_DEFINITIONS = [
        {
            "type": "function",
            "function": {
                "name": "get_product_details",
                "description": "Get detailed information about a specific product. IMPORTANT: This tool gets details for ONE product at a time. If the user mentions or asks about multiple products, you MUST call this tool multiple times (once for each product_id).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": "The product ID (only one ID per call)"
                        }
                    },
                    "required": ["product_id"]
                }
            }
        },
    #     {
    #         "type": "function",
    #         "function": {
    #             "name": "track_package",
    #             "description": "Track a package by order ID or tracking number",
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                     "order_id": {
    #                         "type": "string",
    #                         "description": "The order ID"
    #                     },
    #                     "tracking_number": {
    #                         "type": "string",
    #                         "description": "The carrier tracking number"
    #                     }
    #                 }
    #             }
    #         }
    #     },
    #     {
    #         "type": "function",
    #         "function": {
    #             "name": "create_support_ticket",
    #             "description": "Create a support ticket and escalate to human agent",
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                     "customer_email": {
    #                         "type": "string",
    #                         "description": "Customer's email address"
    #                     },
    #                     "subject": {
    #                         "type": "string",
    #                         "description": "Brief subject of the issue"
    #                     },
    #                     "message": {
    #                         "type": "string",
    #                         "description": "Detailed description of the issue"
    #                     }
    #                 },
    #                 "required": ["customer_email", "subject", "message"]
    #             }
    #         }
    #     }
    # 
    ]

    async def execute(self, company_id: str, tool_name: str, arguments: dict) -> str:
        """Execute a tool and return the result as a string."""
        handlers = {
            "get_product_details": self._get_product_details,
            "track_package": self._track_package,
            "create_support_ticket": self._create_support_ticket,
        }

        handler = handlers.get(tool_name)
        if not handler:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        # Debug: log arguments
        print(f"[TOOL] {tool_name} called with arguments: {arguments}")

        try:
            result = await handler(company_id, **arguments)
            return json.dumps(result, default=str)
        except TypeError as e:
            print(f"[TOOL ERROR] {tool_name} failed: {e}")
            return json.dumps({"error": f"Invalid arguments for {tool_name}: {str(e)}", "arguments_received": arguments})

    async def _get_product_details(self, company_id: str, product_id: str) -> dict:
        product = await self.db.get_product(company_id, product_id)
        if not product:
            return {"found": False, "message": "Product not found."}
        return {
            "found": True,
            "product": {
                "id": str(product["id"]),
                "handle": product.get("handle"),
                "name": product["name"],
                "sku": product.get("sku"),
                "description": product.get("description"),
                "short_description": product.get("short_description"),
                "price": float(product["price"]) if product.get("price") else None,
                "compare_at_price": float(product["compare_at_price"]) if product.get("compare_at_price") else None,
                "stock": product.get("stock", 0),
                "in_stock": product.get("stock", 0) > 0,
                "image_url": product.get("image_url"),
                "images": json.loads(product["images"]) if product.get("images") else [],
                "variants": json.loads(product["variants"]) if product.get("variants") else [],
            }
        }

    async def _track_package(
        self, company_id: str, order_id: str = None, tracking_number: str = None
    ) -> dict:
        order = None
        if order_id:
            order = await self.db.get_order(company_id, order_id)
        elif tracking_number:
            order = await self.db.get_order_by_tracking(company_id, tracking_number)

        if not order:
            return {"found": False, "message": "Order not found. Please check your order ID or tracking number."}

        return {
            "found": True,
            "order_id": order["id"],
            "order_status": order.get("status"),
            "shipping": {
                "carrier": order.get("carrier"),
                "tracking_number": order.get("tracking_number"),
                "status": order.get("shipping_status"),
                "estimated_delivery": order.get("estimated_delivery"),
            }
        }

    async def _create_support_ticket(
        self, company_id: str, customer_email: str, subject: str, message: str
    ) -> dict:
        ticket_id = await self.db.log_support_ticket(
            company_id, customer_email, subject, message
        )
        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": f"Support ticket created. A human agent will contact you at {customer_email} shortly."
        }
