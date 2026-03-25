import uasyncio as asyncio
from power import PowerController
from wifi import WiFiManager
from server import HTTPServer
import config


async def wifi_watchdog(wifi, power):
    while True:
        await asyncio.sleep(10)
        if not wifi.is_connected():
            print("WiFi disconnected, reconnecting...")
            power.set_led(False)
            try:
                ip = await wifi.ensure_connected()
                print("Reconnected:", ip)
                power.set_led(True)
            except Exception as e:
                print("Reconnect failed:", e)


async def main():
    power = PowerController()
    wifi = WiFiManager()

    # WiFi接続（リトライ付き）
    while True:
        try:
            print("Connecting to WiFi...")
            ip = await wifi.connect()
            print("Connected:", ip)
            power.set_led(True)
            break
        except OSError as e:
            print("WiFi failed:", e)
            await asyncio.sleep(config.WIFI_RETRY_INTERVAL)

    # HTTPサーバー起動
    srv = HTTPServer(power)
    await srv.start()

    # WiFi監視タスク
    asyncio.create_task(wifi_watchdog(wifi, power))

    # イベントループ維持
    while True:
        await asyncio.sleep(3600)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Shutdown")
