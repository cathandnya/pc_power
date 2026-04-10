#!/bin/bash
# <swiftbar.type>streamable</swiftbar.type>
# <xbar.title>Front Panel Bridge</xbar.title>

BASE_URL="http://<IP or hostname>:8080"

render() {
  local json="$1"
  [[ "$json" == *'"pc_power":true'* ]] && echo "⏻ | color=#4ade80" || echo "⏻ | color=#666666"
  echo "---"
  [[ "$json" == *'"pc_power":true'* ]] && echo "● ON | color=#4ade80" || echo "● OFF | color=#666666"
  [[ "$json" == *'"hdd_active":true'* ]] && echo "● HDD Active | color=#f59e0b" || echo "● HDD Idle | color=#444444"
  [[ "$json" == *'"beep":true'* ]] && echo "● BEEP | color=#f87171" || echo "● BEEP | color=#444444"
  [[ "$json" == *'"busy":true'* ]] && echo "⏳ Busy | color=#facc15"
  echo "---"
  if [[ "$json" == *'"busy":true'* ]]; then
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
}

# 初回表示 (~~~ なしで即表示)
PREV=$(curl -s --connect-timeout 3 --max-time 5 "${BASE_URL}/status" 2>/dev/null)
if [ -n "$PREV" ]; then
  render "$PREV"
else
  echo "⏻ ? | color=#f87171"
  echo "---"
  echo "接続できません | color=#f87171"
  PREV="error"
fi

# 状態が変わった時だけ ~~~ で更新
while true; do
  sleep 1
  STATUS=$(curl -s --connect-timeout 3 --max-time 5 "${BASE_URL}/status" 2>/dev/null)
  CURRENT="${STATUS:-error}"
  if [ "$CURRENT" != "$PREV" ]; then
    echo "~~~"
    if [ -n "$STATUS" ]; then
      render "$STATUS"
    else
      echo "⏻ ? | color=#f87171"
      echo "---"
      echo "接続できません | color=#f87171"
    fi
    PREV="$CURRENT"
  fi
done
