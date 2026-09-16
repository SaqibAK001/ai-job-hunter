from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
async def register():
    return {"message": "Registration endpoint"}


@router.post("/login")
async def login():
    return {"message": "Login endpoint"}


@router.post("/refresh")
async def refresh():
    return {"message": "Refresh endpoint"}


@router.post("/logout")
async def logout():
    return {"message": "Logout endpoint"}