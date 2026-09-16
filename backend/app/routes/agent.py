from fastapi import APIRouter, Header, HTTPException

from app.config import settings
from app.agent.discovery import discover_jobs


router = APIRouter()


@router.post("/run")
async def run_agent(
    x_cron_secret: str | None = Header(default=None)
):

    if x_cron_secret != settings.cron_secret:
        raise HTTPException(
            status_code=401,
            detail="Invalid scheduler credentials"
        )

    result = await discover_jobs()

    return {
        "status": "completed",
        "message": "Job discovery completed",
        **result
    }


@router.get("/status")
async def agent_status():
    return {
        "status": "idle"
    }


@router.get("/logs")
async def agent_logs():
    return {
        "logs": []
    }