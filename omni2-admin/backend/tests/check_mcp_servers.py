"""Check mcp_servers table structure."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database import AsyncSessionLocal


async def check_mcp_servers_table():
    async with AsyncSessionLocal() as session:
        # Get column names and types
        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'mcp_servers'
            ORDER BY ordinal_position
        """))
        
        print("\n=== mcp_servers table structure ===")
        for row in result:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
        
        # Check sample data
        result = await session.execute(text("SELECT * FROM mcp_servers LIMIT 1"))
        sample = result.fetchone()
        if sample:
            print(f"\n=== Sample data (first row) ===")
            print(f"  {dict(zip(result.keys(), sample))}")
        else:
            print("\n=== No data in mcp_servers ===")


if __name__ == "__main__":
    asyncio.run(check_mcp_servers_table())
