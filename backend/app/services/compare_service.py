from app.services.fetchers.blinkit_fetcher import search_blinkit
# from app.services.fetchers.instamart_fetcher import search_instamart
from app.services.fetchers.zepto_fetcher import search_zepto
from app.services.product_matcher import match_products
import asyncio

async def compare_products(extracted_products, pincode):
    total_price = {"zepto": 0, "blinkit": 0}
    available_cart = {"zepto": [], "blinkit": []}
    unavailable_products = []
    results = []

    for product in extracted_products:
        print(f"DEBUG product: {product}")
        query = (product["name"] + " " + product.get("quantity", ""))
        print(f"\nSearching for: {query}")

        # --- Sequential fetches: one browser at a time ---
        try:
            zepto_products = await asyncio.wait_for(search_zepto(query, pincode), timeout=90)
        except Exception as e:
            print(f"[zepto] fetch failed: {e}")
            zepto_products = []

        try:
            blinkit_products = await asyncio.wait_for(search_blinkit(query, pincode), timeout=90)
        except Exception as e:
            print(f"[blinkit] fetch failed: {e}")
            blinkit_products = []

        # try:
        #     instamart_products = await asyncio.wait_for(search_instamart(query), timeout=90)
        # except Exception as e:
        #     print(f"[instamart] fetch failed: {e}")
        #     instamart_products = []
        # -------------------------------------------------

        print(f"Zepto products: {len(zepto_products)}")
        print(f"Blinkit products: {len(blinkit_products)}")
        # print(f"Instamart products: {len(instamart_products)}")

        matches = {
            "zepto": match_products(query, zepto_products, 60),
            "blinkit": match_products(query, blinkit_products, 60),
            # "instamart": match_products(query, instamart_products, 60)
        }

        product_result = {  "query": query,
                            "original_price": product.get("original_price"),
                            "discounted_price": product.get("discounted_price"),
                            "matches": {}, 
                            "best_match": None
                        }
        best_price = float("inf")
        best_platform = None

        print(f"Zepto matches: {len(matches['zepto'])}")
        print(f"Blinkit matches: {len(matches['blinkit'])}")
        # print(f"Instamart matches: {len(matches['instamart'])}")

        for app, app_matches in matches.items():
            if not app_matches:
                product_result["matches"][app] = {"found": False}
                continue

            print(f"\n===== {app.upper()} MATCHES =====")

            for m in app_matches[:3]:
                print({
                    "name": m.get("name"),
                    "match_score": m.get("match_score"),
                    "name_score": m.get("name_score"),
                    "quantity_score": m.get("quantity_score"),
                    "packsize": m.get("packsize")
                })

            best_match = app_matches[0]
            if not best_match.get("in_stock", True):
                product_result["matches"][app] = {"found": True, "in_stock": False, "product": best_match}
                continue

            quantity_str = str(product.get("quantity", "1")).strip()
            try:
                cart_qty = int(quantity_str.split("(")[0].strip())
            except (ValueError, TypeError, IndexError):
                cart_qty = 1

            price = best_match.get("selling_price", 0)
            total_price[app] += price * cart_qty
            available_cart[app].append({
                "name": best_match.get("name"),
                "unit price": price,
                "quantity": cart_qty,
                "total": price * cart_qty
            })
            product_result["matches"][app] = {"found": True, "in_stock": True, "product": best_match}

            if price < best_price:
                best_price = price
                best_platform = app

        if best_platform is None:
            unavailable_products.append(query)
        else:
            product_result["best_match"] = {"platform": best_platform, "price": best_price}

        results.append(product_result)

    valid_totals = {app: price for app, price in total_price.items() if price > 0}
    if valid_totals:
        best_app = min(valid_totals, key=valid_totals.get)
        min_price = valid_totals[best_app]
    else:
        best_app = None
        min_price = 0

    return {
        "best_app": best_app,
        "best_total_price": min_price,
        "platform_totals": total_price,
        "available_cart": available_cart,
        "unavailable_products": unavailable_products,
        "detailed_results": results
    }