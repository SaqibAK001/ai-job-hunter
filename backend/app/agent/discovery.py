from urllib.parse import urlparse

from app.services.job_search import search_jobs
from app.services.job_normalizer import normalize_job
from app.services.job_analyzer import (
    analyze_job,
    reset_gemini_counter
)
from app.services.job_matcher import calculate_match
from app.services.profile_service import get_default_profile
from app.database import jobs_collection


SEARCH_QUERIES = [
    "AI ML intern India apply",
    "Machine learning intern India apply",
    "Artificial intelligence intern India apply",
    "Python developer intern India apply",
    "software developer intern India apply",
]


def is_likely_job(result: dict) -> bool:

    title = result.get("title", "").lower().strip()
    url = result.get("url", "").lower().strip()
    content = result.get("content", "").lower().strip()

    if not title or not url:
        return False

    parsed = urlparse(url)

    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    # --------------------------------
    # Reject obvious generic titles
    # --------------------------------

    rejected_title_patterns = [
        "job vacancies",
        "job vacancy",
        "jobs in india",
        "jobs in bengaluru",
        "jobs in bangalore",
        "internships in india",
        "internship opportunities",
        "find internships",
        "find jobs",
        "latest jobs",
        "job openings",
        "career opportunities",
        "jobs and internships",
        "job search",
        "search jobs",
        "search results",
        "job listings",
        "job opportunities in",
    ]

    for pattern in rejected_title_patterns:

        if pattern in title:
            return False

    # --------------------------------
    # Reject obvious search pages
    # --------------------------------

    rejected_path_patterns = [
        "/search?",
        "/search/",
        "/job-search",
        "/job_search",
        "/internship-search",
        "/category/",
        "/categories/",
        "/browse/",
    ]

    for pattern in rejected_path_patterns:

        if pattern in path:
            return False

    # --------------------------------
    # Known aggregation websites
    # --------------------------------

    aggregator_domains = [
        "indeed.com",
        "internshala.com",
        "naukri.com",
        "glassdoor.co.in",
        "glassdoor.com",
        "ziprecruiter.com",
        "simplyhired.com",
    ]

    for aggregator in aggregator_domains:

        if aggregator in domain:
            return False

    # --------------------------------
    # Obvious multi-job result pages
    # --------------------------------

    job_count_patterns = [
        "100+ jobs",
        "200+ jobs",
        "300+ jobs",
        "500+ jobs",
        "1000+ jobs",
        "job vacancies",
        "job listings",
        "jobs available",
        "jobs found",
    ]

    first_part = content[:1500]

    for pattern in job_count_patterns:

        if pattern in title or pattern in first_part:
            return False

    # --------------------------------
    # Reject obvious informational pages
    # --------------------------------

    informational_patterns = [
        "what is machine learning",
        "what is artificial intelligence",
        "machine learning tutorial",
        "artificial intelligence tutorial",
        "learn machine learning",
        "learn artificial intelligence",
        "machine learning guide",
        "artificial intelligence guide",
    ]

    for pattern in informational_patterns:

        if pattern in title:
            return False

    return True


async def discover_jobs():

    discovered = 0
    duplicates = 0
    rejected = 0
    analyzed = 0
    skipped_pre_filter = 0
    rate_limited = 0
    run_limit_reached = 0

    # Reset Gemini counter for this run.
    reset_gemini_counter()

    profile = get_default_profile()

    for query in SEARCH_QUERIES:

        print(f"\nSearching: {query}")

        try:

            results = await search_jobs(
                query=query,
                max_results=10
            )

        except Exception as e:

            print(
                f"Search error for '{query}': {e}"
            )

            continue

        for result in results:

            # --------------------------------
            # STEP 1
            # Cheap pre-filter
            # --------------------------------

            if not is_likely_job(result):

                print(
                    f"Pre-filter rejected: "
                    f"{result.get('title', 'Unknown')}"
                )

                rejected += 1
                skipped_pre_filter += 1

                continue

            # --------------------------------
            # STEP 2
            # Normalize
            # --------------------------------

            job = normalize_job(result)

            if not job["title"] or not job["url"]:

                rejected += 1

                continue

            # --------------------------------
            # STEP 3
            # Duplicate check
            # --------------------------------

            existing = jobs_collection.find_one({
                "url": job["url"]
            })

            if existing:

                print(
                    f"Duplicate: {job['title']}"
                )

                duplicates += 1

                continue

            # --------------------------------
            # STEP 4
            # Gemini analysis
            # --------------------------------

            print(
                f"Analyzing: {job['title']}"
            )

            analysis = await analyze_job(job)

            # --------------------------------
            # Gemini quota reached
            # --------------------------------

            if analysis.get("rate_limited"):

                rate_limited += 1

                print(
                    "Gemini quota unavailable. "
                    "Stopping discovery run."
                )

                return {
                    "discovered": discovered,
                    "duplicates": duplicates,
                    "rejected": rejected,
                    "analyzed": analyzed,
                    "pre_filter_rejected": skipped_pre_filter,
                    "rate_limited": rate_limited,
                    "run_limit_reached": run_limit_reached
                }

            # --------------------------------
            # Per-run Gemini limit
            # --------------------------------

            if analysis.get("run_limit_reached"):

                run_limit_reached += 1

                print(
                    "Gemini per-run limit reached. "
                    "Stopping discovery run."
                )

                return {
                    "discovered": discovered,
                    "duplicates": duplicates,
                    "rejected": rejected,
                    "analyzed": analyzed,
                    "pre_filter_rejected": skipped_pre_filter,
                    "rate_limited": rate_limited,
                    "run_limit_reached": run_limit_reached
                }

            analyzed += 1

            # --------------------------------
            # STEP 5
            # Reject non-jobs
            # --------------------------------

            if not analysis.get("is_job", False):

                print(
                    f"Rejected non-job: "
                    f"{job['title']}"
                )

                rejected += 1

                continue

            # --------------------------------
            # STEP 6
            # Match against profile
            # --------------------------------

            match = calculate_match(
                analysis,
                profile
            )

            # --------------------------------
            # STEP 7
            # Store job
            # --------------------------------

            job["analysis"] = analysis
            job["match"] = match

            try:

                jobs_collection.insert_one(job)

                discovered += 1

                print(
                    f"Added: {job['title']} "
                    f"| Score: {match['match_score']} "
                    f"| {match['recommendation']}"
                )

            except Exception as e:

                if "duplicate key" in str(e).lower():

                    duplicates += 1

                    print(
                        f"Duplicate insert prevented: "
                        f"{job['title']}"
                    )

                else:

                    print(
                        f"Database error for "
                        f"{job['title']}: {e}"
                    )

    return {
        "discovered": discovered,
        "duplicates": duplicates,
        "rejected": rejected,
        "analyzed": analyzed,
        "pre_filter_rejected": skipped_pre_filter,
        "rate_limited": rate_limited,
        "run_limit_reached": run_limit_reached
    }