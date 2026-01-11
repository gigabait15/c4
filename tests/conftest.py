"""Фикстуры для тестов."""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.base.model import Base
from core.db.session import get_db
from main import app

# ================== Database Fixtures ==================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for session scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_db_engine():
    """Create async test database engine (SQLite in memory)."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_db_session(async_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session."""
    async_session_maker = async_sessionmaker(
        bind=async_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(
    async_db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for API testing."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(async_db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create sync test client."""

    def override_get_db():
        return async_db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# ================== Mock Fixtures ==================


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Create mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.get = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    return session


# ================== Test Data Fixtures ==================


@pytest.fixture
def user_data() -> dict:
    """Sample user data."""
    return {
        "first_name": "Иван",
        "last_name": "Иванов",
        "full_name": "Иван Иванов",
        "telegram_id": "123456789",
    }


@pytest.fixture
def user_data_2() -> dict:
    """Second sample user data."""
    return {
        "first_name": "Петр",
        "last_name": "Петров",
        "full_name": "Петр Петров",
        "telegram_id": "987654321",
    }


@pytest.fixture
def object_data() -> dict:
    """Sample object data."""
    return {
        "name": "Математика",
        "point": 85,
        "user_id": 1,
    }


@pytest.fixture
def object_data_2() -> dict:
    """Second sample object data."""
    return {
        "name": "Русский язык",
        "point": 92,
        "user_id": 1,
    }
