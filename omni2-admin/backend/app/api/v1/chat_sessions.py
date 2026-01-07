"""Chat session management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.dependencies import get_current_user, get_db
from app.models.admin_user import AdminUser
from app.models.chat_session import ChatSession, ChatMessage

router = APIRouter()


class MessageCreate(BaseModel):
    """Message creation model."""
    sender: str
    message: str
    tool_calls: int = 0
    tools_used: List[str] = []


class MessageResponse(BaseModel):
    """Message response model."""
    id: int
    sender: str
    message: str
    timestamp: datetime
    tool_calls: int
    tools_used: List[str]
    message_metadata: dict = {}

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    """Session creation model."""
    title: str


class SessionResponse(BaseModel):
    """Session response model."""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_pinned: bool
    message_count: int = 0

    class Config:
        from_attributes = True


class SessionWithMessages(SessionResponse):
    """Session with messages."""
    messages: List[MessageResponse]


@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Get all chat sessions for current admin user."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.admin_user_id == current_user.id)
        .order_by(desc(ChatSession.updated_at))
    )
    sessions = result.scalars().all()
    
    # Get message counts
    response = []
    for session in sessions:
        msg_result = await db.execute(
            select(ChatMessage).where(ChatMessage.session_id == session.id)
        )
        messages = msg_result.scalars().all()
        response.append(
            SessionResponse(
                id=session.id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                is_pinned=session.is_pinned,
                message_count=len(messages)
            )
        )
    
    return response


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Create a new chat session."""
    session = ChatSession(
        admin_user_id=current_user.id,
        title=session_data.title
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return SessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        is_pinned=session.is_pinned,
        message_count=0
    )


@router.get("/sessions/{session_id}", response_model=SessionWithMessages)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Get a specific session with all messages."""
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.id == session_id,
            ChatSession.admin_user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    msg_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp)
    )
    messages = msg_result.scalars().all()
    
    return SessionWithMessages(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        is_pinned=session.is_pinned,
        message_count=len(messages),
        messages=[MessageResponse.from_orm(msg) for msg in messages]
    )


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def add_message(
    session_id: int,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Add a message to a session."""
    # Verify session exists and belongs to user
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.id == session_id,
            ChatSession.admin_user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    message = ChatMessage(
        session_id=session_id,
        sender=message_data.sender,
        message=message_data.message,
        tool_calls=message_data.tool_calls,
        tools_used=message_data.tools_used
    )
    db.add(message)
    
    # Update session timestamp
    session.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(message)
    
    return MessageResponse.from_orm(message)


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Delete a chat session."""
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.id == session_id,
            ChatSession.admin_user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.delete(session)
    await db.commit()
    
    return {"success": True, "message": "Session deleted"}


@router.patch("/sessions/{session_id}/pin")
async def toggle_pin(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Toggle pin status of a session."""
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.id == session_id,
            ChatSession.admin_user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_pinned = not session.is_pinned
    await db.commit()
    
    return {"success": True, "is_pinned": session.is_pinned}
