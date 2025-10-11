# For sale Example
# import json
#
# import pandas as pd
# import requests
#
# # The URL remains the same for the API request
# url = "https://ll8iz711cs-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.25.2)%3B%20Browser%20(lite)&x-algolia-api-key=15cb8b0a2d2d435c6613111d860ecfc5&x-algolia-application-id=LL8IZ711CS"
#
# headers = {
#     "Accept": "*/*",
#     "Accept-Encoding": "gzip, deflate, br, zstd",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Connection": "keep-alive",
#     "Host": "ll8iz711cs-2.algolianet.com",
#     "Origin": "https://www.bayut.com",
#     "Referer": "https://www.bayut.com/",
#     "Sec-Fetch-Dest": "empty",
#     "Sec-Fetch-Mode": "cors",
#     "Sec-Fetch-Site": "cross-site",
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
#     "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": '"macOS"'
# }
#
# payload = {
#     "requests": [
#         {
#             "indexName": "bayut-production-ads-verified-score-en",
#             "params": (
#                 "page=0"
#                 "&hitsPerPage=24"
#                 "&query="
#                 "&optionalWords="
#                 "&facets=%5B%5D"
#                 "&maxValuesPerFacet=10"
#                 "&attributesToHighlight=%5B%5D"
#                 "&attributesToRetrieve=%5B%22type%22%2C%22agency%22%2C%22area%22%2C%22baths%22%2C%22category%22%2C%22additionalCategories%22%2C%22contactName%22%2C%22externalID%22%2C%22sourceID%22%2C%22id%22%2C%22location%22%2C%22objectID%22%2C%22phoneNumber%22%2C%22coverPhoto%22%2C%22photoCount%22%2C%22price%22%2C%22product%22%2C%22productLabel%22%2C%22purpose%22%2C%22geography%22%2C%22permitNumber%22%2C%22referenceNumber%22%2C%22rentFrequency%22%2C%22rooms%22%2C%22slug%22%2C%22slug_l1%22%2C%22slug_l2%22%2C%22slug_l3%22%2C%22title%22%2C%22title_l1%22%2C%22title_l2%22%2C%22title_l3%22%2C%22createdAt%22%2C%22updatedAt%22%2C%22ownerID%22%2C%22isVerified%22%2C%22propertyTour%22%2C%22verification%22%2C%22completionDetails%22%2C%22completionStatus%22%2C%22furnishingStatus%22%2C%22-agency.tier%22%2C%22coverVideo%22%2C%22videoCount%22%2C%22description%22%2C%22description_l1%22%2C%22description_l2%22%2C%22description_l3%22%2C%22descriptionTranslated%22%2C%22descriptionTranslated_l1%22%2C%22descriptionTranslated_l2%22%2C%22descriptionTranslated_l3%22%2C%22floorPlanID%22%2C%22panoramaCount%22%2C%22hasMatchingFloorPlans%22%2C%22state%22%2C%22photoIDs%22%2C%22reactivatedAt%22%2C%22hidePrice%22%2C%22extraFields%22%2C%22projectNumber%22%2C%22locationPurposeTier%22%2C%22hasRedirectionLink%22%2C%22ownerAgent%22%2C%22hasEmail%22%2C%22plotArea%22%2C%22offplanDetails%22%2C%22paymentPlans%22%2C%22paymentPlanSummaries%22%2C%22project%22%2C%22availabilityStatus%22%2C%22userExternalID%22%2C%22units%22%2C%22unitCategories%22%2C%22downPayment%22%2C%22clips%22%2C%22contactMethodAvailability%22%2C%22agentAdStoriesCount%22%2C%22isProjectOwned%22%2C%22documents%22%5D"
#                 "&filters=purpose%3A%22for-sale%22%20AND%20%28category.slug%3A%22residential%22%29%20AND%20completionStatus%3A%22under-construction%22%20AND%20%28product%3A%22superhot%22%29"
#                 "&numericFilters="
#             )
#         }
#     ]
# }
#
# try:
#     response = requests.post(url, headers=headers, json=payload)
#     response.raise_for_status()
#
#     data = response.json()
#
#     extracted_data = []
#     properties = data['results'][0]['hits']  # Access the list of hits
#
#     for property_item in properties:
#         latitude = property_item.get('geography', {}).get('lat')
#         longitude = property_item.get('geography', {}).get('lng')
#         price = property_item.get('price')
#         purpose = property_item.get('purpose')
#         print(f"purpose is {purpose}")
#
#
#         # --- New part for image URLs ---
#         photo_ids = property_item.get('photoIDs', [])
#         all_image_urls = []
#         if photo_ids:
#             # Base URL pattern for thumbnails
#             base_image_url_pattern = "https://images.bayut.com/thumbnails/{image_id}-400x300.webp"
#             for image_id in photo_ids:
#                 constructed_image_url = base_image_url_pattern.format(image_id=image_id)
#                 all_image_urls.append(constructed_image_url)
#         # --- End new part ---
#
#         extracted_data.append({
#             'id': property_item.get('id'),
#             'title': property_item.get('title'),
#             'price': price,
#             'area': property_item.get('area'),
#             'rooms': property_item.get('rooms'),
#             'baths': property_item.get('baths'),
#             'purpose': property_item.get('purpose'),
#             'completion_status': property_item.get('completionStatus'),
#             'latitude': latitude,
#             'longitude': longitude,
#             'location_name': property_item.get('location')[-1].get('name') if property_item.get('location') else None,
#             'cover_photo_url': property_item.get('coverPhoto', {}).get('url'),
#             'all_image_urls': all_image_urls,  # Added the list of all image URLs
#             'agency_name': property_item.get('agency', {}).get('name'),
#             'contact_name': property_item.get('contactName'),
#             'mobile_number': property_item.get('phoneNumber', {}).get('mobile'),
#             'whatsapp_number': property_item.get('phoneNumber', {}).get('whatsapp'),
#             'down_payment_percentage': property_item.get('paymentPlanSummaries', [{}])[0].get('breakdown', {}).get(
#                 'downPaymentPercentage') if property_item.get('paymentPlanSummaries') else None
#         })
#
#     print("\n--- Extracted Data (first property example with all image URLs) ---")
#     if extracted_data:
#         print(json.dumps(extracted_data[0], indent=4))
#
#     try:
#         df = pd.DataFrame(extracted_data)
#         # If you want to save the image URLs as a string in the CSV (e.g., comma-separated)
#         df['all_image_urls'] = df['all_image_urls'].apply(lambda x: ', '.join(x) if x else '')
#         # df.to_csv("bayut_properties_all_images.csv", index=False)
#         print("\nData successfully put into a pandas DataFrame.")
#         print(df.head())
#     except ImportError:
#         print("\nInstall pandas (pip install pandas) to easily save to CSV or perform advanced data manipulation.")
#
#
# except requests.exceptions.HTTPError as err:
#     print(f"HTTP error occurred: {err}")
#     print(f"Response content: {response.text}")
# except requests.exceptions.RequestException as err:
#     print(f"An error occurred: {err}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")

