import io
import math
import re
import requests
import asyncio
from urllib.parse import urlencode
from flask import Flask, request, jsonify, send_file, abort, render_template, g
from ollam import parse_natural_query, llama_fallback
import database
import test_prop as tp
import property_finder
from datetime import datetime
import sqlite3
from intelligent_agent import agent

def generate_agent_insights(listings, query, filters):
    """Generate AI agent insights based on search results"""
    insights = []
    
    if listings:
        # Price analysis
        prices = [item.get("price", 0) for item in listings if item.get("price")]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            insights.append({
                "type": "price_analysis",
                "title": "Price Insights",
                "message": f"Found {len(listings)} properties with prices ranging from AED {min_price:,.0f} to AED {max_price:,.0f}",
                "data": {
                    "average_price": avg_price,
                    "price_range": {"min": min_price, "max": max_price},
                    "property_count": len(listings)
                }
            })
        
        # Location analysis
        locations = [item.get("location_name", "") for item in listings if item.get("location_name")]
        if locations:
            unique_locations = list(set(locations))
            insights.append({
                "type": "location_analysis",
                "title": "Location Distribution",
                "message": f"Properties found in {len(unique_locations)} different areas within {filters.get('query', 'the search area')}",
                "data": {
                    "unique_locations": len(unique_locations),
                    "top_locations": unique_locations[:5]
                }
            })
    else:
        insights.append({
            "type": "no_results",
            "title": "No Properties Found",
            "message": "No properties found matching your criteria. Try adjusting your search parameters.",
            "suggestions": [
                "Try a broader location search",
                "Consider different property types",
                "Adjust your price range",
                "Check spelling of location names"
            ]
        })
    
    return insights

def generate_proactive_suggestions(listings, query, filters):
    """Generate proactive suggestions based on search results"""
    suggestions = []
    
    if listings:
        suggestions.extend([
            "Would you like me to filter by price range?",
            "I can help you compare similar properties",
            "Would you like to see properties on a map?",
            "I can set up alerts for new properties matching your criteria"
        ])
        
        # Add specific suggestions based on results
        if len(listings) > 10:
            suggestions.append("You have many options! Would you like me to narrow down the search?")
        
        prices = [item.get("price", 0) for item in listings if item.get("price")]
        if prices:
            avg_price = sum(prices) / len(prices)
            suggestions.append(f"The average price is AED {avg_price:,.0f}. Would you like to see properties around this price?")
    else:
        suggestions.extend([
            "Try searching in nearby areas",
            "Consider different property types",
            "Adjust your budget range",
            "Contact me for personalized assistance"
        ])
    
    return suggestions

