"""Admin user model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func

from app.database import Base


class AdminUser(Base):
    """Admin user model for dashboard authentication."""
    
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False, default="viewer", index=True)  # 'admin' or 'viewer'
    
    is_active = Column(Boolean, default=True, index=True)
    is_super_admin = Column(Boolean, default=False)
    
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    preferences = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<AdminUser {self.email} ({self.role})>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin" or self.is_super_admin
    
    @property
    def is_locked(self) -> bool:
        """Check if account is locked."""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
