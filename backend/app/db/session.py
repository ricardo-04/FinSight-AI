from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./finsight_dev.db"
)

_connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_async_engine(DATABASE_URL, echo=False, connect_args=_connect_args)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create all tables. Call once at startup. Retries connection to DB."""
    from app.db.base import Base
    from app.models.document import Document, DocumentChunk  # noqa: F401
    from app.models.metrics import FinancialMetric  # noqa: F401

    # For SQLite, patch the Vector column to Text so schema creation works
    if DATABASE_URL.startswith("sqlite"):
        from sqlalchemy import Text as SAText
        for col in DocumentChunk.__table__.columns:
            if col.name == "embedding":
                col.type = SAText()

    for attempt in range(10):
        try:
            async with engine.begin() as conn:
                if not DATABASE_URL.startswith("sqlite"):
                    await conn.execute(
                        __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS vector")
                    )
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully.")
            return
        except Exception as exc:
            if attempt < 9:
                logger.warning("DB connection attempt %d failed: %s. Retrying in 3s...", attempt + 1, exc)
                await asyncio.sleep(3)
            else:
                raise
