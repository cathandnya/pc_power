#!/bin/bash
# Front Panel Bridge - xbar / SwiftBar Plugin
# macOS メニューバーに PC 電源状態を表示し、クリックで操作

# <xbar.title>Front Panel Bridge</xbar.title>
# <xbar.version>2.0</xbar.version>
# <xbar.author>nya</xbar.author>
# <xbar.dependencies>bash,python3</xbar.dependencies>
# <swiftbar.type>streamable</swiftbar.type>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.environment>[FP_BRIDGE_BASE_URL=,FP_BRIDGE_PYTHON=,FP_BRIDGE_ROOT=]</swiftbar.environment>

# ここを自分の環境に合わせて変更
DEFAULT_BASE_URL="http://<IP or hostname>:8080"
BASE_URL="${FP_BRIDGE_BASE_URL:-$DEFAULT_BASE_URL}"
BASE_URL="${BASE_URL%/}"
CURL_BIN="/usr/bin/curl"

render_status_menu() {
  local status="$1"
  local note="$2"

  if [ -z "$status" ] || [[ "$status" != *'"pc_power"'* ]]; then
    echo "⏻ ? | color=#f87171"
    echo "---"
    echo "接続できません | color=#f87171"
    if [ -n "$note" ]; then
      echo "$note | color=#f59e0b size=12"
    fi
    echo "${BASE_URL} | color=#888888 size=12"
    return
  fi

  [[ "$status" == *'"pc_power":true'* ]] && echo "⏻ | color=#4ade80" || echo "⏻ | color=#666666"

  echo "---"

  [[ "$status" == *'"pc_power":true'* ]] && echo "● ON | color=#4ade80" || echo "● OFF | color=#666666"
  [[ "$status" == *'"hdd_active":true'* ]] && echo "● HDD Active | color=#f59e0b" || echo "● HDD Idle | color=#444444"
  [[ "$status" == *'"beep":true'* ]] && echo "● BEEP | color=#f87171" || echo "● BEEP | color=#444444"
  [[ "$status" == *'"busy":true'* ]] && echo "⏳ Busy | color=#facc15"
  if [ -n "$note" ]; then
    echo "$note | color=#f59e0b size=12"
  fi

  echo "---"

  if [[ "$status" == *'"busy":true'* ]]; then
    echo "Power Toggle | color=#444444"
    echo "Reset | color=#444444"
    echo "Force OFF | color=#444444"
  else
    echo "Power Toggle | bash='${CURL_BIN}' param1='-sf' param2='--connect-timeout' param3='3' param4='--max-time' param5='5' param6='${BASE_URL}/power/toggle' terminal=false refresh=true"
    echo "Reset | bash='${CURL_BIN}' param1='-sf' param2='--connect-timeout' param3='3' param4='--max-time' param5='5' param6='${BASE_URL}/reset' terminal=false refresh=true"
    echo "Force OFF | bash='${CURL_BIN}' param1='-sf' param2='--connect-timeout' param3='3' param4='--max-time' param5='5' param6='${BASE_URL}/power/off' terminal=false refresh=true color=#f87171"
  fi

  echo "---"
  echo "Web UI を開く | href=${BASE_URL}"
}

fetch_status() {
  "${CURL_BIN}" -sf --connect-timeout 3 --max-time 5 "${BASE_URL}/status" 2>/dev/null
}

