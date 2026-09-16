import json

from google import genai
from app.config import settings


client = genai.Client(api_key=settings.gemini_api_key)

# Maximum Gemini calls allowed during one discovery run.
MAX_GEMINI_CALLS = 3

gemini_calls = 0


def reset_gemini_counter():
    global gemini_calls
    gemini_calls = 0


def can_use_gemini():
    return gemini_calls < MAX_GEMINI_CALLS


async def analyze_job(job: dict):

    global gemini_calls

    # --------------------------------
    # Check per-run Gemini limit
    # --------------------------------

    if not can_use_gemini():

        print(
            f"Gemini run limit reached "
            f"({MAX_GEMINI_CALLS} calls)."
        )

        return {
            "is_job": None,
            "rate_limited": False,
            "run_limit_reached": True,
            "required_skills": [],
            "preferred_skills": [],
            "experience_required": "",
            "education_required": "",
            "job_type": "",
            "location": "",
            "remote": False,
            "role_category": "",
            "summary": "Gemini run limit reached"
        }

    # --------------------------------
    # Count this Gemini request
    # --------------------------------

    gemini_calls += 1

    print(
        f"Gemini analysis "
        f"{gemini_calls}/{MAX_GEMINI_CALLS}"
    )

    prompt = f"""
You are a strict job-posting analyzer.

Analyze this specific job/internship posting.

TITLE:
{job.get("title", "")}

COMPANY:
{job.get("company", "")}

DESCRIPTION:
{job.get("description", "")}

URL:
{job.get("url", "")}

The input has already passed a basic job filter.

Determine whether it is actually a specific job or internship opportunity.

A valid job should have:
- A specific role
- A company or organization
- Responsibilities, requirements, or qualifications
- An opportunity to apply or be considered

Reject:
- Articles
- Blog posts
- Promotional content
- Career advice
- Generic company career pages
- Job search pages
- Job category pages
- Lists of multiple jobs
- News pages
- Social media discussion posts

Return ONLY valid JSON.

For a valid job:

{{
    "is_job": true,
    "required_skills": [],
    "preferred_skills": [],
    "experience_required": "",
    "education_required": "",
    "job_type": "",
    "location": "",
    "remote": false,
    "role_category": "",
    "summary": ""
}}

For an invalid result:

{{
    "is_job": false,
    "required_skills": [],
    "preferred_skills": [],
    "experience_required": "",
    "education_required": "",
    "job_type": "",
    "location": "",
    "remote": false,
    "role_category": "",
    "summary": "Reason why this is not a specific job posting"
}}

Important:
- Do not invent skills.
- Only include skills explicitly required or preferred by the posting.
- Keep required_skills and preferred_skills concise.
- Return JSON only.
- No markdown.
- No code fences.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        try:

            result = json.loads(text)

            result["run_limit_reached"] = False
            result["rate_limited"] = False

            return result

        except json.JSONDecodeError:

            print("Gemini returned invalid JSON.")

            return {
                "is_job": False,
                "rate_limited": False,
                "run_limit_reached": False,
                "required_skills": [],
                "preferred_skills": [],
                "experience_required": "",
                "education_required": "",
                "job_type": "",
                "location": "",
                "remote": False,
                "role_category": "",
                "summary": "Gemini returned invalid JSON"
            }

    except Exception as e:

        error_text = str(e)

        # --------------------------------
        # Gemini quota
        # --------------------------------

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):

            print(
                "Gemini quota unavailable. "
                "Stopping Gemini analysis."
            )

            return {
                "is_job": None,
                "rate_limited": True,
                "run_limit_reached": False,
                "required_skills": [],
                "preferred_skills": [],
                "experience_required": "",
                "education_required": "",
                "job_type": "",
                "location": "",
                "remote": False,
                "role_category": "",
                "summary": "Gemini API quota exhausted"
            }

        print(
            f"Gemini analysis error: {e}"
        )

        return {
            "is_job": None,
            "rate_limited": False,
            "run_limit_reached": False,
            "required_skills": [],
            "preferred_skills": [],
            "experience_required": "",
            "education_required": "",
            "job_type": "",
            "location": "",
            "remote": False,
            "role_category": "",
            "summary": f"Analysis failed: {str(e)}"
        }