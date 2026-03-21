"""
Shared pytest fixtures for testing.

Provides test database with automatic cleanup and async HTTP client.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.dependencies import get_db
from app.models import Base


# Test database URL (separate from development database)
TEST_DATABASE_URL = "postgresql+psycopg://logs_user:changeme_in_production@postgres:5432/test_logs_db"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """
    Create test database engine.

    Creates fresh engine for each test function.
    Ensures test isolation.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,  # Disable SQL logging in tests
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine):
    """
    Create test database session.

    Provides async database session for tests.
    Automatically rolls back after each test.
    """
    # Create session factory
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    """
    Create async HTTP test client.

    Provides httpx AsyncClient for testing API endpoints.
    Overrides get_db dependency to use test database.
    """
    # Override get_db dependency to use test database
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    # Create async client with ASGI transport
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    # Cleanup: Clear dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Configure async backend for pytest-asyncio.

    Uses asyncio as the backend.
    """
    return "asyncio"
