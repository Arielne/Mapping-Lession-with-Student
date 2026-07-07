from fastapi import APIRouter, Depends, HTTPException, Request, status
from pymongo.errors import DuplicateKeyError

from app.dependencies import get_current_user, require_database
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.security import create_access_token, hash_password, verify_password
from app.services.login_rate_limit_service import (
    ensure_login_allowed,
    record_failed_login,
    reset_login_attempts,
)
from app.utils import now_utc, serialize_document

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db=Depends(require_database)):
    existing_user = await db.users.find_one({"email": payload.email.lower()})
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email da ton tai.")

    user = {
        "full_name": payload.full_name,
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "role": "user",
        "created_at": now_utc(),
    }
    try:
        result = await db.users.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email da ton tai.")

    created_user = await db.users.find_one({"_id": result.inserted_id})
    return serialize_document(created_user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, request: Request, db=Depends(require_database)):
    ensure_login_allowed(payload.email, request)
    user = await db.users.find_one({"email": payload.email.lower()})
    if user is None or not verify_password(payload.password, user["password_hash"]):
        record_failed_login(payload.email, request)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hoac password khong dung.")

    reset_login_attempts(payload.email, request)
    user_response = serialize_document(user)
    token = create_access_token(user_response["id"])
    return {"access_token": token, "token_type": "bearer", "user": user_response}


@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    return serialize_document(current_user)
