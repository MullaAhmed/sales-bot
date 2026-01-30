"""
Creates products.json and documents.json from source data.
- products.json: from cleaned_products.csv (includes images and variants)
- documents.json: from docs.json
"""

import csv
import json
import re
import uuid
from html import unescape
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
CSV_PATH = SCRIPTS_DIR.parent / "cleaned_products.csv"
DOCS_PATH = SCRIPTS_DIR / "docs.json"
PRODUCTS_OUTPUT = SCRIPTS_DIR / "products.json"
DOCUMENTS_OUTPUT = SCRIPTS_DIR / "documents.json"


def make_uuid(name: str) -> str:
    """Generate a deterministic UUID from a string."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))


def strip_html(html: str) -> str:
    """Remove HTML tags and decode entities."""
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_list_field(value: str) -> list:
    """Parse Shopify's list format like ['item1', 'item2']."""
    if not value or value == "nan":
        return []
    try:
        if value.startswith("["):
            import ast
            parsed = ast.literal_eval(value)
            # Filter out 'nan' strings
            return [x for x in parsed if x != "nan" and str(x) != "nan"]
    except (ValueError, SyntaxError):
        pass
    return [value] if value else []


def parse_price(value) -> float:
    """Parse price field (can be single value or list)."""
    if not value or value == "nan":
        return 0.0
    try:
        if isinstance(value, (int, float)):
            return float(value)
        prices = parse_list_field(str(value))
        if isinstance(prices, list) and prices:
            return float(prices[0])
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def parse_all_prices(value: str) -> list[float]:
    """Parse all prices from a field."""
    if not value or value == "nan":
        return []
    try:
        prices = parse_list_field(value)
        return [float(p) for p in prices if p and str(p) != "nan"]
    except (ValueError, TypeError):
        return []


def parse_stock(value: str) -> int:
    """Parse stock quantity."""
    if not value or value == "nan":
        return 0
    try:
        stocks = parse_list_field(value)
        if isinstance(stocks, list) and stocks:
            return sum(int(float(s)) for s in stocks if s and str(s) != "nan")
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def clean_image_url(url: str) -> str:
    """Clean and validate image URL."""
    if not url or url == "nan":
        return ""
    url = str(url).strip()
    if url.startswith("http"):
        return url
    return ""


def create_products_json():
    """Create products.json from cleaned_products.csv."""
    print(f"Reading: {CSV_PATH}")
    products = []

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row.get("Status", "").lower() != "active":
                continue

            handle = row.get("Handle", "").strip()
            if not handle:
                continue

            title = row.get("Title", "").strip()
            body_html = row.get("Body (HTML)", "")
            vendor = row.get("Vendor", "").strip()
            short_desc = row.get("Short Description (product.metafields.custom.short_description)", "").strip()

            # Parse SKUs
            sku_raw = row.get("Variant SKU", "")
            skus = parse_list_field(sku_raw)
            sku = skus[0] if skus else handle.upper().replace("-", "")

            # Parse prices
            price = parse_price(row.get("Variant Price", ""))
            compare_at_price = parse_price(row.get("Variant Compare At Price", ""))
            all_prices = parse_all_prices(row.get("Variant Price", ""))

            # Parse stock
            stock = parse_stock(row.get("Variant Inventory Qty", ""))

            # Parse images
            image_src_raw = row.get("Image Src", "")
            images = [clean_image_url(url) for url in parse_list_field(image_src_raw)]
            images = [url for url in images if url]  # Filter empty
            image_url = images[0] if images else ""

            # Parse variant images
            variant_image_raw = row.get("Variant Image", "")
            variant_images = [clean_image_url(url) for url in parse_list_field(variant_image_raw)]
            variant_images = [url for url in variant_images if url]

            # Parse variants
            option_name = row.get("Option1 Name", "").strip()
            option_values_raw = row.get("Option1 Value", "")
            option_values = parse_list_field(option_values_raw)

            variants = []
            if option_name and option_name != "Title" and option_values:
                for i, opt_value in enumerate(option_values):
                    if not opt_value or opt_value == "Default Title":
                        continue
                    variant = {
                        "option": option_name,
                        "value": str(opt_value),
                        "sku": skus[i] if i < len(skus) else sku,
                        "price": all_prices[i] if i < len(all_prices) else price,
                        "image_url": variant_images[i] if i < len(variant_images) else image_url,
                    }
                    variants.append(variant)

            description = strip_html(body_html)

            # Build rich text for vector search
            text_parts = [
                f"{title} (SKU: {sku})",
                f"Price: Rs. {price:.0f}" if price else "",
                short_desc if short_desc else "",
                description if description else "",
            ]
            text = "\n".join(part for part in text_parts if part)

            products.append({
                "id": make_uuid(f"prod-{handle}"),
                "handle": handle,
                "title": title,
                "description": description,
                "short_description": short_desc,
                "sku": sku,
                "price": price,
                "compare_at_price": compare_at_price if compare_at_price > 0 else None,
                "stock": stock,
                "image_url": image_url,
                "images": images[:5],  # Limit to 5 images
                "variants": variants,
                "vendor": vendor,
                "text": text,  # For Qdrant
            })

    print(f"Writing: {PRODUCTS_OUTPUT} ({len(products)} products)")
    with open(PRODUCTS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    return len(products)


def create_documents_json():
    """Create documents.json from docs.json."""
    print(f"Reading: {DOCS_PATH}")

    with open(DOCS_PATH, encoding="utf-8") as f:
        docs_raw = json.load(f)

    documents = []
    for title, text in docs_raw.items():
        slug = title.lower().replace(" ", "-").replace("&", "and")
        slug = re.sub(r"[^a-z0-9-]", "", slug)

        documents.append({
            "id": make_uuid(f"doc-{slug}"),
            "title": title,
            "text": text,
            "metadata": {
                "category": slug,
                "type": "policy",
            },
        })

    print(f"Writing: {DOCUMENTS_OUTPUT} ({len(documents)} documents)")
    with open(DOCUMENTS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    return len(documents)


def main():
    print("=" * 50)
    print("  CREATE DATA SCRIPT")
    print("=" * 50)
    print()

    products_count = create_products_json()
    documents_count = create_documents_json()

    print()
    print("=" * 50)
    print(f"  Created {products_count} products, {documents_count} documents")
    print("=" * 50)
    print()
    print("Next steps:")
    print("  1. python scripts/seed_supabase.py  # Seed database")
    print("  2. python scripts/seed_qdrant.py    # Seed vector store")


if __name__ == "__main__":
    main()
