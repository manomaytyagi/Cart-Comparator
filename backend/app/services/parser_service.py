"""
parser_service.py

App-agnostic cart parser using Gemini 2.5 Flash Vision.
Uses new google-genai SDK (google.generativeai is deprecated).
Falls back to regex heuristics if Vision call fails.

Returned format (list of dicts):
    [
        {
            "name": str,
            "quantity": str | None,   # e.g. "1 pack (75 g)"
            "original_price": int | None,
            "discounted_price": int,  # the price actually paid
        },
        ...
    ]

Setup:
    pip install google-genai pillow

    Set env var before running:
        Windows:  set kvmt=YOUR_ACTUAL_API_KEY
        Mac/Linux: export kvmt=YOUR_ACTUAL_API_KEY
"""

import re
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()  # reads .env from project root into os.environ

# ── Config ────────────────────────────────────────────────────────────────────

client = genai.Client(api_key=os.environ["kvmt"])

GEMINI_MODEL = "gemini-2.5-flash"

PROMPT = """You are a cart extraction assistant.
Given a screenshot of any quick-commerce cart (Blinkit, Zepto, Swiggy Instamart, etc.),
extract ONLY the cart line-items — skip coupons, banners, delivery info, totals.

Return ONLY a JSON array, no explanation, no markdown fences.
Schema per item:
{
  "name": "<product name, clean and full>",
  "quantity": "<pack size or unit shown, e.g. '1 pack (75 g)' or null, Return the quantity of items being brought then the quantity as in weight or volume in the brackets only. if quantity is one retuurn 1 (weight/volume), so return format is quantity (weight/volume)>",
  "original_price": <integer or null>,
  "discounted_price": <integer — the final price the user pays>
}"""


# ── Gemini Vision call ────────────────────────────────────────────────────────

def parse_with_vision(image_path: str) -> list[dict]:
    """
    Primary parser — sends image to Gemini 2.5 Flash Vision.
    Returns parsed product list.
    Raises on network / API error (caller falls back to regex).
    """
    image = Image.open(image_path)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[PROMPT, image],
    )

    raw_text = response.text.strip()

    # Strip markdown fences if model adds them despite instructions
    raw_text = re.sub(r"^```[a-z]*\n?", "", raw_text)
    raw_text = re.sub(r"\n?```$", "", raw_text)

    products = json.loads(raw_text)

    # Normalise — ensure discounted_price always present
    for p in products:
        if p.get("discounted_price") is None and p.get("original_price"):
            p["discounted_price"] = p["original_price"]

    return products


# ── Regex fallback ────────────────────────────────────────────────────────────

_NOISE_PATTERNS = re.compile(
    r"""(
        delivering\s+in
        | forgot\s+something
        | add\s+more\s+items
        | coupons?\s*&?\s*offers?
        | view\s+all
        | apply
        | locked
        | shop\s+for
        | save\s+₹
        | cashback
        | schedule
        | pay\s+(online|cash|upi)
        | to\s+pay
        | yay!
        | unlock
    )""",
    re.IGNORECASE | re.VERBOSE,
)

_QUANTITY_PATTERN = re.compile(
    r"^\d+\s*(pack|pc|pcs|piece|pieces|g|kg|ml|l|litre|liter)\b",
    re.IGNORECASE,
)

_PRICE_PATTERN = re.compile(r"₹\s*(\d+)")


def _is_noise(line: str) -> bool:
    return bool(_NOISE_PATTERNS.search(line))


def _is_quantity(line: str) -> bool:
    return bool(_QUANTITY_PATTERN.match(line))


def parse_with_regex(raw_text: str) -> list[dict]:
    """
    Fallback parser for plain OCR text.
    Less accurate — use only when Vision call fails.
    """
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    products = []
    name_parts: list[str] = []
    quantity: str | None = None
    prices_in_window: list[int] = []

    def flush():
        nonlocal name_parts, quantity, prices_in_window
        if name_parts and prices_in_window:
            original = prices_in_window[0] if len(prices_in_window) > 1 else None
            discounted = prices_in_window[-1]
            products.append({
                "name": " ".join(name_parts),
                "quantity": quantity,
                "original_price": original,
                "discounted_price": discounted,
            })
        name_parts = []
        quantity = None
        prices_in_window = []

    for line in lines:
        if _is_noise(line):
            flush()
            continue

        found_prices = [int(m) for m in _PRICE_PATTERN.findall(line)]

        if found_prices:
            prices_in_window.extend(found_prices)
            text_before = _PRICE_PATTERN.sub("", line).strip().rstrip("₹").strip()
            if text_before and not _is_quantity(text_before):
                name_parts.append(text_before)
            if not text_before:
                flush()
        elif _is_quantity(line):
            quantity = line
        else:
            if prices_in_window:
                flush()
            name_parts.append(line)

    flush()
    return products


# ── Public API ────────────────────────────────────────────────────────────────

def parse_cart_image(image_path: str) -> list[dict]:
    """
    Primary entry point.
    1. Try Gemini 2.5 Flash Vision (accurate, app-agnostic).
    2. Fall back to regex on any error.
    """
    try:
        return parse_with_vision(image_path)
    except Exception as e:
        print(f"[parser] Vision failed ({e}), falling back to regex.")
        from app.services.ocr_service import extract_text
        raw = extract_text(image_path)
        return parse_with_regex(raw)