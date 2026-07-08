import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app import storage


@pytest.mark.asyncio
async def test_register_event():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        store_resp = await client.post(
            "/store_state",
            json={
                "agent_id": "agent-1",
                "ciphertext": "encrypted-data",
            },
        )
        state_id = store_resp.json()["state_id"]

        resp = await client.post(
            "/register_event",
            json={
                "agent_id": "agent-1",
                "agent_webhook_url": "http://example.com/wakeup",
                "event_name": "payment_completed",
                "state_id": state_id,
            },
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "subscription_id" in data
    assert len(data["subscription_id"]) > 0


@pytest.mark.asyncio
async def test_register_event_missing_state():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/register_event",
            json={
                "agent_id": "agent-1",
                "agent_webhook_url": "http://example.com/wakeup",
                "event_name": "payment_completed",
                "state_id": "nonexistent",
            },
        )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_publish_event_no_subscribers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/publish_event",
            json={
                "event_name": "unknown_event",
            },
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["triggered_count"] == 0


@pytest.mark.asyncio
async def test_publish_event_with_data():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        store_resp = await client.post(
            "/store_state",
            json={
                "agent_id": "agent-1",
                "ciphertext": "encrypted-data",
            },
        )
        state_id = store_resp.json()["state_id"]

        await client.post(
            "/register_event",
            json={
                "agent_id": "agent-1",
                "agent_webhook_url": "http://example.com/wakeup",
                "event_name": "order_shipped",
                "state_id": state_id,
            },
        )

        resp = await client.post(
            "/publish_event",
            json={
                "event_name": "order_shipped",
                "event_data": {"order_id": "12345", "tracking": "TRACK001"},
            },
        )
    assert resp.status_code == 200
    data = resp.json()
    # The webhook call will fail (example.com), so triggered_count stays 0
    assert data["triggered_count"] == 0


@pytest.mark.asyncio
async def test_subscription_persisted():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        store_resp = await client.post(
            "/store_state",
            json={
                "agent_id": "agent-1",
                "ciphertext": "data",
            },
        )
        state_id = store_resp.json()["state_id"]

        await client.post(
            "/register_event",
            json={
                "agent_id": "agent-1",
                "agent_webhook_url": "http://example.com/wakeup",
                "event_name": "test_event",
                "state_id": state_id,
            },
        )

        subs = storage.get_subscriptions_by_event("test_event")
    assert len(subs) == 1
    assert subs[0]["event_name"] == "test_event"
    assert subs[0]["agent_id"] == "agent-1"
