from fastapi import FastAPI

from app.routes import auth, profile, jobs, agent, notifications


app = FastAPI(
    title="Autonomous AI Job Hunter",
    description="Agentic AI system for autonomous job discovery and personalized recommendations",
    version="1.0.0"
)


app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    profile.router,
    prefix="/profile",
    tags=["Profile"]
)

app.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["Jobs"]
)

app.include_router(
    agent.router,
    prefix="/agent",
    tags=["Agent"]
)

app.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)


@app.get("/")
async def root():
    return {
        "name": "Autonomous AI Job Hunter",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }