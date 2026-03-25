import uasyncio as asyncio
import ujson as json
import config


class HTTPServer:
    def __init__(self, power_controller):
        self._power = power_controller
        self._routes = {
            ("GET", "/status"): self._handle_status,
            ("POST", "/power/on"): self._handle_power_on,
            ("POST", "/power/off"): self._handle_power_off,
            ("POST", "/power/toggle"): self._handle_power_toggle,
            ("POST", "/reset"): self._handle_reset,
        }

    async def start(self, host="0.0.0.0", port=None):
        port = port or config.SERVER_PORT
        await asyncio.start_server(self._handle_client, host, port)
        print("HTTP server on port", port)

    async def _handle_client(self, reader, writer):
        try:
            request_line = await asyncio.wait_for(reader.readline(), timeout=5)
            if not request_line:
                return

            parts = request_line.decode().strip().split(" ", 2)
            if len(parts) < 2:
                return
            method, path = parts[0], parts[1]

            # ヘッダー読み捨て
            while True:
                line = await reader.readline()
                if line in (b"\r\n", b"\n", b""):
                    break

            # CORS preflight
            if method == "OPTIONS":
                await self._send_cors_preflight(writer)
                return

            handler = self._routes.get((method, path))
            if handler:
                result = await handler()
                await self._send_json(writer, result, 200)
            else:
                await self._send_json(writer, {"error": "not_found", "path": path}, 404)

        except Exception as e:
            try:
                await self._send_json(writer, {"error": str(e)}, 500)
            except:
                pass
        finally:
            await writer.aclose()

    async def _send_json(self, writer, data, status):
        body = json.dumps(data)
        status_text = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}.get(status, "Error")
        writer.write(
            "HTTP/1.1 {} {}\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Connection: close\r\n"
            "\r\n".format(status, status_text, len(body)).encode()
        )
        writer.write(body.encode())
        await writer.drain()

    async def _send_cors_preflight(self, writer):
        writer.write(
            "HTTP/1.1 204 No Content\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
            "Access-Control-Allow-Headers: Content-Type\r\n"
            "Connection: close\r\n"
            "\r\n".encode()
        )
        await writer.drain()

    async def _handle_status(self):
        return {"pc_power": self._power.get_pc_status(), "busy": self._power._busy}

    async def _handle_power_on(self):
        return await self._power.power_on()

    async def _handle_power_off(self):
        return await self._power.power_off()

    async def _handle_power_toggle(self):
        return await self._power.power_toggle()

    async def _handle_reset(self):
        return await self._power.reset()
