import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.gpio_controller import GPIOController
from app.ws_manager import WSManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

gpio = GPIOController()
ws_manager = WSManager()


async def on_gpio_change(state: dict):
    await ws_manager.broadcast(state)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    gpio.set_on_change(on_gpio_change)
    monitor_task = asyncio.create_task(gpio.monitor())
    logger.info("PC Power Controller started")
    yield
    # Shutdown
    monitor_task.cancel()
    gpio.cleanup()
    logger.info("Shutdown")


app = FastAPI(lifespan=lifespan)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


# --- REST API ---

@app.get("/status")
async def get_status():
    return gpio.get_status()


@app.post("/power/on")
async def power_on():
    return await gpio.power_on()


@app.post("/power/off")
async def power_off():
    return await gpio.power_off()


@app.post("/power/toggle")
async def power_toggle():
    return await gpio.power_toggle()


@app.post("/reset")
async def reset():
    return await gpio.reset()


# --- WebSocket ---

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    # 接続直後に現在の状態を送信
    await ws.send_json(gpio.get_status())
    try:
        while True:
            # クライアントからのメッセージを待機（切断検出用）
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)


# --- Static files ---

@app.get("/")
async def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/manifest.json")
async def manifest():
    return FileResponse(WEB_DIR / "manifest.json", media_type="application/manifest+json")


@app.get("/sw.js")
async def service_worker():
    return FileResponse(WEB_DIR / "sw.js", media_type="application/javascript")


@app.get("/icon.svg")
async def icon():
    return FileResponse(WEB_DIR / "icon.svg", media_type="image/svg+xml")
