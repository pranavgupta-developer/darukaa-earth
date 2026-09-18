"""
User Pydantic schemas for request/response validation.

Separates input (create/login) from output (response) contracts.
Passwords are never included in response schemas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """Response schema for user data. Never exposes password."""

    id: uuid.UUID
    email: str
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Response schema for JWT authentication token."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