def update_agent_memory(query, results, success):
    """Update agent memory with interaction data"""
    # Simple memory update - can be enhanced later
    pass

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
    Fetches property listings using the Property Finder API and caches them.
    """
    print(f"search filters in app.py {filters}")
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
        print(f"Cache hit for query: {query_string}")
        # Retrieve paginated properties from the cache
        properties_data = database.get_properties_for_query(query_id)

        # Calculate pagination details
        total_properties = len(properties_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_properties = properties_data[start:end]

        return paginated_properties
    else:
        print(f"Cache miss for query: {query_string}. Fetching live from Property Finder...")

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


def handle_analytical_question(query, filters, search_properties_func):
    """Handle analytical questions like price analysis, market insights, etc."""
    query_lower = query.lower()
    
    # Check for comparison questions (e.g., "DIFC versus Downtown Dubai")
    comparison_patterns = [r"versus", r"\bvs\.?\b", r"compared?\s+to", r"difference\s+between"]
    is_comparison = any(re.search(pattern, query_lower) for pattern in comparison_patterns)
    
    if is_comparison:
        # Extract two locations for comparison
        locations = []
        
        # Try to extract locations using various patterns
        vs_match = re.search(r"(?:in\s+)?([A-Za-z\s]+?)\s+(?:versus|vs\.?|compared?\s+to)\s+([A-Za-z\s]+?)(?:\?|$|\s+for|\s+properties)", query, re.IGNORECASE)
        if vs_match:
            locations = [vs_match.group(1).strip(), vs_match.group(2).strip()]
        else:
            # Try "difference between X and Y"
            diff_match = re.search(r"difference\s+between\s+([A-Za-z\s]+?)\s+and\s+([A-Za-z\s]+?)(?:\?|$)", query, re.IGNORECASE)
            if diff_match:
                locations = [diff_match.group(1).strip(), diff_match.group(2).strip()]
            else:
                # Try "Compare X vs Y" pattern
                compare_match = re.search(r"compare\s+(?:prices?\s+in\s+)?([A-Za-z\s]+?)\s+(?:vs\.?|versus)\s+([A-Za-z\s]+?)(?:\?|$)", query, re.IGNORECASE)
                if compare_match:
                    locations = [compare_match.group(1).strip(), compare_match.group(2).strip()]
                else:
                    # Try simpler pattern: "X vs Y"
                    simple_match = re.search(r"([A-Za-z\s]+?)\s+(?:vs\.?|versus)\s+([A-Za-z\s]+?)(?:\?|$)", query, re.IGNORECASE)
                    if simple_match:
                        locations = [simple_match.group(1).strip(), simple_match.group(2).strip()]
        
        print(f"Extracted locations: {locations}")
        if len(locations) == 2:
            # Search both locations
            results = {}
            for location in locations:
                try:
                    search_filters = {"query": location}
                    print(f"Searching for: {location}")
                    props = search_properties_func(search_filters)
                    results[location] = props
                    print(f"Found {len(props) if props else 0} properties for {location}")
                except Exception as e:
                    print(f"Error searching {location}: {e}")
                    results[location] = []
            
            # Calculate statistics for each location
            comparison_data = {}
            for location, props in results.items():
                if props:
                    prices = [p.get("price", 0) for p in props if p.get("price")]
                    if prices:
                        comparison_data[location] = {
                            "count": len(props),
                            "avg_price": sum(prices) / len(prices),
                            "min_price": min(prices),
                            "max_price": max(prices)
                        }
                    else:
                        comparison_data[location] = {"count": len(props), "avg_price": None}
                else:
                    comparison_data[location] = {"count": 0, "avg_price": None}
            
            # Build comparison answer
            if all(data.get("avg_price") for data in comparison_data.values()):
                loc1, loc2 = locations
                data1, data2 = comparison_data[loc1], comparison_data[loc2]
                
                diff = data1["avg_price"] - data2["avg_price"]
                diff_pct = (diff / data2["avg_price"]) * 100 if data2["avg_price"] > 0 else 0
                
                answer = {
                    "text": f"Comparison between {loc1} and {loc2}:",
                    "comparison": {
                        loc1: {
                            "average_price": f"AED {data1['avg_price']:,.0f}",
                            "price_range": f"AED {data1['min_price']:,.0f} - AED {data1['max_price']:,.0f}",
                            "property_count": data1['count']
                        },
                        loc2: {
                            "average_price": f"AED {data2['avg_price']:,.0f}",
                            "price_range": f"AED {data2['min_price']:,.0f} - AED {data2['max_price']:,.0f}",
                            "property_count": data2['count']
                        }
                    },
                    "insights": [
                        f"{loc1} has an average price of AED {data1['avg_price']:,.0f} ({data1['count']} properties)",
                        f"{loc2} has an average price of AED {data2['avg_price']:,.0f} ({data2['count']} properties)",
                        f"Difference: AED {abs(diff):,.0f} ({abs(diff_pct):.1f}% {'higher' if diff > 0 else 'lower'} in {loc1})"
                    ]
                }
            else:
                answer = {
                    "text": "Comparison results:",
                    "comparison": comparison_data,
                    "insights": [
                        f"{loc}: {data['count']} properties found" + (f" (avg: AED {data['avg_price']:,.0f})" if data.get('avg_price') else " (no price data)")
                        for loc, data in comparison_data.items()
                    ]
                }
            
            # Combine all properties for display
            all_props = []
            for props in results.values():
                all_props.extend(props if props else [])
            
            return jsonify({
                "is_question": True,
                "question_type": "comparison_question",
                "query": query,
                "answer": answer,
                "data": all_props
            }), 200
    
    # Get relevant properties for analysis
    try:
        listings = search_properties_func(filters.get('filters', {}))
    except Exception as e:
        try:
            print(f"Error fetching properties for analysis: {e}")
        except:
            print("Error fetching properties for analysis")
        listings = []
    
    # Affordability questions (e.g., "how many years of work needed ...", "can I afford ...")
    if any(phrase in query_lower for phrase in ["how many years", "years of work", "can i afford", "afford", "salary needed", "how long to save"]):
        # Pull listings using current filters (now enriched with keywords/location)
        prices = []
        if listings:
            prices = [item.get("price", 0) for item in listings if item.get("price")]

        # If no prices found, try a fallback broader search using only location/type inferred
        if not prices:
            base_filters = filters.get('filters', {}).copy()
            # Keep only broad location/type filters
            base_filters = {
                k: v for k, v in base_filters.items() if k in ["query", "property_type", "keywords", "purpose", "beds"] and v
            }
            try:
                fallback_listings = search_properties_func(base_filters)
                prices = [item.get("price", 0) for item in fallback_listings if item.get("price")]
            except Exception:
                prices = []

        if prices:
            avg_price = sum(prices) / len(prices)
            # Assumptions for affordability model
            # - Default annual salary if not provided by user
            # - 20% savings rate toward property purchase
            # - No mortgage leverage considered (cash saving model for conservative estimate)
            default_annual_salary = 240_000  # AED (~20k/month)
            savings_rate = 0.20
            annual_savings = default_annual_salary * savings_rate
            years_needed = avg_price / annual_savings if annual_savings > 0 else None

            location_label = filters.get('filters', {}).get('query', 'the area')
            answer = {
                "text": f"Estimated years of work needed to buy in {location_label}:",
                "analysis": {
                    "assumptions": {
                        "annual_salary_aed": default_annual_salary,
                        "savings_rate": f"{int(savings_rate*100)}%"
                    },
                    "average_price": f"AED {avg_price:,.0f}",
                    "estimated_years_needed": f"{years_needed:.1f}" if years_needed is not None else "N/A"
                },
                "insights": [
                    f"With AED {default_annual_salary:,.0f}/year income and {int(savings_rate*100)}% savings, you'd need ~{years_needed:.1f} years for the average property.",
                    "Provide your actual yearly income or savings rate for a personalized estimate.",
                    "Using mortgage financing can significantly reduce savings time; ask 'estimate with mortgage'."
                ]
            }
        else:
            answer = {
                "text": "No properties found to estimate affordability.",
                "suggestions": [
                    "Try specifying the location more clearly (e.g., 'Victory Heights')",
                    "Include the property type (e.g., 'Carmen villa')",
                    "Ask again with your annual salary, e.g., 'with 300k AED salary'"
                ]
            }

        return jsonify({
            "is_question": True,
            "question_type": "analytical_question",
            "query": query,
            "answer": answer,
            "data": listings if listings else []
        }), 200

    # Price analysis questions
    if any(phrase in query_lower for phrase in ["average price", "price range", "how much", "price analysis"]):
        if listings:
            prices = [item.get("price", 0) for item in listings if item.get("price")]
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                answer = {
                    "text": f"Based on {len(listings)} available properties, here's the price analysis:",
                    "analysis": {
                        "average_price": f"AED {avg_price:,.0f}",
                        "price_range": f"AED {min_price:,.0f} - AED {max_price:,.0f}",
                        "property_count": len(listings),
                        "location": filters.get('filters', {}).get('query', 'the search area')
                    },
                    "insights": [
                        f"The average price is AED {avg_price:,.0f}",
                        f"Prices range from AED {min_price:,.0f} to AED {max_price:,.0f}",
                        f"Found {len(listings)} properties matching your criteria"
                    ]
                }
            else:
                answer = {
                    "text": "I found properties but couldn't analyze prices as price information is not available.",
                    "analysis": {"property_count": len(listings)}
                }
        else:
            answer = {
                "text": "No properties found for price analysis. Try adjusting your search criteria.",
                "suggestions": [
                    "Try a broader location search",
                    "Consider different property types",
                    "Check if the location name is spelled correctly"
                ]
            }
        
        return jsonify({
            "is_question": True,
            "question_type": "analytical_question",
            "query": query,
            "answer": answer,
            "data": listings if listings else []
        }), 200
    
    # How-to questions
    elif any(phrase in query_lower for phrase in ["how to buy", "how to purchase", "how to sell"]):
        location = filters.get('filters', {}).get('query', 'Dubai')
        property_type = filters.get('filters', {}).get('property_type', 'property')
        
        if "buy" in query_lower or "purchase" in query_lower:
            answer = {
                "text": f"Here's how to buy a {property_type} in {location}:",
                "steps": [
                    "1. **Get Pre-Approval**: Contact a bank for mortgage pre-approval to know your budget",
                    "2. **Find a Property**: Search for available properties in the area",
                    "3. **Make an Offer**: Work with a real estate agent to make a competitive offer",
                    "4. **Legal Process**: Complete due diligence, property inspection, and legal documentation",
                    "5. **Final Payment**: Complete the transaction and transfer ownership"
                ],
                "additional_info": {
                    "location": location,
                    "property_type": property_type,
                    "current_listings": len(listings) if listings else 0
                }
            }
        else:  # selling
            answer = {
                "text": f"Here's how to sell a {property_type} in {location}:",
                "steps": [
                    "1. **Property Valuation**: Get a professional valuation to set the right price",
                    "2. **Prepare the Property**: Clean, stage, and make necessary repairs",
                    "3. **List the Property**: Work with a real estate agent or list online",
                    "4. **Showings & Negotiations**: Handle property viewings and negotiate offers",
                    "5. **Legal Process**: Complete documentation and transfer ownership"
                ],
                "additional_info": {
                    "location": location,
                    "property_type": property_type,
                    "market_activity": len(listings) if listings else 0
                }
            }
        
        return jsonify({
            "is_question": True,
            "question_type": "analytical_question",
            "query": query,
            "answer": answer,
            "data": listings if listings else []
        }), 200
    
    # Market analysis questions
    elif any(phrase in query_lower for phrase in ["market analysis", "market trends", "market overview"]):
        if listings:
            answer = {
                "text": f"Market analysis for {filters.get('filters', {}).get('query', 'the area')}:",
                "analysis": {
                    "total_listings": len(listings),
                    "property_types": list(set([item.get("property_type", "Unknown") for item in listings])),
                    "price_insights": "Contact us for detailed market analysis"
                },
                "insights": [
                    f"Found {len(listings)} active listings",
                    "Market appears active with multiple options available",
                    "Recommend consulting with a local real estate expert for detailed trends"
                ]
            }
        else:
            answer = {
                "text": "No current market data available. The market may be quiet or the search criteria may be too specific.",
                "suggestions": [
                    "Try broader location search",
                    "Consider different property types",
                    "Contact a local real estate agent for market insights"
                ]
            }
        
        return jsonify({
            "is_question": True,
            "question_type": "analytical_question",
            "query": query,
            "answer": answer,
            "data": listings if listings else []
        }), 200
    
    # Default analytical response
    else:
        answer = {
            "text": f"I understand you're asking about '{query}'. I can help with:",
            "capabilities": [
                "Price analysis and market insights",
                "How-to guides for buying/selling",
                "Property search and listings",
                "Location-specific information"
            ],
            "suggestions": [
                "Try asking 'What's the average price of villas in Dubai?'",
                "Ask 'How to buy a villa in Damac Hills?'",
                "Request 'Show me all villas for sale in Dubai Marina'"
            ]
        }
        
        return jsonify({
            "is_question": True,
            "question_type": "analytical_question",
            "query": query,
            "answer": answer,
            "data": []
        }), 200


@app.route('/api/intelligent_search', methods=['POST'])
def intelligent_search():
    """Intelligent search using the AI agent"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Use the intelligent agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent.process_query(query))
            return jsonify(result)
        finally:
            loop.close()
            
    except Exception as e:
        print(f"Error in intelligent search: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/api/nl_search", methods=["POST"])
