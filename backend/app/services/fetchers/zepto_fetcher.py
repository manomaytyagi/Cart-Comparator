"""
zepto_fetcher.py
"""

import asyncio
import re
from playwright.async_api import async_playwright

ZEPTO_URL = "https://www.zepto.com"
SEARCH_API_PATH = "/user-search-service/api/v3/search"

class UserConfig:
    PINCODE = "110075"
    MAX_PRODUCTS = 100
    HEADLESS = True
    SLOW_MO = 150

ZEPTO_STOPWORDS = {
    # descriptors that narrow results too much on zepto
    "original", "fresh", "classic", "premium", "delicious",
    "crunchy", "creamy", "combo", "pack", "family", "style", "cone",
    "caramelized", "caramel", "roasted", "salted", "unsalted",
    "flavour", "flavor", "flavored", "flavoured", "wholegrain",
    "whole", "grain", "natural", "organic", "lite", "light", "dark",
    "white", "mini", "crispy", "soft", "thin", "thick", "filled",
    "coated", "dipped", "assorted", "variety", "special", "extra", "super",
}

# Matches pure quantity tokens like "75g", "1kg", "200ml", "2pcs"
_QTY_RE = re.compile(r"^\d+(\.\d+)?(g|kg|ml|l|mg|oz|lb|pc|pcs|piece|pieces|gm|ltr)?$")

def optimize_zepto_query(query):
    """
    Keep brand + one core product noun only (max 2 words).
    Zepto search degrades badly with 3+ specific tokens — broad queries
    return more results for the matcher to filter downstream.
    """
    if not query:
        return ""
    query = query.lower()
    query = re.sub(r"[^a-z0-9\s]", " ", query)
    words = query.split()
    words = [w for w in words if w not in ZEPTO_STOPWORDS and not _QTY_RE.match(w)]
    seen = set()
    filtered = []
    for word in words:
        if word not in seen:
            filtered.append(word)
            seen.add(word)
    return " ".join(filtered[:2])

def extract_zepto_products(response_json, limit=50):
    extracted_products = []
    for widget in response_json.get("layout", []):
        widget_id = widget.get("widgetId", "")
        widget_name = widget.get("widgetName", "")
        if widget_id != "PRODUCT_GRID" and not widget_name.startswith("SEARCHED_PRODUCTS"):
            continue
        items = (
            widget.get("data", {})
            .get("resolver", {})
            .get("data", {})
            .get("items", [])
        )
        for item in items:
            pr = item.get("productResponse")
            if not pr:
                continue
            try:
                product_info = pr.get("product", {})
                variant_info = pr.get("productVariant", {})
                extracted_products.append({
                    "platform": "zepto",
                    "product_id": pr.get("id"),
                    "store_id": pr.get("storeId"),
                    "name": product_info.get("name"),
                    "brand": product_info.get("brand"),
                    "selling_price": pr.get("discountedSellingPrice", 0) / 100,
                    "mrp": pr.get("mrp", 0) / 100,
                    "discount_percent": pr.get("discountPercent", 0),
                    "in_stock": not pr.get("outOfStock", True),
                    "available_quantity": pr.get("availableQuantity", 0),
                    "packsize": variant_info.get("formattedPacksize"),
                    "rating": variant_info.get("ratingSummary", {}).get("averageRating"),
                    "rating_count": variant_info.get("ratingSummary", {}).get("totalRatings"),
                    "image": variant_info.get("images", [{}])[0].get("path"),
                    "raw": pr
                })
                if len(extracted_products) >= limit:
                    return extracted_products
            except Exception as e:
                print(f"[zepto] parse error: {e}")
    return extracted_products

async def dismiss_modals(page):
    
    # remove known modal containers by id
    await page.evaluate("""
        ['zui-modal-undefined'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.remove();
        });
        document.querySelectorAll('[data-vaul-overlay]').forEach(e => e.remove());
    """)
    
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

