"""Seed Qdrant with sample documents via API endpoints."""

import asyncio
import sys
from pathlib import Path

import httpx

# Default API base URL
API_BASE_URL = "http://localhost:8000"

# Sample company ID (matches seed_data.sql)
COMPANY_ID = "acme-store"

# Sample FAQ/Policy documents
SAMPLE_DOCUMENTS = [
    {
        "id": "faq-shipping",
        "title": "Shipping Policy",
        "text": """
Our standard shipping takes 3-5 business days. Express shipping is available for an additional fee and delivers within 1-2 business days.
We ship to all 50 US states and Canada. International shipping is available to select countries.
Free shipping is available on orders over $50. Orders are processed within 24 hours on business days.
        """.strip(),
        "metadata": {"category": "shipping", "type": "faq"},
    },
    {
        "id": "faq-returns",
        "title": "Return Policy",
        "text": """
We offer a 30-day return policy on all items. Items must be in original condition with tags attached.
To initiate a return, contact our support team with your order number. We will provide a prepaid return label.
Refunds are processed within 5-7 business days after we receive the returned item.
Exchanges are also available for different sizes or colors of the same item.
        """.strip(),
        "metadata": {"category": "returns", "type": "faq"},
    },
    {
        "id": "faq-warranty",
        "title": "Warranty Information",
        "text": """
All electronic products come with a 1-year manufacturer warranty. The warranty covers defects in materials and workmanship.
To claim warranty, contact support with your order number and description of the issue.
Warranty does not cover damage from misuse, accidents, or unauthorized modifications.
Extended warranty options are available for purchase at checkout.
        """.strip(),
        "metadata": {"category": "warranty", "type": "faq"},
    },
    {
        "id": "faq-payment",
        "title": "Payment Methods",
        "text": """
We accept all major credit cards including Visa, Mastercard, American Express, and Discover.
PayPal and Apple Pay are also accepted. We offer Buy Now Pay Later options through Affirm.
All transactions are secured with SSL encryption. We never store your full credit card number.
        """.strip(),
        "metadata": {"category": "payment", "type": "faq"},
    },
    {
        "id": "faq-contact",
        "title": "Contact Information",
        "text": """
Customer support is available Monday through Friday, 9 AM to 6 PM EST.
Email us at support@acmestore.com or call 1-800-ACME-HELP.
Live chat is available on our website during business hours.
For urgent issues outside business hours, please email and we'll respond within 24 hours.
        """.strip(),
        "metadata": {"category": "contact", "type": "faq"},
    },
]

