import re


def simple_spell_correct(word, vocabulary, threshold=2):
    def distance(a, b):
        return sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))

    closest = min(vocabulary, key=lambda x: distance(word, x))
    return closest if distance(word, closest) <= threshold else None


def extract_price(text: str):
    text = text.lower().replace(",", "")
    price_min = None
    price_max = None

    def normalize_price(value_str):
        value_str = value_str.lower().strip()
        if "million" in value_str:
            return int(float(value_str.replace("million", "")) * 1_000_000)
        elif "m" in value_str:
            return int(float(value_str.replace("m", "")) * 1_000_000)
        elif "k" in value_str:
            return int(float(value_str.replace("k", "")) * 1_000)
        else:
            return int(re.sub(r"[^\d.]", "", value_str))

    # "between 2M and 4M"
    range_match = re.search(r"between\s+(\d+(?:\.\d+)?\s*[mk]?(?:illion)?)\s+and\s+(\d+(?:\.\d+)?\s*[mk]?(?:illion)?)",
                            text)
    if range_match:
        price_min = normalize_price(range_match.group(1))
        price_max = normalize_price(range_match.group(2))
        return price_min, price_max

    # "budget is 2 million" or "budget 500k"
    budget_match = re.search(r"(?:budget\s*(?:is|=)?|i can pay up to)\s*(\d+(?:\.\d+)?\s*[mk]?(?:illion)?)", text)
    if budget_match:
        price_max = normalize_price(budget_match.group(1))

    # "under 2M", "less than 3 million"
    max_match = re.search(r"(?:under|max(?:imum)?|less than)\s*(\d+(?:\.\d+)?\s*[mk]?(?:illion)?)", text)
    if max_match:
        price_max = normalize_price(max_match.group(1))

    # "above 1M", "at least 100k"
    min_match = re.search(r"(?:above|at least|more than|min(?:imum)?)\s*(\d+(?:\.\d+)?\s*[mk]?(?:illion)?)", text)
    if min_match:
        price_min = normalize_price(min_match.group(1))

    return price_min, price_max


def parse_user_input(text: str) -> dict:
    text = text.lower()

    purposes = []
    if "buy" in text or "sale" in text:
        purposes.append("for-sale")
    elif "rent" in text or "lease" in text:
        purposes.append("for-rent")

    completion_status = None
    rent_frequency = None
    if "ready" in text:
        completion_status = "Ready"
    elif "off-plan" in text:
        completion_status = "Off-Plan"
    elif "yearly" in text:
        rent_frequency = "Yearly"
    elif "monthly" in text:
        rent_frequency = "Monthly"
    elif "weekly" in text:
        rent_frequency = "Weekly"
    elif "daily" in text:
        rent_frequency = "Daily"

    # Property types
    property_keywords = ["apartment", "townhouse", "villa", "penthouse", "compound", "land", "floor", "building",
        "office", "shop", "warehouse", "labour", "bulk", "factory", "industrial", "mixed", "showroom", "commercial",
        "residential"]
    tokens = re.findall(r"\b[a-z]+\b", text)
    property_types = []

    for token in tokens:
        corrected = simple_spell_correct(token, property_keywords)
        if corrected:
            if corrected == "compound":
                property_types.append("Villa Compound")
            elif corrected == "labour":
                property_types.append("Labour Camp")
            elif corrected == "bulk":
                property_types.append("Bulk Unit")
            elif corrected == "industrial":
                property_types.append("Industrial Land")
            elif corrected == "mixed":
                property_types.append("Mixed Used Land")
            elif corrected == "commercial":
                property_types.append("Other Commercial")
            else:
                property_types.append(corrected.title())

    # Area
    area_match = re.search(r"(?:area\s*of|area)\s*(\d{3,6})", text)
    area = int(area_match.group(1)) if area_match else None

    # Rooms
    rooms = None
    room_match = re.search(r"(?:room[s]?|rom[s]?|rom)\s*(of)?\s*(\d+)", text)
    if room_match:
        rooms = int(room_match.group(2))

    # Baths
    baths = None
    bath_match = re.search(r"(?:bath[s]?|toilet[s]?|bathroom[s]?)\s*(of)?\s*(\d+)", text)
    if bath_match:
        baths = int(bath_match.group(2))

    # Location
    location_match = re.search(r"in\s+([a-zA-Z\s]+?)(?:\s+with|\s+area|\s+price|$)", text)
    location_query = location_match.group(1).strip().title() if location_match else ""

    # Price
    price_min, price_max = extract_price(text)

    return {"location_query": location_query, "area": area, "rooms": rooms, "baths": baths, "price_min": price_min,
        "price_max": price_max, "purposes": purposes, "property_types": list(set(property_types)),
        "completion_status": completion_status, "rent_frequency": rent_frequency}


user_input = "I want a apratment in Dubai with roms of 2, 2 baths, area 1200, under 3 million"
filters = parse_user_input(user_input)
print(filters)
user_input = "I want a villa in JVC between 2m and 4m with 3 bathrooms"
filters = parse_user_input(user_input)
print(filters)
user_input = "Looking for apartment, budget is 500k"
filters = parse_user_input(user_input)
print(filters)
user_input = "I don’t care about the price, just want 2 rooms and 1 bath"
filters = parse_user_input(user_input)
print(filters)
