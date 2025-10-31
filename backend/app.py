import os
import uuid
from datetime import datetime
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, Store, Plan, Sticker, User, Device, Session, DepinLedger, EventLog, PaymentFailCounter
from config import Config
from depin import calc_settlement

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app, db)
    register_routes(app)
    return app

# --------- 共通ユーティリティ ---------
def ok(data=None, status=200):
    return jsonify({"ok": True, "data": data or {}}), status

def err(message="error", status=400):
    return jsonify({"ok": False, "error": message}), status

def get_json():
    try:
        return request.get_json(force=True) or {}
    except Exception:
        return {}

def get_or_create_anon_user(anon_id=None):
    if anon_id:
        u = User.query.filter_by(anon_id=anon_id).first()
        if u: return u
    # 新規作成
    new_anon = anon_id or uuid.uuid4().hex[:24]
    u = User(anon_id=new_anon)
    db.session.add(u); db.session.commit()
    return u

def log_event(session_id, typ, payload=None):
    ev = EventLog(session_id=session_id, type=typ, payload=str(payload or ""))
    db.session.add(ev); db.session.commit()

# --------- ルート定義 ---------
def register_routes(app: Flask):
    @app.get("/healthz")
    def health():
        return ok({"ts": datetime.utcnow().isoformat()})

    # NFCタグ → 店舗/ステッカー解決
    @app.post("/api/nfc/resolve")
    def nfc_resolve():
        body = get_json()
        tag = body.get("tag") or request.args.get("tag")
        if not tag:
            return err("tag is required")
        st = Sticker.query.filter_by(tag_uid=str(tag)).first()
        if not st or st.status != "active":
            return err("tag not found or inactive", 404)
        store = Store.query.get(st.store_id)
        plan = Plan.query.get(store.plan_id)
        return ok({
            "store_id": store.id,
            "store_name": store.name,
            "sticker_id": st.id,
            "plan": {"id": plan.id, "free_minutes": plan.free_minutes, "price_per_min": plan.price_per_min}
        })

    # セッション開始
    @app.post("/api/session/start")
    def session_start():
        body = get_json()
        store_id = body.get("store_id"); sticker_id = body.get("sticker_id")
        anon_id = body.get("anon_id")  # フロントでCookie代替など
        if not store_id or not sticker_id:
            return err("store_id and sticker_id required")
        user = get_or_create_anon_user(anon_id)
        sess = Session(user_id=user.id, store_id=store_id, sticker_id=sticker_id)
        db.session.add(sess); db.session.commit()
        log_event(sess.id, "session_start", {"store": store_id, "sticker": sticker_id})
        return ok({"session_id": sess.id, "anon_id": user.anon_id})

    # ハートビート（3秒=1分換算）
    @app.post("/api/session/heartbeat")
    def session_heartbeat():
        body = get_json()
        sid = body.get("session_id")
        if not sid:
            return err("session_id required")
        sess = Session.query.get(sid)
        if not sess:
            return err("session not found", 404)
        store = Store.query.get(sess.store_id)
        plan = Plan.query.get(store.plan_id)

        # デモ換算: 1ビート = 1メータ分
        sess.hb_ticks = (sess.hb_ticks or 0) + 1
        sess.metered_minutes = sess.metered_minutes + 1
        db.session.commit()

        # 登録促進の閾値判定
        should_prompt = sess.metered_minutes >= plan.free_minutes and not sess.registered_after_free
        remaining = max(plan.free_minutes - sess.metered_minutes, 0)
        log_event(sess.id, "heartbeat", {"used": sess.metered_minutes, "freeRemaining": remaining})
        return ok({
            "usedMinutes": sess.metered_minutes,
            "freeRemaining": remaining,
            "shouldPromptRegister": should_prompt
        })

    # 閾値到達か問い合わせ（フロントで定期確認したい場合）
    @app.get("/api/user/prompt-register")
    def prompt_register():
        sid = request.args.get("session_id")
        sess = Session.query.get(sid) if sid else None
        if not sess:
            return err("session not found", 404)
        store = Store.query.get(sess.store_id)
        plan = Plan.query.get(store.plan_id)
        should_prompt = sess.metered_minutes >= plan.free_minutes and not sess.registered_after_free
        return ok({"shouldPromptRegister": should_prompt})

    # 軽量登録（メール or ウォレット擬似）+ フラグ
    @app.post("/api/register")
    def register_user():
        body = get_json()
        sid = body.get("session_id")
        email = (body.get("email") or "").strip() or None
        wallet = (body.get("wallet_addr") or "").strip() or None
        if not sid:
            return err("session_id required")
        sess = Session.query.get(sid)
        if not sess:
            return err("session not found", 404)
        user = User.query.get(sess.user_id)
        # 既存ユーザにメール/ウォレットを付与（簡略）
        if email: user.email = email
        if wallet: user.wallet_addr = wallet
        sess.registered_after_free = True
        db.session.commit()
        log_event(sess.id, "user_register", {"email": email, "wallet": wallet})
        return ok({"user_id": user.id, "email": user.email, "wallet_addr": user.wallet_addr})

    # セッション終了 & 清算（DePIN疑似台帳へ書込）
    @app.post("/api/depin/settle")
    def depin_settle():
        body = get_json()
        sid = body.get("session_id")
        if not sid:
            return err("session_id required")
        sess = Session.query.get(sid)
        if not sess:
            return err("session not found", 404)
        store = Store.query.get(sess.store_id)
        plan = Plan.query.get(store.plan_id)

        res = calc_settlement(
            metered_minutes=sess.metered_minutes,
            free_minutes=plan.free_minutes,
            price_per_min=plan.price_per_min,
            store_share_rate=app.config["STORE_SHARE"]
        )
        # 台帳へ書込み
        ledger = DepinLedger(
            session_id=sess.id,
            minutes=res.minutes_billable,
            amount=res.amount,
            store_share=res.store_share,
            protocol_fee=res.protocol_fee,
        )
        sess.charge_amount = res.amount
        sess.ended_at = datetime.utcnow()
        db.session.add(ledger); db.session.commit()
        log_event(sess.id, "depin_settle", {
            "minutes_billable": res.minutes_billable,
            "amount": res.amount,
            "store_share": res.store_share,
            "protocol_fee": res.protocol_fee
        })

        # 効果演出：回避できた決済失敗数（簡易）を after_cnt に追加
        # 仮ルール: 課金対象分が1分以上発生したら after_cnt += 1
        if res.minutes_billable >= 1:
            pfc = PaymentFailCounter.query.filter_by(store_id=store.id, period="today").first()
            if pfc:
                pfc.after_cnt = (pfc.after_cnt or 0) + 1
                db.session.commit()

        return ok({
            "minutes_billable": res.minutes_billable,
            "amount": res.amount,
            "store_share": res.store_share,
            "protocol_fee": res.protocol_fee
        })

    # 手動クローズ（UI遷移時に呼ぶ想定。清算は別エンドポイント）
    @app.post("/api/session/close")
    def session_close():
        body = get_json()
        sid = body.get("session_id")
        if not sid:
            return err("session_id required")
        sess = Session.query.get(sid)
        if not sess:
            return err("session not found", 404)
        sess.ended_at = datetime.utcnow()
        db.session.commit()
        log_event(sess.id, "session_close", {})
        return ok({"ended_at": sess.ended_at.isoformat()})

    # 店舗ダッシュボード（今日の数字）
    @app.get("/api/store/dashboard")
    def store_dashboard():
        store_id = request.args.get("store_id", type=int)
        if not store_id:
            return err("store_id required")
        # セッション集計（簡易：当日分のみなどは省略）
        sessions = Session.query.filter_by(store_id=store_id).all()
        total_sessions = len(sessions)
        avg_stay = round(sum(s.metered_minutes for s in sessions) / total_sessions, 2) if total_sessions else 0.0
        total_amount = round(sum(s.charge_amount for s in sessions), 2) if total_sessions else 0.0

        pfc = PaymentFailCounter.query.filter_by(store_id=store_id, period="today").first()
        avoided = (pfc.after_cnt if pfc else 0)
        base_fail = (pfc.before_cnt if pfc else 0)
        return ok({
            "total_sessions": total_sessions,
            "avg_stay_minutes": avg_stay,
            "revenue_amount": total_amount,
            "payment_fail_avoided": avoided,
            "payment_fail_base": base_fail
        })

    # 管理者向け：台帳一覧（最新100）
    @app.get("/api/admin/ledger")
    def admin_ledger():
        recs = DepinLedger.query.order_by(DepinLedger.id.desc()).limit(100).all()
        data = [{
            "id": r.id, "session_id": r.session_id, "minutes": r.minutes, "amount": r.amount,
            "store_share": r.store_share, "protocol_fee": r.protocol_fee, "timestamp": r.timestamp.isoformat()
        } for r in recs]
        return ok({"records": data})

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)), debug=True)
