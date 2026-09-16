from fastapi import APIRouter
from app.database import jobs_collection

router = APIRouter()


@router.get("")
async def get_jobs():
    jobs = list(
        jobs_collection.find({}).sort("discovered_at", -1).limit(50)
    )

    for job in jobs:
        job["_id"] = str(job["_id"])

    return jobs


@router.get("/recommendations")
async def get_recommendations():
    jobs = list(
        jobs_collection.find(
            {"match.match_score": {"$gte": 75}}
        ).sort("match.match_score", -1).limit(20)
    )

    for job in jobs:
        job["_id"] = str(job["_id"])

    return jobs


@router.get("/history")
async def get_job_history():
    jobs = list(
        jobs_collection.find({}).sort("discovered_at", -1).limit(100)
    )

    for job in jobs:
        job["_id"] = str(job["_id"])

    return jobs


@router.get("/{job_id}")
async def get_job(job_id: str):
    return {"job_id": job_id}