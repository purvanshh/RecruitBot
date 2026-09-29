import sys
sys.path.insert(0, "/app")

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_database_connection():
    from app.db.connection import get_db_connection
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 as test")
            result = cur.fetchone()
            assert result["test"] == 1