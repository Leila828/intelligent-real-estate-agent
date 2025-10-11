import io
import math
import requests
from urllib.parse import urlencode
from flask import Flask, request, jsonify, send_file, abort, render_template, g
from ollam import parse_natural_query, llama_fallback
import database
import test_prop as tp

import sqlite3
from datetime import datetime, timedelta

# --- Flask App Configuration ---
app = Flask(__name__)
app.config['DATABASE'] = 'bayut_properties.db'
app.config['DEBUG'] = True

database.init_app(app)


# --- API Constants ---
# CRITICAL FIX: Using the correct, modern Algolia endpoint and index name
ALGOLIA_API_URL = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.25.2)%3B%20Browser%20(lite)&x-algolia-api-key=15cb8b0a2d2d435c6613111d860ecfc5&x-algolia-application-id=LL8IZ711CS"
ALGOLIA_API_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "ll8iz711cs-dsn.algolia.net",
    "Origin": "https://www.bayut.com",
    "Referer": "https://www.bayut.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"'
}
ALGOLIA_INDEX_NAME = "bayut-production-ads-en"
IMAGE_URL_PATTERN = "https://images.bayut.com/thumbnails/{image_id}-400x300.webp"

# --- Database Initialization (inside app context) ---
with app.app_context():
    database.init_db()


# --- Helper Functions ---
def _construct_algolia_payload(filters, page, hits_per_page):
    """
    Constructs the dynamic Algolia API payload based on user filters.
    """
    # CRITICAL FIX: The query parameter must be handled separately.
    query_value = filters.get('location_query', '')
    params_string_parts = [
        f"page={page}",
        f"hitsPerPage={hits_per_page}",
        f"query={requests.utils.quote(query_value)}"  # Correctly uses location_query for the API 'query'
    ]

    filter_clauses = []
    if 'purpose' in filters:
        filter_clauses.append(f'purpose:"{filters["purpose"]}"')
    if 'rooms' in filters:
        filter_clauses.append(f'rooms:{filters["rooms"]}')
    if 'baths' in filters:
        filter_clauses.append(f'baths:{filters["baths"]}')
    if 'min_price' in filters:
        filter_clauses.append(f'price>={filters["min_price"]}')
    if 'max_price' in filters:
        filter_clauses.append(f'price<={filters["max_price"]}')

    # CRITICAL FIX: Handle property_types
    if 'property_types' in filters and filters['property_types']:
        types_str = " OR ".join([f'category.slug:"{pt}"' for pt in filters['property_types']])
        filter_clauses.append(f'({types_str})')

    if filter_clauses:
        full_filters = " AND ".join(filter_clauses)
        params_string_parts.append(f"filters={requests.utils.quote(full_filters)}")

    # NOTE: The attributesToRetrieve list is very long and has to be included.
    attrs_to_retrieve = "attributesToRetrieve=%5B%22type%22%2C%22agency%22%2C%22area%22%2C%22baths%22%2C%22category%22%2C%22additionalCategories%22%2C%22contactName%22%2C%22externalID%22%2C%22sourceID%22%2C%22id%22%2C%22location%22%2C%22objectID%22%2C%22phoneNumber%22%2C%22coverPhoto%22%2C%22photoCount%22%2C%22price%22%2C%22product%22%2C%22productLabel%22%2C%22purpose%22%2C%22geography%22%2C%22permitNumber%22%2C%22referenceNumber%22%2C%22rentFrequency%22%2C%22rooms%22%2C%22slug%22%2C%22slug_l1%22%2C%22slug_l2%22%2C%22slug_l3%22%2C%22title%22%2C%22title_l1%22%2C%22title_l2%22%2C%22title_l3%22%2C%22createdAt%22%2C%22updatedAt%22%2C%22ownerID%22%2C%22isVerified%22%2C%22propertyTour%22%2C%22verification%22%2C%22completionDetails%22%2C%22completionStatus%22%2C%22furnishingStatus%22%2C%22-agency.tier%22%2C%22coverVideo%22%2C%22videoCount%22%2C%22description%22%2C%22description_l1%22%2C%22description_l2%22%2C%22description_l3%22%2C%22descriptionTranslated%22%2C%22descriptionTranslated_l1%22%2C%22descriptionTranslated_l2%22%2C%22descriptionTranslated_l3%22%2C%22floorPlanID%22%2C%22panoramaCount%22%2C%22hasMatchingFloorPlans%22%2C%22state%22%2C%22photoIDs%22%2C%22reactivatedAt%22%2C%22hidePrice%22%2C%22extraFields%22%2C%22projectNumber%22%2C%22locationPurposeTier%22%2C%22hasRedirectionLink%22%2C%22ownerAgent%22%2C%22hasEmail%22%2C%22plotArea%22%2C%22offplanDetails%22%2C%22paymentPlans%22%2C%22paymentPlanSummaries%22%2C%22project%22%2C%22availabilityStatus%22%2C%22userExternalID%22%2C%22units%22%2C%22unitCategories%22%2C%22downPayment%22%2C%22clips%22%2C%22contactMethodAvailability%22%2C%22agentAdStoriesCount%22%2C%22isProjectOwned%22%2C%22documents%22%5D"
    params_string_parts.append(attrs_to_retrieve)

    # We also need to add the other parameters that come after the filters
    params_string_parts.extend(
        ["facets=%5B%5D", "maxValuesPerFacet=10", "attributesToHighlight=%5B%5D", "numericFilters="])

    params_string = "&".join(params_string_parts)
    return {"requests": [{"indexName": ALGOLIA_INDEX_NAME, "params": params_string}]}


