import requests
import re
import json
from urllib.parse import urlencode

# ----------------------------------
# Headers & Mappings
# ----------------------------------
NEXT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "x-nextjs-data": "1",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.propertyfinder.ae/en/buy/dubai/villas-for-sale.html",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

PROPERTY_TYPE_MAP = {
    "apartment": "1",
    "villa": "35",
    "townhouse": "22",
    "penthouse": "20",
    "compound": "42",
    "duplex": "24",
    "full floor": "18",
    "half floor": "29",
    "whole building": "10",
    "land": "5",
    "bulk sale unit": "30",
    "bungalow": "31",
    "hotel & hotel apartment": "45"
}

FILTERS_MAP = {
    "amenities": "filter[amenities]",
    "bathrooms": "filter[number_of_bathrooms]",
    "beds": "filter[number_of_bedrooms]",
    "furnished": "filter[furnished]",
    "virtual_viewings": "filter[virtual_viewings]",
    "completion_status": "filter[completion_status]",
    "min_installment_years": "filter[min_installment_years]",
    "max_installment_years": "filter[max_installment_years]",
    "verified": "filter[verified]",
    "trusted_agent": "filter[trusted_agent]",
    "listed_within": "filter[listed_within]",
    "is_developer_property": "filter[is_developer_property]",
    "category_id": "filter[category_id]",
    "property_type_id": "filter[property_type_id]",
    "min_price": "filter[min_price]",
    "max_price": "filter[max_price]",
    "min_area": "filter[min_area]",
    "max_area": "filter[max_area]",
    "keywords": "filter[keywords]",
    "locations_ids": "filter[locations_ids]",
    "sort": "sort"
}


# ----------------------------------
# Helper Function for Data Mapping
# ----------------------------------
def _map_pf_data_to_db_schema(pf_listing):
    """
    Maps a single Property Finder listing dictionary to the
    database schema format.
    """
    property_data = pf_listing.get("property", {})
    if not property_data:
        return None

    all_image_urls = [
        img.get("medium") for img in property_data.get("images", []) if img.get("medium")
    ]
    # Keep as list instead of comma-separated string to avoid JSON parsing issues
    all_image_urls_str = all_image_urls

    mobile_number = None
    whatsapp_number = None
    for contact in property_data.get("contact_options", []):
        if contact.get("type") == "phone":
            mobile_number = contact.get("value")
        elif contact.get("type") == "whatsapp":
            whatsapp_number = contact.get("value")

    down_payment = None
    if 'offplan_details' in property_data and 'payment_plan' in property_data['offplan_details']:
        down_payment = property_data['offplan_details']['payment_plan'].get('downPaymentPercentage')

    listing_id = property_data.get("id")
    if not listing_id:
        return None

    return {
        "id": listing_id,
        "title": property_data.get("title"),
        "price": property_data.get("price", {}).get("value"),
        "area": property_data.get("size", {}).get("value"),
        "rooms": property_data.get("bedrooms_value"),
        "baths": property_data.get("bathrooms_value"),
        "purpose": property_data.get("offering_type"),
        "completion_status": property_data.get("completion_status"),
        "latitude": property_data.get("location", {}).get("coordinates", {}).get("lat"),
        "longitude": property_data.get("location", {}).get("coordinates", {}).get("lon"),
        "location_name": property_data.get("location", {}).get("full_name"),
        "cover_photo_url": property_data.get("images", [{}])[0].get("medium") if property_data.get("images") else None,
        "all_image_urls": all_image_urls_str,
        "agency_name": property_data.get("broker", {}).get("name"),
        "contact_name": property_data.get("agent", {}).get("name"),
        "mobile_number": mobile_number,
        "whatsapp_number": whatsapp_number,
        "down_payment_percentage": down_payment,
    }


