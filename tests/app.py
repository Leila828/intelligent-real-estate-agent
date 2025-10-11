import os
import sys
import requests
import io
import math  # For math.ceil
import threading  # For background cache loading
import time  # For time.sleep during cache loading

from flask import Flask, request, jsonify, abort, send_file, Response

# Add the project root to sys.path to allow imports from 'api' package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Import functions from your API module
from api import bayut_scraper  # Imports get_bayut_property_data and flatten_property_dict

app = Flask(__name__)
app.config['DEBUG'] = True  # Set to False in production

# --- In-memory Cache ---
# Stores flattened property data fetched from the API
property_cache = []
property_cache_by_id = {}  # For faster lookup by ID
cache_loading_in_progress = False  # Flag to prevent multiple concurrent loads


def load_property_cache_threaded():
    """
    Fetches data from Bayut API and populates the in-memory cache in a separate thread.
    This prevents the Flask app from blocking during startup for large fetches.
    """
    global property_cache
    global property_cache_by_id
    global cache_loading_in_progress

    if cache_loading_in_progress:
        print("Cache loading already in progress. Skipping new load request.")
        return

    cache_loading_in_progress = True
    print("\n--- Starting background property cache load ---")
    try:
        # Fetch raw data using the scraper
        raw_fetched_properties = bayut_scraper.get_bayut_property_data(
            purposes=["for-sale", "for-rent"],  # All data for both purposes
            location_query="",  # All UAE
            property_types=[],  # All types
            max_pages_to_fetch=10,  # Limiting to 10 pages (~1000 properties) for faster startup in debug
            # Set to None to fetch all ~1700 properties (might take longer)
            delay_seconds=0.1
        )

        # Flatten the properties and populate the cache
        new_property_cache = []
        new_property_cache_by_id = {}
        for raw_prop in raw_fetched_properties:
            flat_prop = bayut_scraper.flatten_property_dict(raw_prop)
            new_property_cache.append(flat_prop)
            if flat_prop.get('id') is not None:
                new_property_cache_by_id[flat_prop['id']] = flat_prop

        # Atomically update the cache
        property_cache = new_property_cache
        property_cache_by_id = new_property_cache_by_id

        print(f"--- Property cache loaded with {len(property_cache)} properties. ---")
    except Exception as e:
        print(f"Error loading property cache: {e}")
    finally:
        cache_loading_in_progress = False


@app.before_first_request
def initialize_cache_on_startup():
    """
    Called once when the application first starts serving requests.
    Starts the cache loading in a background thread.
    """
    print("App starting. Initializing cache in background.")
    cache_thread = threading.Thread(target=load_property_cache_threaded)
    cache_thread.daemon = True  # Allow the main program to exit even if thread is running
    cache_thread.start()


# --- Flask Routes (API Endpoints) ---

@app.route('/')
def api_root():
    """
    Root API endpoint. Provides basic info about the API.
    """
    return jsonify({
        "message": "Welcome to the Real Estate API!",
        "endpoints": {
            "/api/properties": "GET: Get a paginated list of properties.",
            "/api/properties/<int:property_id>": "GET: Get details for a specific property by ID.",
            "/api/map_data": "POST: Get properties within geographical map bounds.",
            "/get_image?url=<image_url>": "GET: Image proxy for external image URLs.",
            "/refresh_cache": "GET: Manually refresh the in-memory property cache."
        },
        "cache_status": {
            "loaded_properties": len(property_cache),
            "loading_in_progress": cache_loading_in_progress
        }
    })


@app.route('/refresh_cache')
def refresh_cache():
    """Manually triggers a refresh of the in-memory cache."""
    print("Manual cache refresh requested.")
    load_property_cache_threaded()  # Re-trigger cache load
    return jsonify({"status": "Cache refresh initiated. Check server logs for progress."}), 200


