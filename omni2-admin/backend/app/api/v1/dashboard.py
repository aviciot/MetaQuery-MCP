"""Dashboard API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models.omni2 import User, MCPServer, AuditLog
from app.schemas.dashboard import DashboardStats, ActivityItem, MCPServerResponse
from app.dependencies import get_current_user
from app.models.admin_user import AdminUser

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Get dashboard statistics."""
    
    # Count total MCPs
    total_mcps_result = await db.execute(select(func.count(MCPServer.id)))
    total_mcps = total_mcps_result.scalar() or 0
    
    # Count active MCPs (is_enabled=True)
    active_mcps_result = await db.execute(
        select(func.count(MCPServer.id)).where(MCPServer.is_enabled == True)
    )
    active_mcps = active_mcps_result.scalar() or 0
    
    # Count total users
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    # Count active users
    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0
    
    # Count API calls today (from total_requests)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    api_calls_result = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= today)
    )
    api_calls_today = api_calls_result.scalar() or 0
    
    # Count API calls yesterday
    yesterday = today - timedelta(days=1)
    api_calls_yesterday_result = await db.execute(
        select(func.count(AuditLog.id)).where(
            and_(AuditLog.created_at >= yesterday, AuditLog.created_at < today)
        )
    )
    api_calls_yesterday = api_calls_yesterday_result.scalar() or 0
    
    # Calculate cost estimates from audit logs
    cost_today_result = await db.execute(
        select(func.coalesce(func.sum(AuditLog.cost_estimate), 0.0))
        .where(AuditLog.created_at >= today)
    )
    cost_today = float(cost_today_result.scalar() or 0.0)
    
    week_ago = today - timedelta(days=7)
    cost_week_result = await db.execute(
        select(func.coalesce(func.sum(AuditLog.cost_estimate), 0.0))
        .where(AuditLog.created_at >= week_ago)
    )
    cost_week = float(cost_week_result.scalar() or 0.0)
    
    # Calculate uptime (based on healthy MCPs)
    healthy_mcps_result = await db.execute(
        select(func.count(MCPServer.id)).where(
            and_(MCPServer.is_enabled == True, MCPServer.is_healthy == True)
        )
    )
    healthy_mcps = healthy_mcps_result.scalar() or 0
    uptime = (healthy_mcps / active_mcps * 100) if active_mcps > 0 else 100.0
    
    return DashboardStats(
        total_mcps=total_mcps,
        active_mcps=active_mcps,
        total_users=total_users,
        active_users=active_users,
        total_api_calls_today=api_calls_today,
        api_calls_yesterday=api_calls_yesterday,
        system_uptime_percentage=round(uptime, 1),
        total_cost_today=round(cost_today, 4),
        total_cost_week=round(cost_week, 4)
    )


@router.get("/activity", response_model=List[ActivityItem])
async def get_recent_activity(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Get recent activity feed from audit logs - only user requests."""
    
    # Get recent audit logs - only actual user requests (with messages)
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.message.isnot(None))  # Only user requests, not system logs
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    
    # Get user info for each log
    user_cache = {}
    for log in logs:
        if log.user_id not in user_cache:
            user_result = await db.execute(
                select(User).where(User.id == log.user_id)
            )
            user = user_result.scalar_one_or_none()
            user_cache[log.user_id] = user
    
    # Convert to activity items
    activities = []
    for log in logs:
        user = user_cache.get(log.user_id)
        user_email = user.email if user else "Unknown"
        user_name = user.name if user and user.name else user_email
        
        # Determine icon and color based on request type and success
        if not log.success:
            icon = '❌'
            color = 'bg-red-100'
            title = f'Error - {user_name}'
        elif log.request_type == 'chat':
            icon = '💬'
            color = 'bg-blue-100'
            title = f'Chat - {user_name}'
        elif log.tool_calls_count and log.tool_calls_count > 0:
            icon = '⚡'
            color = 'bg-yellow-100'
            title = f'{log.tool_calls_count} Tool Calls'
        else:
            icon = '📝'
            color = 'bg-gray-100'
            title = 'Query'
        
        # Get description from message or error
        description = log.message_preview or log.error_message or 'No description'
        if len(description) > 80:
            description = description[:77] + '...'
        
        # Calculate time ago
        now = datetime.utcnow().replace(tzinfo=log.timestamp.tzinfo) if log.timestamp.tzinfo else datetime.utcnow()
        time_diff = now - log.timestamp
        if time_diff.total_seconds() < 60:
            time_ago = "Just now"
        elif time_diff.total_seconds() < 3600:
            minutes = int(time_diff.total_seconds() / 60)
            time_ago = f"{minutes} min ago"
        elif time_diff.total_seconds() < 86400:
            hours = int(time_diff.total_seconds() / 3600)
            time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = int(time_diff.total_seconds() / 86400)
            time_ago = f"{days} day{'s' if days > 1 else ''} ago"
        
        activities.append(ActivityItem(
            id=log.id,
            icon=icon,
            title=title,
            description=description,
            time_ago=time_ago,
            color=color,
            created_at=log.timestamp
        ))
    
    return activities


@router.get("/mcps", response_model=List[MCPServerResponse])
async def get_mcp_servers(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Get MCP servers for dashboard table."""
    
    result = await db.execute(
        select(MCPServer).order_by(MCPServer.created_at.desc())
    )
    servers = result.scalars().all()
    
    # Convert to response format
    mcp_responses = []
    for server in servers:
        # Determine status based on is_enabled and is_healthy
        if not server.is_enabled:
            status = "Stopped"
        elif server.is_healthy:
            status = "Running"
        elif server.is_healthy == False:
            status = "Error"
        else:
            status = "Unknown"
        
        # Calculate uptime percentage from requests
        total = server.total_requests or 0
        successful = server.successful_requests or 0
        if total > 0:
            uptime_pct = (successful / total) * 100
            uptime = f"{uptime_pct:.1f}%"
        else:
            uptime = "N/A"
        
        mcp_responses.append(MCPServerResponse(
            id=server.id,
            name=server.name,
            description=None,  # Not in Omni2 schema
            status=status,
            health_status="healthy" if server.is_healthy else ("error" if server.is_healthy == False else "unknown"),
            requests=server.total_requests or 0,
            uptime=uptime,
            version=server.version,
            endpoint=server.url,
            is_active=server.is_enabled,
            created_at=server.created_at
        ))
    
    return mcp_responses
