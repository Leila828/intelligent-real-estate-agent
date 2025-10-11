import requests
import json

# The URL of the API endpoint
url = "https://dubailand.gov.ae/umbraco/surface/LandStatusV2/GetPropInfo"

# The query parameter
params = {
    "propId": "103457"
}

# The headers from your inspector
# NOTE: The captchaHash and cookie values are dynamic and will change.
# The values below are just for demonstration and will not work long-term.
# You will need to find a way to get a valid, current captchaHash.
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "BNI_persistence=... (your cookie values here)...",
    "Host": "dubailand.gov.ae",
    "Referer": "https://dubailand.gov.ae/ar/eservices/property-status-overview/property-status",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "captchaHash": "wXv5BiNEsfeHorwABhZbiJcjFYXmOgzF5bQanYFK9wKZqZpxwaYTXhWvdVHWlujH/ENcxWRaO88LXg5znHG1BKXPfQWB90l9mhJzp0mt+5EpITwU3RTDBD8R9Z9mFGbobS17hLH6UgVngXy39586T1wuUh+F4VyaUEMaKN8fgvVBsNrw5mewqpMRODQViF/WGT4KwwoXGeFuRISPPZb2fKBsEFJti455fmLOXm555Evg1+NeN2Erd9Snryr5xabcZecGYT7J59uvSunbm46lzfXqy2M8f770sen9TYFOG1l4FjEmV8cV6+9RPP8bAFe8MeiaDeANbKwE3EnMIFC8NRjsYB8uyrZnTtzFFwWZDSYqGyqX2XSOwTXCW1CAEhX17aETJFyewTUDmLd3mFWXWDJaSHR0nOcz09WbY15Z17ZOqOqaJygNF7FlGOC7YId7rlr7ftXiPzuy87L1zFtA7PG/hfQma4gT6ioSl8XB/lb2lsF2C1IzK5wTUrsGjUpeiogRxxhkmTvE93/9PXBxyv8AFS7loS7lGa9z/mNTiojyi+Ggs3zPUN7RpfM1gojvOH+2fjI1ivPtg0RJnBe4DN2rG9oQoXQp79qwuCggDYyQBMMEWPA4hQfUccbchn/TkKgVZHeKe4c/dFjPxSDhzPbRbgJF2OikHWjc0H4PMXY4PZz26hZDfC4Ziuyg7WSWdRtDcA6YW96ATcXuxA21guw4nepFp61HyIjQPtNQM7i98qq9TtRKRNwILYeRfN1IjukcN9mOg1qCbu8CTOQL06C2aoPF8G4aDOI5laX/cMsW4O6WTW9TNWVc3yby6EDQiV3oha1pD+Hcpj+b0lkaduqYSh3f8g0ozHhe5GgJNmxKuKcA2JIXuLMaHTZGfcje1rkLXMFa7Jn49IS0B/hZ/Mv/HPKsdzp6EwmcjKy8DSPLB3S+A+I7MxxUOK8o85yJVTs1nzmCL5xv4y4XbWyFt5URsgCmu2Jl2QQbJzINBO+oThJc/aJPIk/u+CArVNZSdaSzywxKQBDKzwl05zn8uUqqqzQAMxsApmSnlSaknVevNRPlKlPgB54BGlpPlUxXSB5J2NT8LcS3Ya2puCawVbrPljhAS8upCNePSKEPClXymJKJFSUvL2RVgjsJK2TFvlCcrRtA1o9NZ/ik1nltSGB1puefxKAaUdvamseS4HCVc1zgo6oF1AScHUEKNWp2"
}

# Make the GET request
response = requests.get(url, params=params, headers=headers)

# Check the status code and handle the response
if response.status_code == 200:
    print("Success! Data received:")
    try:
        data = response.json()
        print(json.dumps(data, indent=4, ensure_ascii=False)) # Use ensure_ascii=False to display Arabic characters correctly
    except json.JSONDecodeError:
        print("Response is not in JSON format.")
        print(response.text)
else:
    print(f"Request failed with status code: {response.status_code}")
    print(f"Response content: {response.text}")