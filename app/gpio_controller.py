import asyncio
import os
import random
import threading
import time
import logging
from gpiozero import OutputDevice, InputDevice, DigitalInputDevice
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
        # SPEAKER は矩形波エッジ検知のため DigitalInputDevice (when_activated/when_deactivated 対応)
        self._speaker = DigitalInputDevice(config.PIN_SPEAKER, pull_up=False)

        self._busy = False
        self._on_change = None

        # 前回の状態（変化検出用）
        self._prev_state = None

        # ビープ検知（矩形波）: gpiozero のエッジコールバックは別スレッドから呼ばれる
        self._edge_count = 0
        self._edge_lock = threading.Lock()
        self._beep_active = False
        self._speaker.when_activated = self._on_speaker_edge
        self._speaker.when_deactivated = self._on_speaker_edge

    @property
    def busy(self):
        return self._busy

    def get_status(self):
        return {
            "pc_power": bool(self._power_led.is_active),
            "hdd_active": bool(self._hdd_led.is_active),
            "beep": self._beep_active and bool(self._power_led.is_active),
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

    def _on_speaker_edge(self, _device=None):
        """SPEAKER GPIO のエッジコールバック（gpiozero の別スレッドから呼ばれる）。"""
        with self._edge_lock:
            self._edge_count += 1

    def _evaluate_beep_once(self):
        """直近窓のエッジ数を評価し、_beep_active を更新する。"""
        with self._edge_lock:
            count = self._edge_count
            self._edge_count = 0
        self._beep_active = count >= config.BEEP_EDGE_THRESHOLD

    async def _beep_evaluator(self):
        """エッジ数を BEEP_EVAL_INTERVAL ごとに評価して beep 状態を更新する。"""
        logger.info(
            "Beep detector started (window=%sms threshold=%d)",
            int(config.BEEP_EVAL_INTERVAL * 1000),
            config.BEEP_EDGE_THRESHOLD,
        )
        while True:
            await asyncio.sleep(config.BEEP_EVAL_INTERVAL)
            self._evaluate_beep_once()

    async def _mock_beep(self, freq_hz=1000, duration=0.3):
        """Mock mode: simulate POST beep as a square wave on the SPEAKER pin."""
        half_period = 0.5 / freq_hz
        end = time.monotonic() + duration
        while time.monotonic() < end:
            self._speaker.pin.drive_high()
            await asyncio.sleep(half_period)
            self._speaker.pin.drive_low()
            await asyncio.sleep(half_period)

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
        asyncio.create_task(self._beep_evaluator())
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
        self._speaker.when_activated = None
        self._speaker.when_deactivated = None
        self._power_sw.close()
        self._reset_sw.close()
        self._power_led.close()
        self._hdd_led.close()
        self._speaker.close()
