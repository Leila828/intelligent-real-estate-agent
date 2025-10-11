from flask import Flask, render_template, request, jsonify, send_file, abort
import requests
import json
import database
import io
import math # Import math for ceil function for total pages

app = Flask(__name__)
app.config['DATABASE'] = 'bayut_properties.db'
app.config['DEBUG'] = True # Enable debug mode for development

# Register database teardown and CLI commands
database.init_app(app)

# --- Function to fetch data from Algolia API (remains the same) ---
def fetch_properties_from_algolia():
    url = "https://ll8iz711cs-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.25.2)%3B%20Browser%20(lite)&x-algolia-api-key=15cb8b0a2d2d435c6613111d860ecfc5&x-algolia-application-id=LL8IZ711CS"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "ll8iz711cs-2.algolianet.com",
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
    payload = {
        "requests": [
            {
                "indexName": "bayut-production-ads-verified-score-en",
                "params": (
                    "page=0"
                    "&hitsPerPage=24"
                    "&query="
                    "&optionalWords="
                    "&facets=%5B%5D"
                    "&maxValuesPerFacet=10"
                    "&attributesToHighlight=%5B%5D"
                    # Keep attributesToRetrieve as is for now, it seems comprehensive
                    "&attributesToRetrieve=%5B%22type%22%2C%22agency%22%2C%22area%22%2C%22baths%22%2C%22category%22%2C%22additionalCategories%22%2C%22contactName%22%2C%22externalID%22%2C%22sourceID%22%2C%22id%22%2C%22location%22%2C%22objectID%22%2C%22phoneNumber%22%2C%22coverPhoto%22%2C%22photoCount%22%2C%22price%22%2C%22product%22%2C%22productLabel%22%2C%22purpose%22%2C%22geography%22%2C%22permitNumber%22%2C%22referenceNumber%22%2C%22rentFrequency%22%2C%22rooms%22%2C%22slug%22%2C%22slug_l1%22%2C%22slug_l2%22%2C%22slug_l3%22%2C%22title%22%2C%22title_l1%22%2C%22title_l2%22%2C%22title_l3%22%2C%22createdAt%22%2C%22updatedAt%22%2C%22ownerID%22%2C%22isVerified%22%2C%22propertyTour%22%2C%22verification%22%2C%22completionDetails%22%2C%22completionStatus%22%2C%22furnishingStatus%22%2C%22-agency.tier%22%2C%22coverVideo%22%2C%22videoCount%22%2C%22description%22%2C%22description_l1%22%2C%22description_l2%22%2C%22description_l3%22%2C%22descriptionTranslated%22%2C%22descriptionTranslated_l1%22%2C%22descriptionTranslated_l2%22%2C%22descriptionTranslated_l3%22%2C%22floorPlanID%22%2C%22panoramaCount%22%2C%22hasMatchingFloorPlans%22%2C%22state%22%2C%22photoIDs%22%2C%22reactivatedAt%22%2C%22hidePrice%22%2C%22extraFields%22%2C%22projectNumber%22%2C%22locationPurposeTier%22%2C%22hasRedirectionLink%22%2C%22ownerAgent%22%2C%22hasEmail%22%2C%22plotArea%22%2C%22offplanDetails%22%2C%22paymentPlans%22%2C%22paymentPlanSummaries%22%2C%22project%22%2C%22availabilityStatus%22%2C%22userExternalID%22%2C%22units%22%2C%22unitCategories%22%2C%22downPayment%22%2C%22clips%22%2C%22contactMethodAvailability%22%2C%22agentAdStoriesCount%22%2C%22isProjectOwned%22%2C%22documents%22%5D"
                    # --- SIMPLIFY THE FILTERS HERE ---
                    # Start with something very broad, then add back filters one by one
                    "&filters=purpose%3A%22for-sale%22"  # Just "for-sale"
                    # "&filters=purpose%3A%22for-sale%22%20AND%20%28category.slug%3A%22residential%22%29%20AND%20completionStatus%3A%22under-construction%22%20AND%20%28product%3A%22superhot%22%29" # Original (comment out)
                    "&numericFilters="
                )
            }
        ]
    }
    base_image_url_pattern = "https://images.bayut.com/thumbnails/{image_id}-400x300.webp"

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        properties = data['results'][0]['hits']
        extracted_data = []

        for property_item in properties:
            property_id = property_item.get('id')
            title = property_item.get('title')
            print(f"DEBUG: Processing Algolia property_item: {json.dumps(property_item, indent=2)}")
            if property_id is None or title is None:
                print(f"Skipping malformed property: ID={property_id}, Title={title}. Full item: {property_item}")
                continue

            photo_ids = property_item.get('photoIDs', [])
            all_image_urls = []
            if photo_ids:
                for image_id in photo_ids:
                    constructed_image_url = base_image_url_pattern.format(image_id=image_id)
                    all_image_urls.append(constructed_image_url)

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
                'location_name': property_item.get('location')[-1].get('name') if property_item.get('location') else None,
                'cover_photo_url': property_item.get('coverPhoto', {}).get('url'),
                'all_image_urls': all_image_urls,
                'agency_name': property_item.get('agency', {}).get('name'),
                'contact_name': property_item.get('contactName'),
                'mobile_number': property_item.get('phoneNumber', {}).get('mobile'),
                'whatsapp_number': property_item.get('phoneNumber', {}).get('whatsapp'),
                'down_payment_percentage': property_item.get('paymentPlanSummaries', [{}])[0].get('breakdown', {}).get('downPaymentPercentage') if property_item.get('paymentPlanSummaries') else None
            })
        return extracted_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Algolia: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during Algolia fetch: {e}")
        return []

