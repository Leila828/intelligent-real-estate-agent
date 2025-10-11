import json
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import time

# (Your fetch_bayut_properties function goes here, as in the last complete snippet)
def fetch_bayut_properties(
    purposes=None,
    location_query="",
    property_types=None,
    completion_status=None,
    rent_frequency=None,
    page=0,
    hits_per_page=24,
    return_raw_response=False
):
    """
    Fetches property data from the Bayut API with enhanced filtering.
    ... (docstring content remains the same) ...
    """
    if purposes is None:
        purposes = []
    if isinstance(purposes, str):
        purposes = [purposes]

    if property_types is None:
        property_types = []
    if isinstance(property_types, str):
        property_types = [property_types]

    url = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.25.2)%3B%20Browser%20(lite)&x-algolia-api-key=15cb8b0a2d2d435c6613111d860ecfc5&x-algolia-application-id=LL8IZ711CS"

    headers = {
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
                "indexName": "bayut-production-ads-en",
                "params": params_string
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if return_raw_response:
            return data['results'][0]
        else:
            return data['results'][0]['hits']
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response content: {response.text}")
        return [] if not return_raw_response else {}
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        return [] if not return_raw_response else {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [] if not return_raw_response else {}

# --- Main script execution ---
if __name__ == "__main__":
    all_extracted_data = []

    print("\n--- Initiating Broad UAE Property Search for Pagination Info ---")

    # Step 1: Make an initial call to get pagination information (nbPages, hitsPerPage)
    initial_response_data = fetch_bayut_properties(
        purposes=["for-sale", "for-rent"],
        location_query="Ras Al Khaimah",
        property_types=[],
        completion_status=None,
        rent_frequency=None,
        page=0,
        hits_per_page=100, # This is correct for getting full pagination metadata
        return_raw_response=True
    )

    total_nb_hits = initial_response_data.get('nbHits', 0)
    total_nb_pages = initial_response_data.get('nbPages', 0)
    effective_hits_per_page = initial_response_data.get('hitsPerPage', 100)

    print(f"API reports: Total Hits = {total_nb_hits}, Total Pages = {total_nb_pages} (at {effective_hits_per_page} hits/page).")
    print(f"We will attempt to fetch up to {total_nb_pages} pages.")

    # Step 2: Use the obtained information to paginate and fetch all available data
    print("\n--- Fetching ALL 'for-sale' and 'for-rent' properties across UAE (paginated) ---")

    collected_pages_count = 0 # To keep track of how many pages we actually fetched
    total_properties_collected_in_loop = 0 # To verify the count during the loop

    for p in range(total_nb_pages):
        print(f"  Fetching page {p} for ALL UAE properties...")
        page_properties = fetch_bayut_properties(
            purposes=["for-sale", "for-rent"],
            location_query="",
            property_types=[],
            completion_status=None,
            rent_frequency=None,
            page=p,
            hits_per_page=effective_hits_per_page,
            return_raw_response=False
        )

        if not page_properties:
            print(f"  Page {p} returned 0 properties. This means we've hit the end of available data for these filters.")
            break # Stop if a page returns no properties
        else:
            num_properties_on_page = len(page_properties)
            print(f"  Page {p} returned {num_properties_on_page} properties.")
            total_properties_collected_in_loop += num_properties_on_page
            collected_pages_count += 1

        for prop in page_properties:
            all_extracted_data.append({
                'id': prop.get('id'), 'title': prop.get('title'), 'price': prop.get('price'),
                'area': prop.get('area'), 'rooms': prop.get('rooms'), 'baths': prop.get('baths'),
                'purpose': prop.get('purpose'), 'completion_status': prop.get('completionStatus'),
                'latitude': prop.get('geography', {}).get('lat'), 'longitude': prop.get('geography', {}).get('lng'),
                'location_name': prop.get('location')[-1].get('name') if prop.get('location') else None,
                'cover_photo_url': prop.get('coverPhoto', {}).get('url'),
                'all_image_urls': [f"https://images.bayut.com/thumbnails/{img_id}-400x300.webp" for img_id in prop.get('photoIDs', [])],
                'agency_name': prop.get('agency', {}).get('name'), 'contact_name': prop.get('contactName'),
                'mobile_number': prop.get('phoneNumber', {}).get('mobile'), 'whatsapp_number': prop.get('phoneNumber', {}).get('whatsapp'),
                'down_payment_percentage': prop.get('paymentPlanSummaries', [{}])[0].get('breakdown', {}).get('downPaymentPercentage')
            })
        time.sleep(0.1) # Add a small delay between requests to avoid rate limiting.

    print(f"\nCompleted pagination loop. Actually collected {total_properties_collected_in_loop} properties across {collected_pages_count} pages.")
    print(f"Total properties in final list: {len(all_extracted_data)}") # Should match total_properties_collected_in_loop

    # --- Consolidate, Process, and Save all data ---
    if all_extracted_data:
        try:
            df = pd.DataFrame(all_extracted_data)
            df['all_image_urls'] = df['all_image_urls'].apply(lambda x: ', '.join(x) if x else '')
            output_csv_filename = "bayut_properties_uae_all_dynamic_paginated.csv"
            df.to_csv(output_csv_filename, index=False)
            print(f"\nAll extracted data successfully put into a pandas DataFrame and saved to {output_csv_filename}.")

            print("\n--- First 5 rows of the DataFrame ---")
            print(df.head())
            print("\n--- Information about the DataFrame ---")
            df.info()

            print("\n--- Generating some basic plots ---")
            sns.set_style("whitegrid")
            plt.figure(figsize=(12, 7))
            sns.histplot(df['price'].dropna(), bins=50, kde=True, color='skyblue')
            plt.title('Distribution of Property Prices (All UAE)', fontsize=16)
            plt.xlabel('Price (AED)', fontsize=12)
            plt.ylabel('Number of Properties', fontsize=12)
            plt.ticklabel_format(style='plain', axis='x')
            plt.show()

            plt.figure(figsize=(8, 6))
            sns.countplot(data=df, x='purpose', palette='viridis')
            plt.title('Number of Properties by Purpose (All UAE)', fontsize=16)
            plt.xlabel('Purpose', fontsize=12)
            plt.ylabel('Count', fontsize=12)
            plt.show()

            if 'category.slug' in df.columns:
                 plt.figure(figsize=(10, 6))
                 sns.countplot(data=df, y='category.slug', order=df['category.slug'].value_counts().index, palette='crest')
                 plt.title('Number of Properties by Category/Type (All UAE)', fontsize=16)
                 plt.xlabel('Count', fontsize=12)
                 plt.ylabel('Category Slug', fontsize=12)
                 plt.show()
            else:
                 print("\n'category.slug' column not found for category distribution plot. Check data extraction.")

            df_filtered_plot = df[(df['area'].notna()) & (df['price'].notna())]
            df_filtered_plot = df_filtered_plot[(df_filtered_plot['area'] < df_filtered_plot['area'].quantile(0.99)) &
                                                (df_filtered_plot['price'] < df_filtered_plot['price'].quantile(0.99))]
            plt.figure(figsize=(14, 8))
            sns.scatterplot(data=df_filtered_plot, x='area', y='price', hue='purpose', style='purpose', s=50, alpha=0.7)
            plt.title('Property Area vs. Price (by Purpose, All UAE)', fontsize=16)
            plt.xlabel('Area (sq unit)', fontsize=12)
            plt.ylabel('Price (AED)', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.ticklabel_format(style='plain', axis='y')
            plt.show()

        except ImportError:
            print("\nInstall pandas, matplotlib, and seaborn (pip install pandas matplotlib seaborn) to save to CSV, perform advanced data manipulation, and visualization.")
        except Exception as e:
            print(f"\nAn error occurred during DataFrame processing or plotting: {e}")
    else:
        print("\nNo data was extracted across all attempts. CSV file was not created.")