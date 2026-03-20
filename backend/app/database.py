from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

# Database URL (will be configured via environment variable in Plan 02)
DATABASE_URL = "postgresql+psycopg://logs_user:changeme@postgres:5432/logs_db"

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL logging for development
    pool_size=20,  # Persistent connections
    max_overflow=10,  # Additional temporary connections
    pool_pre_ping=True,  # Validate connections on checkout
    pool_recycle=3600  # Recycle connections after 1 hour
)

# Create session factory with expire_on_commit=False
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False  # Prevents attribute expiration after commit
)


# FastAPI dependency for session injection
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
