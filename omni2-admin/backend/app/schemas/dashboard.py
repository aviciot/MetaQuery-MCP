"""Pydantic schemas for dashboard data."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_mcps: int
    active_mcps: int
    total_users: int
    active_users: int
    total_api_calls_today: int
    api_calls_yesterday: int
    system_uptime_percentage: float
    total_cost_today: Optional[float] = 0.0
    total_cost_week: Optional[float] = 0.0


class ActivityItem(BaseModel):
    """Activity feed item."""
    id: int
    icon: str
    title: str
    description: str
    time_ago: str
    color: str
    created_at: datetime


class MCPServerResponse(BaseModel):
    """MCP server response."""
    id: int
    name: str
    description: Optional[str]
    status: str
    health_status: str
    requests: int
    uptime: str
    version: Optional[str]
    endpoint: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuickStat(BaseModel):
    """Quick stat item."""
    label: str
    value: str
    percentage: int