# For rent
import json
import pandas as pd
import requests

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

# --- Broadened payload for 'for-rent' ---
payload_for_rent_broad = {
    "requests": [
        {
            "indexName": "bayut-production-ads-verified-score-en",
            "params": (
                "page=0"
                "&hitsPerPage=24"
                "&query= villa"
                "&optionalWords="
                "&facets=%5B%5D"
                "&maxValuesPerFacet=10"
                "&attributesToHighlight=%5B%5D"
                "&attributesToRetrieve=%5B%22type%22%2C%22agency%22%2C%22area%22%2C%22baths%22%2C%22category%22%2C%22additionalCategories%22%2C%22contactName%22%2C%22externalID%22%2C%22sourceID%22%2C%22id%22%2C%22location%22%2C%22objectID%22%2C%22phoneNumber%22%2C%22coverPhoto%22%2C%22photoCount%22%2C%22price%22%2C%22product%22%2C%22productLabel%22%2C%22purpose%22%2C%22geography%22%2C%22permitNumber%22%2C%22referenceNumber%22%2C%22rentFrequency%22%2C%22rooms%22%2C%22slug%22%2C%22slug_l1%22%2C%22slug_l2%22%2C%22slug_l3%22%2C%22title%22%2C%22title_l1%22%2C%22title_l2%22%2C%22title_l3%22%2C%22createdAt%22%2C%22updatedAt%22%2C%22ownerID%22%2C%22isVerified%22%2C%22propertyTour%22%2C%22verification%22%2C%22completionDetails%22%2C%22completionStatus%22%2C%22furnishingStatus%22%2C%22-agency.tier%22%2C%22coverVideo%22%2C%22videoCount%22%2C%22description%22%2C%22description_l1%22%2C%22description_l2%22%2C%22description_l3%22%2C%22descriptionTranslated%22%2C%22descriptionTranslated_l1%22%2C%22descriptionTranslated_l2%22%2C%22descriptionTranslated_l3%22%2C%22floorPlanID%22%2C%22panoramaCount%22%2C%22hasMatchingFloorPlans%22%2C%22state%22%2C%22photoIDs%22%2C%22reactivatedAt%22%2C%22hidePrice%22%2C%22extraFields%22%2C%22projectNumber%22%2C%22locationPurposeTier%22%2C%22hasRedirectionLink%22%2C%22ownerAgent%22%2C%22hasEmail%22%2C%22plotArea%22%2C%22offplanDetails%22%2C%22paymentPlans%22%2C%22paymentPlanSummaries%22%2C%22project%22%2C%22availabilityStatus%22%2C%22userExternalID%22%2C%22units%22%2C%22unitCategories%22%2C%22downPayment%22%2C%22clips%22%2C%22contactMethodAvailability%22%2C%22agentAdStoriesCount%22%2C%22isProjectOwned%22%2C%22documents%22%5D"
                "&filters=purpose%3A%22for-rent%22" # Removed category.slug: "residential"
                "&numericFilters="
            )
        }
    ]
}

