from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def validate_local_email(value: str) -> str:
    normalized = value.strip().lower()
    if "@" not in normalized:
        raise ValueError("Email phai co ky tu @.")

    local_part, domain = normalized.rsplit("@", 1)
    if not local_part or not domain or "." not in domain:
        raise ValueError("Email khong hop le.")
    return normalized


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str
    password: str = Field(..., min_length=6, max_length=100)

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, value: str) -> str:
        return validate_local_email(value)


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, value: str) -> str:
        return validate_local_email(value)


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: Literal["user", "student", "admin"]
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
