"""Pydantic schemas for authentication."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class AdminUserResponse(BaseModel):
    """Admin user response schema."""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_super_admin: bool
    last_login: Optional[str] = None
    preferences: dict = {}
    created_at: str
    
    class Config:
        from_attributes = True


class AdminUserCreate(BaseModel):
    """Admin user creation schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = Field(default="viewer", pattern="^(admin|viewer)$")
    is_super_admin: bool = False


class AdminUserUpdate(BaseModel):
    """Admin user update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|viewer)$")
    is_active: Optional[bool] = None
    preferences: Optional[dict] = None
