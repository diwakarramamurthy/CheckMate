"""Authentication routes."""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import uuid

from database import db
from models import UserCreate, UserLogin, UserResponse, TokenResponse
from auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter()

@router.post("/auth/register", response_model=TokenResponse)
async def register(user: UserCreate):
    """Register a new user."""
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    user_doc = {
        "user_id": user_id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "phone": user.phone,
        "license_number": user.license_number,
        "firm_name": user.firm_name,
        "password_hash": hash_password(user.password),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)

    token = create_token(user_id, user.email, user.role)
    user_response = UserResponse(
        user_id=user_id,
        email=user.email,
        name=user.name,
        role=user.role,
        phone=user.phone,
        license_number=user.license_number,
        firm_name=user.firm_name,
        created_at=user_doc["created_at"],
        is_active=True
    )
    return TokenResponse(access_token=token, user=user_response)

@router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with email and password."""
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user["user_id"], user["email"], user["role"])
    user_response = UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        phone=user.get("phone"),
        license_number=user.get("license_number"),
        firm_name=user.get("firm_name"),
        created_at=user["created_at"],
        is_active=user.get("is_active", True)
    )
    return TokenResponse(access_token=token, user=user_response)

@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"],
        phone=current_user.get("phone"),
        license_number=current_user.get("license_number"),
        firm_name=current_user.get("firm_name"),
        created_at=current_user["created_at"],
        is_active=current_user.get("is_active", True)
    )
