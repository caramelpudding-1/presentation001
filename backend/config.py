import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'demo.sqlite3')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    # デモ換算: 3秒 = 1分
    HEARTBEAT_SECONDS_PER_METERED_MIN = int(os.getenv("HB_SECONDS_PER_MIN", 3))
    # デモ料金（seedでPlanに入れるがデフォルトも用意）
    DEFAULT_FREE_MINUTES = int(os.getenv("DEFAULT_FREE_MINUTES", 15))
    DEFAULT_PRICE_PER_MIN = float(os.getenv("DEFAULT_PRICE_PER_MIN", 8.0))
    # 収益配分
    STORE_SHARE = float(os.getenv("STORE_SHARE", 0.85))
