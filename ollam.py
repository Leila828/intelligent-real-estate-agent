# nl_parser.py
import re
import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"


def _split_location_and_keywords(location_str):
    """
    Intelligently splits a location string into a main query and keywords.
    This helps handle nested locations like 'Carmen Villa in Victory Heights'.
    """
    location_str = location_str.strip()

    # Common separators for nested locations
    split_words = [" in ", ", "]

    for word in split_words:
        if word in location_str:
            parts = location_str.split(word)
            # The last part is often the main community/city
            main_location = parts[-1].strip()
            # The rest are keywords
            keywords = word.join(parts[:-1]).strip()
            return main_location, keywords

    # If no separator found, assume the whole thing is the main location
    return location_str, ""


def parse_natural_query(query):
    query = query.lower()
    filters = {}

    # Prioritize 'sale' over 'rent'
    if "buy" in query or "sale" in query or "own" in query:
        filters["purpose"] = "sale"
    elif "rent" in query:
        filters["purpose"] = "rent"

    # Property types
    property_types_map = {
        "townhouse": "townhouse", "penthouse": "penthouse", "hotel apartment": "hotel apartment",
        "villa": "villa", "house": "villa", "apartment": "apartment", "flat": "apartment",
        "building": "whole building", "warehouse": "warehouse", "office": "office",
        "land": "land", "plot": "land", "compound": "compound", "duplex": "duplex",
        "full floor": "full floor", "half floor": "half floor"
    }
    found_type = None
    for term, api_name in property_types_map.items():
        if term in query:
            found_type = api_name
            break
    if found_type:
        filters["property_type"] = found_type

    if "studio" in query:
        filters["beds"] = "0"
        filters["property_type"] = "apartment"

    # Bedrooms and Bathrooms
    beds_match = re.search(r"(\d+)\s*(bed|bedroom|rooms?)\b", query)
    if beds_match:
        filters["beds"] = beds_match.group(1)
    baths_match = re.search(r"(\d+)\s*(bath|bathroom|baths?)", query)
    if baths_match:
        filters["baths"] = baths_match.group(1)

    # Price ranges
    match_min_price = re.search(r"(over|above|more than)\s*(\d+(\.\d+)?)(\s*(million|m|thousand|k))?", query)
    if match_min_price:
        value = float(match_min_price.group(2))
        unit = match_min_price.group(5)
        if unit in ['million', 'm']:
            value *= 1_000_000
        elif unit in ['thousand', 'k']:
            value *= 1_000
        filters["min_price"] = int(value)

    match_max_price = re.search(r"(under|below|less than)\s*(\d+(\.\d+)?)(\s*(million|m|thousand|k))?", query)
    if match_max_price:
        value = float(match_max_price.group(2))
        unit = match_max_price.group(5)
        if unit in ['million', 'm']:
            value *= 1_000_000
        elif unit in ['thousand', 'k']:
            value *= 1_000
        filters["max_price"] = int(value)

    match_between_price = re.search(
        r"between\s*(\d+)(\s*(million|m|thousand|k)?)\s*(and|to|-)\s*(\d+)(\s*(million|m|thousand|k)?)", query)
    if match_between_price:
        min_val = float(match_between_price.group(1))
        max_val = float(match_between_price.group(5))
        min_unit = match_between_price.group(3)
        max_unit = match_between_price.group(7)
        if min_unit in ['million', 'm']:
            min_val *= 1_000_000
        elif min_unit in ['thousand', 'k']:
            min_val *= 1_000
        if max_unit in ['million', 'm']:
            max_val *= 1_000_000
        elif max_unit in ['thousand', 'k']:
            max_val *= 1_000
        filters["min_price"] = int(min_val)
        filters["max_price"] = int(max_val)

    # Area
    area_match = re.search(r"area\s*(of|at least|minimum)?\s*(\d+)", query)
    if area_match:
        filters["min_area"] = int(area_match.group(2))

    # REVISED LOCATION EXTRACTION
    location_match = re.search(r"in\s+(.+?)(\s+under|\s+with|\s+for|\s+between|$)", query)
    if location_match:
        location_raw = location_match.group(1).strip()
        main_location, keywords = _split_location_and_keywords(location_raw)

        # Set the main query and keywords filters
        if main_location:
            filters["query"] = main_location.title()
        if keywords:
            filters["keywords"] = keywords.title()

    # Fallback if filters are not enough or it's a question
    if len(filters) < 3 or query.endswith("?") or query.startswith(("what", "how", "show", "tell")):
        print("🧠 Fallback to LLaMA model...")
        llama_output = llama_fallback(query)
        print(f"output llm {llama_output}")
        if 'filters' in llama_output:
            llama_filters = llama_output.get('filters', {})
            if 'location_query' in llama_filters:
                filters['query'] = llama_filters.pop('location_query').title()
            if 'rooms' in llama_filters:
                filters['beds'] = str(llama_filters.pop('rooms'))
            if 'property_types' in llama_filters:
                if isinstance(llama_filters['property_types'], list) and llama_filters['property_types']:
                    filters['property_type'] = llama_filters.pop('property_types')[0].rstrip('s')
            if 'keywords' in llama_filters:
                filters['keywords'] = llama_filters.pop('keywords')

            filters.update({k: v for k, v in llama_filters.items() if v})

            if llama_output.get("is_question"):
                # Normalize before returning
                llama_filters = llama_output.get("filters", {})
                normalized = {}

                if 'location_query' in llama_filters:
                    normalized['query'] = llama_filters['location_query'].title()

                if 'property_types' in llama_filters and isinstance(llama_filters['property_types'], list):
                    if llama_filters['property_types']:
                        normalized['property_type'] = llama_filters['property_types'][0].rstrip("s")

                if 'rooms' in llama_filters:
                    normalized['beds'] = str(llama_filters['rooms'])

                if 'keywords' in llama_filters:
                    normalized['keywords'] = llama_filters['keywords']

                # Preserve question metadata + normalized filters
                return {
                    "is_question": True,
                    "question_type": llama_output.get("question_type"),
                    "filters": normalized
                }

    print("Parsed:", filters)
    return {"is_question": False, "filters": filters}


