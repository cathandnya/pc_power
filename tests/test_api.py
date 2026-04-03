import os

os.environ["GPIOZERO_PIN_FACTORY"] = "mock"

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app, gpio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_get_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/status")
    assert res.status_code == 200
    data = res.json()
    assert "pc_power" in data
    assert "hdd_active" in data
    assert "beep" in data
    assert "busy" in data


@pytest.mark.asyncio
async def test_power_on():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/power/on")
    assert res.status_code == 200
    assert "status" in res.json()


@pytest.mark.asyncio
async def test_power_off():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/power/off")
    assert res.status_code == 200
    assert "status" in res.json()


@pytest.mark.asyncio
async def test_power_toggle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/power/toggle")
    assert res.status_code == 200
    assert res.json()["status"] == "toggle_sent"


@pytest.mark.asyncio
async def test_reset():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/reset")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_index_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