# ----------------------------------
# Initialise the API Token Key (return the build_id)
# ----------------------------------
def initialise(filters: dict):
    """
    Fetches the current PropertyFinder buildId from the search page,
    using the provided search filters.
    """
    base_url = "https://www.propertyfinder.ae/en/search"
    url_params = {}

    purpose_map = {"rent": 2, "sale": 1}
    if "purpose" in filters:
        url_params["c"] = "1" if filters["purpose"] == "sale" else "2"
    if "property_type" in filters:
        pt_id = PROPERTY_TYPE_MAP.get(filters["property_type"].lower())
        if pt_id:
            url_params["t"] = pt_id
    if "location_id" in filters:
        url_params["l"] = filters["location_id"]
    if "sort" in filters:
        url_params["ob"] = filters["sort"]

    res = requests.get(base_url, params=url_params, headers=NEXT_HEADERS)
    res.raise_for_status()
    html = res.text

    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if match:
        try:
            data = json.loads(match.group(1))
            return data.get("buildId")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    return None


# ----------------------------------
# Search Location
# ----------------------------------
def search_location(query: str, limit: int = 20):
    url = "https://www.propertyfinder.ae/api/pwa/locations"
    params = {"locale": "en", "filters.name": query, "pagination.limit": limit}
    res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    res.raise_for_status()
    return res.json()


# ----------------------------------
# Fetch Listings
# ----------------------------------
def fetch_propertyfinder_listings(filters: dict, build_id: str):
    """
    Fetch listings from Property Finder and map them to the database schema.
    """
    if not build_id:
        print("❌ Build ID is missing. Cannot fetch listings.")
        return []

    url = f"https://www.propertyfinder.ae/search/_next/data/{build_id}/en/search.json"
    api_params = {"ob": "mr", "fu": "0", "c": "1"}

    for key, value in filters.items():
        if key == "property_type":
            pt_id = PROPERTY_TYPE_MAP.get(value.lower())
            if pt_id:
                api_params["t"] = pt_id
        elif key == "purpose":
            api_params["c"] = "1" if value == "sale" else "2"
        elif key == "page":
            api_params["page[number]"] = value
        elif key == "location_id":
            api_params["l"] = value
        else:
            api_key = FILTERS_MAP.get(key)
            if api_key and value is not None:
                if isinstance(value, list):
                    api_params[api_key] = ','.join(str(v) for v in value)
                else:
                    api_params[api_key] = value

    try:
        res = requests.get(url, params=api_params, headers=NEXT_HEADERS)
        res.raise_for_status()
        data = res.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Property Finder API: {e}")
        return []

    listings = data.get("pageProps", {}).get("searchResult", {}).get("listings", [])

    mapped_results = []
    for r in listings:
        if r['listing_type'] == 'property':
            mapped_item = _map_pf_data_to_db_schema(r)
            if mapped_item:
                mapped_results.append(mapped_item)

    return mapped_results


# ----------------------------------
# Main Search Function
# ----------------------------------
def property_finder_search(search_filters: dict):
    """
    Main function to execute the full search workflow with keywords.
    """
    # Use the main location query for the initial location search
    print(f"print filters ff {search_filters}")
    query = search_filters['filters'].get("location_query", "dubai")
    print(f"querry of location {query}")
    print(f"query ff {query}")
    locations = search_location(query)
    # print(f"locations {locations}")
    attributes = locations.get("data", {}).get("attributes", [])
    first_location = attributes[0] if attributes else None
    
    if not first_location:
        print(f"Could not find location for query: {query}.")
        return []

    search_filters["location_id"] = first_location["id"]
    print(f"Found city ID: {search_filters['location_id']}")

    # Add the keywords filter if it exists in the parsed filters
    keywords = search_filters.get("keywords")
    if keywords:
        search_filters["keywords"] = keywords  # 'keywords' is the key in our `FILTERS_MAP`

    build_id = initialise(search_filters)
    if not build_id:
        print("Could not get build ID. The website structure may have changed.")
        return []

    page = search_filters.get("page", 1)
    print(f"Fetching listings for page {page}...")
    listings = fetch_propertyfinder_listings(search_filters, build_id)
    print(f"Found {len(listings)} properties on page {page}")

    return listings