import asyncio
import logging
from gpiozero import OutputDevice, InputDevice
from app import config

logger = logging.getLogger(__name__)


class GPIOController:
    def __init__(self):
        # 出力: 通常Hi-Z (active_high=False で LOW を出力)
        self._power_sw = OutputDevice(config.PIN_POWER_SW, active_high=False, initial_value=False)
        self._reset_sw = OutputDevice(config.PIN_RESET_SW, active_high=False, initial_value=False)

        # 入力: プルダウン
        self._power_led = InputDevice(config.PIN_POWER_LED, pull_up=False)
        self._hdd_led = InputDevice(config.PIN_HDD_LED, pull_up=False)
        self._speaker = InputDevice(config.PIN_SPEAKER, pull_up=False)

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
            "beep": bool(self._speaker.is_active),
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

    async def power_on(self):
        if self._power_led.is_active:
            return {"status": "already_on", "pc_power": True}
        await self._pulse(self._power_sw, config.PULSE_POWER_ON)
        return {"status": "power_on_sent", "pc_power": self._power_led.is_active}

    async def power_off(self):
        if not self._power_led.is_active:
            return {"status": "already_off", "pc_power": False}
        await self._pulse(self._power_sw, config.PULSE_POWER_OFF)
        return {"status": "power_off_sent", "pc_power": self._power_led.is_active}

    async def power_toggle(self):
        await self._pulse(self._power_sw, config.PULSE_POWER_ON)
        return {"status": "toggle_sent", "pc_power": self._power_led.is_active}

    async def reset(self):
        if not self._power_led.is_active:
            return {"status": "pc_is_off", "pc_power": False}
        await self._pulse(self._reset_sw, config.PULSE_RESET)
        return {"status": "reset_sent", "pc_power": self._power_led.is_active}

    async def monitor(self):
        """GPIO入力を監視し、変化時にコールバックを呼ぶ"""
        logger.info("GPIO monitor started (interval: %sms)", int(config.MONITOR_INTERVAL * 1000))
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
