from fastapi import APIRouter
from app.models.user import UserProfile

router = APIRouter()


@router.get("")
async def get_profile():
    return {"message": "Get profile"}


@router.put("")
async def update_profile(profile: UserProfile):
    return {
        "message": "Profile updated",
        "profile": profile
    }


@router.get("/preferences")
async def get_preferences():
    return {"message": "Get preferences"}


@router.put("/preferences")
async def update_preferences():
    return {"message": "Preferences updated"}