"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    AdminUserResponse,
)
from app.services.auth_service import AuthService, AuthenticationError
from app.dependencies import get_current_user
from app.models.admin_user import AdminUser

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns JWT access token and refresh token.
    """
    try:
        user, tokens = await AuthService.authenticate_user(
            db, request.email, request.password
        )
        return tokens
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    try:
        tokens = await AuthService.refresh_access_token(
            db, request.refresh_token
        )
        return tokens
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Logout current user.
    
    Note: With JWT, logout is handled client-side by deleting the token.
    This endpoint is provided for completeness and can be extended
    to implement token blacklisting if needed.
    """
    return {
        "message": "Successfully logged out",
        "user": current_user.email
    }


@router.get("/me", response_model=AdminUserResponse)
async def get_me(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return AdminUserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_super_admin=current_user.is_super_admin,
        last_login=current_user.last_login.isoformat() if current_user.last_login else None,
        preferences=current_user.preferences or {},
        created_at=current_user.created_at.isoformat(),
    )
