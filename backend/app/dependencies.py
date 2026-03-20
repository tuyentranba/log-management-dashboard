"""FastAPI dependency injection functions."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency.

    Provides async database session to route handlers.
    Session is automatically closed after request completes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
