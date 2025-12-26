import json
from app.db import TenantDB


class ToolService:
    """Tool implementations for the chatbot."""

    def __init__(self, db: TenantDB):
        self.db = db

    # Tool definitions for OpenAI function calling
    TOOL_DEFINITIONS = [
        {
            "type": "function",
            "function": {
                "name": "search_products",
                "description": "Search for products by name, SKU, or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for product name, SKU, or keywords"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_product_details",
                "description": "Get detailed information about a specific product",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": "The product ID"
                        }
                    },
                    "required": ["product_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "track_package",
                "description": "Track a package by order ID or tracking number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order ID"
                        },
                        "tracking_number": {
                            "type": "string",
                            "description": "The carrier tracking number"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_support_ticket",
                "description": "Create a support ticket and escalate to human agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_email": {
                            "type": "string",
                            "description": "Customer's email address"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Brief subject of the issue"
                        },
                        "message": {
                            "type": "string",
                            "description": "Detailed description of the issue"
                        }
                    },
                    "required": ["customer_email", "subject", "message"]
                }
            }
        }
    ]

    async def execute(self, tenant_id: str, tool_name: str, arguments: dict) -> str:
        """Execute a tool and return the result as a string."""
        handlers = {
            "search_products": self._search_products,
            "get_product_details": self._get_product_details,
            "track_package": self._track_package,
            "create_support_ticket": self._create_support_ticket,
        }

        handler = handlers.get(tool_name)
        if not handler:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        result = await handler(tenant_id, **arguments)
        return json.dumps(result, default=str)

    async def _search_products(self, tenant_id: str, query: str) -> dict:
        products = await self.db.search_products(tenant_id, query)
        if not products:
            return {"found": False, "message": "No products found matching your search."}
        return {
            "found": True,
            "count": len(products),
            "products": [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "sku": p.get("sku"),
                    "price": float(p["price"]) if p.get("price") else None,
                    "in_stock": p.get("stock", 0) > 0,
                }
                for p in products
            ]
        }

    async def _get_product_details(self, tenant_id: str, product_id: str) -> dict:
        product = await self.db.get_product(tenant_id, product_id)
        if not product:
            return {"found": False, "message": "Product not found."}
        return {
            "found": True,
            "product": {
                "id": product["id"],
                "name": product["name"],
                "sku": product.get("sku"),
                "description": product.get("description"),
                "price": float(product["price"]) if product.get("price") else None,
                "stock": product.get("stock", 0),
                "in_stock": product.get("stock", 0) > 0,
            }
        }

    async def _track_package(
        self, tenant_id: str, order_id: str = None, tracking_number: str = None
    ) -> dict:
        order = None
        if order_id:
            order = await self.db.get_order(tenant_id, order_id)
        elif tracking_number:
            order = await self.db.get_order_by_tracking(tenant_id, tracking_number)

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
        self, tenant_id: str, customer_email: str, subject: str, message: str
    ) -> dict:
        ticket_id = await self.db.log_support_ticket(
            tenant_id, customer_email, subject, message
        )
        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": f"Support ticket created. A human agent will contact you at {customer_email} shortly."
        }