async def set_location(page, pincode):
    try:
        print(f"[zepto] setting location: {pincode}")
        await page.wait_for_timeout(3000)
        await dismiss_modals(page)

        opened = False
        for selector in ['text=Select Location', 'button:has-text("Location")', '[data-testid="location-button"]']:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=2000):
                    await btn.click()
                    opened = True
                    break
            except Exception:
                continue

        if not opened:
            print("[zepto] location button not found")
            return

        await page.wait_for_timeout(2000)

        input_box = None
        for selector in ['input[placeholder*="pincode" i]', 'input[placeholder*="location" i]', 'input[type="text"]']:
            try:
                box = page.locator(selector).first
                if await box.is_visible(timeout=2000):
                    input_box = box
                    break
            except Exception:
                continue

        if not input_box:
            print("[zepto] location input not found")
            return

        await input_box.fill("")
        await page.wait_for_timeout(500)
        await input_box.type(pincode, delay=100)
        await page.wait_for_timeout(3000)

        # Click the first address-search-item suggestion
        clicked = False
        try:
            suggestion = page.locator('[data-testid="address-search-item"]').first
            await suggestion.wait_for(state="visible", timeout=5000)
            await suggestion.click(force=True)
            clicked = True
            print(f"[zepto] location selected via address-search-item")
        except Exception as e:
            print(f"[zepto] address-search-item click failed: {e}")

        if not clicked:
            print("[zepto] no matching location suggestion")
            return
        

        await page.wait_for_timeout(4000)
        await dismiss_modals(page)

    except Exception as e:
        print(f"[zepto] location error: {e}")

async def search_zepto(query, pincode: str = UserConfig.PINCODE):
    optimized_query = optimize_zepto_query(query)
    print(f"[zepto] raw query: {query}")
    print(f"[zepto] optimized query: {optimized_query}")

    captured_products = []
    seen_ids = set()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=UserConfig.HEADLESS,
                slow_mo=UserConfig.SLOW_MO
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
                    data = await response.json()
                    products = extract_zepto_products(data, limit=UserConfig.MAX_PRODUCTS)
                    for product in products:
                        pid = product.get("product_id")
                        if pid in seen_ids:
                            continue
                        seen_ids.add(pid)
                        captured_products.append(product)
                    if products:
                        print(f"[zepto] captured {len(captured_products)} products")
                except Exception as e:
                    print(f"[zepto] response error: {e}")

            page.on("response", handle_response)

            print("[zepto] opening website...")
            await page.goto(ZEPTO_URL, wait_until="domcontentloaded", timeout=60000)
            await set_location(page, pincode)
            await dismiss_modals(page)

            # ✅ Click the <a href="/search"> link, then type in real input
            print(f"[zepto] searching: {optimized_query}")

            try:
                await page.click(
                    '[data-testid="search-bar-icon"], a[href="/search"]',
                    timeout=5000
                )
                # Wait for navigation to /search page before looking for input
                await page.wait_for_url("**/search**", timeout=8000)
                await page.wait_for_timeout(1000)

                # Target the first visible text input on the /search page
                search_input = page.locator('input[type="text"], input:not([type])').first
                await search_input.wait_for(state="visible", timeout=8000)
                await search_input.click()
                await search_input.fill("")

                await search_input.type(optimized_query, delay=120)
                await page.wait_for_timeout(800)
                # Press Enter to dismiss the autocomplete dropdown and trigger
                # the actual search results page + API call. Without this Zepto
                # just sits on the suggestion screen and never fires the search API.
                await page.keyboard.press("Enter")
                
                print(f"[zepto] query submitted, waiting for API response...")

                # Wait until handle_response has actually populated captured_products
                # Poll every 500ms for up to 20s — this avoids the race between
                # wait_for_response (which resolves on HTTP headers) and the async
                # body parsing + extraction inside handle_response
                for _ in range(40):
                    await page.wait_for_timeout(500)
                    if captured_products:
                        print(f"[zepto] extraction confirmed: {len(captured_products)} products")
                        break
                else:
                    print("[zepto] timeout: no products captured after 20s")

            except Exception as e:
                print(f"[zepto] search failed: {e}")

            await browser.close()
            return captured_products

    except Exception as e:
        print(f"[zepto] fatal error: {e}")
        return []

if __name__ == "__main__":
    async def main():
        products = await search_zepto("Lotus Biscoff Original Caramelized Cookie 75g")
        print("\n========== PRODUCTS ==========\n")
        for p in products[:10]:
            print({"name": p.get("name"), "price": p.get("selling_price"), "packsize": p.get("packsize"), "stock": p.get("in_stock")})
    asyncio.run(main())