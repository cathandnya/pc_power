# Front Panel Bridge

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
| 抵抗 3.3kΩ | 2 | PWR_LED / HDD_LED 分圧（下側） |
| 抵抗 6.8kΩ | 2 | PWR_LED / HDD_LED 分圧（上側） |
| 抵抗 10kΩ | 1 | SPEAKER クランプ |
| ユニバーサル基板（小型） | 1 | 中継ボード・分圧回路 |

## GPIO 割り当て

| GPIO | Pin番号 | 方向 | 接続先 | 備考 |
|------|---------|------|--------|------|
| GPIO17 | 11 | 出力 | PWR_SW ヘッダー | 通常Hi-Z、操作時LOW |
| GPIO27 | 13 | 出力 | RST_SW ヘッダー | 通常Hi-Z、操作時LOW |
| GND | 14 | - | 共通GND | マザーボード各ヘッダーのGNDと共通 |
| GPIO22 | 15 | 入力 | PWR_LED ヘッダー | 分圧抵抗経由 |
| GPIO23 | 16 | 入力 | HDD_LED ヘッダー | 分圧抵抗経由 |
| GPIO24 | 18 | 入力 | SPEAKER ヘッダー | 10kΩクランプ経由（5V/3.3V両対応） |

## 回路図

![回路図](hardware/schematic.svg)

### 分圧回路（PWR_LED / HDD_LED 共通）

マザーボードのLEDヘッダーは5V出力の場合があるため、分圧抵抗でGPIOを保護する。

```
LED+ (5V) ── 6.8kΩ ──┬── GPIO (≈1.65V)
                      │
                    3.3kΩ
                      │
                     GND
```

### GND接続について

Zero W の GND とマザーボードの各ヘッダーの GND（PWR_SW-, RST_SW-, PWR_LED-, HDD_LED-, SPEAKER-）は**すべて共通**でなければならない。

ユニバーサル基板上で GND レールを1本作り、以下をすべて接続する:

- Zero W の GND ピン（Pin 6, 9, 14, 20, 25, 30, 34, 39 のいずれか）
- 分圧回路の 3.3kΩ 下端
- SPEAKER の 10kΩ クランプの GND 側
- マザーボード各ヘッダーの GND 側（デュポンケーブル経由）

## 配線

### 接続手順

1. **基板を製作**: ユニバーサル基板にピンヘッダーをはんだ付け（PWR_SW / RST_SW / HDD_LED 各2本、SPEAKER 2本）
2. **分圧回路を実装**: PWR_LED用・HDD_LED用の分圧回路を基板上にはんだ付け
3. **ケースのボタンを接続**: 電源ボタン・リセットボタンのコネクタをピンヘッダーに差し込む
4. **マザーボードと接続**: デュポンケーブルで基板からマザーボードの各ヘッダーへ接続
5. **Zero W と接続**: デュポンケーブルで基板から Zero W の各GPIOへ接続
6. **Zero W を給電**: マザーボード内部USBヘッダーから Zero W の PWR端子（OTG側ではない方）に接続

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

#### 分圧回路の確認（電圧モード）

ユニバーサル基板上の分圧回路にZero Wの5V（Pin 2）から入力し、中点の電圧を測定する。

| 入力 | 測定箇所 | 期待値 |
|------|---------|--------|
| Pin 2 (5V) → 6.8kΩ入力側 | 3.3kΩ上端（GPIO接続点） | ≈1.65V |

#### 入力ピンの確認（Web UI反映）

Zero Wでアプリを起動した状態で、Pin 2（5V）からジャンパー線で各入力回路にテスト信号を入れる。

| テスト | 方法 | 期待値 |
|--------|------|--------|
| PWR_LED | 5V → 分圧回路入力 → GPIO22 | Web UI の電源アイコン点灯 |
| HDD_LED | 5V → 分圧回路入力 → GPIO23 | Web UI のディスクアイコン点灯 |
| SPEAKER | 3.3V (Pin 1) → 10kΩ → GPIO24 | Web UI のビープアイコン点灯 |

#### 出力ピンの確認（電圧モード）

APIを叩きながら、マルチメーターでGPIOピンの電圧を測定する。

| 状態 | 測定 (GPIO ↔ GND) | 期待値 |
|------|-------------------|--------|
| 通常時 | GPIO17 | ハイインピーダンス（不安定な値） |
| `curl http://<IP>:8080/power/toggle` 中 | GPIO17 | ≈0V (LOW) |
| 通常時 | GPIO27 | ハイインピーダンス |
| `curl http://<IP>:8080/reset` 中 | GPIO27 | ≈0V (LOW) |

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

1. [xbar/fp-bridge.sh](xbar/fp-bridge.sh) の `BASE_URL` を自分の環境に合わせて変更
2. プラグインディレクトリにコピー（ファイル名でリフレッシュ間隔を指定、例: `.5s.` = 5秒）:
   ```bash
   # SwiftBar の場合
   cp xbar/fp-bridge.sh ~/Library/Application\ Support/SwiftBar/plugins/fp-bridge.5s.sh

   # xbar の場合
   cp xbar/fp-bridge.sh ~/Library/Application\ Support/xbar/plugins/fp-bridge.5s.sh
   ```
3. xbar / SwiftBar を起動

- メニューバー: 電源状態をアイコンの色で表示（緑=ON、グレー=OFF、赤=接続エラー）
- ドロップダウン: 電源 / HDD / ビープの詳細表示 + Power Toggle / Reset / Force OFF 操作

## 免責事項

- 本プロジェクトは個人の趣味・実験目的で作成したものです
- マザーボードやATX電源への接続は自己責任で行ってください。誤った配線はハードウェアの故障・破損・火災の原因となる可能性があります
- 本プロジェクトの使用によって生じたいかなる損害についても、作者は一切の責任を負いません
- 認証やアクセス制御は実装されていません。信頼できるネットワーク内でのみ使用してください

## ライセンス

MIT
