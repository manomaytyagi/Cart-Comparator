from rapidfuzz import fuzz
import re

# Only structural/packaging words that are NEVER variant-defining.
# Do NOT add adjectives like crunchy, crispy, dark, white — those distinguish variants.
STOPWORDS = {
    "pack", "pcs", "piece", "pieces", "combo", "set",
    "new", "fresh", "offer", "free", "buy", "get",
}

def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    name = re.sub(r"[^a-z0-9\s]", " ", name)
    # Strip quantity tokens (75g, 200ml, 1kg etc.) from name — quantity is scored separately
    name = re.sub(r"\b\d+(\.\d+)?\s*(kg|g|l|ml|mg|oz|lb|gm|ltr)\b", " ", name)
    words = [w for w in name.split() if w not in STOPWORDS]
    return " ".join(words)


def extract_brand(query: str) -> str:
    """
    Heuristic: brand is usually the first word (or two) before a known product name.
    Returns lowercased first word as the brand token.
    """
    words = normalize_name(query).split()
    return words[0] if words else ""


def normalize_quantity(text):
    if not text:
        return None
    text = text.lower()
    text = text.replace(",", " ")
    text = re.sub(r"[()]", " ", text)
    text = re.sub(r"\s+", " ", text)

    # MULTIPACK: e.g. "3 x 50g", "2x200ml"
    match = re.search(r'(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*(kg|g|l|ml)', text)
    if match:
        count = int(match.group(1))
        value = float(match.group(2))
        unit = match.group(3)
        total = count * value
        if unit == "kg":
            total *= 1000; unit = "g"
        elif unit == "l":
            total *= 1000; unit = "ml"
        return {"value": total, "unit": unit}

    # SINGLE: e.g. "75g", "1.5l", "500 ml"
    match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|l|ml|gm|ltr)', text)
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        # Normalize aliases
        if unit == "gm": unit = "g"
        if unit == "ltr": unit = "ml"; value *= 1000
        if unit == "kg": value *= 1000; unit = "g"
        if unit == "l": value *= 1000; unit = "ml"
        return {"value": value, "unit": unit}

    return None


def compute_quantity_score(query_quantity, candidate_quantity):
    # Both unparseable — neutral, not a penalty
    if not query_quantity and not candidate_quantity:
        return 70

    # One side unparseable — mild penalty, don't destroy the match
    if not query_quantity or not candidate_quantity:
        return 70

    # Unit mismatch after full normalization → definitely wrong size family
    if query_quantity["unit"] != candidate_quantity["unit"]:
        return 0

    q = query_quantity["value"]
    c = candidate_quantity["value"]
    diff_percent = (abs(q - c) / max(q, c)) * 100
    return max(0, 100 - diff_percent)


def compute_name_score(normalized_query: str, normalized_candidate: str) -> float:
    """
    Combines two signals:
    - token_sort_ratio: good recall, handles word-order variation
    - WRatio: precision-aware, penalizes length/token mismatches

    Then applies an extra-token penalty: if the candidate has significantly
    more tokens than the query, scale the score down — avoids bloated product
    names (e.g. "... Combo Edition Gift Pack 300g") scoring high against a
    tight query.
    """
    if not normalized_query or not normalized_candidate:
        return 0.0

    token_sort = fuzz.token_sort_ratio(normalized_query, normalized_candidate)
    wratio     = fuzz.WRatio(normalized_query, normalized_candidate)

    base_score = 0.5 * token_sort + 0.5 * wratio

    # Extra-token penalty
    q_tokens = len(normalized_query.split())
    c_tokens = len(normalized_candidate.split())
    if c_tokens > q_tokens:
        # Scale penalty: each extra token beyond query length costs up to ~5 points,
        # capped so we never zero out a good match purely on length
        extra = c_tokens - q_tokens
        penalty = min(extra * 4, 20)
        base_score = max(0, base_score - penalty)

    return base_score


def match_products(query, products, threshold=75):
    matches = []

    normalized_query = normalize_name(query)
    query_quantity   = normalize_quantity(query)
    brand_token      = extract_brand(query)

    for product in products:
        candidate_name = product.get("name", "")
        if not candidate_name:
            continue

        candidate_text     = f"{candidate_name} {product.get('packsize', '') or ''}"
        normalized_candidate = normalize_name(candidate_text)

        # --- Brand check ---
        # If the query has a clear brand token and it's completely absent from
        # the candidate, apply a hard penalty — brand is non-negotiable.
        brand_penalty = 0
        if brand_token and brand_token not in normalized_candidate:
            brand_penalty = 25

        # --- Name score ---
        name_score = compute_name_score(normalized_query, normalized_candidate)

        # --- Quantity score ---
        candidate_quantity = normalize_quantity(candidate_text)
        quantity_score     = compute_quantity_score(query_quantity, candidate_quantity)

        # --- Final score ---
        # Brand is embedded in name_score already; brand_penalty is a hard deduction
        # applied after weighting so it can't be washed out by a great quantity match.
        raw_score  = 0.55 * name_score + 0.45 * quantity_score
        final_score = max(0, raw_score - brand_penalty)

        product["match_score"]    = round(final_score, 2)
        product["name_score"]     = round(name_score, 2)
        product["quantity_score"] = round(quantity_score, 2)

        if final_score >= threshold:
            matches.append(product)

    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches