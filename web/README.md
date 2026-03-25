# Web UI

PC Remote Power Controller の Web インターフェース。

静的 HTML ファイル1つで動作する。任意の Web サーバーでホスト可能。

## 起動方法

```bash
# Python
python3 -m http.server 8080 -d web/

# Node.js
npx serve web/
```

ブラウザで `http://<サーバーIP>:8080` にアクセスし、Pico W の IP アドレスを入力して接続。

## 注意

- Pico W の `server.py` に CORS 対応が必要（対応済み）
- IP アドレスは localStorage に保存され、次回アクセス時に自動接続される
