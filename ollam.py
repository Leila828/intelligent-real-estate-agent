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


def split_multi_questions(query):
    """Split a query into multiple questions if it contains 'and' or commas between distinct questions."""
    # Common question starters
    question_starters = (
        "what", "how", "where", "when", "do", "can", "could", "would", "is", "are", 
        "show", "tell", "find", "give", "list", "what's", "what're", "what're", "what is", "what are"
    )
    
    # Split on "and" or comma if followed by a question starter
    parts = []
    current_part = ""
    
    # First split by explicit "and" between questions
    segments = re.split(r'\s*,?\s+and\s+', query)
    for i, segment in enumerate(segments):
        segment = segment.strip()
        # Skip empty segments
        if not segment:
            continue
            
        # If this segment starts with a question word or
        # if it's not the first segment (meaning it came after "and")
        is_question = i > 0 and (
            any(segment.lower().startswith(starter) for starter in question_starters) or
            any(segment.lower().startswith(f"{starter} ") for starter in question_starters)
        )
        
        if is_question:
            if current_part:
                parts.append(current_part.strip())
            current_part = segment
        else:
            if current_part:
                current_part += " and " + segment
            else:
                current_part = segment
    
    if current_part:
        parts.append(current_part.strip())
    
    # If no splits were found, return the original query as a single part
    result = parts if parts else [query]
    print(f"Split multi-question: {query} -> {result}")
    return result

# Define analytical patterns at module level
analytical_patterns = [
    # Price analysis patterns
    r"what'?s\s+the\s+average\s+price",
    r"average\s+price",
    r"average\s+asking\s+price",
    r"price\s+range",
    r"typical\s+price",
    r"how\s+much\s+do.*cost",
    r"what'?s\s+the\s+price",
    # Comparison patterns
    r"versus",
    r"vs\.?",
    r"compared?\s+to",
    r"difference\s+between",
    r"compare",
    # Market analysis patterns
    r"market\s+analysis",
    r"market\s+trends",
    r"market\s+overview",
    # Affordability patterns
    r"years?\s+of\s+work",
    r"years?\s+needed",
    r"can\s+i\s+afford",
    r"afford",
    r"salary\s+needed",
    # How-to patterns
    r"how\s+to\s+buy",
    r"how\s+to\s+purchase",
    r"how\s+to\s+sell",
    # General analytical patterns
    r"what\s+should\s+i",
    r"what\s+do\s+i\s+need",
    r"tell\s+me\s+about",
    r"explain",
    r"analysis",
    r"insights?",
    r"statistics",
    r"stats"
]

