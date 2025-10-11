# nl_parser.py
import re

def normalize_price(value_str):
    value_str = value_str.lower().strip().replace(",", "")
    match = re.match(r"(\d+(?:\.\d+)?)(\s*(m|million|k))?", value_str)
    if not match:
        return None

    number = float(match.group(1))
    suffix = match.group(3)

    if suffix in ['m', 'million']:
        number *= 1_000_000
    elif suffix == 'k':
        number *= 1_000

    return int(number)

def parse_natural_query(query):
    query = query.lower()
    filters = {}

    # Purpose
    if "rent" in query:
        filters["purpose"] = "for-rent"
    elif any(word in query for word in ["buy", "sale", "own", "purchase"]):
        filters["purpose"] = "for-sale"

    # Rooms
    match = re.search(r"(\d+)\s*(bed|bedroom|rooms?)", query)
    if match:
        filters["rooms"] = int(match.group(1))

    # Baths
    match = re.search(r"(\d+)\s*(bath|bathroom)", query)
    if match:
        filters["baths"] = int(match.group(1))

    # Price - Under
    match = re.search(r"(under|less than|max(?:imum)?)\s+(\d+(?:\.\d+)?(?:\s*(m|million|k))?)", query)
    if match:
        value = normalize_price(match.group(2))
        if value:
            filters["max_price"] = value

    # Price - Over
    match = re.search(r"(above|more than|min(?:imum)?)\s+(\d+(?:\.\d+)?(?:\s*(m|million|k))?)", query)
    if match:
        value = normalize_price(match.group(2))
        if value:
            filters["min_price"] = value

    # Price - Between
    match = re.search(r"between\s+(\d+(?:\.\d+)?)([mk]?)\s+(and|to|-)\s+(\d+(?:\.\d+)?)([mk]?)", query)
    if match:
        min_val = float(match.group(1))
        max_val = float(match.group(4))
        if match.group(2) == 'm':
            min_val *= 1_000_000
        elif match.group(2) == 'k':
            min_val *= 1_000
        if match.group(5) == 'm':
            max_val *= 1_000_000
        elif match.group(5) == 'k':
            max_val *= 1_000
        filters["min_price"] = int(min_val)
        filters["max_price"] = int(max_val)

    # Area (in sqft)
    match = re.search(r"area\s*(of|>=|at least|minimum)?\s*(\d+)", query)
    if match:
        filters["min_area"] = int(match.group(2))

    # Property type
    types = ["apartment", "villa", "townhouse", "penthouse", "land", "office", "shop", "warehouse"]
    for t in types:
        if t in query:
            filters["property_type"] = t
            break

    # Location (naively extract last word if it matches UAE cities)
    locations = ["dubai", "abu dhabi", "sharjah", "ajman", "ras al khaimah", "fujairah", "umm al quwain"]
    for loc in locations:
        if loc in query:
            filters["location"] = loc.title()
            break

    return filters



