from app.database import users_collection


def get_default_profile():
    profile = users_collection.find_one({})

    if profile:
        profile["_id"] = str(profile["_id"])
        return profile

    profile = {
        "name": "Saqib",
        "email": "saqibak045@gmail.com",
        "skills": [
            "Python",
            "Machine Learning",
            "Artificial Intelligence",
            "FastAPI",
            "React",
            "JavaScript",
            "MongoDB",
            "SQL",
            "Git",
            "REST API",
            "Data Analysis",
            "LLM",
            "LangChain"
        ],
        "education": "B.Tech in Artificial Intelligence and Data Science",
        "graduation_year": 2027,
        "preferred_locations": [
            "Bengaluru",
            "India"
        ],
        "remote_allowed": True,
        "target_roles": [
            "AI Engineer",
            "Machine Learning Engineer",
            "AI/ML Intern",
            "Software Developer Intern",
            "Python Developer",
            "Data Analyst"
        ],
        "minimum_match_score": 75
    }

    users_collection.insert_one(profile)

    return profile