"""Check tables in database."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check_tables():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
        )
        tables = result.fetchall()
        print('\nTables in Omni2 database:')
        for t in tables:
            print(f'  - {t[0]}')

if __name__ == "__main__":
    asyncio.run(check_tables())
