from machine import Pin
import uasyncio as asyncio
import config


class PowerController:
    def __init__(self):
        # パワー/リセットスイッチ: 通常時はPin.IN（Hi-Z = スイッチ開放）
        Pin(config.PIN_POWER_SW, Pin.IN)
        Pin(config.PIN_RESET_SW, Pin.IN)

        # Power LED読み取り: 入力、プルダウン
        self._power_led = Pin(config.PIN_POWER_LED, Pin.IN, Pin.PULL_DOWN)

        # 内蔵LED
        self._led = Pin("LED", Pin.OUT)

        # パルス実行中フラグ（多重実行防止）
        self._busy = False

    def get_pc_status(self):
        val = self._power_led.value()
        if config.POWER_LED_ACTIVE_HIGH:
            return bool(val)
        return not bool(val)

    async def _pulse(self, pin_num, duration_ms):
        if self._busy:
            raise RuntimeError("busy")
        self._busy = True
        try:
            Pin(pin_num, Pin.OUT, value=0)
            await asyncio.sleep_ms(duration_ms)
        finally:
            Pin(pin_num, Pin.IN)
            self._busy = False

    async def power_on(self):
        if self.get_pc_status():
            return {"status": "already_on", "pc_power": True}
        await self._pulse(config.PIN_POWER_SW, config.PULSE_POWER_ON)
        return {"status": "power_on_sent", "pc_power": self.get_pc_status()}

    async def power_off(self):
        if not self.get_pc_status():
            return {"status": "already_off", "pc_power": False}
        await self._pulse(config.PIN_POWER_SW, config.PULSE_POWER_OFF)
        return {"status": "power_off_sent", "pc_power": self.get_pc_status()}

    async def power_toggle(self):
        await self._pulse(config.PIN_POWER_SW, config.PULSE_POWER_ON)
        return {"status": "toggle_sent", "pc_power": self.get_pc_status()}

    async def reset(self):
        if not self.get_pc_status():
            return {"status": "pc_is_off", "pc_power": False}
        await self._pulse(config.PIN_RESET_SW, config.PULSE_RESET)
        return {"status": "reset_sent", "pc_power": self.get_pc_status()}

    def set_led(self, on):
        self._led.value(1 if on else 0)
