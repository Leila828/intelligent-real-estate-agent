import json
import pandas as pd
import requests
import time # For time.sleep()
import matplotlib.pyplot as plt
import seaborn as sns

# --- Constants for the API (can be moved to a config file if needed) ---
BAYUT_API_URL = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.25.2)%3B%20Browser%20(lite)&x-algolia-api-key=15cb8b0a2d2d435c6613111d860ecfc5&x-algolia-application-id=LL8IZ711CS"
BAYUT_API_HEADERS = {
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
BAYUT_INDEX_NAME = "bayut-production-ads-en"

# --- Helper Function for raw API calls (internal use) ---
def _fetch_bayut_api_response(
    purposes=None,
    location_query="",
    property_types=None,
    completion_status=None,
    rent_frequency=None,
    page=0,
    hits_per_page=100
):
    """
    Internal helper function to make a single API call to Bayut.
    Returns the raw JSON response object from Algolia's 'results'[0] entry.
    """
    if purposes is None:
        purposes = []
    if isinstance(purposes, str):
        purposes = [purposes]

    if property_types is None:
        property_types = []
    if isinstance(property_types, str):
        property_types = [property_types]

    filters_raw_parts = []

    if purposes:
        purpose_filters_algolia = [f'purpose:"{p}"' for p in purposes]
        filters_raw_parts.append(f'({" OR ".join(purpose_filters_algolia)})')

    if property_types:
        category_slug_map = {
            "resident": "residential", "commercial": "commercial",
            "apartment": "apartments", "villa": "villas", "townhouse": "townhouses",
            "penthouse": "penthouses", "villa compound": "villas",
            "hotel apartment": "hotel-apartments", "land": "land",
            "floor": "floors", "building": "buildings"
        }
        mapped_types = []
        for p_type in property_types:
            slug = category_slug_map.get(p_type.lower())
            if slug:
                mapped_types.append(f'category.slug:"{slug}"')
        if mapped_types:
            filters_raw_parts.append(f'({" OR ".join(mapped_types)})')

    if "for-sale" in purposes and completion_status:
        if completion_status.lower() == "ready":
            filters_raw_parts.append('completionStatus:"completed"')
        elif completion_status.lower() == "off-plan":
            filters_raw_parts.append('completionStatus:"under-construction"')

    if "for-rent" in purposes and rent_frequency:
        if rent_frequency.lower() in ["yearly", "monthly", "weekly", "daily"]:
            filters_raw_parts.append(f'rentFrequency:"{rent_frequency.lower()}"')

    full_filters_raw = " AND ".join(filters_raw_parts)
    filters_string = requests.utils.quote(full_filters_raw) if full_filters_raw else ""

    encoded_location_query = requests.utils.quote(location_query)

    params_string = (
        f"page={page}"
        f"&hitsPerPage={hits_per_page}"
        f"&query={encoded_location_query}"
        "&optionalWords="
        "&facets=%5B%5D"
        "&attributesToHighlight=%5B%5D"
        "&attributesToRetrieve=%5B%22type%22%2C%22agency%22%2C%22area%22%2C%22baths%22%2C%22category%22%2C%22additionalCategories%22%2C%22contactName%22%2C%22externalID%22%2C%22sourceID%22%2C%22id%22%2C%22location%22%2C%22objectID%22%2C%22phoneNumber%22%2C%22coverPhoto%22%2C%22photoCount%22%2C%22price%22%2C%22product%22%2C%22productLabel%22%2C%22purpose%22%2C%22geography%22%2C%22permitNumber%22%2C%22referenceNumber%22%2C%22rentFrequency%22%2C%22rooms%22%2C%22slug%22%2C%22slug_l1%22%2C%22slug_l2%22%2C%22slug_l3%22%2C%22title%22%2C%22title_l1%22%2C%22title_l2%22%2C%22title_l3%22%2C%22createdAt%22%2C%22updatedAt%22%2C%22ownerID%22%2C%22isVerified%22%2C%22propertyTour%22%2C%22verification%22%2C%22completionDetails%22%2C%22completionStatus%22%2C%22furnishingStatus%22%2C%22-agency.tier%22%2C%22coverVideo%22%2C%22videoCount%22%2C%22description%22%2C%22description_l1%22%2C%22description_l2%22%2C%22description_l3%22%2C%22descriptionTranslated%22%2C%22descriptionTranslated_l1%22%2C%22descriptionTranslated_l2%22%2C%22descriptionTranslated_l3%22%2C%22floorPlanID%22%2C%22panoramaCount%22%2C%22hasMatchingFloorPlans%22%2C%22state%22%2C%22photoIDs%22%2C%22reactivatedAt%22%2C%22hidePrice%22%2C%22extraFields%22%2C%22projectNumber%22%2C%22locationPurposeTier%22%2C%22hasRedirectionLink%22%2C%22ownerAgent%22%2C%22hasEmail%22%2C%22plotArea%22%2C%22offplanDetails%22%2C%22paymentPlans%22%2C%22paymentPlanSummaries%22%2C%22project%22%2C%22availabilityStatus%22%2C%22userExternalID%22%2C%22units%22%2C%22unitCategories%22%2C%22downPayment%22%2C%22clips%22%2C%22contactMethodAvailability%22%2C%22agentAdStoriesCount%22%2C%22isProjectOwned%22%2C%22documents%22%5D"
    )

    if filters_string:
        params_string += f"&filters={filters_string}"
    params_string += "&numericFilters="

    payload = {
        "requests": [
            {
                "indexName": BAYUT_INDEX_NAME,
                "params": params_string
            }
        ]
    }

    try:
        response = requests.post(BAYUT_API_URL, headers=BAYUT_API_HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['results'][0] # Return the full result object for page info and hits
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response content: {response.text}")
        return {}
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}


# --- Main Function to Get Bayut Property Data ---

def get_bayut_property_data(
    purposes: list or str = None,
    location_query: str = "",
    property_types: list or str = None,
    completion_status: str = None,
    rent_frequency: str = None,
    max_pages_to_fetch: int = None, # New: Optional limit on pages to fetch
    initial_hits_per_page: int = 100, # Max hits per page for initial metadata query
    delay_seconds: float = 0.1 # Delay between page requests
) -> pd.DataFrame:
    """
    Fetches property data from the Bayut.com API based on specified filters,
    handles pagination, and returns the data as a pandas DataFrame.

    This function first performs an initial API call to determine the total
    number of pages and optimal hits per page, then iterates through pages
    to collect all available data up to the API's limits.

    Args:
        purposes (list or str, optional): A list of property purposes
            (e.g., ["for-sale", "for-rent"]) or a single purpose string.
            If None or empty, no purpose filter is applied.
            Valid values: "for-sale", "for-rent".
        location_query (str, optional): A free-text query string for location
            (e.g., "Dubai Marina", "Downtown Dubai"). Leave empty for a broad
            search across the entire UAE. Defaults to "".
        property_types (list or str, optional): A list of specific property types
            (e.g., ["apartment", "villa", "commercial"]) or a single type string.
            If None or empty, all property types will be included (unless
            implicitly filtered by other parameters like 'residential' category).
            Mapped values: "resident" -> "residential", "commercial" -> "commercial",
            "apartment" -> "apartments", "villa" -> "villas", "townhouse" -> "townhouses",
            "penthouse" -> "penthouses", "villa compound" -> "villas",
            "hotel apartment" -> "hotel-apartments", "land" -> "land",
            "floor" -> "floors", "building" -> "buildings".
        completion_status (str, optional): Applicable only for "for-sale" properties.
            "ready" (for completed properties) or "off-plan" (for under-construction).
            If None, all completion statuses are included.
        rent_frequency (str, optional): Applicable only for "for-rent" properties.
            "yearly", "monthly", "weekly", or "daily". If None, all frequencies
            are included.
        max_pages_to_fetch (int, optional): An optional hard limit on the number
            of pages to fetch. If None, the function will attempt to fetch all
            pages reported by the API (up to its internal maximum like 500).
            Useful for testing or limiting large data pulls.
        initial_hits_per_page (int, optional): The number of hits per page to
            request for the initial API call to determine pagination metadata.
            It's recommended to keep this at 100 as this is often the max.
            Defaults to 100.
        delay_seconds (float, optional): The delay in seconds between consecutive
            API requests. This is crucial for avoiding hitting API rate limits.
            Defaults to 0.1 seconds.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the collected property data.
                      Returns an empty DataFrame if no data is found or an
                      error occurs during fetching.

    Raises:
        requests.exceptions.RequestException: If a network-related error occurs during API call.
        requests.exceptions.HTTPError: If the API returns an HTTP error status code.
        Exception: For any other unexpected errors during data processing.

    Notes:
        - The Bayut API (Algolia) often limits the total number of pages that can
          be retrieved via sequential pagination (e.g., typically around 500 pages,
          yielding up to 50,000 records). The 'nbHits' from the API is an estimate
          and not fully paginatable for very broad queries.
        - Ensure you have 'pandas', 'requests', 'matplotlib', and 'seaborn' installed:
          `pip install pandas requests matplotlib seaborn`
    """
    all_extracted_data = []

    print("--- Initiating Bayut Property Data Collection ---")

    # Step 1: Make an initial call to get pagination information
    print("  Making initial API call to determine pagination limits...")
    initial_response_data = _fetch_bayut_api_response(
        purposes=purposes,
        location_query=location_query,
        property_types=property_types,
        completion_status=completion_status,
        rent_frequency=rent_frequency,
        page=0,
        hits_per_page=initial_hits_per_page
    )

    if not initial_response_data:
        print("  Initial API call failed or returned no data. Returning empty DataFrame.")
        return pd.DataFrame() # Return empty DataFrame if initial call fails

    total_nb_hits = initial_response_data.get('nbHits', 0)
    total_nb_pages = initial_response_data.get('nbPages', 0)
    effective_hits_per_page = initial_response_data.get('hitsPerPage', initial_hits_per_page)

    print(f"  API reports: Total Hits = {total_nb_hits}, Total Pages = {total_nb_pages} (at {effective_hits_per_page} hits/page).")

    # Determine the actual number of pages to fetch
    pages_to_fetch = total_nb_pages
    if max_pages_to_fetch is not None and max_pages_to_fetch < total_nb_pages:
        pages_to_fetch = max_pages_to_fetch
        print(f"  Fetching limited to {max_pages_to_fetch} pages as requested.")
    else:
        print(f"  Attempting to fetch up to {pages_to_fetch} pages based on API report.")


    # Step 2: Iterate through pages and fetch data
    current_properties_count = 0
    collected_pages_count = 0

    for p in range(pages_to_fetch):
        print(f"  Fetching page {p}...")
        page_result = _fetch_bayut_api_response(
            purposes=purposes,
            location_query=location_query,
            property_types=property_types,
            completion_status=completion_status,
            rent_frequency=rent_frequency,
            page=p,
            hits_per_page=effective_hits_per_page
        )

        page_properties = page_result.get('hits', []) # Extract hits from the result

        if not page_properties:
            print(f"  Page {p} returned 0 properties. End of data or API limit reached for these filters. Stopping pagination.")
            break # Stop if a page returns no properties
        else:
            num_properties_on_page = len(page_properties)
            print(f"  Page {p} returned {num_properties_on_page} properties.")
            current_properties_count += num_properties_on_page
            collected_pages_count += 1

        # Extract relevant fields and append to master list
        for prop in page_properties:
            all_extracted_data.append({
                'id': prop.get('id'),
                'title': prop.get('title'),
                'price': prop.get('price'),
                'area': prop.get('area'),
                'rooms': prop.get('rooms'),
                'baths': prop.get('baths'),
                'purpose': prop.get('purpose'),
                'completion_status': prop.get('completionStatus'),
                'latitude': prop.get('geography', {}).get('lat'),
                'longitude': prop.get('geography', {}).get('lng'),
                'location_name': prop.get('location')[-1].get('name') if prop.get('location') else None,
                'cover_photo_url': prop.get('coverPhoto', {}).get('url'),
                'all_image_urls': [f"https://images.bayut.com/thumbnails/{img_id}-400x300.webp" for img_id in prop.get('photoIDs', [])],
                'agency_name': prop.get('agency', {}).get('name'),
                'contact_name': prop.get('contactName'),
                'mobile_number': prop.get('phoneNumber', {}).get('mobile'),
                'whatsapp_number': prop.get('phoneNumber', {}).get('whatsapp'),
                'down_payment_percentage': prop.get('paymentPlanSummaries', [{}])[0].get('breakdown', {}).get('downPaymentPercentage')
            })
        time.sleep(delay_seconds) # Pause to respect rate limits

    print(f"\nCollection complete. Actually collected {len(all_extracted_data)} properties across {collected_pages_count} pages.")

    # Step 3: Convert to DataFrame and return
    if all_extracted_data:
        df = pd.DataFrame(all_extracted_data)
        # Convert list of image URLs into a comma-separated string for CSV export
        df['all_image_urls'] = df['all_image_urls'].apply(lambda x: ', '.join(x) if x else '')
        return df
    else:
        print("No properties were collected. Returning empty DataFrame.")
        return pd.DataFrame()


# --- Example Usage (in your main script or another module) ---

if __name__ == "__main__":
    print("--- Running Example Data Collection ---")

    # Example 1: Get all "for-sale" apartments in "Dubai Marina", ready status, up to 5 pages
    df_dubai_marina_apartments = get_bayut_property_data(
        purposes="for-sale",
        location_query="Dubai Marina",
        property_types="apartment",
        completion_status="ready",
        max_pages_to_fetch=5 # Fetch only first 5 pages for this specific query
    )
    print("\n--- Dubai Marina Apartments (For Sale, Ready) ---")
    if not df_dubai_marina_apartments.empty:
        print(f"Collected {len(df_dubai_marina_apartments)} properties.")
        print(df_dubai_marina_apartments.head())
        df_dubai_marina_apartments.to_csv("dubai_marina_ready_apartments.csv", index=False)
        print("Saved to dubai_marina_ready_apartments.csv")
    else:
        print("No data collected for Dubai Marina Apartments.")


    # Example 2: Get all "for-rent" villas in "Palm Jumeirah", yearly frequency (all available pages)
    df_palm_villas_rent = get_bayut_property_data(
        purposes="for-rent",
        location_query="Palm Jumeirah",
        property_types="villa",
        rent_frequency="yearly",
        delay_seconds=0.2 # Slightly longer delay
    )
    print("\n--- Palm Jumeirah Villas (For Rent, Yearly) ---")
    if not df_palm_villas_rent.empty:
        print(f"Collected {len(df_palm_villas_rent)} properties.")
        print(df_palm_villas_rent.head())
        df_palm_villas_rent.to_csv("palm_jumeirah_yearly_villas.csv", index=False)
        print("Saved to palm_jumeirah_yearly_villas.csv")
    else:
        print("No data collected for Palm Jumeirah Villas.")


    # Example 3: Get all "for-sale" OR "for-rent" properties for all UAE, all types (dynamic pages)
    # This will attempt to fetch up to 500 pages (max reported by API), resulting in ~1700 properties
    df_uae_all = get_bayut_property_data(
        purposes=["for-sale", "for-rent"],
        location_query="",
        property_types=[], # All types
        delay_seconds=0.1 # Short delay
    )
    print("\n--- All UAE Properties (For Sale OR For Rent) ---")
    if not df_uae_all.empty:
        print(f"Collected {len(df_uae_all)} properties.")
        print(df_uae_all.head())
        df_uae_all.to_csv("uae_all_properties.csv", index=False)
        print("Saved to uae_all_properties.csv")

        # Basic Plotting for the large dataset
        print("\n--- Generating plots for All UAE Properties ---")
        sns.set_style("whitegrid")

        plt.figure(figsize=(12, 7))
        sns.histplot(df_uae_all['price'].dropna(), bins=50, kde=True, color='skyblue')
        plt.title('Distribution of Property Prices (All UAE)', fontsize=16)
        plt.xlabel('Price (AED)', fontsize=12)
        plt.ylabel('Number of Properties', fontsize=12)
        plt.ticklabel_format(style='plain', axis='x')
        plt.show()

        plt.figure(figsize=(8, 6))
        sns.countplot(data=df_uae_all, x='purpose', palette='viridis')
        plt.title('Number of Properties by Purpose (All UAE)', fontsize=16)
        plt.xlabel('Purpose', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.show()

        if 'location_name' in df_uae_all.columns:
            plt.figure(figsize=(12, 8))
            # Get top N locations
            top_locations = df_uae_all['location_name'].value_counts().nlargest(15).index
            sns.countplot(data=df_uae_all[df_uae_all['location_name'].isin(top_locations)],
                          y='location_name', order=top_locations, palette='Spectral')
            plt.title('Top 15 Locations by Property Count (All UAE)', fontsize=16)
            plt.xlabel('Count', fontsize=12)
            plt.ylabel('Location Name', fontsize=12)
            plt.tight_layout()
            plt.show()
        else:
            print("\n'location_name' column not found for location distribution plot.")

    else:
        print("No data collected for All UAE Properties.")