resolve_script_path() {
  local source="${BASH_SOURCE[0]}"
  local dir link

  while [ -L "$source" ]; do
    dir="$(cd "$(dirname "$source")" && pwd)"
    link="$(readlink "$source")"
    if [[ "$link" == /* ]]; then
      source="$link"
    else
      source="${dir}/${link}"
    fi
  done

  dir="$(cd "$(dirname "$source")" && pwd)"
  echo "${dir}/$(basename "$source")"
}

find_python_with_websockets() {
  local script_path script_dir resolved candidate seen key
  local candidates=()

  script_path="$(resolve_script_path)"
  script_dir="$(cd "$(dirname "$script_path")" && pwd)"

  if [ -n "${FP_BRIDGE_PYTHON:-}" ]; then
    candidates+=("${FP_BRIDGE_PYTHON}")
  fi

  if [ -n "${FP_BRIDGE_ROOT:-}" ]; then
    candidates+=("${FP_BRIDGE_ROOT}/.venv/bin/python" "${FP_BRIDGE_ROOT}/.venv/bin/python3")
  fi

  candidates+=(
    "${script_dir}/../.venv/bin/python"
    "${script_dir}/../.venv/bin/python3"
    "${script_dir}/.venv/bin/python"
    "${script_dir}/.venv/bin/python3"
    "python3"
    "python"
  )

  seen=""

  for candidate in "${candidates[@]}"; do
    [ -n "$candidate" ] || continue
    key="::${candidate}::"
    case "$seen" in
      *"$key"*) continue ;;
    esac
    seen="${seen}${key}"

    if [[ "$candidate" == */* ]]; then
      [ -x "$candidate" ] || continue
      resolved="$candidate"
    else
      resolved="$(command -v "$candidate" 2>/dev/null)" || continue
    fi

    if "$resolved" -c 'import websockets' >/dev/null 2>&1; then
      echo "$resolved"
      return 0
    fi
  done

  return 1
}

if [ "${SWIFTBAR:-}" != "1" ]; then
  render_status_menu "$(fetch_status)" ""
  exit 0
fi

PYTHON_BIN="$(find_python_with_websockets || true)"

if [ -z "$PYTHON_BIN" ]; then
  render_status_menu "$(fetch_status)" "WebSocket 用の Python 環境が見つかりません"
  while sleep 300; do
    :
  done
fi

exec "$PYTHON_BIN" - "$BASE_URL" "$CURL_BIN" <<'PY'
import asyncio
import json
import os
import sys
import urllib.request
from pathlib import Path

import websockets

BASE_URL = sys.argv[1].rstrip("/")
CURL_BIN = sys.argv[2]
WS_URL = BASE_URL.replace("http://", "ws://", 1).replace("https://", "wss://", 1) + "/ws"

DATA_DIR = Path(
    os.environ.get("SWIFTBAR_PLUGIN_DATA_PATH")
    or (Path(os.environ.get("TMPDIR", "/tmp")) / "fp_bridge_swiftbar")
)
CACHE_PATH = DATA_DIR / "status.json"

current_status = None
current_note = None
rendered_once = False
last_output = None


def normalize_status(payload):
    if not isinstance(payload, dict) or "pc_power" not in payload:
        return None
    return {
        "pc_power": bool(payload.get("pc_power")),
        "hdd_active": bool(payload.get("hdd_active")),
        "beep": bool(payload.get("beep")),
        "busy": bool(payload.get("busy")),
    }


def load_cache():
    try:
        return normalize_status(json.loads(CACHE_PATH.read_text()))
    except Exception:
        return None


def save_cache(status):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(status))
    except Exception:
        pass


