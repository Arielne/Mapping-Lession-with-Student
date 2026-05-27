from datetime import datetime, timezone

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.database import get_database
from app.dependencies import get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.security import create_access_token, hash_password, verify_password
from app.utils.serializers import serialize_document

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    now = datetime.now(timezone.utc)
    user = {
        "full_name": payload.full_name.strip(),
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "role": payload.role,
        "created_at": now,
        "updated_at": now,
    }
    try:
        result = await get_database().users.insert_one(user)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=400, detail="Email already registered") from exc
    created = await get_database().users.find_one({"_id": result.inserted_id})
    return serialize_document(created)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = await get_database().users.find_one({"email": payload.email})
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(str(user["_id"]), user["role"])
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[dict, Depends(get_current_user)]):
    return serialize_document(user)