# Sample product descriptions (enriched for semantic search)
SAMPLE_PRODUCTS = [
    {
        "id": "prod-wm-001",
        "title": "Wireless Mouse",
        "text": """
Wireless Mouse (SKU: WM-001) - $29.99
Ergonomic wireless mouse with USB receiver. Features include:
- 2.4GHz wireless connectivity with 10m range
- Ergonomic design reduces wrist strain
- 1600 DPI optical sensor for precise tracking
- Compatible with Windows, Mac, and Linux
- Battery life up to 12 months
- Plug and play USB nano receiver
Perfect for office work, gaming, and everyday use.
        """.strip(),
        "metadata": {"sku": "WM-001", "price": 29.99, "category": "accessories"},
    },
    {
        "id": "prod-kb-002",
        "title": "Mechanical Keyboard",
        "text": """
Mechanical Keyboard (SKU: KB-002) - $89.99
RGB mechanical keyboard with blue switches. Features include:
- Cherry MX Blue equivalent switches for tactile feedback
- Full RGB backlighting with customizable effects
- N-key rollover for accurate gaming input
- Durable aluminum frame construction
- Dedicated media controls and volume wheel
- Detachable USB-C cable
Ideal for gaming, programming, and typing enthusiasts.
        """.strip(),
        "metadata": {"sku": "KB-002", "price": 89.99, "category": "accessories"},
    },
    {
        "id": "prod-hb-003",
        "title": "USB-C Hub",
        "text": """
USB-C Hub (SKU: HB-003) - $49.99
7-in-1 USB-C hub with HDMI and SD card reader. Features include:
- 4K HDMI output at 60Hz
- 2x USB 3.0 ports for fast data transfer
- SD and microSD card slots
- USB-C power delivery pass-through (100W)
- Gigabit Ethernet port
- Compact aluminum design for portability
Compatible with MacBook, iPad Pro, and USB-C laptops.
        """.strip(),
        "metadata": {"sku": "HB-003", "price": 49.99, "category": "accessories"},
    },
    {
        "id": "prod-ls-004",
        "title": "Laptop Stand",
        "text": """
Laptop Stand (SKU: LS-004) - $39.99
Adjustable aluminum laptop stand. Features include:
- Adjustable height from 2 to 6 inches
- Supports laptops up to 17 inches
- Hollow design for improved airflow and cooling
- Non-slip silicone pads protect your laptop
- Foldable and portable design
- Holds up to 20 lbs
Ergonomic design raises screen to eye level for better posture.
        """.strip(),
        "metadata": {"sku": "LS-004", "price": 39.99, "category": "accessories"},
    },
    {
        "id": "prod-wc-005",
        "title": "Webcam HD",
        "text": """
Webcam HD (SKU: WC-005) - $59.99
1080p HD webcam with built-in microphone. Features include:
- Full HD 1080p video at 30fps
- Dual stereo microphones with noise cancellation
- Auto light correction for low-light environments
- Wide 90-degree field of view
- Universal clip mount fits any monitor or tripod
- Privacy cover included
Perfect for video calls, streaming, and online meetings.
        """.strip(),
        "metadata": {"sku": "WC-005", "price": 59.99, "category": "accessories"},
    },
]


async def seed_documents(client: httpx.AsyncClient, company_id: str) -> bool:
    """Ingest FAQ/policy documents."""
    print(f"Ingesting {len(SAMPLE_DOCUMENTS)} documents...")

    response = await client.post(
        f"{API_BASE_URL}/ingest/documents",
        json={"company_id": company_id, "documents": SAMPLE_DOCUMENTS},
    )

    if response.status_code == 200:
        result = response.json()
        print(f"  Success: {result['count']} documents ingested")
        return True
    else:
        print(f"  Error: {response.status_code} - {response.text}")
        return False


async def seed_products(client: httpx.AsyncClient, company_id: str) -> bool:
    """Ingest product descriptions."""
    print(f"Ingesting {len(SAMPLE_PRODUCTS)} products...")

    response = await client.post(
        f"{API_BASE_URL}/ingest/products",
        json={"company_id": company_id, "documents": SAMPLE_PRODUCTS},
    )

    if response.status_code == 200:
        result = response.json()
        print(f"  Success: {result['count']} products ingested")
        return True
    else:
        print(f"  Error: {response.status_code} - {response.text}")
        return False


async def check_health(client: httpx.AsyncClient) -> bool:
    """Check if API is running."""
    try:
        response = await client.get(f"{API_BASE_URL}/health")
        return response.status_code == 200
    except httpx.ConnectError:
        return False


async def main():
    """Run the seeding process."""
    # Parse command line args
    company_id = COMPANY_ID
    api_url = API_BASE_URL

    if len(sys.argv) > 1:
        company_id = sys.argv[1]
    if len(sys.argv) > 2:
        api_url = sys.argv[2]
        global API_BASE_URL
        API_BASE_URL = api_url

    print(f"Seeding Qdrant via API at {API_BASE_URL}")
    print(f"Company ID: {company_id}")
    print("-" * 40)

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Check API health
        print("Checking API health...")
        if not await check_health(client):
            print("Error: API is not running. Start the server first:")
            print("  uvicorn app.main:app --reload")
            sys.exit(1)
        print("  API is healthy")
        print()

        # Seed documents
        docs_ok = await seed_documents(client, company_id)

        # Seed products
        products_ok = await seed_products(client, company_id)

        print()
        if docs_ok and products_ok:
            print("Seeding completed successfully!")
        else:
            print("Seeding completed with errors.")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
