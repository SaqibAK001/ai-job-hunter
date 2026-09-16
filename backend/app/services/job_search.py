import httpx
from app.config import settings

TAVILY_URL = "https://api.tavily.com/search"


async def search_jobs(query: str, max_results: int = 10):
    payload = {
        "api_key": settings.job_search_api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            TAVILY_URL,
            json=payload
        )

        response.raise_for_status()

        data = response.json()

    return data.get("results", [])