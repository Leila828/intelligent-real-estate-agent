import io
import math
import requests
from urllib.parse import urlencode
from flask import Flask, request, jsonify, send_file, abort, render_template

import database
from ollam import parse_natural_query
import property_finder

import sqlite3
from datetime import datetime, timedelta

# --- Flask App Configuration ---
app = Flask(__name__)
app.config['DATABASE'] = 'bayut_properties.db'
app.config['DEBUG'] = True

database.init_app(app)

# --- Database Initialization (inside app context) ---
with app.app_context():
    database.init_db()


# --- Core Search Logic (Property Finder) ---
def search_properties(filters, page=1, limit=50):
    """
    Fetches property listings using the Property Finder API and caches them.
    """
    print(f"search filters in ppd {filters}")
    # 1. Prepare filters for the cache key.
    #    Remove empty or invalid filters before creating the cache key string.
    cleaned_filters = {k: v for k, v in filters.items() if v and v != ['']}

    # 2. Add 'page' and 'limit' to the cache key to ensure unique cache entries for different paginations.
    cleaned_filters['page'] = page
    cleaned_filters['limit'] = limit

    # 3. Create a unique query string for caching.
    #    'doseq=True' is crucial for handling lists like beds=['3', '4'].
    sorted_filters = sorted(cleaned_filters.items())
    query_string = urlencode(sorted_filters, doseq=True)

    # 4. Check the cache.
    query_id = database.find_cached_query(query_string)

    if query_id:
        print(f"✅ Cache hit for query: {query_string}")
        # Retrieve paginated properties from the cache
        properties_data = database.get_properties_for_query(query_id)

        # Calculate pagination details
        total_properties = len(properties_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_properties = properties_data[start:end]

        return paginated_properties
    else:
        print(f"🔄 Cache miss for query: {query_string}. Fetching live from Property Finder...")

        # 5. Fetch live data from Property Finder.
        #    Note: The Property Finder API itself does not have a 'limit' parameter,
        #    so you can pass the 'page' and other filters directly.
        # Wrap filters in the expected structure for property_finder_search
        # Convert 'query' to 'location_query' for Property Finder API
        if 'query' in cleaned_filters:
            cleaned_filters['location_query'] = cleaned_filters.pop('query')
        
        search_params = {"filters": cleaned_filters}
        properties = property_finder.property_finder_search(search_params)



        if properties:
            # 6. Save the live data to the database.
            database.save_query_and_properties(query_string, properties)

        return properties
# --- Flask Routes ---
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/api/search', methods=['GET'])
def api_search():
    """
    API endpoint to search for properties using the Property Finder API.
    This replaces the old Bayut API endpoint.
    """
    try:
        filters = {
            "query": request.args.get('query', 'dubai'),
            "purpose": request.args.get('purpose', 'sale'),
            "property_type": request.args.get('property_type', 'villa'),
            "beds": request.args.getlist('beds'),
            "baths": request.args.getlist('baths'),
            "page": request.args.get('page', 1, type=int),
            "sort": request.args.get('sort', 'mr'),
            "min_price": request.args.get('min_price', type=int),
            "max_price": request.args.get('max_price', type=int),
            "min_area": request.args.get('min_area', type=int),
            "max_area": request.args.get('max_area', type=int),
            "listed_within": request.args.get('listed_within', type=int),
            "amenities": request.args.getlist('amenities'),
            "furnished": request.args.get('furnished', type=str)
        }

        results = search_properties(filters)

        if results:
            return jsonify({
                "success": True,
                "listings": results,
                "count": len(results),
            })
        else:
            return jsonify({
                "success": False,
                "message": "No listings found.",
            }), 404

    except Exception as e:
        print(f"Error in API search: {e}")
        return jsonify({
            "success": False,
            "message": f"An error occurred: {str(e)}",
        }), 500


@app.route("/api/nl_search", methods=["POST"])
def nl_search():
    data = request.json
    query = data.get("query", "")

    # Parse query using regex + Ollama fallback
    print(query)
    filters = parse_natural_query(query)

    # If it's a question, handle differently
    if filters.get("is_question"):
        q_type = filters.get("question_type")

        if q_type == "price_range":
            # Extract subfilters directly from the main 'filters' dictionary
            inner_filters = filters.get("filters", {})

            # --- CRITICAL FIX START ---
            # Correctly handle the property_types list and location_query
            if 'property_types' in inner_filters and inner_filters['property_types']:
                inner_filters['property_type'] = inner_filters['property_types'][0]
                # It's good practice to delete the old key
                del inner_filters['property_types']

            if 'location_query' in inner_filters:
                inner_filters['query'] = inner_filters['location_query']
                del inner_filters['location_query']
            # --- CRITICAL FIX END ---

            # Now, call search_properties with the correctly formatted filters
            listings = search_properties(inner_filters)

            if not listings:
                return jsonify({
                    "is_question": True,
                    "question_type": "price_range",
                    "filters": inner_filters,
                    "answer": {"text": "No properties found."},
                }), 200

            prices = [item.get("price", 0) for item in listings if item.get("price")]
            if not prices:
                return jsonify({
                    "is_question": True,
                    "question_type": "price_range",
                    "filters": inner_filters,
                    "answer": {"text": "No valid price data found."}
                }), 200

            min_price = min(prices)
            max_price = max(prices)

            return jsonify({
                "is_question": True,
                "question_type": "price_range",
                "filters": inner_filters,
                "answer": {
                    "min_price": min_price,
                    "max_price": max_price,
                    "text": f"The price range for {inner_filters.get('property_type', 'properties')} in {inner_filters.get('query', 'the selected area')} is AED {min_price:,} – AED {max_price:,}"
                },
                "data": listings,
            }), 200

    # This part handles the "Default: normal property search"
    # The 'filters' dictionary is already in the correct format here.
    listings = search_properties(filters['filters'])
    return jsonify(listings)

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
    abort(501, description="This function has not been updated for Property Finder properties.")


@app.route('/api/properties/<int:property_id>')
def api_property_detail(property_id):
    """
    Returns a single property's details as a JSON object,
    retrieved from the cache (now populated with PF data).
    """
    db = database.get_db()
    cursor = db.cursor()

    # Ensure the ID is a string when querying the database.
    # The URL route is defined with <int:property_id>, so we need to convert it.
    cursor.execute("SELECT * FROM cached_properties WHERE id = ?", (str(property_id),))
    property_row = cursor.fetchone()

    if property_row is None:
        # If the property is not in the database, you could attempt
        # to fetch it live from the API and cache it, but this adds
        # complexity. For now, a 404 is a reasonable response.
        abort(404, description="Property not found in cache.")

    property_dict = dict(property_row)
    if property_dict.get('all_image_urls'):
        property_dict['all_image_urls'] = property_dict['all_image_urls'].split(',')
    else:
        property_dict['all_image_urls'] = []

    return jsonify(property_dict)

@app.route("/map_view")
def map_view():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)

    if lat is None or lng is None:
        abort(400, "Missing latitude or longitude in the URL.")

    return render_template("map_page.html", lat=lat, lng=lng)


if __name__ == '__main__':
    app.run(debug=True)