import httpx
from app.config import settings

try:
    response = httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": settings.job_search_api_key,
            "query": "AI ML internships India",
            "search_depth": "basic",
            "max_results": 3
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    print("Tavily connection successful!")
    print(f"Results found: {len(data.get('results', []))}")

    for result in data.get("results", []):
        print("-", result.get("title"))

except Exception as e:
    print("Tavily connection failed:")
    print(e)