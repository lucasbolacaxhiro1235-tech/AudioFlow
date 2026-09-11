import logging

from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.database import AsyncSessionLocal
from app.models import Plan, PlanTier, Subscription, SubscriptionStatus, User, UserRole

logger = logging.getLogger(__name__)

DEFAULT_PLANS = [
    {
        "tier": PlanTier.FREE,
        "name": "Free",
        "price_cents": 0,
        "daily_download_limit": 10,
        "max_file_size_mb": 50,
        "max_concurrent_downloads": 1,
        "max_storage_gb": 1,
        "queue_priority": 0,
        "features": ["Até 10 downloads por dia", "1 download simultâneo", "1 GB de armazenamento", "Formatos MP3"],
    },
    {
        "tier": PlanTier.PRO,
        "name": "Pro",
        "price_cents": 999,
        "daily_download_limit": 100,
        "max_file_size_mb": 200,
        "max_concurrent_downloads": 4,
        "max_storage_gb": 20,
        "queue_priority": 10,
        "features": ["Downloads ilimitados", "4 downloads simultâneos", "20 GB de armazenamento", "Todos os formatos", "Prioridade na fila"],
    },
    {
        "tier": PlanTier.PREMIUM,
        "name": "Premium",
        "price_cents": 1999,
        "daily_download_limit": 1000,
        "max_file_size_mb": 500,
        "max_concurrent_downloads": 8,
        "max_storage_gb": 100,
        "queue_priority": 20,
        "features": ["Downloads ilimitados", "8 downloads simultâneos", "100 GB de armazenamento", "Todos os formatos", "Prioridade máxima", "Suporte dedicado"],
    },
]


async def seed_plans() -> None:
    async with AsyncSessionLocal() as db:
        for plan_data in DEFAULT_PLANS:
            existing = (
                await db.execute(select(Plan).where(Plan.tier == plan_data["tier"]))
            ).scalar_one_or_none()
            if existing is None:
                db.add(Plan(**plan_data))
        await db.commit()


async def seed_first_admin() -> None:
    if not settings.FIRST_ADMIN_EMAIL or not settings.FIRST_ADMIN_PASSWORD:
        return
    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(User).where(User.email == settings.FIRST_ADMIN_EMAIL.lower()))
        ).scalar_one_or_none()
        if existing is not None:
            return
        user = User(
            email=settings.FIRST_ADMIN_EMAIL.lower(),
            name="Admin",
            username="admin",
            hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            email_verified=True,
        )
        db.add(user)
        await db.flush()
        pro = (await db.execute(select(Plan).where(Plan.tier == PlanTier.PREMIUM))).scalar_one_or_none()
        if pro is not None:
            db.add(Subscription(user_id=user.id, plan_id=pro.id, status=SubscriptionStatus.ACTIVE))
        await db.commit()
        logger.info("First admin created: %s", settings.FIRST_ADMIN_EMAIL)