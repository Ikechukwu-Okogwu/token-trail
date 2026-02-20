"""Auth router: instructor signup, login, and profile."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.db import get_db
from app.core.deps import get_current_instructor
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    MeResponse,
    SignupRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(body: SignupRequest):
    """Register a new instructor account."""
    db = get_db()

    if db.instructors.find_one({"email": body.email}):
        raise HTTPException(status_code=409, detail="Email already registered")

    doc = {
        "name": body.name,
        "email": body.email,
        "passwordHash": hash_password(body.password),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    result = db.instructors.insert_one(doc)
    token = create_access_token(str(result.inserted_id))
    return AuthResponse(accessToken=token)


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest):
    """Log in and receive a JWT access token."""
    db = get_db()
    instructor = db.instructors.find_one({"email": body.email})

    if not instructor or not verify_password(body.password, instructor["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(instructor["_id"]))
    return AuthResponse(accessToken=token)


@router.get("/me", response_model=MeResponse)
async def me(current: dict = Depends(get_current_instructor)):
    """Return the currently authenticated instructor's profile."""
    return MeResponse(**current)
