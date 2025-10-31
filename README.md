# 🛰️ Den-TouchNet Demo

> **“Tap to connect & pay — even underground.”**
> A proof-of-concept app that simulates **NFC → in-store Wi-Fi onboarding → free trial → gentle signup → DePIN-style metered settlement**.

---

## Overview

This demo turns your pitch deck into a clickable experience:

* **Tap an NFC sticker** (or click a test button) to “enter” the store’s Wi-Fi experience.
* Enjoy a **free trial (e.g., 15 min)**; after that, a **signup prompt** appears naturally.
* Usage is **metered** and written to a **DePIN-like ledger** with revenue split.
* A **store dashboard** shows sessions, estimated “failed-payment avoidance,” and revenue.

> Browser limitations mean we **emulate Wi-Fi connection**. On Android Chrome, Web NFC works with `NDEFReader`; on desktop, we provide QR/test buttons.

---

## Architecture

```
den-touchnet-demo/
├─ backend/     # Flask + SQLAlchemy + SQLite API
└─ frontend/    # Vue 3 + Vite + TypeScript (PWA-lite)
```

* **Frontend**: Vue 3 + Router + minimal PWA (service worker caching UI).
* **Backend**: Flask API with SQLite persistence; metering, settlement, and dashboards.
* **Data**: simple relational schema (Stores, Plans, Stickers, Sessions, Ledger…).

---

## Backend

### Files

```
backend/
├─ app.py          # Routes & endpoints
├─ models.py       # SQLAlchemy models
├─ depin.py        # Settlement logic (metering → amount → splits)
├─ seed.py         # DB bootstrap & sample data
├─ config.py       # Runtime config (free minutes, price/min, split %)
└─ requirements.txt
```

### Install & Run

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Initialize DB and seed sample data
python seed.py

