#!/usr/bin/env python3
"""intraday_price_watch.py — cổng giá TRONG PHIÊN + quy trình điều tra + cutloss tự động (SHADOW).

Đặc tả = plan user ĐÃ DUYỆT `kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md`
(Q1 + "Chiến lược cutloss đề xuất" + "4 chế độ" + duyệt 01:12/01:54 ICT 06/10). Logic thuần ở
`bin/intraday_cutloss_engine.py`; file này chỉ là I/O.

⚠️ SHADOW ONLY (job Taylor_20261005_185546): KHÔNG đặt/huỷ/sửa lệnh thật. DNSE chỉ được gọi qua
`ReadOnlyDNSE` (whitelist inquiry: secdef/latest_trade/latest_quote/positions/orders/ohlc) — gọi
bất kỳ hàm nào khác ném PermissionError. "Lệnh bán dự định" / "lệnh mua sẽ hoãn" chỉ GHI LOG
(`data/intraday_watch/shadow_<ngày>.jsonl`) + báo. Không ghi vào `dnse_raw_*.jsonl` (file kế toán
dùng chung, §12) — cố ý không dùng `DNSEBroker.get_quote()` vì nó log vào đó.

Nhịp: cron MỖI PHÚT 09:00-14:59 ICT T2-T6 (dòng đề xuất ở cuối docstring); script tự quyết:
  - QUÉT vũ trụ 15'/lần trong [09:15, 14:30] (bỏ nghỉ trưa).
  - Ca đang mở: mỗi phút — phán quyết/hạn chót/trả lời user/bộ máy bán.
Vũ trụ = vị thế LIVE 2 TK (DNSE positions) + mã có lệnh MUA trong plan hôm nay + watchlist
discretionary (state_*_<TK>.json + excluded_tickers + data/intraday_watch/watchlist.json).

Nguồn giờ: `trading_bot.vn_market.now_ict()` (§16). Tiền: chỉ dùng `total_nav` của
`active_nav_<TK>.json` làm MẪU SỐ HIỂN THỊ %NAV (ghi rõ computed_at) — không đọc field tiền broker
(§25). Same-day giá = DNSE, không BQ (§6). Đọc trả lời user: ccdb `/api/threads/<trading_daily>/
messages` (chỉ tin không phải bot, đúng mã).

Idempotency (§5): state ghi nguyên tử (tmp + os.replace); không tác động ngoài nào chạy trước khi
ý định của nó đã nằm trên đĩa.
  - Báo (Discord/Telegram/email): HỘP THƯ ĐI bền (`st["outbox"]`). Mỗi tin được XẾP HÀNG + ghi đĩa
    TRƯỚC khi gửi; gửi xong kênh nào gạch kênh đó + ghi đĩa. Bị kill giữa chừng (vd `timeout 55`)
    ⇒ lượt sau gửi nốt ⇒ at-least-once THẬT (có thể lặp 1 lần đúng kênh đang gửi dở; không mất).
    Kênh lỗi thử lại tối đa NOTIFY_MAX_ATTEMPTS lượt, rồi cảnh báo qua kênh còn sống.
  - Tin T0 không gửi lúc mở ca mà sau bước dispatch, để nội dung nói ĐÚNG trạng thái điều tra
    (đang điều tra / KHÔNG có điều tra vì …). Cờ `t0_pending` trên đĩa ⇒ kill ở bất kỳ đâu giữa
    "mở ca" và "xếp tin T0" thì lượt sau vẫn xếp tin T0.
  - Dispatch điều tra: at-most-once — ghi `dispatch_attempted_at` TRƯỚC khi gọi; lượt sau thấy cờ
    mà không có job ⇒ KHÔNG dispatch lại, ghi chú "không xác nhận được", báo user trong tin T0.
  - Ngân sách thời gian mỗi lượt RUN_BUDGET_S (< `timeout 55` của cron): hết ngân sách ⇒ dừng việc
    ngoài còn lại, để lượt sau làm tiếp (cờ trên đĩa).

Danh tính dispatch: DISPATCH_FROM=intraday_watch (KHÔNG phải tên agent ⇒ không dính chặn
self-dispatch của dispatch.sh, không sinh auto-callback). `--retries 0` + trần mỗi lượt/mỗi ngày +
dừng dispatch tới hết ngày sau 1 điều tra hết giờ ⇒ nguồn này không tự làm vấp circuit breaker
Taylor (ngưỡng 3 lỗi liên tiếp) của cả fleet.

MẶC ĐỊNH AN TOÀN r2 (hằng số đầu file + engine, CHỜ USER CHỐT): (a) không có phán quyết của agent
⇒ GIỮ + cảnh báo lớn (engine.NON_AGENT_DEFAULT); (b) mã excluded_tickers / restricted.json ⇒ chỉ báo
+ điều tra, không tự bán; (c) kích hoạt ≥ 14:00 hoặc hạn trả lời > 14:15 ⇒ mặc định chỉ áp từ 09:15
phiên sau, 08:30 nhắc lại; (d) log song song ngưỡng tương đối theo biên độ sàn (không hành động).
Trả lời user trong shadow PHẢI có tiền tố: "SHADOW GIỮ PNJ" / "SHADOW BÁN PNJ" / "SHADOW BÁN 50% PNJ".

Dùng:
  intraday_price_watch.py run [--no-dispatch] [--dry-notify] [--state-dir D]
  intraday_price_watch.py verdict --date YYYY-MM-DD --ticker XXX --label BROKEN|NOISE|UNCLEAR --summary "..."
  intraday_price_watch.py status [--date YYYY-MM-DD]

Cron ĐỀ XUẤT (KHÔNG tự cài; crontab host parse giờ UTC: 02-07 ⇔ 09-14 ICT, 1:30 ⇔ 08:30 ICT):
  * 2-7 * * 1-5 cd /home/trido/thanhdt/WorkingClaude && TZ=Asia/Ho_Chi_Minh timeout 55 /home/trido/thanhdt/wc_venv/bin/python mike/bin/intraday_price_watch.py run >> mike/logs/intraday_price_watch.log 2>&1
  30 1 * * 1-5 cd /home/trido/thanhdt/WorkingClaude && TZ=Asia/Ho_Chi_Minh timeout 55 /home/trido/thanhdt/wc_venv/bin/python mike/bin/intraday_price_watch.py run >> mike/logs/intraday_price_watch.log 2>&1
  (dòng 2 = nhắc 08:30 cho ca hoãn qua đêm; script tự nhận cửa sổ 08:25-08:59 = chỉ nhắc)
"""

import argparse
import datetime as dt
import fcntl
import json
import os
import subprocess
import sys
import time
import traceback
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE) if os.path.basename(HERE) == "bin" else HERE
WC = "/home/trido/thanhdt/WorkingClaude"
MIKE = os.path.join(WC, "mike")
sys.path.insert(0, WC)
sys.path.insert(0, HERE)

import intraday_cutloss_engine as E  # noqa: E402

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
STATE_DIR = os.path.join(WC, "data", "intraday_watch")
PLANS_DIR = os.path.join(WC, "data", "trade_plans")
DISC_DIR = os.path.join(PLANS_DIR, "discretionary")
NAV_DIR = os.path.join(WC, "data", "execution_logs")
ACCOUNTS_FILE = os.path.join(WC, "secrets", "trading_bot_accounts.json")
BOT_STOP = os.path.join(WC, "data", "BOT_STOP")
CHANNELS = os.path.join(MIKE, "kb", "discord_channels.json")
NOTIFY_THREAD = os.path.join(MIKE, "bin", "notify_thread.sh")
NOTIFY_TG = os.path.join(MIKE, "bin", "notify_telegram.sh")
EMAIL = os.path.join(MIKE, "bin", "send_macro_note_email.py")
DISPATCH = os.path.join(MIKE, "bin", "dispatch.sh")
CCDB = "http://127.0.0.1:8199"
WATCH_ACCOUNTS = ("SpaceX", "ZaloPay")
SCAN_START, SCAN_END = dt.time(9, 15), dt.time(14, 30)
SCAN_EVERY_MIN = 15
TAG = "[SHADOW]"
TERMINAL = ("DONE", "NO_POSITION")       # HOLD KHÔNG terminal: vẫn đọc trả lời user tới hết ngày
JOBS_DIR = os.path.join(MIKE, "bus", "jobs")
DISPATCH_FROM_ID = "intraday_watch"      # KHÔNG phải tên agent (xem docstring)
JOB_DEAD = ("failed", "timeout", "usage_limited", "cancelled", "orphaned", "done")

# ---- vận hành / mặc định an toàn r2 (cấu hình được — CHỜ USER CHỐT) ----
MAX_DISPATCH_PER_SCAN = 2          # điều tra tối đa mỗi lượt quét (ưu tiên vị thế lớn)
MAX_DISPATCH_PER_DAY = 3           # điều tra tối đa mỗi ngày
STOP_DISPATCH_AFTER_TIMEOUT = True # 1 điều tra hết giờ/hỏng không phán quyết ⇒ dừng dispatch tới hết ngày
DISPATCH_SUBPROC_TIMEOUT = 25      # giây chờ dispatch.sh --bg trả job id
RUN_BUDGET_S = 40                  # ngân sách mỗi lượt (< timeout 55 của cron)
NOTIFY_MAX_ATTEMPTS = 5
LATE_TRIGGER = dt.time(14, 0)      # (c) kích hoạt từ giờ này ⇒ quyết định cho phiên sau
NO_EOD_DEFAULT_AFTER = dt.time(14, 15)   # hạn trả lời sau giờ này ⇒ mặc định áp 09:15 phiên sau
NEXT_SESSION_APPLY = dt.time(9, 15)
REMINDER_WINDOW = (dt.time(8, 25), dt.time(9, 0))
EOD_SUMMARY_AT = dt.time(14, 50)
QUOTE_ERR_ALERT = 0.5              # tỉ lệ lỗi lấy giá trong 1 lượt quét ⇒ cảnh báo sức khoẻ
HEALTH_ALERT_EVERY_MIN = 60        # cảnh báo sức khoẻ cùng loại tối đa 1 lần/60'
VNI_MAX_AGE_MIN = 5                # bar VNINDEX cuối cũ hơn ⇒ coi như không đọc được (DNSE cache theo URL)
REPLY_PREFIX = E.REPLY_PREFIX_SHADOW
SHADOW_NOTE = "ĐÂY LÀ CHẠY THỬ (SHADOW), KHÔNG CÓ LỆNH THẬT"
NO_CARRY = TERMINAL + ("HOLD",)          # sang phiên mới: ca HOLD đóng, mã được kích hoạt lại


