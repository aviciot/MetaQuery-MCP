"""Seed script to create initial admin user."""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, ".")

from app.database import AsyncSessionLocal
from app.models.admin_user import AdminUser
from app.utils.security import hash_password
from app.config import settings


async def seed_admin():
    """Create initial admin user."""
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        from sqlalchemy import select
        result = await session.execute(
            select(AdminUser).where(AdminUser.email == settings.ADMIN_EMAIL)
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print(f"✅ Admin user already exists: {settings.ADMIN_EMAIL}")
            return
        
        # Create new admin user
        admin_user = AdminUser(
            email=settings.ADMIN_EMAIL,
            username="admin",
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            full_name="System Administrator",
            role="admin",
            is_super_admin=True,
            is_active=True,
        )
        
        session.add(admin_user)
        await session.commit()
        
        print(f"✅ Created admin user: {settings.ADMIN_EMAIL}")
        print(f"   Password: {settings.ADMIN_PASSWORD}")
        print("   ⚠️  Please change this password after first login!")


if __name__ == "__main__":
    asyncio.run(seed_admin())
