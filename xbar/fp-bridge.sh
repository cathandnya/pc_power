#!/bin/bash
# Front Panel Bridge - xbar / SwiftBar Plugin
# macOS メニューバーに PC 電源状態を表示し、クリックで操作

# <xbar.title>Front Panel Bridge</xbar.title>
# <xbar.version>1.0</xbar.version>
# <xbar.author>nya</xbar.author>

# ここを自分の環境に合わせて変更
BASE_URL="http://<IP or hostname>:8080"

STATUS=$(curl -s --connect-timeout 3 --max-time 5 "${BASE_URL}/status" 2>/dev/null)

if [ -z "$STATUS" ]; then
  echo "⏻ ? | color=#f87171"
  echo "---"
  echo "接続できません | color=#f87171"
  echo "${BASE_URL} | color=#888888 size=12"
  exit 0
fi

[[ "$STATUS" == *'"pc_power":true'* ]] && echo "⏻ | color=#4ade80" || echo "⏻ | color=#666666"

echo "---"

[[ "$STATUS" == *'"pc_power":true'* ]] && echo "● ON | color=#4ade80" || echo "● OFF | color=#666666"
[[ "$STATUS" == *'"hdd_active":true'* ]] && echo "● HDD Active | color=#f59e0b" || echo "● HDD Idle | color=#444444"
[[ "$STATUS" == *'"beep":true'* ]] && echo "● BEEP | color=#f87171" || echo "● BEEP | color=#444444"
[[ "$STATUS" == *'"busy":true'* ]] && echo "⏳ Busy | color=#facc15"

echo "---"

if [[ "$STATUS" == *'"busy":true'* ]]; then
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
