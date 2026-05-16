"""
instamart_fetcher.py
"""

import asyncio
from playwright.async_api import async_playwright

INSTAMART_URL = "https://www.swiggy.com/instamart"
SEARCH_API_PATH = "/api/instamart/search"

class UserConfig:
    PINCODE = "110075"
    MAX_PRODUCTS = 50
    HEADLESS = False
    SLOW_MO = 150

def _extract_products(data, limit=50):
    extracted = []
    seen_ids = set()

    def recurse(obj):
        if len(extracted) >= limit:
            return
        if isinstance(obj, dict):
            name = obj.get("display_name") or obj.get("name") or obj.get("product_name")
            price = obj.get("price") or obj.get("final_price") or obj.get("selling_price")
            pid = obj.get("id") or obj.get("product_id")
            if name and price and pid and pid not in seen_ids:
                seen_ids.add(pid)
                extracted.append({
                    "platform": "instamart",
                    "product_id": pid,
                    "name": name,
                    "brand": obj.get("brand") or obj.get("brand_name"),
                    "selling_price": price / 100 if price > 1000 else price,  # handle paise
                    "mrp": obj.get("mrp") or obj.get("original_price"),
                    "packsize": obj.get("quantity") or obj.get("weight") or obj.get("variant"),
                    "available_quantity": obj.get("inventory") or obj.get("stock"),
                    "in_stock": (obj.get("inventory", 1) or obj.get("in_stock", 1)) != 0,
                    "rating": obj.get("rating"),
                    "image": obj.get("image") or obj.get("image_url") or obj.get("thumbnail"),
                    "raw": obj
                })
            for v in obj.values():
                recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)

    recurse(data)
    return extracted

async def _dismiss_modals(page):
    for selector in [
        '[aria-label="close"]', '.close-btn',
        'button:has-text("Skip")', 'button:has-text("Maybe Later")',
        'button:has-text("Not Now")', 'button:has-text("Dismiss")',
        '[data-testid="modal-close"]'
    ]:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=1000):
                await btn.click()
                await page.wait_for_timeout(500)
        except Exception:
            pass

async def _handle_location(page, pincode):
    try:
        print(f"[instamart] setting pincode: {pincode}")
        await page.wait_for_timeout(3000)
        await _dismiss_modals(page)

        opened = False
        for selector in ['text=Location', 'text=Select location', 'button:has-text("Location")', '[class*="location"]']:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=2000):
                    await btn.click()
                    opened = True
                    break
            except Exception:
                continue

        if not opened:
            print("[instamart] could not open location modal")
            return

        await page.wait_for_timeout(2000)

        filled = False
        for selector in ['input[placeholder*="search" i]', 'input[placeholder*="location" i]', 'input[placeholder*="pincode" i]', 'input[type="text"]']:
            try:
                input_box = page.locator(selector).first
                if await input_box.is_visible(timeout=2000):
                    await input_box.fill(pincode)
                    filled = True
                    break
            except Exception:
                continue

        if not filled:
            print("[instamart] could not fill pincode")
            return

        await page.wait_for_timeout(3000)

        clicked = False
        suggestions = page.locator(f"text={pincode}")
        count = await suggestions.count()
        for i in range(count):
            try:
                s = suggestions.nth(i)
                if await s.is_visible():
                    text = await s.inner_text()
                    print(f"[instamart] found suggestion: {text}")
                    await s.click()
                    clicked = True
                    print("[instamart] location selected")
                    break
            except Exception:
                continue

        if not clicked:
            print("[instamart] could not click location suggestion")
            return

        await page.wait_for_timeout(4000)
        await _dismiss_modals(page)

    except Exception as e:
        print(f"[instamart] location error: {e}")

async def search_instamart(query, config=UserConfig()):
    captured_products = []

    try:
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
                try:
                    if SEARCH_API_PATH not in response.url:
                        return
                    content_type = response.headers.get("content-type", "")
                    if "application/json" not in content_type:
                        return
                    data = await response.json()
                    products = _extract_products(data, limit=config.MAX_PRODUCTS)
                    if products:
                        captured_products.extend(products)
                        print(f"[instamart] captured {len(products)} products from: {response.url}")
                except Exception:
                    pass

            page.on("response", handle_response)

            print("[instamart] opening Instamart...")
            await page.goto(INSTAMART_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)
            await _handle_location(page, config.PINCODE)

            # ✅ Navigate directly to search URL
            print(f"[instamart] searching: {query}")
            search_url = f"https://www.swiggy.com/instamart/search?custom_back=true&query={query}"
            await page.goto(search_url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(7000)

            await browser.close()

        return captured_products

    except Exception as e:
        print(f"[instamart] fatal error: {e}")
        return []

if __name__ == "__main__":
    async def main():
        products = await asyncio.wait_for(search_instamart("Lotus Biscoff"), timeout=60)
        print(f"\nFound {len(products)} products:\n")
        for p in products[:10]:
            stock = "✓" if p["in_stock"] else "✗"
            print(f"{stock} {str(p['name'])[:55]:<55} {str(p['selling_price']):>8} ({p['packsize']})")
    asyncio.run(main())