# ============================================================== DNSE chỉ-đọc
class ReadOnlyDNSE:
    """Proxy whitelist quanh DNSEClient — cơ chế cứng của "SHADOW ONLY"."""
    ALLOWED = frozenset({"secdef", "latest_trade", "latest_quote", "positions", "orders", "ohlc"})

    def __init__(self, client):
        object.__setattr__(self, "_c", client)

    def __getattr__(self, name):
        if name not in ReadOnlyDNSE.ALLOWED:
            raise PermissionError(f"intraday_price_watch SHADOW: cấm gọi DNSE.{name}")
        return getattr(object.__getattribute__(self, "_c"), name)

    def __setattr__(self, name, value):
        raise PermissionError("ReadOnlyDNSE bất biến")


def _now():
    from trading_bot.vn_market import now_ict
    return now_ict()


def _iso(t):
    return t.isoformat(timespec="seconds") if t else None


def _p(s):
    return dt.datetime.fromisoformat(s) if s else None


def _atomic_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


class LiveMarket:
    """Đọc DNSE thật (chỉ inquiry). Cache trong 1 lượt chạy."""

    def __init__(self):
        from trading_bot.brokers import get_dnse_client
        self.ro = ReadOnlyDNSE(get_dnse_client())
        self._q, self._bars, self._pos = {}, {}, {}

    def quote(self, sym):
        if sym in self._q:
            return self._q[sym]
        from trading_bot.brokers import DNSEBroker, Quote, qget, _fnum
        from trading_bot.vn_market import normalize_price_vnd
        raw, bids = {"symbol": sym}, []
        try:
            raw.update(DNSEBroker._pick_board(self.ro.secdef(sym), "secdefs"))
            raw.update(DNSEBroker._pick_board(self.ro.latest_trade(sym), "trades"))
            qt = DNSEBroker._pick_board(self.ro.latest_quote(sym), "quotes")
            arr = qget(qt, "bid", "bids") if isinstance(qt, dict) else None
            for lv in arr or []:
                if isinstance(lv, dict):
                    bids.append((normalize_price_vnd(_fnum(qget(lv, "price", "p"))),
                                 int(_fnum(qget(lv, "quantity", "qty", "q")) or 0)))
            if bids:
                raw.setdefault("bidPrice1", bids[0][0])
        except Exception as e:      # noqa: BLE001 — 1 mã lỗi không được làm chết cả lượt quét
            self._q[sym] = {"error": f"{type(e).__name__}: {e}"}
            return self._q[sym]
        q = Quote(raw)
        out = {"last": q.last, "ref": q.ref, "floor": q.floor, "ceiling": q.ceiling, "bid": q.bid,
               "bids": [b for b in bids if b[0] and b[1]], "exchange": q.exchange,
               "exchange_known": q.exchange_known, "day_volume": q.day_volume}
        self._q[sym] = out
        return out

    def bars(self, sym, day, index=False):
        key = (sym, day)
        if key not in self._bars:
            a = dt.datetime.combine(day, dt.time(8, 30)).replace(tzinfo=_ICT)
            # `to` theo phút hiện tại, KHÔNG cố định 15:30: DNSE cache /price/ohlc theo URL ⇒ URL
            # cả ngày y hệt trả bản chụp cũ (đo 07/10: rỗng lúc 09:15 hoặc dừng ở bar 09:29 tới 11:20).
            b = min(dt.datetime.combine(day, dt.time(15, 30)),
                    _now().replace(second=0, microsecond=0) + dt.timedelta(minutes=1)).replace(tzinfo=_ICT)
            try:
                r = self.ro.ohlc(sym, resolution="1", bar_type="index" if index else "stock",
                                 **{"from": int(a.timestamp()), "to": int(b.timestamp())})
                k = 1 if index else 1000
                self._bars[key] = [(dt.datetime.fromtimestamp(t, _ICT).replace(tzinfo=None),
                                    r["c"][i] * k, r["v"][i]) for i, t in enumerate(r.get("t", []))]
            except Exception as e:  # noqa: BLE001
                print(f"[ipw] ⚠ bars {sym} {day}: {e}")
                self._bars[key] = []
        return self._bars[key]

    def vni(self, now):
        """(vni_last, vni_ref) — ref = đóng cửa 1D phiên trước."""
        bars = self.bars("VNINDEX", now.date(), index=True)
        last = bars[-1][1] if bars else None
        self.vni_note = None if bars else "không có bar 1 phút nào"
        if bars:
            # nghỉ trưa / sau 14:30 không có bar mới — so với mốc cuối phiên đang mở, không với `now`
            n = now.replace(tzinfo=None)
            ref_t = n
            if dt.time(11, 30) <= n.time() < dt.time(13, 0):
                ref_t = n.replace(hour=11, minute=30, second=0, microsecond=0)
            elif n.time() >= dt.time(14, 30):
                ref_t = n.replace(hour=14, minute=30, second=0, microsecond=0)
            if bars[-1][0] < ref_t - dt.timedelta(minutes=VNI_MAX_AGE_MIN):
                self.vni_note = f"bar cuối {bars[-1][0]:%H:%M} quá cũ ({bars[-1][1]:.2f})"
                last = None
        try:
            a = dt.datetime.combine(now.date() - dt.timedelta(days=12), dt.time(0)).replace(tzinfo=_ICT)
            r = self.ro.ohlc("VNINDEX", resolution="1D", bar_type="index",
                             **{"from": int(a.timestamp()), "to": int(a.timestamp()) + 12 * 86400})
            prev = [(dt.datetime.fromtimestamp(t, _ICT).date(), r["c"][i])
                    for i, t in enumerate(r.get("t", []))]
            prev = [c for d, c in prev if d < now.date()]
            return last, (prev[-1] if prev else None)
        except Exception as e:      # noqa: BLE001
            print(f"[ipw] ⚠ VNINDEX 1D: {e}")
            return last, None

    def positions(self, account_id):
        if account_id in self._pos:
            return self._pos[account_id]
        from trading_bot.brokers import qget, _fnum, _sellable_qty
        r = self.ro.positions(account_id)
        rows = (r.get("positions") or r.get("data")) if isinstance(r, dict) else r
        out = {}
        for p in rows or []:
            # §12: lọc account TRƯỚC mọi phép tính (payload có accountNo)
            if qget(p, "accountno", "account_no") not in (None, "") and \
                    str(qget(p, "accountno", "account_no")) != str(account_id):
                continue
            if str(qget(p, "status", default="OPEN")).upper() == "CLOSED":
                continue
            sym = qget(p, "symbol")
            total = int(_fnum(qget(p, "openquantity", "quantity", default=0)) or 0)
            sell = _sellable_qty(_fnum(qget(p, "tradequantity", "availablequantity", default=None)), total)
            cost = _fnum(qget(p, "costprice", default=None))
            if not sym or total <= 0:
                continue
            o = out.setdefault(sym, {"qty": 0, "sellable": 0, "cost_value": 0.0, "cost_qty": 0})
            o["qty"] += total
            o["sellable"] += sell
            if cost:
                o["cost_value"] += cost * total
                o["cost_qty"] += total
        for o in out.values():
            o["cost"] = o["cost_value"] / o["cost_qty"] if o["cost_qty"] else None
        self._pos[account_id] = out
        return out

    def open_buys(self, account_id, sym):
        r = self.ro.orders(account_id)
        rows = (r.get("orders") or r.get("data")) if isinstance(r, dict) else r
        out = []
        for o in rows or []:
            if str(o.get("accountNo", account_id)) != str(account_id):     # §12
                continue
            if o.get("symbol") != sym or str(o.get("side")) not in ("NB", "buy"):
                continue
            st = str(o.get("orderStatus", "")).lower()
            if any(k in st for k in ("cancel", "reject", "expire")) or st == "filled":
                continue
            out.append({"order_id": o.get("id"), "qty": o.get("quantity"), "price": o.get("price"),
                        "status": o.get("orderStatus"), "filled": o.get("fillQuantity")})
        return out


# ============================================================== vũ trụ + phân loại book
def load_accounts(path=ACCOUNTS_FILE):
    d = _read_json(path, {}) or {}
    out = []
    for a in d.get("accounts", []):
        if a.get("label") in WATCH_ACCOUNTS and a.get("enabled") and a.get("mode") == "live" \
                and a.get("broker") == "dnse":
            out.append({"label": a["label"], "account_id": str(a.get("account_id")),
                        "excluded": [t.upper() for t in a.get("excluded_tickers") or []]})
    return out


