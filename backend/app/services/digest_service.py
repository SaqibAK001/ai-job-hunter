from datetime import datetime, timezone

from app.database import jobs_collection
from app.services.email_service import send_email


def get_matching_jobs():

    jobs = list(
        jobs_collection.find({
            "email_sent": False,
            "match.match_score": {
                "$gte": 75
            }
        }).sort(
            "match.match_score",
            -1
        )
    )

    return jobs


def build_job_card(job):

    match = job.get("match", {})

    title = job.get(
        "title",
        "Unknown Position"
    )

    company = job.get(
        "company",
        "Unknown Company"
    )

    location = job.get(
        "location"
    ) or "Location not specified"

    score = match.get(
        "match_score",
        0
    )

    recommendation = match.get(
        "recommendation",
        "Match"
    )

    matched_skills = match.get(
        "matched_skills",
        []
    )

    missing_skills = match.get(
        "missing_skills",
        []
    )

    reason = match.get(
        "reason",
        ""
    )

    url = job.get(
        "url",
        "#"
    )

    matched_html = ", ".join(
        matched_skills
    ) if matched_skills else "None identified"

    missing_html = ", ".join(
        missing_skills
    ) if missing_skills else "None identified"

    return f"""
    <div style="
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 18px;
    ">

        <h2 style="margin-top: 0;">
            {title}
        </h2>

        <p>
            <strong>Company:</strong>
            {company}
        </p>

        <p>
            <strong>Location:</strong>
            {location}
        </p>

        <p>
            <strong>Match Score:</strong>
            {score}/100
        </p>

        <p>
            <strong>Recommendation:</strong>
            {recommendation}
        </p>

        <p>
            <strong>Matched Skills:</strong>
            {matched_html}
        </p>

        <p>
            <strong>Missing Skills:</strong>
            {missing_html}
        </p>

        <p>
            <strong>Why:</strong>
            {reason}
        </p>

        <p>
            <a
                href="{url}"
                style="
                    display:inline-block;
                    padding:10px 16px;
                    background:#111;
                    color:white;
                    text-decoration:none;
                    border-radius:6px;
                "
            >
                View Job
            </a>
        </p>

    </div>
    """


async def send_daily_digest():

    jobs = get_matching_jobs()

    if not jobs:

        print(
            "No new matching jobs for today's digest."
        )

        return {
            "status": "no_jobs",
            "jobs": 0
        }

    today = datetime.now(
        timezone.utc
    ).strftime("%d %b %Y")

    job_cards = ""

    for job in jobs:

        job_cards += build_job_card(job)

    html = f"""
    <html>

        <body style="
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: auto;
            padding: 20px;
        ">

            <h1>
                AI Job Hunter
            </h1>

            <h3>
                Daily Job Digest - {today}
            </h3>

            <p>
                Found
                <strong>{len(jobs)}</strong>
                new job(s) matching your profile.
            </p>

            {job_cards}

            <hr>

            <p style="color:#777;">
                This email was automatically generated
                by your Autonomous AI Job Hunter.
            </p>

        </body>

    </html>
    """

    try:

        result = await send_email(
            subject=(
                f"AI Job Hunter - "
                f"{len(jobs)} New Matching Job(s)"
            ),
            html=html
        )

        # Only mark jobs as emailed AFTER
        # Resend successfully accepts the email.
        job_ids = [
            job["_id"]
            for job in jobs
        ]

        jobs_collection.update_many(
            {
                "_id": {
                    "$in": job_ids
                }
            },
            {
                "$set": {
                    "email_sent": True,
                    "email_sent_at": datetime.now(
                        timezone.utc
                    )
                }
            }
        )

        print(
            f"Daily digest sent successfully: "
            f"{len(jobs)} jobs"
        )

        return {
            "status": "sent",
            "jobs": len(jobs),
            "resend": result
        }

    except Exception as e:

        print(
            f"Daily digest failed: {e}"
        )

        return {
            "status": "failed",
            "jobs": len(jobs),
            "error": str(e)
        }