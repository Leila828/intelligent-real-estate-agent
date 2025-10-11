import requests
import re
import json


def initialise():
    """
    Fetches the current PropertyFinder buildId from the search page.

    Returns:
        str: The extracted buildId, or None if not found.
    """
    url = "https://www.propertyfinder.ae/en/search?c=1&t=35&fu=0&ob=mr"
    html = requests.get(url).text

    # Extract the JSON inside __NEXT_DATA__
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.S
    )

    if match:
        try:
            data = json.loads(match.group(1))
            return data.get("buildId")
        except json.JSONDecodeError:
            return None
    return None


# Example usage
if __name__ == "__main__":
    build_id = initialise()
    print("Build ID:", build_id)
