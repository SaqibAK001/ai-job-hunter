def calculate_match(job_analysis: dict, profile: dict):

    user_skills = {
        skill.lower().strip()
        for skill in profile.get("skills", [])
    }

    required_skills = {
        skill.lower().strip()
        for skill in job_analysis.get("required_skills", [])
    }

    preferred_skills = {
        skill.lower().strip()
        for skill in job_analysis.get("preferred_skills", [])
    }

    # No actual job requirements = cannot calculate a meaningful match
    if not required_skills and not preferred_skills:
        return {
            "match_score": 0,
            "recommendation": "Insufficient Information",
            "matched_skills": [],
            "missing_skills": [],
            "reason": "The job posting does not contain enough skill information."
        }

    matched_required = user_skills.intersection(required_skills)
    matched_preferred = user_skills.intersection(preferred_skills)

    missing_required = required_skills - user_skills

    if required_skills:
        required_score = (
            len(matched_required) / len(required_skills)
        ) * 60
    else:
        required_score = 60

    if preferred_skills:
        preferred_score = (
            len(matched_preferred) / len(preferred_skills)
        ) * 20
    else:
        preferred_score = 20

    role_score = 20

    score = required_score + preferred_score + role_score

    if score >= 85:
        recommendation = "Strong Match"
    elif score >= 75:
        recommendation = "Good Match"
    elif score >= 60:
        recommendation = "Possible Match"
    else:
        recommendation = "Low Match"

    return {
        "match_score": round(score, 2),
        "recommendation": recommendation,
        "matched_skills": sorted(
            matched_required | matched_preferred
        ),
        "missing_skills": sorted(missing_required),
        "reason": (
            f"Matched {len(matched_required)} of "
            f"{len(required_skills)} required skills and "
            f"{len(matched_preferred)} of "
            f"{len(preferred_skills)} preferred skills."
        )
    }