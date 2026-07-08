import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app import storage


@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    old_path = storage.get_db_path()
    storage.set_db_path("test_chronos.db")
    yield
    storage.set_db_path(old_path)


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "operational"}


@pytest.mark.asyncio
async def test_store_state():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/store_state",
            json={"agent_id": "agent-1", "context_payload": {"step": 1}},
        )
    assert response.status_code == 200
    data = response.json()
    assert "state_id" in data
    assert len(data["state_id"]) > 0


@pytest.mark.asyncio
async def test_store_state_then_retrieve():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        store_resp = await client.post(
            "/store_state",
            json={"agent_id": "agent-1", "context_payload": {"step": 1}},
        )
        state_id = store_resp.json()["state_id"]
        record = storage.get(state_id)
    assert record is not None
    assert record["agent_id"] == "agent-1"
    assert record["context_payload"] == {"step": 1}


@pytest.mark.asyncio
async def test_schedule_wakeup():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        store_resp = await client.post(
            "/store_state",
            json={"agent_id": "agent-1", "context_payload": {"step": 1}},
        )
        state_id = store_resp.json()["state_id"]

        schedule_resp = await client.post(
            "/schedule_wakeup",
            json={
                "agent_webhook_url": "http://example.com/wakeup",
                "state_id": state_id,
                "execute_at_unix": 9999999999,
            },
        )
    assert schedule_resp.status_code == 200
    data = schedule_resp.json()
    assert data["status"] == "scheduled"
    assert "job_id" in data


@pytest.mark.asyncio
async def test_schedule_wakeup_missing_state():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/schedule_wakeup",
            json={
                "agent_webhook_url": "http://example.com/wakeup",
                "state_id": "nonexistent",
                "execute_at_unix": 9999999999,
            },
        )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