def _fetch_from_algolia_live(filters, page, limit):
    """
    Fetches data directly from Algolia with filters.
    """
    payload = _construct_algolia_payload(filters, page - 1, limit)

    try:
        # CRITICAL FIX: Use the correct, global API constants
        response = requests.post(ALGOLIA_API_URL, headers=ALGOLIA_API_HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        results = data['results'][0]
        hits = results['hits']

        extracted_data = []
        for property_item in hits:
            property_id = property_item.get('id')
            title = property_item.get('title')
            if property_id is None or title is None:
                continue

            photo_ids = property_item.get('photoIDs', [])
            all_image_urls = [IMAGE_URL_PATTERN.format(image_id=image_id) for image_id in photo_ids]
            extracted_data.append({
                'id': property_id,
                'title': title,
                'price': property_item.get('price'),
                'area': property_item.get('area'),
                'rooms': property_item.get('rooms'),
                'baths': property_item.get('baths'),
                'purpose': property_item.get('purpose'),
                'completion_status': property_item.get('completionStatus'),
                'latitude': property_item.get('geography', {}).get('lat'),
                'longitude': property_item.get('geography', {}).get('lng'),
                'location_name': property_item.get('location')[-1].get('name') if property_item.get('location') and len(
                    property_item['location']) > 0 else None,
                'cover_photo_url': property_item.get('coverPhoto', {}).get('url'),
                'all_image_urls': all_image_urls,
                'agency_name': property_item.get('agency', {}).get('name'),
                'contact_name': property_item.get('contactName'),
                'mobile_number': property_item.get('phoneNumber', {}).get('mobile'),
                'whatsapp_number': property_item.get('phoneNumber', {}).get('whatsapp'),
                'down_payment_percentage': property_item.get('paymentPlanSummaries', [{}])[0].get('breakdown', {}).get(
                    'downPaymentPercentage') if property_item.get('paymentPlanSummaries') else None
            })

        return extracted_data, results.get('nbHits', 0)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Algolia: {e}")
        return [], 0
    except Exception as e:
        print(f"An unexpected error occurred during Algolia fetch: {e}")
        return [], 0


# --- Core Search Logic ---
def _execute_search(filters, page, limit):
    """
    Executes the main search logic, checking cache or fetching live.
    """
    sorted_filters = sorted(filters.items())
    query_string = urlencode(sorted_filters)

    query_id = database.find_cached_query(query_string)

    if query_id:
        properties_data = database.get_properties_for_query(query_id)
        total_properties = len(properties_data)
        total_pages = math.ceil(total_properties / limit) if total_properties > 0 else 1

        start = (page - 1) * limit
        end = start + limit
        paginated_properties = properties_data[start:end]

        return jsonify(
            {'properties': paginated_properties, 'page': page, 'limit': limit, 'total_properties': total_properties,
             'total_pages': total_pages})
    else:
        print(f"Cache miss for query: {query_string}. Fetching live from Algolia...")
        properties, total_properties = _fetch_from_algolia_live(filters, page, limit)

        if properties:
            database.save_query_and_properties(query_string, properties)

        total_pages = math.ceil(total_properties / limit) if total_properties > 0 else 1

        return jsonify({'properties': properties, 'page': page, 'limit': limit, 'total_properties': total_properties,
                        'total_pages': total_pages})


# --- Flask Routes ---
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/api/search', methods=['GET'])
def api_search():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    filters = {
        'purpose': request.args.get('purpose', 'for-sale', type=str),
        'rooms': request.args.get('rooms', type=int),
        'baths': request.args.get('baths', type=int),
        'min_price': request.args.get('min_price', type=int),
        'max_price': request.args.get('max_price', type=int)
    }

    filters = {k: v for k, v in filters.items() if v is not None}
    return _execute_search(filters, page, limit)


def search_properties(filters, page=1, limit=50):
    """
    Helper to fetch property listings directly from Algolia.
    Saves results into the database (same as normal search).
    """
    properties, total_properties = _fetch_from_algolia_live(filters, page, limit)

    if properties:
        sorted_filters = sorted(filters.items())
        query_string = urlencode(sorted_filters)
        database.save_query_and_properties(query_string, properties)

    return properties


@app.route("/api/nl_search", methods=["POST"])
def nl_search():
    data = request.json
    query = data.get("query", "")

    # Parse query using regex + Ollama fallback
    filters = llama_fallback(query)
    print(f"Query: {query}")
    print(f"Filters is {filters}")

    # ✅ If it's a QUESTION (Q&A mode)
    if filters.get("is_question"):
        q_type = filters.get("intent")
        inner_filters = filters.get("filters", {})

        # --- Normalize filters ---
        if 'property_types' in inner_filters and inner_filters['property_types']:
            inner_filters['property_type'] = inner_filters['property_types'][0].rstrip("s")
            del inner_filters['property_types']

        if 'location_query' in inner_filters:
            inner_filters['query'] = inner_filters['location_query']
            del inner_filters['location_query']

        # Map size → min_area for Algolia search
        if 'size' in inner_filters:
            inner_filters['max_area'] = inner_filters.pop('size')

        print("inner filters", inner_filters)

        # Fetch listings once for analysis
        listings = tp.search_properties(inner_filters)

        if not listings:
            return jsonify({
                "is_question": True,
                "question_type": q_type,
                "filters": inner_filters,
                "answer": {"text": "No properties found."},
            }), 200

        # 🔎 Handle different question types
        if q_type == "price_range":
            prices = [item.get("price", 0) for item in listings if item.get("price")]
            if not prices:
                return jsonify({
                    "is_question": True,
                    "question_type": q_type,
                    "filters": inner_filters,
                    "answer": {"text": "No valid price data found."}
                }), 200

            return jsonify({
                "is_question": True,
                "question_type": q_type,
                "filters": inner_filters,
                "answer": {
                    "min_price": min(prices),
                    "max_price": max(prices),
                    "text": f"The price range is AED {min(prices):,} – AED {max(prices):,}"
                },
                "data": listings,
            }), 200

        elif q_type == "avg_price":
            prices = [item.get("price", 0) for item in listings if item.get("price")]
            avg_price = sum(prices) / len(prices) if prices else 0
            return jsonify({
                "is_question": True,
                "question_type": q_type,
                "filters": inner_filters,
                "answer": {
                    "avg_price": avg_price,
                    "text": f"The average price is AED {avg_price:,.0f}"
                },
                "data": listings,
            }), 200

        elif q_type == "count_listings":
            return jsonify({
                "is_question": True,
                "question_type": q_type,
                "filters": inner_filters,
                "answer": {
                    "count": len(listings),
                    "text": f"There are {len(listings)} listings available."
                },
                "data": listings,
            }), 200

        elif q_type == "availability":
            return jsonify({
                "is_question": True,
                "question_type": q_type,
                "filters": inner_filters,
                "answer": {
                    "available": len(listings) > 0,
                    "text": "Yes, there are properties available." if listings else "No, nothing available."
                },
                "data": listings,
            }), 200


        elif q_type == "estimate_price":

            result = estimate_property_price(listings, filters)

            print(f"the results are {result}")

            return jsonify({
                "is_question": True,
                "question_type": q_type,
                "filters": inner_filters,

                "answer": {

                    "avg_price": result["answer"].get("avg_price"),

                    "min_price": result["answer"].get("min_price"),

                    "max_price": result["answer"].get("max_price"),

                    "sample_size": result["answer"].get("sample_size"),

                    "estimated_price": result["answer"].get("estimated_price"),

                    "price_per_sqft": result["answer"].get("price_per_sqft"),

                    "text": result["answer"].get("text"),

                },

                "data": result.get("data", []),

            }), 200
        else:
            return jsonify({
                "is_question": True,
                "question_type": q_type,
                "filters": inner_filters,
                "answer": {"text": f"Here's your results"},
                "data": listings,
            }), 200



        # 🛑 Default for unknown question types
        return jsonify({
            "is_question": True,
            "question_type": q_type,
            "filters": inner_filters,
            "answer": {"text": f"Sorry, I don’t yet support '{q_type}' type questions."},
            "data": listings,
        }), 200

    # ✅ Default: Normal property search
    listings = tp.search_properties(filters)
    return jsonify(listings)


# -------------------
# Price Estimation
# -------------------

def estimate_property_price(filters,filter ):
    """
    Estimate price of a property based on similar listings in the same location.
    Falls back to general location avg if exact match is not found.
    """

    # First try with given filters
    listings = filters
    # if not listings:
    #     # Relax filters: keep only purpose + property_type + query (location)
    #     relaxed_filters = {
    #         "purpose": filters.get("purpose", "sale"),
    #         "property_type": filters.get("property_type"),
    #         "query": filters.get("query"),
    #     }
    #     print(f"⚠️ No exact matches, retrying with relaxed filters: {relaxed_filters}")
    #     # listings = search_properties(relaxed_filters, page=1, limit=limit)

    # if not listings:
    #     return {
    #         "is_question": True,
    #         "question_type": "estimate_price",
    #         "filters": filters,
    #         "answer": {
    #             "text": "No properties found at all for this location.",
    #             "avg_price": None,
    #             "min_price": None,
    #             "max_price": None,
    #             "sample_size": 0,
    #             "estimated_price": None,
    #             "price_per_sqft": None,
    #         },
    #         "data": [],
    #     }

    # Extract prices and sizes
    prices = [item.get("price") for item in listings if item.get("price")]
    sizes = [item.get("area") for item in listings if item.get("area")]
    print(listings)

    # if not prices or not sizes:
    #     return {
    #         "is_question": True,
    #         "question_type": "estimate_price",
    #         "filters": filters,
    #         "answer": {
    #             "text": "No valid price/size data to estimate.",
    #             "avg_price": None,
    #             "min_price": None,
    #             "max_price": None,
    #             "sample_size": len(listings),
    #             "estimated_price": None,
    #             "price_per_sqft": None,
    #         },
    #         "data": listings,
    #     }

    avg_price = sum(prices) / len(prices)
    avg_size = sum(sizes) / len(sizes)

    price_per_sqft = avg_price / avg_size if avg_size else None
    print(f"Avarage prices is {avg_price} annd avarage size is {avg_size} and price/ size is {price_per_sqft}")

    estimated_price = None
    print(f"Estimate filters are {filter['filters'].get('max_area')}")
    if filter.get("filters") and price_per_sqft:
        estimated_price = round(filter['filters'].get('max_area') * price_per_sqft)

    result_text = (
        f"Based on {len(listings)} similar properties in {filter.get('query', 'the area')}, "
        f"the average price is AED {avg_price:,.0f} "
        f"({price_per_sqft:,.0f} per sqft)."
    )
    if estimated_price:
        result_text += f" Estimated price for your property ({filter['filters'].get('max_area')} sqft) is around AED {estimated_price:,.0f}."
        result_text += f" you can review similar properties in the same location: "

    return {
        "is_question": True,
        "question_type": "estimate_price",
        "filters": filters,
        "answer": {
            "avg_price": round(avg_price),
            "min_price": min(prices),
            "max_price": max(prices),
            "sample_size": len(listings),
            "price_per_sqft": round(price_per_sqft) if price_per_sqft else None,
            "estimated_price": estimated_price,
            "text": result_text,
        },
        "data": listings,
    }


def _compute_estimate(listings, filters):
    """Helper to compute average and estimated price per size"""
    prices = []
    sizes = []

    for item in listings:
        price = item.get("price")
        size = item.get("size")
        if price and size:
            prices.append(price)
            sizes.append(size)

    if not prices or not sizes:
        return {
            "is_question": True,
            "question_type": "estimate_price",
            "filters": filters,
            "answer": {"text": "No valid price/size data to estimate."},
            "data": listings,
        }

    avg_price = sum(prices) / len(prices)
    avg_size = sum(sizes) / len(sizes)
    price_per_sqft = avg_price / avg_size if avg_size else 0

    # Estimate price based on requested size
    target_size = filters.get("size")
    estimated_price = price_per_sqft * target_size if target_size else avg_price

    return {
        "is_question": True,
        "question_type": "estimate_price",
        "filters": filters,
        "answer": {
            "avg_price": avg_price,
            "price_per_sqft": price_per_sqft,
            "estimated_price": estimated_price,
            "text": f"Estimated price: AED {estimated_price:,.0f} "
                    f"(based on {len(prices)} similar listings, "
                    f"avg AED {price_per_sqft:,.0f}/sqft)"
        },
        "data": listings,
    }







@app.route('/get_image')
def get_image():
    image_url = request.args.get('url')
    allowed_image_prefixes = ['https://www.propertyfinder.ae/property/']
    is_valid_prefix = any(image_url and image_url.startswith(prefix) for prefix in allowed_image_prefixes)
    if not is_valid_prefix:
        return "Invalid image URL", 400
    try:
        response = requests.get(image_url, headers={'Referer': 'https://www.propertyfinder.ae/'}, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        return send_file(io.BytesIO(response.content), mimetype=content_type)
    except requests.exceptions.Timeout:
        return "Image fetch timed out", 408
    except requests.exceptions.RequestException as e:
        return f"Image not found or forbidden: {e}", 404
    except Exception as e:
        return f"Internal server error: {e}", 500

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    """
    Renders a detailed page for a single property.
    """
    db = database.get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cached_properties WHERE id = ?", (property_id,))
    property_row = cursor.fetchone()

    if property_row is None:
        abort(404, description="Property not found.")

    property_dict = dict(property_row)
    if property_dict['all_image_urls']:
        property_dict['all_image_urls'] = property_dict['all_image_urls'].split(',')
    else:
        property_dict['all_image_urls'] = []

    return render_template('property_detail.html', property=property_dict)


@app.route('/api/properties/<int:property_id>')
def api_property_detail(property_id):
    """
    Returns a single property's details as a JSON object,
    first from cache, then from a live API fallback.
    """
    db = database.get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cached_properties WHERE id = ?", (property_id,))
    property_row = cursor.fetchone()

    if property_row is None:
        abort(404, description="Property not found in cache.")

    property_dict = dict(property_row)
    if property_dict['all_image_urls']:
        property_dict['all_image_urls'] = property_dict['all_image_urls'].split(',')
    else:
        property_dict['all_image_urls'] = []

    return jsonify(property_dict)


@app.route("/map_view")
def map_view():
    """
    Renders a full-page map with a marker at the specified coordinates.
    Expects 'lat' and 'lng' as URL query parameters.
    """
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)

    if lat is None or lng is None:
        abort(400, "Missing latitude or longitude in the URL.")

    return render_template("map_page.html", lat=lat, lng=lng)


if __name__ == '__main__':
    app.run(debug=True)
