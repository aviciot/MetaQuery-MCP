"""Delete existing admin users."""

import asyncio
import sys
from sqlalchemy import text

sys.path.insert(0, ".")

from app.database import AsyncSessionLocal


async def delete_admin():
    """Delete admin users."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("DELETE FROM admin_users WHERE email LIKE '%omni2%'")
        )
        await session.commit()
        print(f"✅ Deleted {result.rowcount} admin users")


if __name__ == "__main__":
    asyncio.run(delete_admin())
