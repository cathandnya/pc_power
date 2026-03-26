import os

# Must be set before any gpiozero import
os.environ["GPIOZERO_PIN_FACTORY"] = "mock"

import asyncio
from unittest.mock import AsyncMock

import pytest

# Import app.main first — it creates the global GPIOController instance
from app.main import gpio as _app_gpio
from app.ws_manager import WSManager


@pytest.fixture
def gpio():
    """Use the global GPIOController from app.main (pins already reserved)."""
    ctrl = _app_gpio
    # Reset state between tests
    ctrl._busy = False
    ctrl._prev_state = None
    ctrl._on_change = None
    # Reset input pins to LOW
    ctrl._power_led.pin.drive_low()
    ctrl._hdd_led.pin.drive_low()
    ctrl._speaker.pin.drive_low()
    yield ctrl


@pytest.fixture
def ws_manager():
    return WSManager()


@pytest.fixture
def fast_sleep(monkeypatch):
    """Replace asyncio.sleep with instant return for fast tests."""
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
