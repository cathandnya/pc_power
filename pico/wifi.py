import network
import uasyncio as asyncio
import config


class WiFiManager:
    def __init__(self):
        self._wlan = network.WLAN(network.STA_IF)

    async def connect(self):
        self._wlan.active(True)
        self._wlan.config(pm=0xa11140)  # 省電力モード無効化
        self._wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        elapsed = 0
        while not self._wlan.isconnected():
            if elapsed >= config.WIFI_CONNECT_TIMEOUT:
                raise OSError("WiFi connection timeout")
            await asyncio.sleep(1)
            elapsed += 1

        return self._wlan.ifconfig()[0]

    def is_connected(self):
        return self._wlan.isconnected()

    async def ensure_connected(self):
        if not self._wlan.isconnected():
            self._wlan.disconnect()
            await asyncio.sleep(1)
            return await self.connect()
        return self._wlan.ifconfig()[0]
