"""
使い方:
  $ python seed.py
"""
import uuid
from app import create_app, db
from models import Plan, Store, Sticker, PaymentFailCounter

def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # プラン
        p1 = Plan(name="Basic15", free_minutes=15, price_per_min=8.0)
        p2 = Plan(name="Cafe10", free_minutes=10, price_per_min=5.0)
        db.session.add_all([p1, p2]); db.session.commit()

        # 店舗
        s1 = Store(name="Ramen Underground Ginza", location="Ginza", plan_id=p1.id)
        s2 = Store(name="Basement Cafe Shibuya", location="Shibuya", plan_id=p2.id)
        db.session.add_all([s1, s2]); db.session.commit()

        # ステッカー（NFCタグ）
        t1 = Sticker(store_id=s1.id, tag_uid="TAG_GINZA")
        t2 = Sticker(store_id=s2.id, tag_uid="TAG_SHIBUYA")
        db.session.add_all([t1, t2]); db.session.commit()

        # 決済失敗カウンタ（デモ初期値）
        for st in (s1, s2):
            db.session.add(PaymentFailCounter(store_id=st.id, period="today", before_cnt=12, after_cnt=0))
        db.session.commit()

        print("Seed completed.")
        print("Try /api/nfc/resolve with tag: TAG_GINZA / TAG_SHIBUYA")

if __name__ == "__main__":
    main()
