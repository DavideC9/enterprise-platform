import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import Base, AsyncSessionLocal

logger = logging.getLogger(__name__)


async def init_db(conn: AsyncConnection) -> None:
    from app.models.admin import AdminUser  # noqa: F401
    from app.models import section  # noqa: F401

    await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured.")


async def seed_admin() -> None:
    from app.models.admin import AdminUser

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AdminUser.id).limit(1))

        if result.scalar_one_or_none() is not None:
            logger.info("Admin user already exists — skipping seed.")
            return

        admin = AdminUser(
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_active=True,
        )

        session.add(admin)
        await session.commit()
        logger.info(f"Admin user created: {settings.ADMIN_EMAIL}")