# --- Flask Routes ---

@app.route('/')
def index():
    """
    Renders the main map page.
    Automatically triggers database population if the DB is empty.
    """
    properties_in_db = database.get_all_properties_count() # Check count instead of fetching all
    if properties_in_db == 0: # If count is 0, db is empty
        print("Database is empty. Attempting to fetch and populate data automatically...")
        properties_data = fetch_properties_from_algolia()
        if properties_data:
            inserted_count = 0
            for prop in properties_data:
                # Add print statement to check data before insert
                # print(f"Inserting property {prop.get('id')}: Price={prop.get('price')}, Cover Photo URL={prop.get('cover_photo_url')}")
                if database.insert_property(prop):
                    inserted_count += 1
            print(f"Auto-populated {inserted_count} properties.")
        else:
            print("Failed to fetch data from Algolia during auto-population.")

    return render_template('map.html')

@app.route('/home')
def home():
    """
    Renders the home page (e.g., a list view or introductory page).
    You'll need a separate 'home.html' template for this.
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int) # You can adjust this limit

    db = database.get_db()
    cursor = db.cursor()

    # Get total count first for pagination metadata
    cursor.execute("SELECT COUNT(*) FROM properties")
    total_properties = cursor.fetchone()[0]

    # Fetch paginated properties
    offset = (page - 1) * limit
    cursor.execute("SELECT * FROM properties LIMIT ? OFFSET ?", (limit, offset))
    properties_raw = cursor.fetchall()

    properties_processed = []
    for prop_row in properties_raw:
        prop_dict = dict(prop_row)
        # Assuming 'all_image_urls' is stored as a comma-separated string
        if prop_dict['all_image_urls']:
            prop_dict['all_image_urls'] = prop_dict['all_image_urls'].split(',')
        else:
            prop_dict['all_image_urls'] = []
        properties_processed.append(prop_dict)

    total_pages = math.ceil(total_properties / limit) if total_properties > 0 else 1

    return render_template(
        'home.html',
        properties=properties_processed,
        page=page,
        total_pages=total_pages,
        total_properties=total_properties
    )

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    """
    Renders a detailed page for a single property.
    """
    db = database.get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
    property_row = cursor.fetchone()

    if property_row is None:
        abort(404, description="Property not found.")

    property_dict = dict(property_row)
    if property_dict['all_image_urls']:
        property_dict['all_image_urls'] = property_dict['all_image_urls'].split(',')
    else:
        property_dict['all_image_urls'] = []

    return render_template('property_detail.html', property=property_dict)


@app.route('/api/properties')
def api_properties():
    """
    API endpoint to retrieve paginated properties as JSON.
    Accepts 'page' (default 1) and 'limit' (default 10) query parameters.
    This route is suitable for your 'home' page's AJAX if needed for pagination.
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit

    db = database.get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM properties")
    total_properties = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM properties LIMIT ? OFFSET ?", (limit, offset))
    properties_raw = cursor.fetchall()

    properties_processed = []
    for prop_row in properties_raw:
        prop_dict = dict(prop_row)
        if prop_dict['all_image_urls']:
            prop_dict['all_image_urls'] = prop_dict['all_image_urls'].split(',')
        else:
            prop_dict['all_image_urls'] = []
        properties_processed.append(prop_dict)

    total_pages = math.ceil(total_properties / limit) if total_properties > 0 else 1

    return jsonify({
        'properties': properties_processed,
        'page': page,
        'limit': limit,
        'total_properties': total_properties,
        'total_pages': total_pages
    })

