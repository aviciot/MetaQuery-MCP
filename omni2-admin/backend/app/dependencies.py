"""Dependency injection for common dependencies."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.admin_user import AdminUser
from app.services.auth_service import AuthService
from app.utils.security import decode_token

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    """
    Dependency to get current authenticated user from JWT token.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: AdminUser = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await AuthService.get_current_user(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def require_admin(
    current_user: AdminUser = Depends(get_current_user)
) -> AdminUser:
    """
    Dependency to require admin role.
    
    Usage:
        @app.post("/admin-only")
        async def admin_only_route(user: AdminUser = Depends(require_admin)):
            return {"admin": user.email}
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user


# Optional authenticated user (doesn't raise error if not authenticated)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[AdminUser]:
    """
    Dependency to get optional authenticated user.
    Returns None if not authenticated, doesn't raise error.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if not payload or payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await AuthService.get_current_user(db, int(user_id))
        return user
    except Exception:
        return None
