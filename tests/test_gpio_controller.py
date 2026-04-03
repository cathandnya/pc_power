import asyncio

import pytest


@pytest.mark.asyncio
async def test_get_status_default(gpio):
    status = gpio.get_status()
    assert status["pc_power"] is False
    assert status["hdd_active"] is False
    assert status["beep"] is False
    assert status["busy"] is False


@pytest.mark.asyncio
async def test_get_status_power_on(gpio):
    # Simulate PWR_LED HIGH
    gpio._power_led.pin.drive_high()
    status = gpio.get_status()
    assert status["pc_power"] is True


@pytest.mark.asyncio
async def test_get_status_hdd_active(gpio):
    gpio._hdd_led.pin.drive_high()
    status = gpio.get_status()
    assert status["hdd_active"] is True


@pytest.mark.asyncio
async def test_get_status_beep(gpio):
    gpio._power_led.pin.drive_high()
    gpio._speaker.pin.drive_low()
    status = gpio.get_status()
    assert status["beep"] is True


@pytest.mark.asyncio
async def test_power_on_when_off(gpio, fast_sleep):
    result = await gpio.power_on()
    assert result["status"] == "power_on_sent"


@pytest.mark.asyncio
async def test_power_on_when_already_on(gpio, fast_sleep):
    gpio._power_led.pin.drive_high()
    result = await gpio.power_on()
    assert result["status"] == "already_on"
    assert result["pc_power"] is True


@pytest.mark.asyncio
async def test_power_off_when_on(gpio, fast_sleep):
    gpio._power_led.pin.drive_high()
    result = await gpio.power_off()
    assert result["status"] == "power_off_sent"


@pytest.mark.asyncio
async def test_power_off_when_already_off(gpio, fast_sleep):
    result = await gpio.power_off()
    assert result["status"] == "power_off_sent"
    assert result["pc_power"] is False


@pytest.mark.asyncio
async def test_power_toggle(gpio, fast_sleep):
    result = await gpio.power_toggle()
    assert result["status"] == "toggle_sent"


@pytest.mark.asyncio
async def test_reset_when_on(gpio, fast_sleep):
    gpio._power_led.pin.drive_high()
    result = await gpio.reset()
    assert result["status"] == "reset_sent"


@pytest.mark.asyncio
async def test_reset_when_off(gpio, fast_sleep):
    result = await gpio.reset()
    assert result["status"] == "reset_sent"


@pytest.mark.asyncio
async def test_busy_flag(gpio, fast_sleep):
    assert gpio.busy is False
    # Manually set busy to simulate mid-pulse
    gpio._busy = True
    assert gpio.busy is True
    assert gpio.get_status()["busy"] is True
    gpio._busy = False


@pytest.mark.asyncio
async def test_busy_rejects_concurrent(gpio, fast_sleep):
    gpio._busy = True
    with pytest.raises(RuntimeError, match="busy"):
        await gpio.power_on()
    gpio._busy = False


@pytest.mark.asyncio
async def test_monitor_detects_change(gpio):
    changes = []

    async def on_change(state):
        changes.append(state)

    gpio.set_on_change(on_change)

    # Run monitor for a short time
    task = asyncio.create_task(gpio.monitor())

    # Wait for first poll
    await asyncio.sleep(0.1)

    # Simulate PWR_LED change
    gpio._power_led.pin.drive_high()
    await asyncio.sleep(0.1)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert len(changes) >= 1
    assert changes[-1]["pc_power"] is True