try:
    response = requests.post(url, headers=headers, json=payload_for_rent_broad) # Using the new payload
    response.raise_for_status()

    data = response.json()

    extracted_data = []
    properties = data['results'][0]['hits']  # Access the list of hits

    if not properties:
        print("\nNo properties found with the current filters. Consider broadening the search further or checking Bayut directly.")

    for property_item in properties:
        latitude = property_item.get('geography', {}).get('lat')
        longitude = property_item.get('geography', {}).get('lng')
        price = property_item.get('price')
        purpose = property_item.get('purpose')
        print(f"purpose is {purpose}")


        photo_ids = property_item.get('photoIDs', [])
        all_image_urls = []
        if photo_ids:
            base_image_url_pattern = "https://images.bayut.com/thumbnails/{image_id}-400x300.webp"
            for image_id in photo_ids:
                constructed_image_url = base_image_url_pattern.format(image_id=image_id)
                all_image_urls.append(constructed_image_url)

        extracted_data.append({
            'id': property_item.get('id'),
            'title': property_item.get('title'),
            'price': price,
            'area': property_item.get('area'),
            'rooms': property_item.get('rooms'),
            'baths': property_item.get('baths'),
            'purpose': property_item.get('purpose'),
            'completion_status': property_item.get('completionStatus'),
            'latitude': latitude,
            'longitude': longitude,
            'location_name': property_item.get('location')[-1].get('name') if property_item.get('location') else None,
            'cover_photo_url': property_item.get('coverPhoto', {}).get('url'),
            'all_image_urls': all_image_urls,
            'agency_name': property_item.get('agency', {}).get('name'),
            'contact_name': property_item.get('contactName'),
            'mobile_number': property_item.get('phoneNumber', {}).get('mobile'),
            'whatsapp_number': property_item.get('phoneNumber', {}).get('whatsapp'),
            'down_payment_percentage': property_item.get('paymentPlanSummaries', [{}])[0].get('breakdown', {}).get(
                'downPaymentPercentage') if property_item.get('paymentPlanSummaries') else None
        })

    print("\n--- Extracted Data (first property example with all image URLs) ---")
    if extracted_data:
        print(json.dumps(extracted_data[0], indent=4))
    else:
        print("No data extracted.")


    try:
        df = pd.DataFrame(extracted_data)
        df['all_image_urls'] = df['all_image_urls'].apply(lambda x: ', '.join(x) if x else '')
        df.to_csv("bayut_properties_for_rent_broad.csv", index=False)
        print("\nData successfully put into a pandas DataFrame and saved to bayut_properties_for_rent_broad.csv.")
        print(df.head())
    except ImportError:
        print("\nInstall pandas (pip install pandas) to easily save to CSV or perform advanced data manipulation.")


except requests.exceptions.HTTPError as err:
    print(f"HTTP error occurred: {err}")
    print(f"Response content: {response.text}")
except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")