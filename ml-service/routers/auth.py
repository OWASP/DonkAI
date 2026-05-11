"""
Authentication endpoints: login and register.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .deps import db

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


def _user_payload(user) -> dict:
    return {"id": user.id, "username": user.username}


@router.post("/login")
async def login(request: LoginRequest):
    """Authenticate a user and return a session token."""
    user = db.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "success": True,
        "user": _user_payload(user),
        "token": f"user_{user.id}_token",
    }


@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new user account."""
    try:
        user = db.create_user(request.username, request.password)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "success": True,
        "user": _user_payload(user),
        "token": f"user_{user.id}_token",
    }
