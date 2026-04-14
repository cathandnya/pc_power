# Front Panel Bridge

[![YouTube](https://github.com/user-attachments/assets/b789b4b5-9caa-4e29-9ad1-6dc0b42ab799)](https://youtu.be/C-dJnxJGRUc)

Raspberry Pi Zero W を使って、マザーボードのフロントパネルピンヘッダーを無線化するデバイス。

PC電源のON/OFF/リセットをリモート操作し、電源状態・ディスクアクセス・ビープ音をWebSocketでリアルタイム配信する。Web UIとREST APIの両方に対応。

## 機能

| 機能 | 方向 | 方式 |
|------|------|------|
| 電源 ON/OFF | 制御 | REST API / Web UI |
| リセット | 制御 | REST API / Web UI |
| 電源状態 (PWR_LED) | 監視 | WebSocket リアルタイム |
| ディスクアクセス (HDD_LED) | 監視 | WebSocket リアルタイム |
| ビープ音 (SPEAKER) | 監視 | WebSocket リアルタイム |

## 部品リスト

| 部品 | 数量 | 用途 |
|------|------|------|
| Raspberry Pi Zero W | 1 | メインボード |
| microSD カード | 1 | Raspberry Pi OS |
| USB内部ケーブル | 1 | MB内部USBヘッダー → Zero W PWR端子 |
| デュポンケーブル（メス-メス）| 10本 | Zero W ↔ 基板 ↔ マザーボード |
| ピンヘッダー 2.54mm（オス）| 10本 | 基板上の中継端子 |
| フォトカプラ PC817 | 5 | 全 5 系統（PWR_SW/RST_SW/PWR_LED/HDD_LED/SPEAKER）の絶縁 |
| 抵抗 330Ω | 2 | PWR_SW/RST_SW 側 PC817 LED 電流制限 |
| 抵抗 1kΩ | 3 | PWR_LED/HDD_LED/SPEAKER 側 PC817 LED 電流制限 |
| 抵抗 10kΩ | 3 | PWR_LED/HDD_LED/SPEAKER 側 Pi プルダウン |
| ユニバーサル基板（小型） | 1 | 中継ボード |

## GPIO 割り当て

全 5 系統とも PC817 フォトカプラで絶縁されている。Pi 側の接続先はすべてフォトカプラの 2 次側（MB GND には触れない）。

| GPIO | Pin番号 | 方向 | 接続先 | 備考 |
|------|---------|------|--------|------|
| GPIO17 | 11 | 出力 | PC817 (PWR_SW) Pin2 | 通常HIGH、操作時LOW。Pin1は330Ω経由で3.3V |
| GPIO27 | 13 | 出力 | PC817 (RST_SW) Pin2 | 通常HIGH、操作時LOW。Pin1は330Ω経由で3.3V |
| GPIO22 | 15 | 入力 | PC817 (PWR_LED) Pin3 | 10kΩ で Pi GND へプルダウン、Pin4 は 3.3V へ |
| GPIO23 | 16 | 入力 | PC817 (HDD_LED) Pin3 | 同上 |
| GPIO24 | 18 | 入力 | PC817 (SPEAKER) Pin3 | 同上 |
| 3.3V | 1 | - | 各 PC817 の 2 次側電源 | スイッチ側は Pin1(330Ω経由)、入力側は Pin4 |
| GND | 14 | - | Pi 側 GND | **MB GND とは完全分離** |

## 回路図

![回路図](hardware/schematic.svg)

### 完全絶縁（全 5 系統 PC817）

Zero W 故障時にマザーボードを巻き添えにしないよう、フロントパネルとやり取りする全信号をフォトカプラ PC817 で絶縁する。Pi GND と MB GND は一切接続せず、光結合のみで信号が渡る。

#### スイッチ系（PWR_SW / RST_SW）: Pi → MB

```
Pi 3.3V ──[330Ω]── Pin1 (LED A)
                                           PWR_SW+ / RST_SW+ (MB)
                                                  │
GPIO17/27 ────────  Pin2 (LED K)      Pin4 ───────┤
                                                  │
                      ≋≋ 光結合 ≋≋           物理ボタン(任意)
                                                  │
                                       Pin3 ──────┤
                                                  │
                                               MB GND
```

PC817 の 2 次側（Pin4 ↔ Pin3）と物理ボタンが **PWR_SW+ と MB GND の間に並列** に入る。GPIO を `OUTPUT HIGH` で待機し、押下時のみ `OUTPUT LOW` にすると 1 次側 LED に電流が流れ、2 次側が導通して PWR_SW+ が MB GND へ短絡される（GPIO=LOW=押下）。

#### 入力系（PWR_LED / HDD_LED / SPEAKER）: MB → Pi

```
Pi 3.3V ────────  Pin4 (C)          Pin1 (LED A) ──[1kΩ]── PWR_LED+ / HDD_LED+ / SPEAKER+ (MB, 5V)
                                                                         
GPIO22/23/24 ──┬  Pin3 (E)          Pin2 (LED K) ───────── MB GND
               │
            [10kΩ]       ≋≋ 光結合 ≋≋
               │
             Pi GND
```

マザーボード側が点灯・鳴動（5V出力）すると 1 次側 LED が光り、2 次側が導通して Pi 3.3V が GPIO に流れ込み **GPIO=HIGH** になる。マザボ側 OFF 時は 10kΩ プルダウンで **GPIO=LOW**。現状のファームは `pull_up=False`（HIGH=アクティブ）で動いているため、論理が一致しコード変更不要。

SPEAKER のビープ信号は数百Hz〜数kHzの矩形波で、PC817 の応答速度（数十µs）でも追従可能。

### GND 接続について

Pi GND と MB GND は **基板上でも経路上でも一切接続しない**。全 5 系統の信号はフォトカプラの光結合のみで渡る。

**Pi GND**（Zero W 側）
- Zero W の GND ピン（Pin 6, 9, 14, 20, 25, 30, 34, 39 のいずれか）
- 入力系 PC817 (×3) の Pin3 に繋がる 10kΩ プルダウンの下端

**MB GND**（マザーボード側）
- スイッチ系 PC817 (×2) の Pin3（Emitter）
- 入力系 PC817 (×3) の Pin2（1 次側 LED K）
- 物理ボタン（PWR BTN / RST BTN）の GND 側
- マザーボードのフロントパネル PWR_SW- / RST_SW- / PWR_LED- / HDD_LED- / SPEAKER- ヘッダー

ユニバーサル基板上で Pi GND レールと MB GND レールを物理的に分けて配線する。両者を結ぶ配線・ジャンパ・GND プレーンは一切設けないこと。

## 配線

### 接続手順

1. **基板を製作**: ユニバーサル基板にピンヘッダーをはんだ付け。Pi GND レールと MB GND レールを**物理的に分離**して配置
2. **スイッチ系 PC817 を実装**: PWR_SW 用・RST_SW 用に PC817 を 2 個、1 次側に 330Ω を直列配置（Pi 3.3V → 330Ω → Pin1, Pin2 → GPIO）
3. **入力系 PC817 を実装**: PWR_LED / HDD_LED / SPEAKER 用に PC817 を 3 個、1 次側に 1kΩ を直列配置（MB LED+ → 1kΩ → Pin1, Pin2 → MB GND）、2 次側は Pin4 → Pi 3.3V, Pin3 → GPIO + 10kΩ プルダウン → Pi GND
4. **ケースのボタンを接続**: 電源ボタン・リセットボタンのコネクタをスイッチ系 PC817 の 2 次側（MB GND 側）のピンヘッダーに差し込む
5. **マザーボードと接続**: デュポンケーブルで基板からマザーボードの各ヘッダーへ接続（PWR_SW/RST_SW/LED/SPEAKER + 各 MB GND）
6. **Zero W と接続**: デュポンケーブルで基板から Zero W の各 GPIO / 3.3V / Pi GND へ接続
7. **Zero W を給電**: マザーボード内部USBヘッダーから Zero W の PWR端子（OTG側ではない方）に接続

### 給電について

マザーボード内部USBヘッダーから給電する。BIOSで **USB Standby Power** を有効にすれば、PCシャットダウン中もZero Wが動作し続ける。

- BIOS設定例: 「USB Standby Power」「USB Power in S5」「ErP Ready → Disabled」
- メーカーにより設定名が異なる

## セットアップ

### 1. Raspberry Pi OS のインストール

1. [Raspberry Pi Imager](https://www.raspberrypi.com/software/) で microSD に **Raspberry Pi OS Lite (32-bit, Bookworm)** を書き込む（Zero WはARMv6のため64-bit非対応）
2. Imager の設定で WiFi・SSH を有効化
3. microSD を Zero W に挿入、USBで給電して起動

### 2. アプリのインストール

```bash
git clone https://github.com/cathandnya/pc_power.git
cd pc_power
./install.sh
```

### 3. マザーボード接続前のテスト

マルチメーターを使って、マザーボードに接続する前に各回路を検証する。

#### 入力系 PC817 の確認（Web UI反映）

Zero Wでアプリを起動した状態で、マザーボード側 PC817 の 1 次側（LED+ 相当の入力）に Pi の 5V（Pin 2）をジャンパー線で当てる。1 次側 LED が光り、2 次側を通じて GPIO が HIGH になれば OK。

| テスト | 方法 | 期待値 |
|--------|------|--------|
| PWR_LED | Pin 2 (5V) → PC817 (PWR_LED) 1kΩ 入力側 | Web UI の電源アイコン点灯 |
| HDD_LED | Pin 2 (5V) → PC817 (HDD_LED) 1kΩ 入力側 | Web UI のディスクアイコン点灯 |
| SPEAKER | Pin 2 (5V) → PC817 (SPEAKER) 1kΩ 入力側 | Web UI のビープアイコン点灯 |

注意: PC817 の 1 次側に Pi 5V を直接入れる場合、その瞬間だけ Pi GND と MB GND を繋ぐ形になる。テスト用途の割り切り接続として行い、終わったらジャンパーを外す。

#### 出力ピンの確認（導通モード）

PC817 を介しているため GPIO の電圧ではなく、**2 次側（PWR_SW+ ↔ MB GND）の導通**をマルチメーターで確認する。

| 状態 | 測定 (PWR_SW+ ↔ MB GND) | 期待値 |
|------|-------------------------|--------|
| 通常時 | PC817 Pin4 ↔ Pin3 | 開放（∞Ω） |
| `curl http://<IP>:8080/power/toggle` 中 | PC817 Pin4 ↔ Pin3 | 導通（数百Ω以下） |
| 通常時 | RST_SW+ 側 Pin4 ↔ Pin3 | 開放 |
| `curl http://<IP>:8080/reset` 中 | RST_SW+ 側 Pin4 ↔ Pin3 | 導通 |

GPIO 側（1次側）の電圧を測る場合は、GPIO17/27 と **Pi GND** の間で測る（MB GND ではない）。通常時は ≈3.3V (HIGH)、操作時は ≈0V (LOW)。

#### テスト手順まとめ

1. Zero W にOS + アプリをインストール、起動
2. ブラウザで `http://<IP>:8080` にアクセスして Web UI 表示を確認
3. 分圧回路の出力電圧をマルチメーターで確認
4. 3.3V ピンから入力して Web UI のインジケーターが反応するか確認
5. API を叩いて GPIO17/27 が LOW になるかマルチメーターで確認
6. すべて OK ならマザーボードに接続

### 4. 動作確認

ブラウザで `http://<Zero W の IP>:8080` にアクセス。

## Web UI

Zero W 上で Web UI が直接ホストされる。別サーバー不要。

- 電源状態・ディスクアクセス・ビープ音をリアルタイム表示
- Power ON / Power OFF / Reset ボタン
- WebSocket で自動更新（ポーリング不要）

## REST API

### GET /status

```bash
curl http://<IP>:8080/status
```

```json
{"pc_power": true, "hdd_active": false, "beep": false, "busy": false}
```

### GET /power/on

```bash
curl http://<IP>:8080/power/on
```

```json
{"status": "power_on_sent", "pc_power": true}
```

### GET /power/off

```bash
curl http://<IP>:8080/power/off
```

### GET /power/toggle

```bash
curl http://<IP>:8080/power/toggle
```

### GET /reset

```bash
curl http://<IP>:8080/reset
```

## WebSocket

`ws://<IP>:8080/ws` に接続すると、GPIO状態が変化するたびにJSONが配信される。

```json
{"pc_power": true, "hdd_active": true, "beep": false, "busy": false}
```

## iOS ショートカット

| 操作 | URL | メソッド |
|------|-----|----------|
| 電源ON | `http://<IP>:8080/power/on` | GET |
| 電源OFF | `http://<IP>:8080/power/off` | GET |
| リセット | `http://<IP>:8080/reset` | GET |
| 状態確認 | `http://<IP>:8080/status` | GET |

## Scriptable ウィジェット

[Scriptable](https://scriptable.app/) を使って iOS ホーム画面にウィジェットを追加できる。

1. Scriptable アプリで新規スクリプトを作成
2. [scriptable/FPBridge.js](scriptable/FPBridge.js) の内容をコピペ
3. ホーム画面を長押し → + → Scriptable → 小ウィジェットを追加
4. ウィジェットを長押し → 編集 → Script: **FPBridge** を選択

- ウィジェット: 電源状態・HDD・ビープを表示、タップで電源トグル
- アプリ内実行: ステータス表示 + 操作ボタン

## macOS メニューバー (xbar / SwiftBar)

[xbar](https://xbarapp.com/) または [SwiftBar](https://github.com/swiftbar/SwiftBar) を使って macOS メニューバーに PC 電源状態を表示できる。

1. [xbar/fp-bridge.sh](xbar/fp-bridge.sh) 先頭の `DEFAULT_BASE_URL` を自分の環境に合わせて変更する
   - SwiftBar のプラグイン環境変数 `FP_BRIDGE_BASE_URL` で上書きしてもよい
2. SwiftBar で使う場合は、WebSocket 用 Python 環境 (`websockets` パッケージ入り) を見つけやすいように**シンボリックリンク**を推奨:
   ```bash
   ln -sf /absolute/path/to/pc_power/xbar/fp-bridge.sh \
     ~/Library/Application\ Support/SwiftBar/plugins/fp-bridge.sh
   ```
   - コピーして使う場合は `FP_BRIDGE_ROOT=/absolute/path/to/pc_power` または `FP_BRIDGE_PYTHON=/absolute/path/to/pc_power/.venv/bin/python` を SwiftBar 側で設定する
   - SwiftBar では streamable plugin として動くため、`.5s.sh` のようなリフレッシュ間隔付きファイル名は不要
3. xbar で使う場合は従来どおりコピーする:
   ```bash
   cp xbar/fp-bridge.sh ~/Library/Application\ Support/xbar/plugins/fp-bridge.5s.sh
   ```
4. xbar / SwiftBar を起動

- SwiftBar: `/ws` を購読して状態変化時に即時更新
- xbar: 単発表示にフォールバック（WebSocket 常駐更新なし）
- メニューバー: 電源状態をアイコンの色で表示（緑=ON、グレー=OFF、赤=接続エラー）
- ドロップダウン: 電源 / HDD / ビープの詳細表示 + Power Toggle / Reset / Force OFF 操作

## 免責事項

- 本プロジェクトは個人の趣味・実験目的で作成したものです
- マザーボードやATX電源への接続は自己責任で行ってください。誤った配線はハードウェアの故障・破損・火災の原因となる可能性があります
- 本プロジェクトの使用によって生じたいかなる損害についても、作者は一切の責任を負いません
- 認証やアクセス制御は実装されていません。信頼できるネットワーク内でのみ使用してください

## ライセンス

MIT
