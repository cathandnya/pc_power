import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ws_manager import WSManager


def make_mock_ws():
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_connect_and_broadcast(ws_manager):
    ws = make_mock_ws()
    await ws_manager.connect(ws)

    data = {"pc_power": True, "hdd_active": False, "beep": False}
    await ws_manager.broadcast(data)

    ws.send_text.assert_called_once_with(json.dumps(data))


@pytest.mark.asyncio
async def test_disconnect(ws_manager):
    ws = make_mock_ws()
    await ws_manager.connect(ws)
    ws_manager.disconnect(ws)

    await ws_manager.broadcast({"test": True})
    ws.send_text.assert_not_called()


@pytest.mark.asyncio
async def test_multiple_clients(ws_manager):
    ws1 = make_mock_ws()
    ws2 = make_mock_ws()
    await ws_manager.connect(ws1)
    await ws_manager.connect(ws2)

    data = {"pc_power": False}
    await ws_manager.broadcast(data)

    msg = json.dumps(data)
    ws1.send_text.assert_called_once_with(msg)
    ws2.send_text.assert_called_once_with(msg)


@pytest.mark.asyncio
async def test_dead_client_removed(ws_manager):
    ws_good = make_mock_ws()
    ws_dead = make_mock_ws()
    ws_dead.send_text.side_effect = Exception("connection closed")

    await ws_manager.connect(ws_good)
    await ws_manager.connect(ws_dead)

    await ws_manager.broadcast({"test": True})

    # Dead client should be removed
    assert ws_dead not in ws_manager._connections
    assert ws_good in ws_manager._connections