def parse_natural_query(query):
    query = query.lower()
    
    # Split multi-part questions
    questions = split_multi_questions(query)
    if len(questions) > 1:
        # If we have multiple questions, parse each one and return as a multi-question response
        responses = []
        for q in questions:
            # Check if this part is an analytical question before parsing
            is_analytical = (
                any(re.search(pattern, q.lower()) for pattern in analytical_patterns) or
                # Additional checks for price analysis questions
                ("average" in q.lower() and "price" in q.lower()) or
                ("typical" in q.lower() and "price" in q.lower()) or
                ("cost" in q.lower() and any(w in q.lower() for w in ["what", "how", "typical", "average"]))
            )
            
            # Parse the question
            sub_response = parse_natural_query(q)
            
            # Override question type if analytical patterns were found
            if is_analytical:
                sub_response = {
                    "is_question": True,
                    "question_type": "analytical_question",
                    "filters": sub_response.get("filters", {}),
                    "original_query": q
                }
            else:
                sub_response['original_query'] = q
            
            responses.append(sub_response)
        
        return {
            "is_multi_question": True,
            "questions": responses
        }
    
    # Enhanced question detection - distinguish between search requests and analytical questions
    is_analytical_question = (
        query.endswith("?") and not query.lower().startswith(("do you have", "are there", "can you show", "could you show")) or
        any(re.search(pattern, query.lower()) for pattern in analytical_patterns)
    )
    
    # Search requests (these should return property listings)
    is_search_request = (
        query.startswith(("show", "find", "list", "get", "search", "give me")) or
        "all" in query and ("villa" in query or "apartment" in query or "property" in query) or
        "current" in query and ("villa" in query or "apartment" in query or "property" in query) or
        "available" in query and ("villa" in query or "apartment" in query or "property" in query)
    )
    
    # Determine the intent
    if is_analytical_question and not is_search_request:
        is_question = True
        question_type = "analytical_question"
    elif is_search_request:
        is_question = False
        question_type = "search_request"
    else:
        # Default to search if unclear
        is_question = False
        question_type = "search_request"
    
    print(f"Query analysis: '{query}' -> is_question: {is_question}, type: {question_type}")
    
    # If it's a question, try LLaMA first
    if is_question:
        print("Question detected, trying LLaMA first...")
        try:
            llama_output = llama_fallback(query)
            print(f"output llm {llama_output}")
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
                    "question_type": llama_output.get("question_type", "general_question"),
                    "filters": normalized
                }
        except Exception as e:
            print(f"LLaMA Fallback API Error: {e}")
            # If LLaMA fails, continue with regex parsing but mark as question
    
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

    # Bedrooms and Bathrooms - support both "3 bedroom" and "three-bedroom"
    # Word to number mapping
    word_to_num = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"
    }
    
    # Try digit pattern first
    beds_match = re.search(r"(\d+)\s*[-\s]*(bed|bedroom|rooms?)\b", query)
    if beds_match:
        filters["beds"] = beds_match.group(1)
    else:
        # Try word pattern (e.g., "three-bedroom" or "three bedroom")
        for word, num in word_to_num.items():
            if re.search(rf"\b{word}[-\s]*(bed|bedroom|rooms?)\b", query):
                filters["beds"] = num
                break
    
    baths_match = re.search(r"(\d+)\s*[-\s]*(bath|bathroom|baths?)", query)
    if baths_match:
        filters["baths"] = baths_match.group(1)
    else:
        # Try word pattern for bathrooms too
        for word, num in word_to_num.items():
            if re.search(rf"\b{word}[-\s]*(bath|bathroom)\b", query):
                filters["baths"] = num
                break

    # Handle "cheap" or "affordable" - set max price based on location and property type
    if "cheap" in query or "affordable" in query or "budget" in query:
        # Base price varies by location
        base_price = 100_000  # Default monthly price
        if "downtown" in query.lower() or "burj khalifa" in query.lower():
            base_price = 150_000  # Higher base for premium locations
        elif "palm jumeirah" in query.lower():
            base_price = 200_000  # Highest base for luxury locations
        elif "international city" in query.lower() or "discovery gardens" in query.lower():
            base_price = 50_000  # Lower base for affordable areas
        
        # Adjust for property type
        if "villa" in query.lower():
            base_price *= 2  # Villas are typically more expensive
        elif "penthouse" in query.lower():
            base_price *= 2.5  # Penthouses are premium
        elif "studio" in query.lower():
            base_price *= 0.6  # Studios are cheaper
        
        filters["max_price"] = base_price
    
    # Price ranges - enhanced patterns
    price_patterns = [
        # Min price patterns
        (r"(over|above|more than|starting from|from|min|minimum)\s*(\d+[\.,]?\d*)(\s*(million|m|thousand|k|aed))?(\s*(annually|per year|a year|yearly))?", "min_price"),
        # Max price patterns
        (r"(under|below|less than|not more than|don't want to spend more than|max|maximum|up to|within|no more than)\s*(\d+[\.,]?\d*)(\s*(million|m|thousand|k|aed))?(\s*(annually|per year|a year|yearly))?", "max_price"),
        # Exact price patterns
        (r"(exactly|precisely|at|of)\s*(\d+[\.,]?\d*)(\s*(million|m|thousand|k|aed))?(\s*(annually|per year|a year|yearly))?", "exact_price")
    ]
    
    for pattern, price_type in price_patterns:
        price_match = re.search(pattern, query, re.IGNORECASE)
        if price_match:
            value_str = price_match.group(2).replace(',', '')
            value = float(value_str)
            unit = price_match.group(4)
            if unit:
                unit = unit.lower()
                if unit in ['million', 'm']:
                    value *= 1_000_000
                elif unit in ['thousand', 'k']:
                    value *= 1_000
            
            # Handle annual rent conversion
            is_annual = price_match.groups()[-1] is not None and any(term in price_match.groups()[-1].lower() for term in ["annually", "per year", "a year", "yearly"])
            if is_annual and "rent" in query.lower():
                value = value / 12  # Convert annual to monthly
            
            if price_type == "exact_price":
                filters["min_price"] = int(value * 0.95)  # 5% below
                filters["max_price"] = int(value * 1.05)  # 5% above
            elif price_type == "max_price":
                filters["max_price"] = int(value)
                # Remove min_price if it was set by another pattern
                filters.pop("min_price", None)
            elif price_type == "min_price":
                filters["min_price"] = int(value)
                # Remove max_price if it was set by another pattern
                filters.pop("max_price", None)

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

    # REVISED LOCATION EXTRACTION - handle "in", "near", "around", "close to"
    location_raw = None
    
    # First try to find well-known landmarks
    landmark_map = {
        r"burj\s+(?:khalifa|califa)": ("Downtown Dubai", "Burj Khalifa"),
        r"burj\s+(?:al\s+)?arab": ("Jumeirah", "Burj Al Arab"),
        r"dubai\s+mall": ("Downtown Dubai", "Dubai Mall")
    }
    
    # Look for landmarks in the query
    for landmark_pattern, (area, keyword) in landmark_map.items():
        if re.search(landmark_pattern, query, re.IGNORECASE):
            filters["query"] = area
            filters["keywords"] = keyword
            location_raw = area
            print(f"Found landmark: {keyword} -> {area}")
            break
    
    # If no landmark found, try general location patterns
    if "query" not in filters:
        # General location patterns
        general_patterns = [
            r"in\s+(.+?)(?:\s+under|\s+with|\s+for|\s+between|$)",
            r"near\s+(?:the\s+)?([^,\.]+?)(?:\s+units?|\s+propert(?:y|ies)|\s+apart(?:ment)?s?|\s+villas?|\s+and|\s+but|\s*$)",
            r"around\s+(?:the\s+)?([^,\.]+?)(?:\s+units?|\s+propert(?:y|ies)|\s+apart(?:ment)?s?|\s+villas?|\s+and|\s+but|\s*$)",
            r"close to\s+(?:the\s+)?([^,\.]+?)(?:\s+units?|\s+propert(?:y|ies)|\s+apart(?:ment)?s?|\s+villas?|\s+and|\s+but|\s*$)",
            r"by\s+(?:the\s+)?([^,\.]+?)(?:\s+units?|\s+propert(?:y|ies)|\s+apart(?:ment)?s?|\s+villas?|\s+and|\s+but|\s*$)"
        ]
        
        for pattern in general_patterns:
            location_match = re.search(pattern, query, re.IGNORECASE)
            if location_match:
                # All patterns now have the location in group(1)
                location_raw = location_match.group(1).strip()
                # Remove "the" if it's at the start
                location_raw = re.sub(r"^the\s+", "", location_raw, flags=re.IGNORECASE)
                print(f"Found location: {location_raw} using pattern: {pattern}")
                break
    
    
    # Special handling for well-known landmarks - only if not already handled
    if location_raw and "query" not in filters:
        location_lower = location_raw.lower()
        if "burj" in location_lower:
            if "khalifa" in location_lower or "califa" in location_lower:
                location_raw = "Downtown Dubai"  # Map Burj Khalifa to Downtown
                filters["query"] = "Downtown Dubai"  # Set immediately to avoid overwriting
                filters["keywords"] = "Burj Khalifa"  # Add as keyword for better targeting
            elif "jumeirah" in location_lower:
                location_raw = "Jumeirah"  # Map Burj Al Arab to Jumeirah
                filters["query"] = "Jumeirah"  # Set immediately to avoid overwriting
                filters["keywords"] = "Burj Al Arab"  # Add as keyword for better targeting
        elif "dubai mall" in location_lower:
            location_raw = "Downtown Dubai"
            filters["query"] = "Downtown Dubai"  # Set immediately to avoid overwriting
            filters["keywords"] = "Dubai Mall"  # Add as keyword for better targeting
    
    if location_raw:
        main_location, keywords = _split_location_and_keywords(location_raw)
        # Set the main query and keywords filters
        if main_location:
            filters["query"] = main_location.title()
        if keywords:
            filters["keywords"] = keywords.title()

    # Extract potential keyword before the "in" clause for patterns like
    # "Carmen villa in Victory Heights" → keywords: "Carmen"
    pre_in_match = re.search(r"\b([a-z]+)\s+(villa|apartment|penthouse|townhouse)\b", query)
    if pre_in_match:
        keyword_before_type = pre_in_match.group(1).title()
        if keyword_before_type:
            existing_kw = filters.get("keywords")
            if existing_kw:
                filters["keywords"] = f"{existing_kw} {keyword_before_type}"
            else:
                filters["keywords"] = keyword_before_type

    # Check if it's a question (improved detection)
    is_question = (
        query.endswith("?") or 
        query.startswith(("what", "how", "show", "tell", "can", "could", "would", "should", "is", "are", "do", "does", "did")) or
        "how to" in query or
        "what is" in query or
        "what are" in query or
        "can you" in query or
        "could you" in query or
        "tell me" in query or
        "show me" in query
    )
    
    print(f"Question detection: '{query}' -> is_question: {is_question}")
    
    # Fallback if filters are not enough or it's a question
    if len(filters) < 3 or is_question:
        print("Fallback to LLaMA model...")
        try:
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
        except Exception as e:
            print(f"LLaMA Fallback API Error: {e}")
            # If LLaMA fails, use simple question detection
            if is_question:
                return {
                    "is_question": True,
                    "question_type": "general_question",
                    "filters": filters
                }

    print("Parsed:", filters)
    print(f"DEBUG: is_question = {is_question}")
    
    # If it was detected as a question but LLaMA failed, return as question
    if is_question:
        print("DEBUG: Returning as question")
        return {
            "is_question": True,
            "question_type": question_type,
            "filters": filters
        }
    
    print("DEBUG: Returning as search query")
    return {"is_question": False, "question_type": question_type, "filters": filters}


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