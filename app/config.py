# GPIO ピン割り当て
PIN_POWER_SW = 17   # 出力 → PWR_SW ヘッダー
PIN_RESET_SW = 27   # 出力 → RST_SW ヘッダー
PIN_POWER_LED = 22  # 入力 ← PWR_LED ヘッダー（分圧抵抗経由）
PIN_HDD_LED = 23    # 入力 ← HDD_LED ヘッダー（分圧抵抗経由）
PIN_SPEAKER = 24    # 入力 ← SPEAKER ヘッダー

# パルス時間（秒）
PULSE_POWER_ON = 0.5
PULSE_POWER_OFF = 5.0
PULSE_RESET = 0.5

# 監視ポーリング間隔（秒）
MONITOR_INTERVAL = 0.05  # 50ms

# サーバー設定
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080
