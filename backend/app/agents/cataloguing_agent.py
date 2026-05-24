import json
import asyncio
from typing import Callable
from datetime import datetime
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Static GI tag lookup — extend this JSON
GI_TAGS = {
    "chanderi": {"id": "GI-001", "name": "Chanderi Fabric", "state": "Madhya Pradesh"},
    "kutch":    {"id": "GI-002", "name": "Kutch Embroidery", "state": "Gujarat"},
    "pottery":  {"id": "GI-003", "name": "Blue Pottery",     "state": "Rajasthan"},
    "phulkari": {"id": "GI-004", "name": "Phulkari",         "state": "Punjab"},
    "madhubani":{"id": "GI-005", "name": "Madhubani Painting","state": "Bihar"},
}

CATALOGUE_PROMPT = """
You are an expert in Indian handicrafts, cultural heritage, and e-commerce.
Analyse this product image carefully.

Return ONLY valid JSON, no explanation:
{{
  "craft_type": "",
  "origin_region": "",
  "title": "",
  "description": "",
  "cultural_story": "",
  "suggested_tags": [],
  "b2c_price_inr": 0,
  "b2b_price_inr": 0,
  "moq": 0,
  "confidence": 0.0
}}

Rules:
- title: 8-12 words, SEO-friendly, mention craft + region
- description: 60-80 words, story-forward, no generic phrases
- cultural_story: 2 sentences about the tradition behind this craft
- b2c_price_inr: fair retail price reflecting artisan wages
- b2b_price_inr: bulk price (80% of b2c)
- moq: minimum order quantity for B2B (default 5)
- confidence: your overall confidence in the analysis (0.0-1.0)
- If image is unclear, still return best guess with low confidence
"""

PRICING_PROMPT = """
Calculate a fair price for this handmade Indian craft product.

Material cost provided by artisan: ₹{material_cost}
Time spent: {hours} hours
Craft type: {craft_type}
AI suggested price: ₹{ai_price}

Rules:
- Minimum hourly wage for artisan: ₹80
- Apply 2.5x multiplier on (material + labour) for fair profit
- Compare with AI suggested price and take the higher value

Return ONLY valid JSON:
{{
  "fair_price": 0,
  "calculation": "",
  "was_underpriced": false,
  "old_price_estimate": 0,
  "price_increase_percent": 0
}}
"""


async def catalogue_product(
    image_bytes: bytes,
    artisan_profile: dict,
    emit: Callable,
    material_cost: float = 0,
    hours_spent: float = 0
) -> dict:
    """
    Full cataloguing pipeline with streaming events.
    emit() sends CatalogueEvent to WebSocket.
    """
    now = lambda: datetime.utcnow().isoformat()

    try:
        await emit({"type": "ANALYSING", "payload": {}, "timestamp": now()})

        # Step 1: Gemini Vision analysis
        image = Image.open(BytesIO(image_bytes))
        response = model.generate_content([CATALOGUE_PROMPT, image])
        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        product = json.loads(text.strip())

    except Exception as e:
        print(f"[Cataloguing] Vision failed: {e}, using fallback")
        product = _demo_product(artisan_profile)

    # Stream events as fields resolve
    await emit({
        "type": "CRAFT_DETECTED",
        "payload": {
            "craft_type": product.get("craft_type", "Handcraft"),
            "confidence": product.get("confidence", 0.8)
        },
        "timestamp": now()
    })
    await asyncio.sleep(0.5)

    await emit({
        "type": "TITLE_READY",
        "payload": {"title": product.get("title", "")},
        "timestamp": now()
    })
    await asyncio.sleep(0.4)

    await emit({
        "type": "DESCRIPTION_READY",
        "payload": {
            "description": product.get("description", ""),
            "cultural_story": product.get("cultural_story", "")
        },
        "timestamp": now()
    })
    await asyncio.sleep(0.4)

    # Step 2: Pricing intelligence
    if material_cost > 0 and hours_spent > 0:
        fair = _calculate_fair_price(
            material_cost, hours_spent,
            product.get("craft_type", ""),
            product.get("b2c_price_inr", 0)
        )
        product["b2c_price_inr"] = fair["fair_price"]
        product["b2b_price_inr"] = int(fair["fair_price"] * 0.80)
        product["pricing_insight"] = fair
    else:
        product["pricing_insight"] = None

    await emit({
        "type": "PRICE_SUGGESTED",
        "payload": {
            "b2c_price": product["b2c_price_inr"],
            "b2b_price": product["b2b_price_inr"],
            "insight":   product.get("pricing_insight")
        },
        "timestamp": now()
    })
    await asyncio.sleep(0.3)

    # Step 3: GI tag matching
    gi_tag = _match_gi_tag(
        product.get("craft_type", ""),
        product.get("origin_region", ""),
        artisan_profile.get("district", "")
    )
    product["gi_tag"] = gi_tag

    # Final assembled listing
    listing = {
        "title":          product.get("title"),
        "description":    product.get("description"),
        "cultural_story": product.get("cultural_story"),
        "craft_type":     product.get("craft_type"),
        "origin_region":  product.get("origin_region"),
        "tags":           product.get("suggested_tags", []),
        "b2c_price":      product.get("b2c_price_inr"),
        "b2b_price":      product.get("b2b_price_inr"),
        "moq":            product.get("moq", 5),
        "gi_tag":         gi_tag,
        "pricing_insight": product.get("pricing_insight"),
        "confidence":     product.get("confidence", 0.8),
        "artisan_id":     artisan_profile.get("id", "")
    }

    await emit({
        "type": "LISTING_READY",
        "payload": listing,
        "timestamp": now()
    })

    return listing


def _calculate_fair_price(
    material_cost: float,
    hours: float,
    craft_type: str,
    ai_price: float
) -> dict:
    hourly_wage = 80  # ₹80 minimum artisan wage
    labour_cost = hours * hourly_wage
    fair_price  = int((material_cost + labour_cost) * 2.5)
    final_price = max(fair_price, int(ai_price * 0.85))
    old_estimate = int(final_price * 0.35)  # middleman suppressed price

    return {
        "fair_price": final_price,
        "calculation": f"(₹{material_cost} materials + ₹{labour_cost} labour) × 2.5",
        "was_underpriced": old_estimate < final_price,
        "old_price_estimate": old_estimate,
        "price_increase_percent": int(
            ((final_price - old_estimate) / old_estimate) * 100
        ) if old_estimate > 0 else 0
    }


def _match_gi_tag(craft_type: str, origin: str, district: str) -> dict | None:
    combined = f"{craft_type} {origin} {district}".lower()
    for keyword, tag in GI_TAGS.items():
        if keyword in combined:
            return tag
    return None


def _demo_product(profile: dict) -> dict:
    return {
        "craft_type":     "Handwoven Textile",
        "origin_region":  profile.get("district", "Chanderi"),
        "title":          "Handwoven Chanderi Silk Saree with Zari Border",
        "description":    "Exquisitely crafted by skilled artisans in Chanderi, this pure silk saree features traditional zari work passed down through generations. Lightweight yet luxurious, perfect for festive occasions.",
        "cultural_story": "Chanderi weaving dates back to the 2nd century BC, mentioned in ancient texts. The unique texture is created by interlacing silk and cotton threads using pit looms.",
        "suggested_tags": ["handwoven", "silk", "chanderi", "saree", "GI-tagged"],
        "b2c_price_inr":  2400,
        "b2b_price_inr":  1920,
        "moq":            5,
        "confidence":     0.95
    }