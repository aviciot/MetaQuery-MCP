"""Chat proxy to communicate with Omni2."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import httpx
from typing import Optional

from app.dependencies import get_current_user
from app.models.admin_user import AdminUser

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    user_id: str


class ChatResponse(BaseModel):
    """Chat response model."""
    success: bool
    response: str
    tool_calls: int = 0
    tools_used: list = []
    error: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_omni(
    request: ChatRequest,
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Proxy chat requests to Omni2 using admin credentials.
    This gives the admin full access to all MCPs.
    """
    
    # Use a dedicated admin user email for Omni2 requests
    # This ensures full MCP access
    admin_email = "admin@omni2.local"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Send to Omni2's chat endpoint with admin dashboard identification
            response = await client.post(
                "http://omni2-bridge:8000/chat/ask",  # Omni2's internal Docker service
                json={
                    "user_id": admin_email,
                    "message": request.message,
                },
                headers={
                    "X-Source": "omni2-admin-dashboard",
                    "X-Admin-User": current_user.email,
                    "X-Dashboard-Version": "1.0.0",
                    "X-Request-Priority": "high",  # Admin requests get priority
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return ChatResponse(
                    success=data.get("success", True),
                    response=data.get("answer", ""),
                    tool_calls=data.get("tool_calls", 0),
                    tools_used=data.get("tools_used", []),
                    error=data.get("error")
                )
            else:
                return ChatResponse(
                    success=False,
                    response="",
                    error=f"Omni2 returned status {response.status_code}"
                )
                
    except httpx.TimeoutException:
        return ChatResponse(
            success=False,
            response="",
            error="Request timed out. The query might be too complex."
        )
    except httpx.RequestError as e:
        return ChatResponse(
            success=False,
            response="",
            error=f"Failed to connect to Omni2: {str(e)}"
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            response="",
            error=f"Unexpected error: {str(e)}"
        )