def llama_fallback(query):
    system_prompt = """
    You are a real estate query parser.
    You must output ONLY valid JSON.

    Keys:
    - filters: JSON dictionary with extracted filters (like property type, rooms, size, location).
    - is_question: true if the user is asking for information.
    - intent: type of request. Possible values:
        - "search" → looking for listings
        - "price_info" → asking about market prices (range, average)
        - "count" → asking how many listings
        - "availability" → asking if something exists
        - "estimate_price" → asking to estimate the value of THEIR property (phrases like 'my', 'estimate', 'worth', 'how much is my', etc.)

    Examples:

    User: "What’s the price range of villas in Dubai?"
    Output: {"is_question": true, "intent": "price_info", "filters": {"property_types": ["villas"], "location_query": "Dubai"}}

    User: "How many apartments are there in Marina?"
    Output: {"is_question": true, "intent": "count", "filters": {"property_types": ["apartments"], "location_query": "Marina"}}

    User: "Is there a villa in Dubai for sale?"
    Output: {"is_question": true, "intent": "availability", "filters": {"purpose": "sale", "property_types": ["villas"], "location_query": "Dubai"}}

    User: "I have a villa for sale and need to estimate its price. It’s in Dubai with 2 bedrooms and 1200 sqft"
    Output: {"is_question": true, "intent": "estimate_price", "filters": {"purpose": "sale", "property_types": ["villas"], "location_query": "Dubai", "rooms": 2, "size": 1200}}
    """

    prompt = f"{system_prompt.strip()}\n\nUser: {query.strip()}\nOutput:"
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        output = response.json().get('response', '').strip()

        # Extract JSON only
        json_match = re.search(r"\{.*\}", output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            print("❌ Failed to extract JSON from LLaMA output.")
            return {"is_question": False, "filters": {}}

    except Exception as e:
        print(f"❌ LLaMA Fallback API Error: {e}")
        return {"is_question": False, "filters": {}}



if __name__ == "__main__":
    query1 = "I need a studio apartment in Abu Dhabi under 3 million with 2 bathrooms"
    print("\n--- Testing Query 1 ---")
    parse_natural_query(query1)

    query2 = "What’s the price range for villas in Dubai?"
    print("\n--- Testing Query 2 ---")
    parse_natural_query(query2)

    query3 = "all current villa for sale in carmen villa in victory heights"
    print("\n--- Testing your specific query ---")
    parse_natural_query(query3)