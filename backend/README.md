## 起動手順
cd den-touchnet-demo/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# DB初期化 & サンプル投入
python seed.py

# 起動
python app.py