def build_output(status, note):
    lines = []

    if status is None:
        if note:
            lines.extend(
                [
                    "⏻ ? | color=#f87171",
                    "---",
                    "接続できません | color=#f87171",
                    f"{note} | color=#f59e0b size=12",
                    f"{BASE_URL} | color=#888888 size=12",
                ]
            )
        else:
            lines.extend(
                [
                    "⏻ … | color=#facc15",
                    "---",
                    "WebSocket 接続中... | color=#facc15",
                    f"{BASE_URL} | color=#888888 size=12",
                ]
            )
        return "\n".join(lines)

    lines.append("⏻ | color=#4ade80" if status["pc_power"] else "⏻ | color=#666666")
    lines.append("---")
    lines.append("● ON | color=#4ade80" if status["pc_power"] else "● OFF | color=#666666")
    lines.append("● HDD Active | color=#f59e0b" if status["hdd_active"] else "● HDD Idle | color=#444444")
    lines.append("● BEEP | color=#f87171" if status["beep"] else "● BEEP | color=#444444")
    if status["busy"]:
        lines.append("⏳ Busy | color=#facc15")
    if note:
        lines.append(f"{note} | color=#f59e0b size=12")

    lines.append("---")
    if status["busy"]:
        lines.extend(
            [
                "Power Toggle | color=#444444",
                "Reset | color=#444444",
                "Force OFF | color=#444444",
            ]
        )
    else:
        lines.extend(
            [
                f"Power Toggle | bash='{CURL_BIN}' param1='-sf' param2='--connect-timeout' param3='3' param4='--max-time' param5='5' param6='{BASE_URL}/power/toggle' terminal=false refresh=true",
                f"Reset | bash='{CURL_BIN}' param1='-sf' param2='--connect-timeout' param3='3' param4='--max-time' param5='5' param6='{BASE_URL}/reset' terminal=false refresh=true",
                f"Force OFF | bash='{CURL_BIN}' param1='-sf' param2='--connect-timeout' param3='3' param4='--max-time' param5='5' param6='{BASE_URL}/power/off' terminal=false refresh=true color=#f87171",
            ]
        )

    lines.extend(
        [
            "---",
            f"Web UI を開く | href={BASE_URL}",
        ]
    )

    return "\n".join(lines)


def emit(status, note):
    global rendered_once, last_output

    output = build_output(status, note)
    if output == last_output:
        return

    if rendered_once:
        sys.stdout.write("~~~\n")
    sys.stdout.write(output + "\n")
    sys.stdout.flush()

    rendered_once = True
    last_output = output

    if status is not None:
        save_cache(status)


async def run_in_thread(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args)


ACTION_PATHS = {
    "power_toggle": "/power/toggle",
    "reset": "/reset",
    "power_off": "/power/off",
}


async def call_json(path):
    def _request():
        with urllib.request.urlopen(BASE_URL + path, timeout=10) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return json.loads(response.read().decode(charset))

    return await run_in_thread(_request)


async def handle_action(action):
    global current_status, current_note

    path = ACTION_PATHS.get(action)
    if path is None:
        return

    base_status = dict(current_status or {"pc_power": False, "hdd_active": False, "beep": False, "busy": False})
    base_status["busy"] = True
    emit(base_status, "操作を送信中...")

    try:
        payload = await call_json(path)
    except Exception as exc:
        base_status["busy"] = False
        current_status = base_status if current_status is not None else current_status
        current_note = f"操作に失敗: {exc.__class__.__name__}"
        emit(current_status, current_note)
        return

    merged = dict(base_status)
    merged.update(payload if isinstance(payload, dict) else {})
    merged["busy"] = False

    normalized = normalize_status(merged)
    current_status = normalized or current_status or merged
    current_note = None
    emit(current_status, current_note)


async def stdin_loop():
    while True:
        line = await run_in_thread(sys.stdin.readline)
        if line == "":
            return

        action = line.strip()
        if action:
            await handle_action(action)


async def websocket_loop():
    global current_status, current_note

    retry_delay = 1

    while True:
        try:
            async with websockets.connect(
                WS_URL,
                open_timeout=5,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=5,
            ) as ws:
                current_note = None
                emit(current_status, current_note)
                retry_delay = 1

                async for message in ws:
                    payload = normalize_status(json.loads(message))
                    if payload is None:
                        continue
                    current_status = payload
                    current_note = None
                    emit(current_status, current_note)
        except Exception as exc:
            if current_status is None:
                current_note = f"WebSocket 接続失敗: {exc.__class__.__name__}"
            else:
                current_note = "WebSocket 再接続中..."
            emit(current_status, current_note)
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 10)


async def main():
    global current_status

    current_status = load_cache()
    emit(current_status, None)
    await asyncio.gather(websocket_loop(), stdin_loop())


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
PY
