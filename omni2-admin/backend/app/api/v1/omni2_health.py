"""Omni2 health check proxy endpoint."""
from fastapi import APIRouter, Depends, HTTPException
import httpx
from typing import Dict, Any

from app.dependencies import get_current_user
from app.models.admin_user import AdminUser

router = APIRouter()

OMNI2_BASE_URL = "http://omni2-bridge:8000"


@router.get("/health", response_model=Dict[str, Any])
async def get_omni2_health(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Get Omni2 system health status.
    
    Returns:
        - status: overall health (healthy/degraded/unhealthy)
        - version: Omni2 version
        - database: database connection status
        - mcps: MCP server health summary
        - timestamp: server time
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{OMNI2_BASE_URL}/health")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Omni2 health check failed: {str(e)}"
        )


@router.get("/mcps", response_model=Dict[str, Any])
async def get_omni2_mcp_status(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Get detailed MCP server status from Omni2.
    
    Returns MCP server configurations and health status.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get MCP list from Omni2
            response = await client.get(f"{OMNI2_BASE_URL}/mcps")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch MCP status: {str(e)}"
        )
