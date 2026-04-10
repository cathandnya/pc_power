#!/bin/bash
# Front Panel Bridge - xbar Plugin
# macOS メニューバーに PC 電源状態を表示し、クリックで操作

# ここを自分の環境に合わせて変更
BASE_URL="http://<IP or hostname>:8080"

# --- ステータス取得 ---

STATUS=$(curl -s --connect-timeout 3 --max-time 5 "${BASE_URL}/status" 2>/dev/null)

if [ -z "$STATUS" ]; then
  echo "⏻ ? | color=#f87171"
  echo "---"
  echo "接続できません | color=#f87171"
  echo "${BASE_URL} | color=#888888 size=12"
  echo "---"
  echo "Refresh | refresh=true"
  exit 0
fi

# --- JSON パース (python3) ---

read -r PC_POWER HDD_ACTIVE BEEP BUSY <<< "$(echo "$STATUS" | python3 -c '
import sys, json
d = json.load(sys.stdin)
print(d["pc_power"], d["hdd_active"], d["beep"], d["busy"])
')"

# --- メニューバー タイトル ---

if [ "$PC_POWER" = "True" ]; then
  echo "⏻ | color=#4ade80"
else
  echo "⏻ | color=#666666"
fi

echo "---"

# --- ステータス詳細 ---

if [ "$PC_POWER" = "True" ]; then
  echo "● ON | color=#4ade80"
else
  echo "● OFF | color=#666666"
fi

if [ "$HDD_ACTIVE" = "True" ]; then
  echo "● HDD Active | color=#f59e0b"
else
  echo "● HDD Idle | color=#444444"
fi

if [ "$BEEP" = "True" ]; then
  echo "● BEEP | color=#f87171"
else
  echo "● BEEP | color=#444444"
fi

if [ "$BUSY" = "True" ]; then
  echo "⏳ Busy | color=#facc15"
fi

echo "---"

# --- 操作 ---

if [ "$BUSY" = "True" ]; then
  echo "Power Toggle | color=#444444"
  echo "Reset | color=#444444"
  echo "Force OFF | color=#444444"
else
  echo "Power Toggle | bash='curl' param1='-s' param2='${BASE_URL}/power/toggle' terminal=false refresh=true"
  echo "Reset | bash='curl' param1='-s' param2='${BASE_URL}/reset' terminal=false refresh=true"
  echo "Force OFF | bash='curl' param1='-s' param2='${BASE_URL}/power/off' terminal=false refresh=true color=#f87171"
fi

echo "---"
echo "Web UI を開く | href=${BASE_URL}"
echo "Refresh | refresh=true"
