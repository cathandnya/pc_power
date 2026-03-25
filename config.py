# WiFi設定
WIFI_SSID = "YOUR_SSID"
WIFI_PASSWORD = "YOUR_PASSWORD"
WIFI_CONNECT_TIMEOUT = 10  # 秒
WIFI_RETRY_INTERVAL = 5  # 再接続間隔（秒）

# サーバー設定
SERVER_PORT = 80

# GPIOピン割り当て
PIN_POWER_SW = 16  # GP16 → パワースイッチヘッダー
PIN_RESET_SW = 17  # GP17 → リセットスイッチヘッダー
PIN_POWER_LED = 18  # GP18 → Power LEDヘッダー（入力）

# パルス時間（ミリ秒）
PULSE_POWER_ON = 500  # 電源ON: 短押し
PULSE_POWER_OFF = 5000  # 電源OFF: 長押し
PULSE_RESET = 500  # リセット

# 電源LED読み取り
POWER_LED_ACTIVE_HIGH = True  # Power LEDがHIGHでPC ON