_BOOK_MAP = {"BAL": "BAL", "LAG": "LAG", "CAPIT": "CAPIT", "PARK": "CUSTOM30V",
             "CUSTOM30V_PARKING": "CUSTOM30V", "CUSTOM30V": "CUSTOM30V",
             "DISCRETIONARY_SPECIAL": E.DISCRETIONARY}
_PLAN_PREFIXES = ("plan", "park_add", "jit_unpark", "park_trim")


def classify_books(label, today, excluded, disc_tickers, plans_dir=None, lookback=150):
    """mã → book. Lớp (sau đè trước):
      1. bootstrap_book_snapshot_<TK>_*.json (day-0 user duyệt 2026-08-04; book PARK = custom30V);
      2. lệnh MUA gần nhất trong plan_/park_add_/jit_unpark_/park_trim_<TK>_<ngày>.json (≤ lookback
         ngày, kể cả hôm nay) — nhãn `custom30V_parking`/`PARK` ⇒ CUSTOM30V;
      3. mã chỉ thấy ở lệnh BÁN (jit_unpark/park_trim…) mà chưa có book ⇒ lấy book của lệnh bán;
      4. ghi đè: excluded_tickers + state discretionary ⇒ DISCRETIONARY (chỉ tự bán khi GÃY).
    PROBE / legacy_orphan bỏ qua. Mã không truy được ⇒ UNKNOWN (engine xử như discretionary)."""
    import glob
    plans_dir = plans_dir or PLANS_DIR
    books, sells = {}, {}
    for f in sorted(glob.glob(os.path.join(plans_dir, f"bootstrap_book_snapshot_{label}_*.json"))):
        for p in (_read_json(f) or {}).get("positions") or []:
            b = _BOOK_MAP.get(str(p.get("book") or "").upper())
            if b and p.get("ticker"):
                books[p["ticker"].upper()] = b
    d = today - dt.timedelta(days=lookback)
    while d <= today:
        for pre in _PLAN_PREFIXES:
            p = _read_json(os.path.join(plans_dir, f"{pre}_{label}_{d.isoformat()}.json"))
            for o in (p or {}).get("orders", []) if isinstance(p, dict) else []:
                b = _BOOK_MAP.get(str(o.get("book") or "").upper())
                if not b or not o.get("ticker"):
                    continue
                if o.get("side") == "buy":
                    books[o["ticker"].upper()] = b
                elif o.get("side") == "sell":
                    sells[o["ticker"].upper()] = b
        d += dt.timedelta(days=1)
    for t, b in sells.items():
        books.setdefault(t, b)
    for t in list(excluded) + list(disc_tickers):
        books[t.upper()] = E.DISCRETIONARY
    return books


def discretionary_tickers(label, disc_dir=None):
    disc_dir = disc_dir or DISC_DIR
    out = []
    try:
        for f in os.listdir(disc_dir):
            if f.startswith("state_") and f.endswith(f"_{label}.json"):
                out.append(f[len("state_"):-len(f"_{label}.json")].upper())
    except OSError:
        pass
    return out


def plan_buys(label, today, plans_dir=None):
    plans_dir = plans_dir or PLANS_DIR
    p = _read_json(os.path.join(plans_dir, f"plan_{label}_{today.isoformat()}.json"), {}) or {}
    return [{"ticker": o["ticker"].upper(), "qty": o.get("qty"), "book": o.get("book"),
             "id": o.get("id")} for o in p.get("orders", []) if o.get("side") == "buy" and o.get("ticker")]


def nav_info(label, nav_dir=NAV_DIR):
    d = _read_json(os.path.join(nav_dir, f"active_nav_{label}.json"), {}) or {}
    return d.get("total_nav"), d.get("computed_at")


def build_universe(today, market, accounts, state_dir, errors=None):
    """errors (list, tuỳ chọn): nhận mô tả lỗi đọc vị thế để driver cảnh báo sức khoẻ.
    Hạn chế giao dịch: CHƯA có field DNSE nào đã xác minh ⇒ danh sách tay
    `<state_dir>/restricted.json` {"tickers": [...]} (+ excluded_tickers của TK)."""
    uni = {}
    restricted = {t.upper() for t in (_read_json(os.path.join(state_dir, "restricted.json"), {}) or {})
                  .get("tickers", [])}
    watch = _read_json(os.path.join(state_dir, "watchlist.json"), {}) or {}
    for t in watch.get("tickers", []):
        uni.setdefault(t.upper(), {"holdings": {}, "buys": [], "watch": True})
    for a in accounts:
        lab = a["label"]
        disc = discretionary_tickers(lab)
        books = classify_books(lab, today, a["excluded"], disc)
        for t in disc + a["excluded"]:
            uni.setdefault(t, {"holdings": {}, "buys": [], "watch": True})
        try:
            pos = market.positions(a["account_id"])
        except Exception as e:      # noqa: BLE001
            print(f"[ipw] ⚠ positions {lab}: {e} — TK này chỉ còn plan/watchlist trong lượt quét")
            if errors is not None:
                errors.append(f"không đọc được vị thế {lab}: {type(e).__name__}: {str(e)[:200]} — "
                              f"lượt quét KHÔNG thấy vị thế TK này")
            pos = {}
        for t, p in pos.items():
            u = uni.setdefault(t, {"holdings": {}, "buys": [], "watch": False})
            nas = (f"excluded_tickers {lab}" if t in a["excluded"] else
                   "restricted.json (hạn chế giao dịch)" if t in restricted else None)
            u["holdings"][lab] = {"qty": p["qty"], "sellable": p["sellable"], "cost": p.get("cost"),
                                  "book": books.get(t, E.UNKNOWN), "account_id": a["account_id"],
                                  "no_auto_sell": nas}
        for b in plan_buys(lab, today):
            u = uni.setdefault(b["ticker"], {"holdings": {}, "buys": [], "watch": False})
            u["buys"].append({**b, "account": lab, "account_id": a["account_id"]})
    return uni


# ============================================================== báo + dispatch + trả lời
def owner_mention(path=CHANNELS):
    uid = ((_read_json(path, {}) or {}).get("users") or {}).get("owner", {}).get("id")
    return f"<@{uid}> " if uid else ""


