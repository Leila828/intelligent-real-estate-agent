import requests
import json

# API endpoint
url = "https://www.bayut.com/api/agent/stories/search"

# Query parameters
params = {
    "purpose": "for-sale",
    "category_external_id": "1",                      # Apartment
    "locationExternalIDs": "5002,6020,5416",          # Dubai Marina, Downtown, JVC
    "price_min": "500000",
    "price_max": "5000000",
    "area_min": "500",
    "area_max": "3000",
    "rooms_min": "1",
    "rooms_max": "4",
    "sort": "price-desc",
    "verified": "true",
    "distinct_agents": "true",
    "minimal": "true",
    "language": "en"
}


try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    print("✅ API call succeeded. Response:\n")
    print(json.dumps(data, indent=2))

    print("\n🔎 Agents Found:")
    if "data" in data:
        for entry in data["data"]:
            agent = entry.get("agent", {})
            agency = agent.get("agency", {})
            print(f"- Name: {agent.get('name')}")
            print(f"  Phone: {agent.get('phone')}")
            print(f"  WhatsApp: {agent.get('whatsapp')}")
            print(f"  Agency: {agency.get('name')}")
            print("-" * 40)
    else:
        print("No agents found in response.")
except requests.exceptions.RequestException as e:
    print(f"❌ Error during API call: {e}")
