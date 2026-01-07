"""Create sample audit log entries to test dashboard updates."""
import asyncio
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models.omni2 import AuditLog


async def create_test_audit_logs():
    print("\n" + "="*60)
    print("  SIMULATING OMNI2 USER ACTIVITY")
    print("="*60)
    
    async with AsyncSessionLocal() as session:
        # Get before count (use naive datetime for comparison)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await session.execute(
            select(func.count(AuditLog.id)).where(AuditLog.timestamp >= today)
        )
        before_count = result.scalar() or 0
        
        print(f"\n📊 Before: {before_count} API calls today")
        print(f"\n🔄 Creating 5 test interactions...\n")
        
        # Create sample audit logs
        test_logs = [
            AuditLog(
                user_id=1,
                timestamp=datetime.now(timezone.utc),
                request_type='chat',
                message='Test query: What MCPs are available?',
                message_preview='Test query: What MCPs are available?',
                iterations=1,
                tool_calls_count=0,
                tools_used=[],
                mcps_accessed=[],
                tokens_input=50,
                tokens_output=150,
                success=True,
                status='success',
                duration_ms=850,
                ip_address='127.0.0.1',
                user_agent='Test Client'
            ),
            AuditLog(
                user_id=1,
                timestamp=datetime.now(timezone.utc),
                request_type='chat',
                message='Test query: Show me database schema',
                message_preview='Test query: Show me database schema',
                iterations=1,
                tool_calls_count=2,
                tools_used=['list_tables', 'get_schema'],
                mcps_accessed=['database_mcp'],
                tokens_input=45,
                tokens_output=320,
                success=True,
                status='success',
                duration_ms=1250,
                ip_address='127.0.0.1',
                user_agent='Test Client'
            ),
            AuditLog(
                user_id=2,
                timestamp=datetime.now(timezone.utc),
                request_type='tool',
                message='Tool call: search_github',
                message_preview='Tool call: search_github',
                iterations=1,
                tool_calls_count=1,
                tools_used=['search_github'],
                mcps_accessed=['github_mcp'],
                tokens_input=30,
                tokens_output=200,
                success=True,
                status='success',
                duration_ms=2100,
                ip_address='127.0.0.1',
                user_agent='Test Client'
            ),
            AuditLog(
                user_id=3,
                timestamp=datetime.now(timezone.utc),
                request_type='chat',
                message='Help me understand this code',
                message_preview='Help me understand this code',
                iterations=1,
                tool_calls_count=0,
                tools_used=[],
                mcps_accessed=[],
                tokens_input=100,
                tokens_output=450,
                success=True,
                status='success',
                duration_ms=1800,
                ip_address='127.0.0.1',
                user_agent='Test Client'
            ),
            AuditLog(
                user_id=1,
                timestamp=datetime.now(timezone.utc),
                request_type='chat',
                message='List all available tools',
                message_preview='List all available tools',
                iterations=1,
                tool_calls_count=1,
                tools_used=['list_tools'],
                mcps_accessed=['database_mcp', 'github_mcp'],
                tokens_input=25,
                tokens_output=180,
                success=True,
                status='success',
                duration_ms=950,
                ip_address='127.0.0.1',
                user_agent='Test Client'
            ),
        ]
        
        for i, log in enumerate(test_logs, 1):
            session.add(log)
            print(f"   ✓ Activity {i}: {log.message_preview[:50]}...")
        
        await session.commit()
        
        # Get after count (use same naive datetime)
        result = await session.execute(
            select(func.count(AuditLog.id)).where(AuditLog.timestamp >= today)
        )
        after_count = result.scalar() or 0
        
        print(f"\n✅ Created {len(test_logs)} test interactions")
        print(f"\n📊 After: {after_count} API calls today")
        print(f"   Increase: +{after_count - before_count}")
        
        print(f"\n🎯 Now refresh your dashboard to see the updated count!")
        print(f"   Dashboard: http://localhost:3000/dashboard")
        print(f"   The 'API Calls Today' card should show: {after_count}\n")


if __name__ == "__main__":
    asyncio.run(create_test_audit_logs())
