from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------- テーブル定義 ----------
class Store(db.Model):
    __tablename__ = "stores"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    location = db.Column(db.String(255))
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    stickers = db.relationship("Sticker", backref="store", lazy=True)

class Plan(db.Model):
    __tablename__ = "plans"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    free_minutes = db.Column(db.Integer, nullable=False, default=15)
    price_per_min = db.Column(db.Float, nullable=False, default=8.0)
    stores = db.relationship("Store", backref="plan", lazy=True)

class Sticker(db.Model):
    __tablename__ = "stickers"
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)
    tag_uid = db.Column(db.String(128), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="active")  # active, inactive, lost

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    anon_id = db.Column(db.String(64), unique=True, index=True)  # 初回は匿名ID
    email = db.Column(db.String(160), unique=True, index=True)
    wallet_addr = db.Column(db.String(160), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    devices = db.relationship("Device", backref="user", lazy=True)
    sessions = db.relationship("Session", backref="user", lazy=True)

class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    ua_fingerprint = db.Column(db.String(160), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))
    sticker_id = db.Column(db.Integer, db.ForeignKey("stickers.id"))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    metered_minutes = db.Column(db.Integer, default=0)
    charge_amount = db.Column(db.Float, default=0.0)
    registered_after_free = db.Column(db.Boolean, default=False)
    hb_ticks = db.Column(db.Integer, default=0)  # 何回ハートビートを受信したか（デモ用）

class DepinLedger(db.Model):
    __tablename__ = "depin_ledger"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"))
    minutes = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    store_share = db.Column(db.Float, nullable=False)
    protocol_fee = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PaymentFailCounter(db.Model):
    __tablename__ = "payment_fail_counter"
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))
    period = db.Column(db.String(32), nullable=False, default="today")  # today, week, month（デモ簡略）
    before_cnt = db.Column(db.Integer, default=0)
    after_cnt = db.Column(db.Integer, default=0)

class EventLog(db.Model):
    __tablename__ = "event_logs"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"))
    type = db.Column(db.String(64), nullable=False)
    payload = db.Column(db.Text)
    ts = db.Column(db.DateTime, default=datetime.utcnow)

# ---------- ヘルパ ----------
def now():
    return datetime.utcnow()
