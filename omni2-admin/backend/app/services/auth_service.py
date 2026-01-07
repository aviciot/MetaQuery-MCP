"""Authentication service with business logic."""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_user import AdminUser
from app.schemas.auth import LoginRequest, TokenResponse, AdminUserResponse
from app.utils.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import settings


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Tuple[AdminUser, TokenResponse]:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain password
            
        Returns:
            Tuple of (user, tokens)
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Find user by email
        result = await db.execute(
            select(AdminUser).where(AdminUser.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Check if account is locked
        if user.is_locked:
            raise AuthenticationError(
                f"Account is locked until {user.locked_until.isoformat()}"
            )
        
        # Check if account is active
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            
            await db.commit()
            raise AuthenticationError("Invalid email or password")
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        await db.commit()
        
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRY_MINUTES * 60,
        )
        
        return user, tokens
    
    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str
    ) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            db: Database session
            refresh_token: Refresh token
            
        Returns:
            New tokens
            
        Raises:
            AuthenticationError: If refresh fails
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid refresh token")
        
        # Get user
        result = await db.execute(
            select(AdminUser).where(AdminUser.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        # Generate new tokens
        access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRY_MINUTES * 60,
        )
    
    @staticmethod
    async def get_current_user(
        db: AsyncSession,
        user_id: int
    ) -> Optional[AdminUser]:
        """
        Get current user by ID.
        
        Args:
            db: Database session
            user_id: User ID from token
            
        Returns:
            User or None
        """
        result = await db.execute(
            select(AdminUser).where(
                AdminUser.id == user_id,
                AdminUser.is_active == True
            )
        )
        return result.scalar_one_or_none()
