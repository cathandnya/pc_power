import asyncio
import os
import random
import logging
from gpiozero import OutputDevice, InputDevice
from app import config

logger = logging.getLogger(__name__)

MOCK_MODE = os.environ.get("GPIOZERO_PIN_FACTORY") == "mock"


class GPIOController:
    def __init__(self):
        # 出力: 通常Hi-Z (active_high=False で LOW を出力)
        self._power_sw = OutputDevice(config.PIN_POWER_SW, active_high=False, initial_value=False)
        self._reset_sw = OutputDevice(config.PIN_RESET_SW, active_high=False, initial_value=False)

        # 入力: プルダウン
        self._power_led = InputDevice(config.PIN_POWER_LED, pull_up=False)
        self._hdd_led = InputDevice(config.PIN_HDD_LED, pull_up=False)
        self._speaker = InputDevice(config.PIN_SPEAKER, pull_up=True)

        self._busy = False
        self._on_change = None

        # 前回の状態（変化検出用）
        self._prev_state = None

    @property
    def busy(self):
        return self._busy

    def get_status(self):
        return {
            "pc_power": bool(self._power_led.is_active),
            "hdd_active": bool(self._hdd_led.is_active),
            "beep": not self._speaker.is_active,
            "busy": self._busy,
        }

    def set_on_change(self, callback):
        self._on_change = callback

    async def _pulse(self, device, duration):
        if self._busy:
            raise RuntimeError("busy")
        self._busy = True
        try:
            device.on()
            await asyncio.sleep(duration)
        finally:
            device.off()
            self._busy = False

    def _mock_set_power(self, on):
        """Mock mode: simulate PWR_LED state change."""
        if MOCK_MODE:
            if on:
                self._power_led.pin.drive_high()
            else:
                self._power_led.pin.drive_low()

    async def power_on(self):
        if self._power_led.is_active:
            return {"status": "already_on", "pc_power": True}
        await self._pulse(self._power_sw, config.PULSE_POWER_ON)
        self._mock_set_power(True)
        return {"status": "power_on_sent", "pc_power": self._power_led.is_active}

    async def power_off(self):
        await self._pulse(self._power_sw, config.PULSE_POWER_OFF)
        self._mock_set_power(False)
        return {"status": "power_off_sent", "pc_power": self._power_led.is_active}

    async def power_toggle(self):
        await self._pulse(self._power_sw, config.PULSE_POWER_ON)
        self._mock_set_power(not self._power_led.is_active)
        return {"status": "toggle_sent", "pc_power": self._power_led.is_active}

    async def reset(self):
        await self._pulse(self._reset_sw, config.PULSE_RESET)
        if MOCK_MODE:
            asyncio.create_task(self._mock_beep())
        return {"status": "reset_sent", "pc_power": self._power_led.is_active}

    async def _mock_beep(self):
        """Mock mode: simulate POST beep on reset."""
        self._speaker.pin.drive_high()
        await asyncio.sleep(0.3)
        self._speaker.pin.drive_low()

    async def _mock_hdd_activity(self):
        """Mock mode: simulate random HDD LED activity while PC is ON."""
        while True:
            if self._power_led.is_active:
                if random.random() < 0.4:
                    self._hdd_led.pin.drive_high()
                else:
                    self._hdd_led.pin.drive_low()
            else:
                self._hdd_led.pin.drive_low()
            await asyncio.sleep(random.uniform(0.05, 0.3))

    async def monitor(self):
        """GPIO入力を監視し、変化時にコールバックを呼ぶ"""
        logger.info("GPIO monitor started (interval: %sms)", int(config.MONITOR_INTERVAL * 1000))
        if MOCK_MODE:
            asyncio.create_task(self._mock_hdd_activity())
        while True:
            state = self.get_status()
            # busy は監視対象外（制御側の状態なので）
            comparable = (state["pc_power"], state["hdd_active"], state["beep"])
            if comparable != self._prev_state:
                self._prev_state = comparable
                if self._on_change:
                    await self._on_change(state)
            await asyncio.sleep(config.MONITOR_INTERVAL)

    def cleanup(self):
        self._power_sw.close()
        self._reset_sw.close()
        self._power_led.close()
        self._hdd_led.close()
        self._speaker.close()
