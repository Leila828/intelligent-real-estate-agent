import test_prop as tp

def estimate_property_price(details: dict):
    """
    Estimate property price based on similar listings from Property Finder/Bayut API.

    Args:
        details (dict): {
            "purpose": "sale" or "rent",
            "property_type": "apartment",
            "location_query": "Dubai Marina",
            "area": 1200,   # sqft
            "rooms": 2,
            "baths": 2
        }

    Returns:
        dict: {
            "avg_price": ...,
            "min_price": ...,
            "max_price": ...,
            "listings_count": ...,
            "samples": [...]
        }
    """

    # --- Step 1: Build filters for API ---
    filters = {
        "purpose": details.get("purpose", "sale"),
        "property_type": details.get("property_type", "apartment"),
        "query": details.get("location_query", ""),
        "rooms": details.get("rooms"),
        "baths": details.get("baths"),
    }

    # Add area filter (with tolerance, e.g. ±15%)
    if details.get("area"):
        filters["min_area"] = int(details["area"] * 0.85)
        filters["max_area"] = int(details["area"] * 1.15)

    # --- Step 2: Query the API ---
    listings = tp.search_properties(filters)  # or property_finder.property_finder_search(filters)

    if not listings:
        return {
            "avg_price": None,
            "min_price": None,
            "max_price": None,
            "listings_count": 0,
            "samples": []
        }

    # --- Step 3: Extract price data ---
    prices = [l.get("price") for l in listings if l.get("price")]

    if not prices:
        return {
            "avg_price": None,
            "min_price": None,
            "max_price": None,
            "listings_count": len(listings),
            "samples": listings[:5]  # just show a few
        }

    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)

    return {
        "avg_price": round(avg_price),
        "min_price": min_price,
        "max_price": max_price,
        "listings_count": len(listings),
        "samples": listings[:5]  # return 5 sample listings
    }

my_apartment = {
    "purpose": "sale",
    "property_type": "apartment",
    "location_query": "Dubai Marina",
    "area": 1200,
    "rooms": 2,
    "baths": 2
}

result = estimate_property_price(my_apartment)
print(result)
