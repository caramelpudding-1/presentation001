## 起動手順

```shell

cd den-touchnet-demo/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# DB初期化 & サンプル投入
python seed.py

# 起動
python app.py
```



## 動作確認
```shell:動作確認

# NFCタグ解決
curl -s -X POST http://localhost:5001/api/nfc/resolve -H "Content-Type: application/json" -d '{"tag":"TAG_GINZA"}' | jq

# セッション開始
curl -s -X POST http://localhost:5001/api/session/start -H "Content-Type: application/json" -d '{"store_id":1,"sticker_id":1,"anon_id":"demo-visitor"}' | jq
# -> session_id を控える（例：1）

# 心拍（数回打つ: 3〜20回）
curl -s -X POST http://localhost:5001/api/session/heartbeat -H "Content-Type: application/json" -d '{"session_id":1}' | jq

# 閾値判定
curl -s "http://localhost:5001/api/user/prompt-register?session_id=1" | jq

# 仮登録
curl -s -X POST http://localhost:5001/api/register -H "Content-Type: application/json" -d '{"session_id":1,"email":"user@example.com"}' | jq

# 清算（台帳書き込み & 金額算出）
curl -s -X POST http://localhost:5001/api/depin/settle -H "Content-Type: application/json" -d '{"session_id":1}' | jq

# 店舗ダッシュボード
curl -s "http://localhost:5001/api/store/dashboard?store_id=1" | jq

# 台帳
curl -s "http://localhost:5001/api/admin/ledger" | jq
```