from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
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