class Notifier:
    def __init__(self, dry=False):
        self.dry, self.sent = dry, []

    def _run(self, cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return r.returncode == 0, (r.stderr or r.stdout).strip()[-300:]
        except Exception as e:      # noqa: BLE001
            return False, f"{type(e).__name__}: {e}"

    def send(self, msg, channels=("discord", "telegram"), subject=None, mention=False):
        msg = f"{TAG} {msg}"
        res = {}
        for ch in channels:
            if self.dry:
                res[ch] = (True, "dry")
            elif ch == "discord":
                res[ch] = self._run([NOTIFY_THREAD, (owner_mention(CHANNELS) if mention else "") + msg,
                                     "trading_daily"])
            elif ch == "telegram":
                res[ch] = self._run([NOTIFY_TG, msg])
            elif ch == "email":
                p = f"/tmp/ipw_email_{os.getpid()}.md"
                with open(p, "w", encoding="utf-8") as f:
                    f.write(msg)
                res[ch] = self._run([sys.executable, EMAIL, p, "--subject", f"{TAG} {subject or 'Cổng giá'}"])
            self.sent.append({"channel": ch, "ok": res[ch][0], "msg": msg})
        return res


def investigation_prompt(case, verdict_cmd):
    tk, tr = case["ticker"], case["trigger"]
    held = ", ".join(f"{a} {h['qty']}cp ({h['book']})" for a, h in case["holdings"].items()) or "không giữ"
    vmin = E.INVEST_MIN_COMPRESSED if case.get("compressed") else E.INVEST_MIN
    return (
        f"[INTRADAY-WATCH DD — SHADOW, job cổng giá] Mã {tk} kích hoạt cổng giá trong phiên lúc "
        f"{case['t0'][11:16]} ICT: {tr['reason']} (ret {tr['ret']*100:+.1f}%, VNINDEX "
        f"{(tr['vni_ret'] or 0)*100:+.1f}%). Đang giữ: {held}. HẠN CỨNG {vmin} phút từ lúc kích "
        f"hoạt — quá hạn hệ thống tự coi là CHƯA RÕ. Việc: (1) gọi Agent(subagent_type='legal-vn') "
        f"đọc tin 48h gần nhất về {tk} (công bố thông tin, khởi tố, thanh tra, KQKD, giao dịch nội "
        f"bộ, tin ngành); (2) kết luận đúng 1 nhãn: BROKEN (= GÃY: pháp lý dính pháp nhân/tài sản "
        f"lõi, gian lận, KQKD sụp, mất khả năng thanh toán) / NOISE (= NHIỄU: không tìm thấy tin, "
        f"tin cá nhân không dính lõi, cả ngành) / UNCLEAR (= CHƯA RÕ). Không bán theo tâm lý: không "
        f"có tin thì là NOISE. (3) GHI phán quyết bằng đúng lệnh sau (sửa LABEL và SUMMARY ≤300 ký "
        f"tự, có nguồn): {verdict_cmd} --label LABEL --summary 'SUMMARY'. KHÔNG đặt/huỷ lệnh, "
        f"KHÔNG sửa plan — hệ thống tự áp hành động mặc định theo phán quyết. (Shadow: chạy thử.)")


def dispatch_argv(prompt, compressed, dispatch_bin=DISPATCH):
    """argv THẬT gửi dispatch.sh (selfcheck chạy đúng argv này vào stub). --timeout = hạn điều tra
    + 5' (quá hạn thì phán quyết vô dụng); --retries 0 ⇒ 1 lần hết giờ = đúng 1 lỗi ở circuit."""
    tmo = (E.INVEST_MIN_COMPRESSED if compressed else E.INVEST_MIN) * 60 + 300
    return [dispatch_bin, "Taylor", prompt, "--bg", "--thread", "trading_daily", "--timeout", str(tmo),
            "--retries", "0", "--model", "opus", "--effort", "medium"]


def dispatch_investigation(case, verdict_cmd, dry=False, dispatch_bin=DISPATCH):
    """→ (job | "DRY" | "issued" | None, info). None = dispatch HỎNG (info = lỗi thật)."""
    prompt = investigation_prompt(case, verdict_cmd)
    if dry:
        return "DRY", prompt
    env = dict(os.environ, DISPATCH_FROM=DISPATCH_FROM_ID)
    try:
        r = subprocess.run(dispatch_argv(prompt, case.get("compressed"), dispatch_bin),
                           capture_output=True, text=True, env=env, timeout=DISPATCH_SUBPROC_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, (f"dispatch.sh không trả lời sau {DISPATCH_SUBPROC_TIMEOUT}s (TimeoutExpired) — "
                      f"không xác nhận được job")
    except OSError as e:
        return None, f"dispatch.sh không chạy được: {type(e).__name__}: {e}"
    if r.returncode != 0:
        return None, f"dispatch rc={r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}"
    for tok in (r.stdout + r.stderr).replace("(", " ").replace(")", " ").split():
        if tok.startswith("job="):
            return tok.split("=", 1)[1], prompt
    return "issued", prompt


def job_status(job, jobs_dir=JOBS_DIR):
    """Trạng thái job dispatch (bus/jobs/<job>.json) — None nếu không đọc được."""
    return (_read_json(os.path.join(jobs_dir, f"{job}.json"), {}) or {}).get("status")


def fetch_messages(limit=100):
    """Tin gần nhất của Trading Daily qua ccdb (localhost). created_at → ICT naive."""
    sys.path.insert(0, os.path.join(MIKE, "bin"))
    from discord_channels import resolve
    tid = resolve("trading_daily")
    with urllib.request.urlopen(f"{CCDB}/api/threads/{tid}/messages?limit={limit}", timeout=10) as r:
        data = json.loads(r.read().decode())
    out = []
    for m in data.get("messages", []):
        ts = m.get("created_at")
        if ts:
            ts = dt.datetime.fromisoformat(ts).astimezone(_ICT).replace(tzinfo=None)
        out.append({"id": m.get("id"), "is_bot": bool(m.get("is_bot")), "content": m.get("content"),
                    "created_at": ts, "author": m.get("author")})
    return out


# ============================================================== state + log
def state_path(state_dir, day):
    return os.path.join(state_dir, f"state_{day.isoformat()}.json")


def log_event(state_dir, day, kind, **kw):
    os.makedirs(state_dir, exist_ok=True)
    rec = {"ts": _iso(kw.pop("now", None) or _now()), "kind": kind, "mode": "SHADOW", **kw}
    with open(os.path.join(state_dir, f"shadow_{day.isoformat()}.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")


def prev_trading_day(d):
    from trading_bot.vn_market import is_holiday
    d -= dt.timedelta(days=1)
    while d.weekday() >= 5 or is_holiday(d):
        d -= dt.timedelta(days=1)
    return d


def load_state(state_dir, day):
    st = _read_json(state_path(state_dir, day))
    if st:
        return st
    st = {"date": day.isoformat(), "last_scan": None, "cases": {}, "outbox": []}
    prev = _read_json(state_path(state_dir, prev_trading_day(day)))
    # tin chưa gửi xong của phiên trước: gửi nốt (không mất cảnh báo qua đêm)
    st["outbox"] = [m for m in ((prev or {}).get("outbox") or []) if m.get("left")
                    and m.get("attempts", 0) < NOTIFY_MAX_ATTEMPTS]
    for tk, c in ((prev or {}).get("cases") or {}).items():
        if c.get("status") in NO_CARRY:
            continue
        c = json.loads(json.dumps(c))
        c["carryover_from"] = prev["date"]
        for ex in (c.get("execution") or {}).values():
            # chỉ leo thang TRONG ngày: sang phiên mới chọn lại chế độ; lệnh chờ hết hiệu lực
            ex.update({"mode": 0, "open": [], "ato_sent": False, "atc_sent": False})
        c["prev_day_volume"] = None
        st["cases"][tk] = c
    return st


def verdict_path(state_dir, day, tk):
    return os.path.join(state_dir, "verdicts", f"{day.isoformat()}_{tk.upper()}.json")


def read_verdict(state_dir, case):
    """Phán quyết cho ca — tra ngày T0 (ca carryover vẫn tìm đúng file)."""
    v = _read_json(verdict_path(state_dir, dt.date.fromisoformat(case["t0"][:10]), case["ticker"]))
    if v and v.get("label") in (E.BROKEN, E.NOISE, E.UNCLEAR):
        return v
    return None


def write_no_rebuy(state_dir, tk, label, day, book):
    from trading_bot.vn_market import next_trading_day
    until = day
    for _ in range(E.NO_REBUY_SESSIONS):
        until = next_trading_day(until)
    p = os.path.join(state_dir, "no_rebuy_shadow.json")
    led = _read_json(p, {}) or {}
    led[f"{tk}|{label}"] = {"ticker": tk, "account": label, "until": until.isoformat(),
                            "book": book, "custom30v_excluded_until_review": book == "CUSTOM30V",
                            "note": "SHADOW — chưa có consumer; bản live: plan T+1 tự loại"}
    _atomic_json(p, led)
    return until


# ============================================================== 1 nhịp
class Deps:
    """Gói phụ thuộc ngoài — selfcheck thay bằng giả."""

    def __init__(self, market, notifier, state_dir, dispatch=True, messages=fetch_messages,
                 accounts=None, bot_stop_path=BOT_STOP, universe=None, nav=nav_info, dispatch_watch=False,
                 dispatch_bin=DISPATCH, job_status=job_status, budget_s=RUN_BUDGET_S):
        self.market, self.notifier, self.state_dir = market, notifier, state_dir
        self.dispatch_watch = dispatch_watch
        self.dispatch, self.messages, self.bot_stop_path = dispatch, messages, bot_stop_path
        self.accounts = accounts if accounts is not None else load_accounts()
        self.universe, self.nav = universe, nav
        self.dispatch_bin, self.job_status, self.budget_s = dispatch_bin, job_status, budget_s
        self.t_start = time.monotonic()

    def over_budget(self):
        return time.monotonic() - self.t_start > self.budget_s


def _save(deps, day, st):
    _atomic_json(state_path(deps.state_dir, day), st)


def _stats(st):
    s = st.setdefault("stats", {})
    for k in ("scans", "triggers", "market_wide", "dispatches", "dispatch_fail", "dispatch_skipped",
              "quotes", "quote_errors", "notify_fail", "reply_read_errors"):
        s.setdefault(k, 0)
    for k in ("verdicts", "alt_cur", "alt_rel"):
        s.setdefault(k, [])
    return s


# -------------------------------------------------------------- hộp thư đi (at-least-once)
def enqueue(st, msg, channels=("discord", "telegram"), subject=None, mention=False, key=None, now=None):
    """Xếp 1 tin vào hộp thư đi trong state. Caller PHẢI ghi state trước khi flush_outbox gửi.
    key: chống xếp trùng (vd nhắc 08:30)."""
    ob = st.setdefault("outbox", [])
    if key and any(m.get("key") == key for m in ob):
        return None
    st["seq"] = st.get("seq", 0) + 1
    m = {"id": st["seq"], "key": key, "msg": msg, "left": list(channels), "subject": subject,
         "mention": bool(mention), "attempts": 0, "queued_at": _iso(now)}
    ob.append(m)
    return m


def flush_outbox(st, deps, now):
    """Gửi mọi tin còn kênh chưa gửi. Kết quả Notifier được KIỂM: kênh OK mới gạch; kênh lỗi thử lại
    lượt sau (≤ NOTIFY_MAX_ATTEMPTS), bỏ cuộc ⇒ cảnh báo qua kênh khác (1 lần/ngày/kênh)."""
    day = now.date()
    for m in list(st.get("outbox") or []):
        if not m["left"] or m["attempts"] >= NOTIFY_MAX_ATTEMPTS:
            continue
        if deps.over_budget():
            log_event(deps.state_dir, day, "BUDGET", now=now, where="flush_outbox", pending=m["id"])
            return
        m["attempts"] += 1
        _save(deps, day, st)
        res = deps.notifier.send(m["msg"], tuple(m["left"]), subject=m.get("subject"), mention=m["mention"])
        bad = {ch: info for ch, (ok, info) in res.items() if not ok}
        m["left"] = [ch for ch in m["left"] if ch in bad]
        if bad:
            _stats(st)["notify_fail"] += 1
            log_event(deps.state_dir, day, "NOTIFY_FAIL", now=now, id=m["id"], failed=bad,
                      attempts=m["attempts"])
            if m["attempts"] >= NOTIFY_MAX_ATTEMPTS:
                alive = tuple(ch for ch in ("discord", "telegram") if ch not in bad)
                for ch in bad:
                    if alive:
                        enqueue(st, f"🩺 kênh {ch} lỗi {NOTIFY_MAX_ATTEMPTS} lần liên tiếp ({bad[ch][:150]}) — "
                                    f"có tin intraday-watch KHÔNG tới kênh này", alive,
                                key=f"chfail:{ch}:{day}", now=now)
        _save(deps, day, st)


def health_alert(st, kind, msg, now, deps):
    """Cảnh báo sức khoẻ (không im lặng), cùng loại tối đa 1 lần/HEALTH_ALERT_EVERY_MIN."""
    ha = st.setdefault("health_alerts", {})
    last = ha.get(kind)
    log_event(deps.state_dir, now.date(), "HEALTH", now=now, health=kind, msg=msg)
    if last and (now - _p(last)).total_seconds() < HEALTH_ALERT_EVERY_MIN * 60:
        return False
    ha[kind] = _iso(now)
    enqueue(st, f"🩺 SỨC KHOẺ intraday-watch ({kind}): {msg}", now=now)
    return True


def crash_alert(state_dir, kind, err, notifier, now=None):
    """Lỗi cấp cao nhất (state có thể hỏng ⇒ gửi THẲNG, không qua outbox). Tối đa 1 lần/ngày/loại:
    cờ ghi TRƯỚC khi gửi."""
    now = now or _now()
    day = now.date()
    try:
        log_event(state_dir, day, "CRASH", now=now, where=kind, error=err[-3000:])
    except OSError:
        pass
    flag = os.path.join(state_dir, f"crash_{kind}_{day.isoformat()}.flag")
    if os.path.exists(flag):
        return False
    os.makedirs(state_dir, exist_ok=True)
    with open(flag, "w", encoding="utf-8") as f:
        f.write(err[-3000:])
    notifier.send(f"🔥 intraday-watch LỖI ({kind}): {err.strip().splitlines()[-1][:300] if err.strip() else '?'}"
                  f" — cổng giá trong phiên có thể KHÔNG chạy. Báo tối đa 1 lần/ngày; chi tiết "
                  f"mike/logs/intraday_price_watch.log", ("discord", "telegram"), mention=True)
    return True


def _scan_due(now, last_scan, phase):
    if phase not in ("MORNING", "AFTERNOON", "ATC") or not (SCAN_START <= now.time() <= SCAN_END):
        return False
    if last_scan is None:
        return True
    return (now - _p(last_scan)).total_seconds() >= SCAN_EVERY_MIN * 60 - 30


def _fmt(x):
    return f"{x:,.0f}" if isinstance(x, (int, float)) else "?"


def _fmt_hold(case, deps, q):
    lines = []
    for lab, h in case["holdings"].items():
        nav, nav_at = deps.nav(lab)
        val = h["qty"] * (q.get("last") or 0)
        pnl = (q["last"] / h["cost"] - 1) * 100 if h.get("cost") and q.get("last") else None
        lines.append(f"  • {lab}: {h['qty']:,}cp (bán được {h['sellable']:,}) ≈ {val/1e6:,.1f}tr"
                     + (f" = {val/nav*100:.1f}% NAV (NAV {str(nav_at)[:16]})" if nav else "")
                     + (f", lãi/lỗ {pnl:+.1f}% (giá vốn {h['cost']:,.0f})" if pnl is not None else "")
                     + f", book {h['book']}" + (" ⚠️ book KHÔNG xác định" if h["book"] == E.UNKNOWN else "")
                     + (f" ⛔ {h['no_auto_sell']} ⇒ KHÔNG tự bán" if h.get("no_auto_sell") else ""))
    return "\n".join(lines) or "  • không giữ (watchlist / lệnh mua)"


def _reply_cmds(tk):
    return (f"\"{REPLY_PREFIX} GIỮ {tk}\" / \"{REPLY_PREFIX} BÁN {tk}\" / \"{REPLY_PREFIX} BÁN 50% {tk}\" "
            f"— {SHADOW_NOTE}")


def open_case(tk, u, tr, q, now, deps, st):
    """Mở ca — KHÔNG tác động ngoài (dispatch + tin T0 làm ở _pending_work sau khi state đã lên đĩa)."""
    day = now.date()
    case = {"ticker": tk, "t0": _iso(now), "trigger": tr, "exchange": q.get("exchange"),
            "exchange_known": q.get("exchange_known"), "holdings": u["holdings"], "watch": u.get("watch"),
            "compressed": E.room_of(q["last"], q["floor"], q["ref"]) is not None
            and E.room_of(q["last"], q["floor"], q["ref"]) <= E.ROOM_COMPRESS + E.EPS,
            "status": "INVESTIGATING", "deferred_buys": [], "execution": {},
            "t0_quote": {k: q.get(k) for k in ("last", "ref", "floor")},
            "late": now.time() >= LATE_TRIGGER, "t0_pending": True}
    for b in u["buys"]:
        try:
            live = deps.market.open_buys(b["account_id"], tk)
        except Exception as e:      # noqa: BLE001
            live = [{"error": str(e)}]
        case["deferred_buys"].append({**b, "live_orders": live,
                                      "would": "HUỶ lệnh đã ra sàn" if live else "GỠ khỏi plan trước khi bot đặt"})
    case["watch_only"] = not case["holdings"] and not case["deferred_buys"]
    if case["watch_only"] and not deps.dispatch_watch:
        case["status"], case["need_dispatch"] = "NO_POSITION", False
    else:
        case["need_dispatch"] = True
    st["cases"][tk] = case
    _stats(st)["triggers"] += 1
    log_event(deps.state_dir, day, "TRIGGER", now=now, ticker=tk, trigger=tr, quote=q,
              holdings=case["holdings"], deferred_buys=case["deferred_buys"], late=case["late"])
    return case


def _t0_msg(case, deps):
    tk, tr, q = case["ticker"], case["trigger"], case.get("t0_quote") or {}
    t0 = _p(case["t0"])
    inv = case.get("investigation") or {}
    vd = E.verdict_deadline(t0, case["compressed"])
    buys = "".join(f"\n  🛑 lệnh MUA {b['account']} {b.get('qty')}cp ({b.get('book')}) ⇒ bản live sẽ "
                   f"{b['would']} (shadow: CHỈ ghi log)" for b in case["deferred_buys"])
    if case["status"] == "NO_POSITION":
        inv_line = "  ℹ️ chỉ watchlist (không giữ, không lệnh mua) ⇒ KHÔNG dispatch điều tra"
    elif inv.get("job"):
        inv_line = (f"  ⇒ đang điều tra (legal-vn + Taylor, job {inv['job']}), hạn phán quyết {vd:%H:%M}"
                    + (" — CHẾ ĐỘ RÚT GỌN vì sát sàn" if case["compressed"] else ""))
    else:
        inv_line = (f"  ⚠️⚠️ KHÔNG CÓ ĐIỀU TRA TỰ ĐỘNG — {inv.get('skipped') or inv.get('note') or '?'}\n"
                    f"  ⇒ hết hạn {vd:%H:%M} hệ thống KHÔNG tự bán (mặc định GIỮ). ANH CẦN TỰ XEM TIN {tk}.")
    late = ("\n  ⏳ kích hoạt sau 14:00 ⇒ chỉ báo + điều tra; mặc định (nếu có) chỉ áp từ 09:15 phiên sau, "
            "08:30 nhắc lại" if case.get("late") else "")
    return (f"🚨 CỔNG GIÁ TRONG PHIÊN — {tk} {t0:%H:%M}: {tr['reason']}\n"
            f"  giá {_fmt(q.get('last'))} (TC {_fmt(q.get('ref'))}, sàn {_fmt(q.get('floor'))}) | VNINDEX "
            f"{(tr['vni_ret'] or 0)*100:+.1f}%" + (" ⚠️ không đọc được VNINDEX" if tr["vni_missing"] else "")
            + f"\n{_fmt_hold(case, deps, q)}{buys}\n{inv_line}{late}"
            + (f"\n  Ra lệnh sớm (tuỳ chọn): {_reply_cmds(tk)}" if case["holdings"] else f"\n  ({SHADOW_NOTE})"))


def _dispatch_gate(st, case, deps):
    if deps.dispatch is None:
        return False, "chạy với --no-dispatch"
    if st.get("dispatch_halted"):
        return False, f"dispatch đã DỪNG tới hết hôm nay: {st['dispatch_halted']}"
    if _stats(st)["dispatches"] >= MAX_DISPATCH_PER_DAY:
        return False, f"đã đủ trần {MAX_DISPATCH_PER_DAY} điều tra/ngày"
    if (st.get("dispatch_by_scan") or {}).get(case["t0"], 0) >= MAX_DISPATCH_PER_SCAN:
        return False, f"đã đủ trần {MAX_DISPATCH_PER_SCAN} điều tra/lượt quét"
    return True, ""


def _case_value(case):
    last = (case.get("t0_quote") or {}).get("last") or 0
    return sum(h["qty"] for h in case["holdings"].values()) * last


def _pending_work(st, deps, now):
    """Dispatch (at-most-once) rồi xếp tin T0 — theo thứ tự giá trị vị thế giảm dần."""
    day = now.date()
    for tk, case in sorted(st["cases"].items(), key=lambda kv: -_case_value(kv[1])):
        if not (case.get("need_dispatch") or case.get("t0_pending")):
            continue
        if deps.over_budget():
            log_event(deps.state_dir, day, "BUDGET", now=now, where="pending_work", ticker=tk)
            return
        if case.get("need_dispatch"):
            inv = case.get("investigation")
            if inv is None:
                ok, why = _dispatch_gate(st, case, deps)
                if not ok:
                    case["investigation"] = {"skipped": why}
                    _stats(st)["dispatch_skipped"] += 1
                    log_event(deps.state_dir, day, "DISPATCH_SKIPPED", now=now, ticker=tk, why=why)
                else:
                    case["investigation"] = {"dispatch_attempted_at": _iso(now)}
                    _stats(st)["dispatches"] += 1
                    dbs = st.setdefault("dispatch_by_scan", {})
                    dbs[case["t0"]] = dbs.get(case["t0"], 0) + 1
                    _save(deps, day, st)                        # at-most-once: ghi TRƯỚC khi gọi
                    cmd = (f"{sys.executable} {os.path.abspath(__file__)} verdict --date {day.isoformat()} "
                           f"--ticker {tk} --state-dir {deps.state_dir}")
                    job, info = dispatch_investigation(case, cmd, dry=not deps.dispatch,
                                                       dispatch_bin=deps.dispatch_bin)
                    case["investigation"].update({"job": job, "note": None if job else info})
                    if not job:
                        _stats(st)["dispatch_fail"] += 1
                    log_event(deps.state_dir, day, "DISPATCH", now=now, ticker=tk, job=job, info=info[:3000])
            elif not inv.get("job") and not inv.get("note") and not inv.get("skipped"):
                # lượt trước bị cắt giữa "ghi cờ" và "nhận job" ⇒ KHÔNG dispatch lại
                inv["note"] = ("tiến trình bị cắt giữa lúc dispatch — không xác nhận được job; KHÔNG "
                               "dispatch lại (at-most-once)")
                _stats(st)["dispatch_fail"] += 1
                log_event(deps.state_dir, day, "DISPATCH_UNCERTAIN", now=now, ticker=tk, note=inv["note"])
            case["need_dispatch"] = False
            _save(deps, day, st)
        if case.get("t0_pending"):
            enqueue(st, _t0_msg(case, deps), ("discord", "telegram", "email"), subject=f"Cổng giá {tk}",
                    mention=True, now=now)
            case["t0_pending"] = False
            case["t0_notified"] = True
            _save(deps, day, st)


def _snap(case, q, deps, now):
    bars = deps.market.bars(case["ticker"], now.date())
    px5 = None
    for t, c, _v in bars:
        if t <= now - dt.timedelta(minutes=5):
            px5 = c
    dv = q.get("day_volume")
    prev = case.get("prev_day_volume")
    case["prev_day_volume"] = dv
    snap = {"last": q.get("last"), "ref": q.get("ref"), "floor": q.get("floor"), "bid": q.get("bid"),
            "bids": [tuple(b) for b in q.get("bids") or []], "px_5m_ago": px5,
            "dvol": (dv - prev) if (dv is not None and prev is not None) else 0}
    # kết quả phiên định kỳ: bar 09:15 = ATO, bar 14:45 = ATC (chỉ bar ĐÃ có — không nhìn trước)
    snap["auctions"] = {k: (c, v) for t, c, v in bars
                        for k, hm in (("ATO", dt.time(9, 15)), ("ATC", dt.time(14, 45))) if t.time() == hm}
    return snap


def _reply_deadline(case, now):
    """(hạn, hoãn_sang_phiên_sau). (c): kích hoạt ≥14:00 hoặc hạn > 14:15 ⇒ 09:15 phiên sau."""
    from trading_bot.vn_market import next_trading_day
    rd = E.reply_deadline(now, case.get("compressed"))
    if (case.get("late") and now.date() == _p(case["t0"]).date()) or rd.time() > NO_EOD_DEFAULT_AFTER \
            or rd.date() > now.date():
        return dt.datetime.combine(next_trading_day(now.date()), NEXT_SESSION_APPLY), True
    return rd, False


def _no_verdict_reason(inv):
    if inv.get("job"):
        return f"điều tra (job {inv['job']}) hết giờ, KHÔNG có phán quyết"
    return f"không có điều tra: {inv.get('skipped') or inv.get('note') or 'không rõ'}"


def process_case(case, now, deps, st):
    from trading_bot.vn_market import session_phase
    day, tk = now.date(), case["ticker"]
    q = deps.market.quote(tk)
    if q.get("error") or not q.get("last"):
        # chưa có giá khớp (trước ATO) / lỗi: vẫn chạy hạn chót + bộ máy bán (ATO không cần giá)
        log_event(deps.state_dir, day, "QUOTE_ERROR", now=now, ticker=tk, quote=q)
        q = {k: v for k, v in q.items() if k != "error"}
    changed = False
    t0 = _p(case["t0"])

    # (a) bảo vệ khi rơi nhanh trước phán quyết
    room = E.room_of(q.get("last"), q.get("floor"), q.get("ref"))
    if not case.get("verdict") and not case.get("compressed") and room is not None \
            and room <= E.ROOM_COMPRESS + E.EPS:
        case["compressed"] = True
        changed = True
        log_event(deps.state_dir, day, "COMPRESSED", now=now, ticker=tk, room=room)

    # (b) phán quyết (agent ghi file) hoặc hết hạn ⇒ KHÔNG có phán quyết agent
    if not case.get("verdict"):
        v = read_verdict(deps.state_dir, case)
        inv = case.get("investigation") or {}
        job = inv.get("job")
        if v is None and job and job not in ("DRY", "issued") and not inv.get("job_dead"):
            js = deps.job_status(job)
            if js in JOB_DEAD:
                v = read_verdict(deps.state_dir, case)        # đọc lại: agent có thể vừa ghi xong
                if v is None:
                    inv["job_dead"] = js
                    st["dispatch_halted"] = st.get("dispatch_halted") or \
                        f"job điều tra {job} ({tk}) kết thúc '{js}' mà không có phán quyết"
                    log_event(deps.state_dir, day, "JOB_DEAD", now=now, ticker=tk, job=job, status=js)
                    enqueue(st, f"⚠️ Điều tra {tk} (job {job}) đã kết thúc '{js}' mà KHÔNG có phán quyết ⇒ "
                                f"hết hạn sẽ GIỮ (không tự bán); dừng dispatch điều tra tới hết hôm nay. "
                                f"ANH CẦN TỰ XEM TIN {tk}. ({SHADOW_NOTE})", mention=True, now=now)
                    changed = True
        if v or now >= E.verdict_deadline(t0, case.get("compressed")):
            if v:
                case["verdict"] = {"label": v["label"], "summary": v.get("summary"), "source": "agent",
                                   "at": v.get("at")}
            else:
                src = "timeout" if job else "no_dispatch"
                case["verdict"] = {"label": E.UNCLEAR, "summary": _no_verdict_reason(inv), "source": src,
                                   "at": _iso(now)}
                if src == "timeout" and STOP_DISPATCH_AFTER_TIMEOUT and not st.get("dispatch_halted"):
                    st["dispatch_halted"] = f"điều tra {tk} hết giờ không phán quyết"
            lat = round((now - t0).total_seconds() / 60.0, 1)
            case["verdict"]["latency_min"] = lat
            _stats(st)["verdicts"].append({"ticker": tk, "source": case["verdict"]["source"],
                                           "compressed": bool(case.get("compressed")), "latency_min": lat})
            if case["status"] not in ("INVESTIGATING", "AWAITING_REPLY"):
                # user đã ra lệnh & ca đã chạy/xong trước phán quyết ⇒ chỉ GHI phán quyết (đánh giá shadow)
                log_event(deps.state_dir, day, "VERDICT_LATE", now=now, ticker=tk, verdict=case["verdict"],
                          status=case["status"])
                enqueue(st, f"📋 Phán quyết {tk}: {E.VERDICT_VN[case['verdict']['label']]} "
                            f"({case['verdict']['source']}) — ca đã {case['status']} theo lệnh user.", now=now)
                _save(deps, day, st)
                return
            vv = case["verdict"]
            case["actions_default"] = {lab: E.default_action(vv["label"], h["book"], vv["source"],
                                                             bool(h.get("no_auto_sell")))
                                       for lab, h in case["holdings"].items()}
            case["report_at"] = _iso(now)
            rd, deferred = _reply_deadline(case, now)
            case["reply_deadline"], case["reply_deferred"] = _iso(rd), deferred
            case["status"] = "AWAITING_REPLY" if case["holdings"] else "NO_POSITION"
            _save(deps, day, st)
            log_event(deps.state_dir, day, "VERDICT", now=now, ticker=tk, verdict=vv,
                      actions_default=case["actions_default"], reply_deadline=case["reply_deadline"],
                      deferred=deferred, latency_min=lat, compressed=bool(case.get("compressed")))
            acts = "\n".join(
                f"  • {lab}: mặc định {E.ACTION_VN[a]} (book {case['holdings'][lab]['book']})"
                + (f" ⛔ {case['holdings'][lab]['no_auto_sell']} ⇒ hệ thống KHÔNG đặt lệnh, kể cả theo lệnh anh"
                   if case["holdings"][lab].get("no_auto_sell") else "")
                for lab, a in case["actions_default"].items()) or "  • không giữ — chỉ hoãn mua"
            warn = (f"  ⚠️⚠️ KHÔNG CÓ PHÁN QUYẾT TỪ ĐIỀU TRA ({vv['source']}) ⇒ mặc định GIỮ, KHÔNG tự bán. "
                    f"ANH CẦN TỰ XEM {tk}.\n" if vv["source"] != "agent" else "")
            when = (f"  ⏰ HẠN CHÓT {rd:%d/%m %H:%M} (phiên sau — mặc định chỉ áp từ 09:15; 08:30 nhắc lại)"
                    if deferred else f"  ⏰ HẠN CHÓT {rd:%H:%M}"
                    + (" (RÚT GỌN — sát sàn)" if case.get("compressed") else ""))
            enqueue(st, f"📋 PHÁN QUYẾT {tk}: **{E.VERDICT_VN[vv['label']]}** ({vv['source']})\n"
                        f"{warn}  {(vv.get('summary') or '')[:400]}\n{acts}\n{when}"
                        f" — trả lời trong Trading Daily: {_reply_cmds(tk)}. Im lặng ⇒ mặc định.",
                    ("discord", "telegram", "email"), subject=f"Phán quyết {tk}", mention=True, now=now)
            changed = True
    if case["status"] in TERMINAL:
        if changed:
            _save(deps, day, st)
        return

    # (c) trả lời user (từ T0 — user ra lệnh sớm cũng được tôn trọng) — đè mặc định
    if case["holdings"]:
        try:
            msgs = deps.messages()
        except Exception as e:      # noqa: BLE001
            msgs = []
            _stats(st)["reply_read_errors"] += 1
            log_event(deps.state_dir, day, "REPLY_READ_ERROR", now=now, ticker=tk, error=str(e))
            health_alert(st, "ccdb", f"không đọc được tin Trading Daily ({type(e).__name__}: {str(e)[:150]}) "
                                     f"⇒ lệnh trả lời của anh cho {tk} có thể KHÔNG được thấy", now, deps)
            changed = True
        act, msg = E.parse_reply(msgs, tk, since=t0, prefix=REPLY_PREFIX)
        dec = case.get("decision") or {}
        if act and str(msg.get("id")) != str(dec.get("msg_id")):
            case["decision"] = {"source": "user", "action": act, "msg_id": msg.get("id"),
                                "at": _iso(msg["created_at"]),
                                "per_account": {lab: act for lab in case["holdings"]}}
            log_event(deps.state_dir, day, "USER_REPLY", now=now, ticker=tk, action=act,
                      content=msg.get("content"), author=msg.get("author"))
            skipped = _apply_decision(case, now, deps)
            enqueue(st, f"✅ Đã nhận \"{REPLY_PREFIX} {E.ACTION_VN[act]} {tk}\" từ user — áp (mô phỏng) cho mọi TK "
                        f"đang giữ" + "".join(f"; {lab}: {why} ⇒ KHÔNG đặt lệnh, thao tác tay" for lab, why in skipped)
                    + f". ({SHADOW_NOTE})", now=now)
            changed = True

    # (d) hết hạn, im lặng ⇒ mặc định
    if not case.get("decision") and case.get("reply_deadline") and now >= _p(case["reply_deadline"]):
        case["decision"] = {"source": "default", "at": _iso(now), "per_account": case["actions_default"]}
        log_event(deps.state_dir, day, "DEFAULT_APPLIED", now=now, ticker=tk,
                  per_account=case["actions_default"])
        _apply_decision(case, now, deps)
        enqueue(st, f"⏰ Hết hạn, không có trả lời ⇒ áp MẶC ĐỊNH cho {tk}: " + ", ".join(
            f"{lab} {E.ACTION_VN[a]}" for lab, a in case["actions_default"].items()) + f" ({SHADOW_NOTE})",
            now=now)
        changed = True

    # (e) bộ máy bán (shadow) — mỗi phút
    if case.get("execution"):
        hp, _ = session_phase(now)
        phase = E.exchange_phase(hp, now, case.get("exchange"))
        bot_stop = os.path.exists(deps.bot_stop_path)
        snap = _snap(case, q, deps, now)
        for lab, ex in case["execution"].items():
            if ex["status"] != "EXECUTING":
                continue
            h = case["holdings"][lab]
            try:
                sellable = deps.market.positions(h["account_id"]).get(tk, {}).get("sellable", 0)
            except Exception as e:  # noqa: BLE001
                log_event(deps.state_dir, day, "POSITIONS_ERROR", now=now, ticker=tk, account=lab, error=str(e))
                health_alert(st, "positions", f"không đọc được vị thế {lab} khi đang bán {tk}: {str(e)[:150]}",
                             now, deps)
                changed = True
                continue
            mode0 = ex["mode"]
            intents, events = E.step_execution(ex, snap, phase, now, case.get("exchange"),
                                               sellable, bot_stop)
            if intents or events:
                log_event(deps.state_dir, day, "CUTLOSS_TICK", now=now, ticker=tk, account=lab,
                          phase=phase, snap=snap, intents=intents, events=events, sold=ex["sold"],
                          target=ex["target"], mode=ex["mode"])
                changed = True
            if ex["mode"] != mode0:
                enqueue(st, f"⚙️ {tk} {lab}: chế độ bán {E.MODE_VN.get(mode0, '-')} → "
                            f"{E.MODE_VN[ex['mode']]} | đã bán (mô phỏng) {ex['sold']:,}/"
                            f"{ex['target']:,}cp — lệnh dự định: " + "; ".join(
                                f"{i['kind_effective'] if 'kind_effective' in i else i['kind']} "
                                f"{i['qty']}@{i.get('price') or 'thị trường'}" for i in intents[:3]), now=now)
            if ex["status"] == "DONE":
                until = write_no_rebuy(deps.state_dir, tk, lab, day, h["book"])
                avg = E.avg_price(ex)
                enqueue(st, f"🏁 {tk} {lab}: XONG (mô phỏng) {ex['sold']:,}cp giá TB "
                            f"{avg:,.0f} — cấm mua lại tới {until} (shadow ledger)", now=now)
        if all(ex["status"] != "EXECUTING" for ex in case["execution"].values()):
            # dừng theo lệnh GIỮ của user ⇒ HOLD (vẫn nhận "BÁN" sau đó), chỉ bán đủ hết mới DONE
            case["status"] = "DONE" if all(ex["status"] == "DONE" for ex in case["execution"].values()) else "HOLD"
            changed = True
    if changed:
        _save(deps, day, st)


def _apply_decision(case, now, deps):
    """→ [(TK, lý do)] các TK bị bỏ qua vì no_auto_sell (b)."""
    per = case["decision"]["per_account"]
    skipped = []
    for lab, h in case["holdings"].items():
        act = per.get(lab, E.HOLD)
        if h.get("no_auto_sell") and act != E.HOLD:
            skipped.append((lab, h["no_auto_sell"]))
            log_event(deps.state_dir, now.date(), "NO_AUTO_SELL", now=now, ticker=case["ticker"], account=lab,
                      action=act, reason=h["no_auto_sell"])
            continue
        tgt = E.target_qty(act, h["qty"])
        ex = case["execution"].get(lab)
        if ex is None:
            if tgt > 0:
                case["execution"][lab] = E.new_execution(tgt, now)
            continue
        if act == E.HOLD:                           # user GIỮ giữa chừng ⇒ dừng phần còn lại
            ex["status"], ex["open"] = "STOPPED_BY_USER", []
        else:
            ex["target"] = max(tgt, ex["sold"])
            if ex["status"] == "STOPPED_BY_USER":
                ex["status"] = "EXECUTING"
    if case["execution"]:
        case["status"] = "EXECUTING"
    if not any(ex["status"] == "EXECUTING" for ex in case["execution"].values()):
        case["status"] = "HOLD"
    return skipped


class RunKilled(Exception):
    """Lượt chạy bị SIGTERM (vd `timeout 55`) — để crash_alert báo người, không chết im lặng."""


def _scan(now, deps, st):
    day = now.date()
    errs = []
    uni = deps.universe if deps.universe is not None else build_universe(
        day, deps.market, deps.accounts, deps.state_dir, errors=errs)
    for e in errs:
        health_alert(st, "positions", e, now, deps)
    vl, vr = deps.market.vni(now)
    if not (vl and vr):
        why = getattr(deps.market, "vni_note", None)
        health_alert(st, "vnindex", f"không đọc được VNINDEX (last={vl}, ref={vr}"
                                    f"{'; ' + why if why else ''}) ⇒ idio = ret; mọi kích hoạt "
                                    f"lượt này gộp thành cảnh báo cả thị trường", now, deps)
    hits, alt, n_q, n_err = [], [], 0, 0
    for tk, u in sorted(uni.items()):
        if tk in st["cases"]:
            continue                                    # tối đa 1 lần/ngày/mã
        q = deps.market.quote(tk)
        n_q += 1
        if q.get("error"):
            n_err += 1
            log_event(deps.state_dir, day, "QUOTE_ERROR", now=now, ticker=tk, quote=q)
            continue
        tr = E.trigger_check(q.get("last"), q.get("ref"), q.get("floor"), vl, vr)
        trr = E.trigger_check_rel(q.get("last"), q.get("ref"), q.get("floor"), vl, vr, q.get("exchange"))
        if (tr and tr["hit"]) or (trr and trr["hit"]):
            alt.append({"ticker": tk, "exchange": q.get("exchange"), "ret": tr["ret"], "idio": tr["idio"],
                        "hit_cur": bool(tr["hit"]), "hit_rel": bool(trr["hit"]),
                        "held": bool(u["holdings"])})
        if tr and tr["hit"]:
            hits.append((tk, u, tr, q))
    s = _stats(st)
    s["scans"] += 1
    s["quotes"] += n_q
    s["quote_errors"] += n_err
    if n_q >= 4 and n_err / n_q > QUOTE_ERR_ALERT:
        health_alert(st, "quote", f"{n_err}/{n_q} mã lỗi lấy giá DNSE trong lượt quét {now:%H:%M} ⇒ cổng giá "
                                  f"gần như MÙ", now, deps)
    if alt:
        log_event(deps.state_dir, day, "ALT_THRESHOLD", now=now, rows=alt,
                  rel=E.REL_TRIG, rel_idio=E.REL_IDIO)
        for a in alt:
            for k, f in (("alt_cur", "hit_cur"), ("alt_rel", "hit_rel")):
                if a[f] and a["ticker"] not in s[k]:
                    s[k].append(a["ticker"])
    reason = E.market_wide_reason([h[2] for h in hits])
    opened = []
    if reason:
        mw = st.setdefault("market_wide", {})
        new = [h for h in hits if h[0] not in mw]
        for tk, u, tr, q in hits:
            mw.setdefault(tk, {"first": _iso(now), "reason": reason, "ret": tr["ret"],
                               "held": {lab: h["qty"] for lab, h in u["holdings"].items()}})
        log_event(deps.state_dir, day, "MARKET_WIDE", now=now, reason=reason,
                  tickers=[h[0] for h in hits], new=[h[0] for h in new])
        if new:
            s["market_wide"] += 1
            rows = "\n".join(
                f"  • {tk} {tr['ret']*100:+.1f}%" + (" CHẠM SÀN" if tr["at_floor"] else "")
                + ("".join(f" | giữ {lab} {h['qty']:,}cp" for lab, h in u["holdings"].items()) or " | không giữ")
                + (" | có lệnh MUA trong plan" if u["buys"] else "") for tk, u, tr, q in new)
            enqueue(st, f"🌐 CẢNH BÁO GỘP — CẢ THỊ TRƯỜNG ({reason}), {now:%H:%M}: {len(new)} mã mới kích hoạt "
                        f"(tổng {len(hits)} lượt này)\n{rows}\n  ⇒ KHÔNG dispatch điều tra từng mã, KHÔNG tự "
                        f"hành động; mã sẽ được xét lại riêng nếu lượt sau không còn là biến động chung. "
                        f"Anh tự đánh giá. ({SHADOW_NOTE})", mention=True, now=now)
    else:
        for tk, u, tr, q in hits:
            opened.append(tk)
            open_case(tk, u, tr, q, now, deps, st)
    st["last_scan"] = _iso(now)
    log_event(deps.state_dir, day, "SCAN", now=now, n_universe=len(uni), triggered=opened,
              market_wide=reason, vni=[vl, vr], quote_errors=n_err)
    _save(deps, day, st)
    return opened


def _eod_summary(st, now, deps):
    if now.time() < EOD_SUMMARY_AT or st.get("eod_summary_sent"):
        return
    s = _stats(st)
    vs = s["verdicts"]

    def n(src, comp=None):
        return sum(1 for v in vs if v["source"] == src and (comp is None or v["compressed"] == comp))
    lat = sorted(v["latency_min"] for v in vs if v["source"] == "agent")
    med = lat[len(lat) // 2] if lat else None
    crashes = 0
    p = os.path.join(deps.state_dir, f"shadow_{now.date().isoformat()}.jsonl")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            crashes = sum(1 for x in f if '"kind": "CRASH"' in x)
    st["eod_summary_sent"] = _iso(now)
    enqueue(st, f"📊 Tóm tắt SHADOW intraday-watch {now:%d/%m}: {s['scans']} lượt quét · {s['triggers']} kích "
                f"hoạt · {s['market_wide']} cảnh báo gộp · {s['dispatches']} điều tra ({s['dispatch_fail']} lỗi, "
                f"{s['dispatch_skipped']} bị chặn) · phán quyết agent {n('agent')} / hết giờ {n('timeout')} / "
                f"không điều tra {n('no_dispatch')} (rút gọn: agent {n('agent', True)}, hết giờ "
                f"{n('timeout', True)}; thường: agent {n('agent', False)}, hết giờ {n('timeout', False)}) · trễ "
                f"trung vị phán quyết agent {med if med is not None else '-'}' · ngưỡng tương đối "
                f"{len(s['alt_rel'])} mã vs hiện hành {len(s['alt_cur'])} mã · lỗi giá {s['quote_errors']}/"
                f"{s['quotes']} · lỗi gửi tin {s['notify_fail']} · lỗi đọc trả lời {s['reply_read_errors']} · "
                f"crash {crashes}" + (f" · dispatch DỪNG: {st['dispatch_halted']}" if st.get("dispatch_halted")
                                      else "") + f" ({SHADOW_NOTE})", ("discord",), now=now)


def run_tick(now, deps):
    from trading_bot.vn_market import is_holiday
    day = now.date()
    if now.weekday() >= 5 or is_holiday(day):
        return {"skipped": "ngày không giao dịch"}
    t = now.time()
    if REMINDER_WINDOW[0] <= t < REMINDER_WINDOW[1]:
        fn = _run_reminder
    elif dt.time(9, 0) <= t < dt.time(15, 0):
        fn = _run_locked
    else:
        return {"skipped": "ngoài giờ"}
    deps.t_start = time.monotonic()
    os.makedirs(deps.state_dir, exist_ok=True)
    with open(os.path.join(deps.state_dir, ".lock"), "w") as lockf:
        try:
            fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {"skipped": "lượt trước còn chạy"}
        return fn(now, deps)


def _run_reminder(now, deps):
    """08:25-08:59: CHỈ nhắc ca hoãn qua đêm (c) + gửi nốt tin tồn. Không quét, không bán."""
    day = now.date()
    st = load_state(deps.state_dir, day)
    n = 0
    for tk, c in st["cases"].items():
        if c.get("reply_deferred") and not c.get("decision") and c.get("reply_deadline"):
            acts = ", ".join(f"{lab} {E.ACTION_VN[a]}" for lab, a in (c.get("actions_default") or {}).items())
            vv = c.get("verdict") or {}
            if enqueue(st, f"⏰ NHẮC 08:30 — {tk}: phán quyết {E.VERDICT_VN.get(vv.get('label'), '?')} "
                           f"({vv.get('source')}); mặc định [{acts or 'không giữ'}] sẽ áp lúc "
                           f"{_p(c['reply_deadline']):%H:%M} nếu anh không trả lời. Lệnh: {_reply_cmds(tk)}",
                       mention=True, key=f"remind:{tk}:{day}", now=now):
                n += 1
    _save(deps, day, st)
    flush_outbox(st, deps, now)
    _save(deps, day, st)
    return {"reminded": n}


def _run_locked(now, deps):
    from trading_bot.vn_market import session_phase
    day = now.date()
    hp, _ = session_phase(now)
    st = load_state(deps.state_dir, day)
    _stats(st)
    flush_outbox(st, deps, now)                       # tin tồn từ lượt bị cắt
    opened = _scan(now, deps, st) if _scan_due(now, st.get("last_scan"), hp) else []
    _pending_work(st, deps, now)
    for tk, case in list(st["cases"].items()):
        pending_verdict = not case.get("verdict") and case.get("investigation")
        if (case.get("status") not in TERMINAL or pending_verdict) and tk not in opened:
            process_case(case, now, deps, st)
    _eod_summary(st, now, deps)
    _save(deps, day, st)
    flush_outbox(st, deps, now)
    _save(deps, day, st)
    return {"opened": opened, "open_cases": [t for t, c in st["cases"].items() if c["status"] not in TERMINAL]}


# ============================================================== CLI
def cmd_verdict(a):
    if a.label not in (E.BROKEN, E.NOISE, E.UNCLEAR):
        sys.exit(f"label phải là BROKEN|NOISE|UNCLEAR, nhận {a.label}")
    p = verdict_path(a.state_dir, dt.date.fromisoformat(a.date), a.ticker)
    if os.path.exists(p):
        print(f"đã có phán quyết {p} — giữ bản đầu (không ghi đè)")
        return
    _atomic_json(p, {"ticker": a.ticker.upper(), "label": a.label, "summary": a.summary[:600],
                     "at": _iso(_now())})
    print(f"ghi {p}")


def main(argv=None, market_factory=None, notifier=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--no-dispatch", action="store_true")
    r.add_argument("--dry-notify", action="store_true")
    r.add_argument("--dispatch-watch", action="store_true",
                   help="dispatch điều tra cả mã chỉ-watchlist (mặc định: chỉ báo)")
    r.add_argument("--state-dir", default=STATE_DIR)
    v = sub.add_parser("verdict")
    v.add_argument("--date", required=True)
    v.add_argument("--ticker", required=True)
    v.add_argument("--label", required=True)
    v.add_argument("--summary", required=True)
    v.add_argument("--state-dir", default=STATE_DIR)
    s = sub.add_parser("status")
    s.add_argument("--date")
    s.add_argument("--state-dir", default=STATE_DIR)
    a = ap.parse_args(argv)
    if a.cmd == "verdict":
        return cmd_verdict(a)
    if a.cmd == "status":
        d = dt.date.fromisoformat(a.date) if a.date else _now().date()
        print(json.dumps(_read_json(state_path(a.state_dir, d), {}), ensure_ascii=False, indent=1))
        return
    notifier = notifier or Notifier(dry=a.dry_notify)
    # `timeout 55` của cron gửi SIGTERM: biến thành ngoại lệ để đi qua crash_alert (không chết im lặng)
    import signal

    def _on_term(signum, frame):
        raise RunKilled(f"nhận tín hiệu {signum} (timeout cron?) — lượt bị cắt giữa chừng")
    signal.signal(signal.SIGTERM, _on_term)
    try:
        market = (market_factory or LiveMarket)()
    except Exception:       # noqa: BLE001 — khởi tạo DNSE hỏng ⇒ cảnh báo (1 lần/ngày), không im lặng
        crash_alert(a.state_dir, "init", traceback.format_exc(), notifier)
        raise SystemExit(1)
    try:
        deps = Deps(market, notifier, a.state_dir, dispatch=None if a.no_dispatch else True,
                    dispatch_watch=a.dispatch_watch)
        print(json.dumps(run_tick(_now(), deps), ensure_ascii=False))
    except Exception:       # noqa: BLE001
        crash_alert(a.state_dir, "crash", traceback.format_exc(), notifier)
        raise


if __name__ == "__main__":
    main()