@app.route('/get_image')
def get_image():
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
        response = requests.get(image_url, headers={'Referer': 'https://www.bayut.com/'}, timeout=10) # Added timeout
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        # print(f"Successfully fetched image from {image_url}, Content-Type: {content_type}") # Uncomment for debugging

        return send_file(
            io.BytesIO(response.content),
            mimetype=content_type
        )
    except requests.exceptions.Timeout:
        print(f"Timeout fetching image from Bayut CDN via proxy ({image_url})")
        return "Image fetch timed out", 408
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from Bayut CDN via proxy ({image_url}): {e}")
        return "Image not found or forbidden", 404
    except Exception as e:
        print(f"An unexpected error occurred in get_image ({image_url}): {e}")
        return "Internal server error", 500

@app.route('/map_data', methods=['POST'])
def map_data():
    """
    API endpoint to retrieve properties within specified geographical bounds.
    Expects 'north', 'east', 'south', 'west' in the JSON request body.
    Returns properties with ALL necessary details for the map and list.
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

    db = database.get_db()
    cursor = db.cursor()

    # --- THE CRITICAL CHANGE IS HERE ---
    # Select all columns to ensure frontend has all data for popups and list
    query = """
    SELECT *
    FROM properties
    WHERE latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?
    """
    cursor.execute(query, (north, south, east, west))
    properties_raw = cursor.fetchall()

    properties_for_map = []
    for prop_row in properties_raw:
        prop_dict = dict(prop_row)
        # Ensure latitude and longitude are float for Leaflet
        try:
            prop_dict['latitude'] = float(prop_dict['latitude'])
            prop_dict['longitude'] = float(prop_dict['longitude'])

            # If 'all_image_urls' is stored as a comma-separated string, convert it to a list
            # This is primarily for the detail page, but including it for consistency if needed.
            # For map, 'cover_photo_url' is more direct.
            if 'all_image_urls' in prop_dict and prop_dict['all_image_urls']:
                prop_dict['all_image_urls'] = prop_dict['all_image_urls'].split(',')
            else:
                prop_dict['all_image_urls'] = []

            properties_for_map.append(prop_dict)
        except (ValueError, TypeError) as e:
            print(f"Skipping property {prop_dict.get('id')} due to invalid lat/lng: {prop_dict.get('latitude')}, {prop_dict.get('longitude')} - Error: {e}")
            continue

    return jsonify(properties_for_map)

if __name__ == '__main__':
    with app.app_context():
        database.init_db()
    app.run(debug=True)