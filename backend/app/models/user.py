from pydantic import BaseModel, Field
from typing import List, Optional


class UserProfile(BaseModel):
    name: str
    email: str
    skills: List[str] = []
    education: Optional[str] = None
    graduation_year: Optional[int] = None
    preferred_locations: List[str] = []
    remote_allowed: bool = True
    target_roles: List[str] = []
    minimum_match_score: float = Field(
        default=75,
        ge=0,
        le=100
    )