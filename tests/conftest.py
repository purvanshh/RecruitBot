import sys
sys.path.insert(0, "/app")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.connection import execute_schema, execute_seed


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Initialize database schema and seed data before tests."""
    execute_schema()
    execute_seed()
    yield


@pytest_asyncio.fixture
async def client():
    """Create test client with proper lifespan."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client