@app.route('/api/properties')
def api_list_properties():
    """
    API endpoint to retrieve a paginated list of properties from cache.
    Accepts 'page' (default 1) and 'limit' (default 20) query parameters.
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    if not property_cache and cache_loading_in_progress:
        return jsonify({
                           "message": "Properties are currently loading. Please try again shortly."}), 202  # Accepted, but not yet ready
    elif not property_cache:
        # Cache is empty and not loading (e.g., initial load failed or app restarted and no one hit / yet)
        return jsonify(
            {"message": "No properties available in cache. Consider /refresh_cache."}), 503  # Service Unavailable

    # Implement pagination from the in-memory cache
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    properties_to_display = property_cache[start_idx:end_idx]
    total_properties = len(property_cache)
    total_pages = math.ceil(total_properties / limit) if total_properties > 0 else 1

    return jsonify({
        'properties': properties_to_display,
        'page': page,
        'limit': limit,
        'total_properties': total_properties,
        'total_pages': total_pages
    })


@app.route('/api/properties/<int:property_id>')
def api_property_detail(property_id):
    """
    API endpoint to retrieve details for a single property by ID from cache.
    """
    if not property_cache_by_id and cache_loading_in_progress:
        return jsonify({"message": "Properties are currently loading. Please try again shortly."}), 202
    elif not property_cache_by_id:
        return jsonify({"message": "No properties available in cache."}), 503

    prop = property_cache_by_id.get(property_id)  # Fast lookup by ID

    if prop:
        return jsonify(prop)
    abort(404, description="Property not found in cache.")


@app.route('/api/map_data', methods=['POST'])
def api_map_data():
    """
    API endpoint to retrieve properties within specified geographical bounds from cache.
    Expected from a frontend map (e.g., Leaflet) AJAX call.
    Expects 'north', 'east', 'south', 'west' in the JSON request body.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    north = data.get('north')
    east = data.get('east')
    south = data.get('south')
    west = data.get('west')

    if not all([north, east, south, west]):
        return jsonify({"error": "Missing geographical bounds (north, east, south, west)"}), 400

    if not property_cache:
        # If cache is empty, it might be loading or failed to load.
        # Return an empty list, map frontend handles no data.
        return jsonify([])

    properties_in_bounds = []
    for prop in property_cache:
        lat = prop.get('latitude')
        lng = prop.get('longitude')

        # Ensure lat/lng are actual numbers before comparison
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)) and \
                south <= lat <= north and \
                west <= lng <= east:
            properties_in_bounds.append(prop)

    # For very dense areas, you might want to return a subset or implement clustering on the frontend.
    # For this example, we return all in-bounds properties.

    return jsonify(properties_in_bounds)


@app.route('/get_image')
def get_image():
    """
    A simple image proxy to bypass potential CORS issues when loading images
    from Bayut's CDN directly in the browser.
    """
    image_url = request.args.get('url')

    allowed_image_prefixes = [
        'https://images.bayut.com/thumbnails/',
        'https://bayut-production.s3.eu-central-1.amazonaws.com/image/'
    ]

    is_valid_prefix = False
    for prefix in allowed_image_prefixes:
        if image_url and image_url.startswith(prefix):
            is_valid_prefix = True
            break

    if not is_valid_prefix:
        print(f"Warning: Invalid image URL requested for proxy: {image_url}")
        return "Invalid image URL", 400

    try:
        response = requests.get(image_url, headers={'Referer': 'https://www.bayut.com/'}, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        # Use make_response for more control over headers, or send_file
        return send_file(
            io.BytesIO(response.content),
            mimetype=content_type
        )
    except requests.exceptions.Timeout:
        print(f"Timeout fetching image from Bayut CDN via proxy ({image_url})")
        return Response("Image fetch timed out", status=408)  # Use Response object for custom status
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from Bayut CDN via proxy ({image_url}): {e}")
        return Response("Image not found or forbidden", status=404)
    except Exception as e:
        print(f"An unexpected error occurred in get_image ({image_url}): {e}")
        return Response("Internal server error", status=500)


if __name__ == '__main__':
    # When app.run() is called, @app.before_first_request will execute
    # to start loading the cache in a background thread.
    app.run(debug=True)