def nl_search():
    data = request.json
    query = data.get("query", "")

    # Parse query using regex + Ollama fallback
    try:
        filters = parse_natural_query(query)
        print(f"Query: {query}")
        try:
            print(f"Filters: {filters}")
        except Exception as e:
            print(f"Filters contains non-printable characters: {type(e).__name__}")
    except Exception as e:
        print(f"Error parsing query: {e}")
        return jsonify({
            "error": "Failed to parse query",
            "success": False,
            "details": str(e)
        }), 500

    # Handle multi-part questions
    if filters.get("is_multi_question"):
        print("Processing multi-part question...")
        combined_response = {
            "is_multi_question": True,
            "answers": [],
            "combined_data": []
        }
        
        try:
            questions = filters.get("questions", [])
            print(f"Found {len(questions)} sub-questions")
            if not questions:
                print("No questions found in multi-question request")
                return jsonify({
                    "error": "No questions found in multi-question request",
                    "success": False
                }), 400
            
            for i, sub_question in enumerate(questions):
                try:
                    print(f"\nProcessing sub-question {i + 1}:")
                    # Process each sub-question
                    sub_query = sub_question.get("original_query", "")
                    if not sub_query:
                        print("Empty sub-query, skipping...")
                        continue
                    print(f"Sub-query: {sub_query}")
                        
                    sub_type = sub_question.get("question_type", "search_request")
                    sub_filters = sub_question.get("filters", {})
                    print(f"Sub-type: {sub_type}")
                    print(f"Sub-filters: {sub_filters}")
                    
                    if sub_type == "analytical_question":
                        # Get properties for analysis
                        listings = search_properties(sub_filters)
                        
                        # Generate analytical response
                        if "average" in sub_query.lower() and "price" in sub_query.lower():
                            if listings:
                                prices = [item.get("price", 0) for item in listings if item.get("price")]
                                if prices:
                                    avg_price = sum(prices) / len(prices)
                                    min_price = min(prices)
                                    max_price = max(prices)
                                    
                                    answer = {
                                        "text": f"Based on {len(listings)} properties in {sub_filters.get('query', 'the area')}:",
                                        "analysis": {
                                            "average_price": f"AED {avg_price:,.0f}",
                                            "price_range": f"AED {min_price:,.0f} - AED {max_price:,.0f}",
                                            "property_count": len(listings)
                                        }
                                    }
                                else:
                                    answer = {
                                        "text": "Found properties but couldn't analyze prices.",
                                        "analysis": {"property_count": len(listings)}
                                    }
                            else:
                                answer = {
                                    "text": "No properties found for price analysis.",
                                    "analysis": {"property_count": 0}
                                }
                        else:
                            answer = {
                                "text": f"Found {len(listings)} properties matching your criteria.",
                                "analysis": {"property_count": len(listings)}
                            }
                        
                        combined_response["answers"].append({
                            "query": sub_query,
                            "answer": answer,
                            "type": "analytical"
                        })
                        combined_response["combined_data"].extend(listings if listings else [])
                    else:
                        # Handle search request
                        listings = search_properties(sub_filters)
                        combined_response["answers"].append({
                            "query": sub_query,
                            "answer": {
                                "text": f"Found {len(listings)} matching properties",
                                "count": len(listings)
                            },
                            "type": "search"
                        })
                        combined_response["combined_data"].extend(listings if listings else [])
                except Exception as e:
                    print(f"Error processing sub-question: {e}")
                    combined_response["answers"].append({
                        "query": sub_query,
                        "answer": {"text": "Error processing this part of your question"},
                        "type": "error"
                    })
        except Exception as e:
            print(f"Error processing multi-question request: {e}")
            return jsonify({
                "error": "Failed to process multi-question request",
                "success": False,
                "details": str(e)
            }), 500
        
        if not combined_response["answers"]:
            return jsonify({
                "error": "No valid answers generated",
                "success": False
            }), 400
        
        return jsonify(combined_response), 200

    # Extract question type early
    q_type = filters.get("question_type", "search_request")

    # Handle analytical questions FIRST (before other question types)
    if q_type == "analytical_question":
        return handle_analytical_question(query, filters, search_properties)

    # ✅ If it's a QUESTION (Q&A mode)
    if filters.get("is_question"):
        # q_type already extracted above
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
        try:
            listings = search_properties(inner_filters)
        except Exception as e:
            print(f"Error fetching properties for question: {e}")
            listings = []

        if not listings:
            # Provide helpful response even when no properties are found
            if q_type == "general_question" and ("how to buy" in query.lower() or "how to purchase" in query.lower()):
                answer = {
                    "text": f"To buy a villa in {inner_filters.get('query', 'Dubai')}, here's what you need to know:",
                    "steps": [
                        "1. **Get Pre-Approval**: Contact a bank for mortgage pre-approval",
                        "2. **Find a Property**: Search for available villas in the area",
                        "3. **Make an Offer**: Work with a real estate agent to make an offer",
                        "4. **Legal Process**: Complete due diligence and legal documentation",
                        "5. **Final Payment**: Complete the transaction and transfer ownership"
                    ],
                    "additional_info": {
                        "note": "No current listings found, but the process remains the same",
                        "location": inner_filters.get('query', 'Dubai')
                    }
                }
                return jsonify({
                    "is_question": True,
                    "question_type": q_type,
                    "filters": inner_filters,
                    "answer": answer,
                }), 200
            else:
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

            result = estimate_property_price(listings, inner_filters)

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
        elif q_type == "general_question":
            # Handle general questions like "how to buy a villa"
            if "how to buy" in query.lower() or "how to purchase" in query.lower():
                answer = {
                    "text": f"To buy a villa in {inner_filters.get('query', 'Dubai')}, here's what you need to know:",
                    "steps": [
                        "1. **Get Pre-Approval**: Contact a bank for mortgage pre-approval",
                        "2. **Find a Property**: Browse available villas (I found {len(listings)} options for you)",
                        "3. **Make an Offer**: Work with a real estate agent to make an offer",
                        "4. **Legal Process**: Complete due diligence and legal documentation",
                        "5. **Final Payment**: Complete the transaction and transfer ownership"
                    ],
                    "additional_info": {
                        "average_price": f"AED {sum([item.get('price', 0) for item in listings if item.get('price')]) / len([item for item in listings if item.get('price')]):,.0f}" if listings else "Contact for pricing",
                        "available_properties": len(listings),
                        "location": inner_filters.get('query', 'Dubai')
                    }
                }
            else:
                # Generic question - return listings with analysis
                answer = {
                    "text": f"Found {len(listings)} properties matching your criteria in {inner_filters.get('query', 'the area')}"
                }

            return jsonify({
                "is_question": True,
                "question_type": q_type,
                "filters": inner_filters,
                "answer": answer,
                "data": listings,
                "agent_insights": generate_agent_insights(listings, query, inner_filters),
                "suggestions": generate_proactive_suggestions(listings, query, inner_filters)
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
    listings = search_properties(filters.get('filters', {}))
    
    # Add agent capabilities to the response
    response = {
        "success": True,
        "agent_id": "real_estate_agent_v1",
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "parsed_filters": filters,
        "properties": listings,
        "property_count": len(listings) if listings else 0,
        "agent_insights": [],
        "suggestions": []
    }
    
    # Generate insights if we have results
    if listings:
        # Price analysis
        prices = [item.get("price", 0) for item in listings if item.get("price")]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            response["agent_insights"].append({
                "type": "price_analysis",
                "title": "Price Insights",
                "message": f"Found {len(listings)} properties with prices ranging from AED {min_price:,.0f} to AED {max_price:,.0f}",
                "data": {
                    "average_price": avg_price,
                    "price_range": {"min": min_price, "max": max_price},
                    "property_count": len(listings)
                }
            })
        
        # Location analysis
        locations = [item.get("location_name", "") for item in listings if item.get("location_name")]
        if locations:
            unique_locations = list(set(locations))
            response["agent_insights"].append({
                "type": "location_analysis",
                "title": "Location Distribution",
                "message": f"Properties found in {len(unique_locations)} different areas within {filters.get('filters', {}).get('query', 'the search area')}",
                "data": {
                    "unique_locations": len(unique_locations),
                    "top_locations": unique_locations[:5]
                }
            })
        
        # Proactive suggestions
        response["suggestions"].extend([
            "Would you like me to filter by price range?",
            "I can help you compare similar properties",
            "Would you like to see properties on a map?",
            "I can set up alerts for new properties matching your criteria"
        ])
    else:
        response["agent_insights"].append({
            "type": "no_results",
            "title": "No Properties Found",
            "message": "No properties found matching your criteria. Try adjusting your search parameters.",
            "suggestions": [
                "Try a broader location search",
                "Consider different property types",
                "Adjust your price range",
                "Check spelling of location names"
            ]
        })
    
    return jsonify(response)


# -------------------
# Price Estimation
# -------------------

def estimate_property_price(listings, filters):
    """
    Estimate price of a property based on similar listings in the same location.
    Falls back to general location avg if exact match is not found.
    """

    # First try with given filters
    # listings = filters
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
    print(f"Estimate filters are {filters.get('max_area')}")
    if filters.get("max_area") and price_per_sqft:
        estimated_price = round(filters.get('max_area') * price_per_sqft)

    result_text = (
        f"Based on {len(listings)} similar properties in {filters.get('query', 'the area')}, "
        f"the average price is AED {avg_price:,.0f} "
        f"({price_per_sqft:,.0f} per sqft)."
    )
    if estimated_price:
        result_text += f" Estimated price for your property ({filters.get('max_area')} sqft) is around AED {estimated_price:,.0f}."
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
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
