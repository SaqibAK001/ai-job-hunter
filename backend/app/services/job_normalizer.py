from datetime import datetime, timezone
from urllib.parse import urlparse


def normalize_job(result: dict):
    url = result.get("url", "").strip()

    parsed_url = urlparse(url)

    return {
        "title": result.get("title", "").strip(),
        "company": extract_company(result),
        "location": None,
        "url": url,
        "domain": parsed_url.netloc,
        "source": parsed_url.netloc,
        "description": result.get("content", "").strip(),
        "discovered_at": datetime.now(timezone.utc),
        "match": None,
        "email_sent": False,
    }


def extract_company(result: dict):
    title = result.get("title", "")

    return title.split(" - ")[-1].strip() if " - " in title else "Unknown"