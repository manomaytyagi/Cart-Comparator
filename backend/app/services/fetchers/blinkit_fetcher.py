"""
blinkit_fetcher.py
"""

import asyncio
from playwright.async_api import async_playwright

BLINKIT_URL = "https://blinkit.com"
SEARCH_API_PATH = "/v1/layout/search"

class UserConfig:
    PINCODE = "110075"
    MAX_PRODUCTS = 50
    HEADLESS = True
    SLOW_MO = 150

def _parse_price(value):
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, dict):
        value = value.get("text") or value.get("value") or ""
    if not isinstance(value, str):
        value = str(value)
    digits = ''.join(filter(str.isdigit, value))
    return int(digits or 0)

def _extract_products(response_json, limit=50):
    extracted_products = []
    snippets = response_json.get("response", {}).get("snippets", [])
    for snippet in snippets:
        if snippet.get("widget_type") != "product_card_snippet_type_2":
            continue
        try:
            data = snippet.get("data", {})
            discounted = (
                data.get("price")
                or data.get("discounted_price")
                or data.get("final_price")
                or data.get("selling_price")
            )
            mrp = data.get("mrp") or data.get("normal_price") or data.get("original_price")
            extracted_products.append({
                "platform": "blinkit",
                "product_id": data.get("product_id"),
                "merchant_id": data.get("merchant_id"),
                "name": data.get("name", {}).get("text"),
                "brand": data.get("brand_name", {}).get("text"),
                # Use discounted/current price for comparisons, not MRP.
                "selling_price": _parse_price(discounted) or _parse_price(data.get("normal_price")),
                "mrp": _parse_price(mrp) or None,
                "packsize": data.get("variant", {}).get("text"),
                "available_quantity": data.get("inventory"),
                "in_stock": not data.get("is_sold_out", True),
                "rating": data.get("rating", {}).get("bar", {}).get("value"),
                "rating_count": data.get("rating", {}).get("bar", {}).get("title", {}).get("text"),
                "image": data.get("image", {}).get("url"),
                "raw": data
            })
            if len(extracted_products) >= limit:
                break
        except Exception as e:
            print(f"[blinkit] parsing error: {e}")
    return extracted_products

async def _handle_location(page, pincode):
    try:
        print(f"[blinkit] setting pincode: {pincode}")
        await page.wait_for_timeout(3000)

        # Blinkit shows pincode input directly on homepage
        location_selectors = [
            '[data-testid="address-button"]',
            'button:has-text("delivery")',
            'button:has-text("Delivery")',
            'button:has-text("Select location")',
            '[class*="LocationBar"]',
        ]
        clicked = False
        for selector in location_selectors:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=2000):
                    await btn.click()
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            print("[blinkit] could not open location modal")
            return

        await page.wait_for_timeout(2000)

        for selector in ['input[type="text"]', 'input[placeholder*="pin" i]', 'input[placeholder*="search" i]']:
            try:
                input_box = page.locator(selector).first
                if await input_box.is_visible(timeout=2000):
                    await input_box.fill(pincode)
                    break
            except Exception:
                continue

        await page.wait_for_timeout(3000)

        # Click first suggestion
        for selector in ['[data-testid="location-row"]', '[class*="LocationRow"]', '[class*="location"]']:
            try:
                suggestion = page.locator(selector).first
                if await suggestion.is_visible(timeout=2000):
                    await suggestion.click()
                    print("[blinkit] location selected")
                    break
            except Exception:
                continue

        await page.wait_for_timeout(3000)

    except Exception as e:
        print(f"[blinkit] location error: {e}")

async def search_blinkit(query, pincode: str = UserConfig.PINCODE, config=UserConfig()):
    config.PINCODE = pincode
    captured_products = []
    seen_ids = set()  # ✅ deduplicate

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.0.0 Mobile Safari/537.36"
            ),
            viewport={"width": 390, "height": 844},
            locale="en-IN"
        )
        page = await context.new_page()

        async def handle_response(response):
            if SEARCH_API_PATH not in response.url:
                return
            try:
                data = await response.json()
                products = _extract_products(data, limit=config.MAX_PRODUCTS)
                for product in products:
                    pid = product.get("product_id")
                    if pid in seen_ids:
                        continue
                    seen_ids.add(pid)
                    captured_products.append(product)
                if products:
                    print(f"[blinkit] captured {len(captured_products)} products total")
            except Exception as e:
                print(f"[blinkit] response parse error: {e}")

        page.on("response", handle_response)

        print("[blinkit] opening Blinkit...")
        await page.goto(BLINKIT_URL, wait_until="domcontentloaded")
        await _handle_location(page, pincode)

        print(f"[blinkit] searching: {query}")
        await page.goto(
            f"https://blinkit.com/s/?q={query}",
            wait_until="networkidle"
        )
        await page.wait_for_timeout(5000)
        await browser.close()

    return captured_products

if __name__ == "__main__":
    async def main():
        products = await asyncio.wait_for(search_blinkit("Lotus Biscoff"), timeout=60)
        print(f"\nFound {len(products)} products:\n")
        for p in products[:10]:
            stock = "✓" if p["in_stock"] else "✗"
            print(f"{stock} {str(p['name'])[:55]:<55} {str(p['selling_price']):>8} ({p['packsize']})")
    asyncio.run(main())