# Start API
python app.py
# -> http://localhost:5001
```

### Configuration (env)

| Variable                |     Default | Meaning                                      |
| ----------------------- | ----------: | -------------------------------------------- |
| `DATABASE_URL`          | sqlite file | SQLAlchemy DB URL                            |
| `HB_SECONDS_PER_MIN`    |         `3` | Demo time scale (3 sec ≈ 1 metered “minute”) |
| `DEFAULT_FREE_MINUTES`  |        `15` | Fallback plan free minutes                   |
| `DEFAULT_PRICE_PER_MIN` |       `8.0` | Fallback price/min                           |
| `STORE_SHARE`           |      `0.85` | Store revenue share (85%)                    |

> If you serve the frontend from a different origin, enable CORS (e.g., add `flask-cors`).

### API Endpoints (selected)

| Method & Path                    | Purpose                                                |
| -------------------------------- | ------------------------------------------------------ |
| `POST /api/nfc/resolve`          | Map NFC tag UID → `{store, plan, sticker}`             |
| `POST /api/session/start`        | Start a session (creates anon user if needed)          |
| `POST /api/session/heartbeat`    | Meter usage (demo: +1 “minute” per call)               |
| `GET  /api/user/prompt-register` | Should we show the signup prompt now?                  |
| `POST /api/register`             | Attach email / wallet to user; mark signup             |
| `POST /api/depin/settle`         | Compute billable minutes & amounts; write ledger       |
| `POST /api/session/close`        | Mark session as ended (separate from settlement)       |
| `GET  /api/store/dashboard`      | Aggregates: sessions, avg stay, revenue, avoided fails |
| `GET  /api/admin/ledger`         | Last 100 ledger rows                                   |

### Data Model (minimal)

* **Store(id, name, location, plan_id)**
* **Plan(id, name, free_minutes, price_per_min)**
* **Sticker(id, store_id, tag_uid, status)**
* **User(id, anon_id, email, wallet_addr, created_at)**
* **Device(id, user_id, ua_fingerprint, created_at)**
* **Session(id, user_id, store_id, sticker_id, started_at, ended_at, metered_minutes, charge_amount, registered_after_free, hb_ticks)**
* **DepinLedger(id, session_id, minutes, amount, store_share, protocol_fee, timestamp)**
* **PaymentFailCounter(id, store_id, period, before_cnt, after_cnt)**
* **EventLog(id, session_id, type, payload, ts)**

### Settlement Logic (`depin.py`)

```python
billable = max(0, metered_minutes - free_minutes)
amount = round(billable * price_per_min, 2)
store_share = round(amount * STORE_SHARE, 2)
protocol_fee = round(amount - store_share, 2)
```

---

## Frontend

### Files

```
frontend/
├─ index.html
├─ public/
│  └─ sw.js                 # Simple cache for UI shell
├─ src/
│  ├─ main.ts
│  ├─ router.ts
│  ├─ api/index.ts          # API client (BASE defaults to http://localhost:5001)
│  ├─ components/
│  │  ├─ SignalAnim.vue
│  │  └─ FreeTimer.vue
│  └─ pages/
│     ├─ Tap.vue            # Web NFC / test buttons
│     ├─ Wifi.vue           # Heartbeat, free-time meter, prompt logic
│     ├─ Register.vue       # Email/Wallet signup
│     ├─ PayResult.vue      # Before/After & settlement summary
│     ├─ store/Dashboard.vue
│     └─ admin/Ledger.vue
├─ package.json
├─ tsconfig.json
└─ vite.config.ts
```

### Install & Run

```bash
cd frontend
npm install
npm run dev
# -> http://localhost:5173
```

> Change API base via `VITE_API_BASE` or edit `src/api/index.ts`.

### Route Flow

1. **`/` (Tap)**

   * Use Web NFC (Android Chrome) or click **Ginza/Shibuya** test buttons.
   * Resolves tag → starts session → redirects to `/wifi`.
2. **`/wifi`**

   * Sends `heartbeat` every 3s (demo scale) to increase metered minutes.
   * When free minutes are consumed, shows **signup card**.
3. **`/register`**

   * Minimal signup (email and/or wallet). Returns to `/wifi`.
4. **Finish & Settle**

   * Calls `/api/depin/settle` → `/pay-result` with settlement summary.
5. **Dashboards**

   * `/store/dashboard?store_id=1` and `/admin/ledger`.

### PWA Note

A tiny service worker caches the app shell so UI remains visible offline (network calls still require connectivity).

---

## Seed Data

After running `python seed.py`:

| Store                   | NFC Tag       |        Plan | Price/min |
| ----------------------- | ------------- | ----------: | --------: |
| Ramen Underground Ginza | `TAG_GINZA`   | free 15 min |        ¥8 |
| Basement Cafe Shibuya   | `TAG_SHIBUYA` | free 10 min |        ¥5 |

---

## End-to-End Demo (90-second script)

1. Open **Frontend** → **Tap** page. Click **Ginza** (or scan NFC on Android Chrome).
2. Redirects to **Wifi**; watch free minutes count down (3s ≈ 1 min).
3. After free time, a **signup card** appears → register with an email.
4. Click **Finish & Settle** → see **PayResult** (billable minutes, amount, splits).
5. Open **Store Dashboard** and **Admin Ledger** to confirm metrics and ledger entries.

---

## Why This Demo Works in a Pitch

* **Frictionless start**: “Tap once, you’re in” — easy to grasp and to show live.
* **Value before signup**: Free minutes create positive bias, then a soft prompt.
* **Transparent economics**: DePIN-like ledger spells out revenue and fees.
* **Merchant value**: “Avoided payment failures” metric highlights ROI.

---

## Extending the Demo

* Tokenize a portion of `protocol_fee` as **rewards** (DePIN incentive loop).
* Add **Bluetooth Beacon** fallback.
* Integrate real **payment gateways** (e.g., Stripe) for topping up time.
* Export **CSV** from admin and store views.
* CLI for **NFC provisioning** workflows.

---

## License

MIT License — For demo purposes.
© 2025 FICY Tech / Den-TouchNet Demo
