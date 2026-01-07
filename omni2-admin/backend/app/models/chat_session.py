"""Chat session models for persistence."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class ChatSession(Base):
    """Chat session model."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_pinned = Column(Boolean, default=False)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    admin_user = relationship("AdminUser", foreign_keys=[admin_user_id])


class ChatMessage(Base):
    """Chat message model."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String(10), nullable=False)  # 'user' or 'bot'
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    tool_calls = Column(Integer, default=0)
    tools_used = Column(JSONB, default=list)
    message_metadata = Column(JSONB, default=dict)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
