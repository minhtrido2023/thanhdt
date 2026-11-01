#!/usr/bin/env python3
"""intraday_price_watch.py — cổng giá TRONG PHIÊN ⇒ BÁO NGAY + HỒ SƠ DD KHỦNG HOẢNG 7 ngày.

QUYẾT ĐỊNH USER 2026-11-01 20:05 ICT (nguyên văn): "việc cutloss không tự làm. Nếu có tín hiệu bán
mạnh, chỉ cần làm due diligence dạng khủng hoảng lấy tin trong vòng 1 tuần xử lý là được. Tôi sẽ
phải quyết bán, không thì mặc định giữ". (job Taylor_20261101_130722)
⇒ KHÔNG còn đường bán nào, kể cả mô phỏng/shadow-intent (đã gỡ: phán quyết 20/30' → mặc định
GÃY=bán hết / CHƯA RÕ=bán 50%, đọc trả lời kiểu "SHADOW GIỮ/BÁN <mã>", 4 chế độ bán, ATO/ATC, cấm mua lại).
Mặc định MỌI trường hợp = GIỮ. Bán chỉ khi user ra lệnh rõ qua kênh đặt lệnh thường (DollarBill/
Mafee) — watcher này KHÔNG đọc lệnh bán, KHÔNG đặt/huỷ/sửa lệnh.

Luồng:
  1. Kích hoạt (ngưỡng GIỮ NGUYÊN: ret ≤ −5% ∧ idio ≤ −4%; chạm sàn chỉ mở ca riêng khi idio đạt;
     gộp cả thị trường như cũ) ⇒ báo NGAY Trading Daily + Telegram (+ email) và MỞ HỒ SƠ
     `data/intraday_watch/crisis_dd/<MÃ>_<ngày>/` (dossier.json do watcher ghi; DOSSIER.md +
     notes/ do agent ghi qua lệnh `dd-note`). Ngày 1: dispatch tóm tắt nhanh (legal-vn + tin DN/BCTC/ngành).
  2. Ngày 2..7 (ngày LỊCH; cron chỉ chạy ngày giao dịch): mỗi ngày 1 dispatch cập nhật hồ sơ.
  3. Nhắc user ngày 3 và ngày 6 nếu hồ sơ còn mở (lượt đầu tiên có ngày ≥ mốc).
  4. Hết 7 ngày hoặc agent báo SỰ KIỆN LỚN (`--major-event`) ⇒ dispatch báo cáo KẾT LUẬN GÃY / NHIỄU /
     CHƯA RÕ để user quyết. Không trả lời = GIỮ. Agent không ra kết luận ⇒ CHƯA RÕ (no_agent), GIỮ.
  5. Mã kích hoạt lại khi hồ sơ còn mở ⇒ chỉ báo + ghi vào hồ sơ (không mở hồ sơ thứ 2).
  6. Từ 14:55 ghi 1 dòng EOD_OOS/ngày (vni_day + ret_close mỗi ca/mã gộp) — dữ liệu OOS rẻ, giữ.

DNSE chỉ được gọi qua `ReadOnlyDNSE` (whitelist inquiry: secdef/latest_trade/latest_quote/positions/
orders/ohlc) — gọi bất kỳ hàm nào khác ném PermissionError. Không ghi vào `dnse_raw_*.jsonl` (§12).

Nguồn giờ: `trading_bot.vn_market.now_ict()` (§16). Tiền: chỉ dùng `total_nav` của
`active_nav_<TK>.json` làm MẪU SỐ HIỂN THỊ %NAV (§25). Same-day giá = DNSE, không BQ (§6).

Idempotency (§5): state ghi nguyên tử (tmp + os.replace); không tác động ngoài nào chạy trước khi
ý định của nó đã nằm trên đĩa.
  - Báo: HỘP THƯ ĐI bền (`st["outbox"]`), at-least-once, kênh lỗi thử lại ≤ NOTIFY_MAX_ATTEMPTS.
  - Dispatch DD: at-most-once — ghi cờ vào dossier.json TRƯỚC khi gọi; lượt sau thấy cờ mà không có
    job ⇒ KHÔNG dispatch lại, ghi chú + báo.
  - Ngân sách thời gian mỗi lượt RUN_BUDGET_S (< `timeout 55` của cron).

Danh tính dispatch: DISPATCH_FROM=intraday_watch, `--retries 0`, trần/ngày, dừng dispatch tới hết
ngày sau 1 job chết không ghi gì ⇒ không tự làm vấp circuit breaker Taylor.

Dùng:
  intraday_price_watch.py run [--no-dispatch] [--dry-notify] [--state-dir D]
  intraday_price_watch.py dd-note --dossier MÃ_YYYY-MM-DD --kind quick|daily|final --summary "..."
                                  [--label BROKEN|NOISE|UNCLEAR] [--major-event] [--detail-file F.md]
  intraday_price_watch.py status [--date YYYY-MM-DD]

Cron (ĐÃ CÀI, KHÔNG đổi ở thay đổi này; host parse giờ UTC: 02-07 ⇔ 09-14 ICT, 1:30 ⇔ 08:30 ICT):
  * 2-7 * * 1-5 … intraday_price_watch.py run   (quét + hồ sơ)
  30 1 * * 1-5 … intraday_price_watch.py run    (08:25-08:59 = chỉ việc hồ sơ: nhắc/cập nhật/kết luận)
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
CHANNELS = os.path.join(MIKE, "kb", "discord_channels.json")
NOTIFY_THREAD = os.path.join(MIKE, "bin", "notify_thread.sh")
NOTIFY_TG = os.path.join(MIKE, "bin", "notify_telegram.sh")
EMAIL = os.path.join(MIKE, "bin", "send_macro_note_email.py")
DISPATCH = os.path.join(MIKE, "bin", "dispatch.sh")
WATCH_ACCOUNTS = ("SpaceX", "ZaloPay")
SCAN_START, SCAN_END = dt.time(9, 15), dt.time(14, 30)
SCAN_EVERY_MIN = 15
TAG = "[SHADOW]"
JOBS_DIR = os.path.join(MIKE, "bus", "jobs")
DISPATCH_FROM_ID = "intraday_watch"      # KHÔNG phải tên agent (xem docstring)
JOB_DEAD = ("failed", "timeout", "usage_limited", "cancelled", "orphaned", "done")
DD_DIR_NAME = "crisis_dd"

# ---- vận hành (cấu hình được) ----
MAX_DISPATCH_PER_SCAN = 2          # hồ sơ MỚI dispatch tối đa mỗi lượt quét (ưu tiên vị thế lớn)
MAX_DISPATCH_PER_DAY = 3           # hồ sơ MỚI dispatch tối đa mỗi ngày
MAX_DD_DISPATCH_PER_DAY = 6        # dispatch cập nhật/kết luận hồ sơ cũ tối đa mỗi ngày
STOP_DISPATCH_AFTER_TIMEOUT = True # 1 job chết không ghi gì ⇒ dừng dispatch tới hết ngày
DISPATCH_SUBPROC_TIMEOUT = 25      # giây chờ dispatch.sh --bg trả job id
DD_JOB_TIMEOUT_S = {"quick": 1500, "daily": 1500, "final": 1800}
RUN_BUDGET_S = 40                  # ngân sách mỗi lượt (< timeout 55 của cron)
NOTIFY_MAX_ATTEMPTS = 5
REMINDER_WINDOW = (dt.time(8, 25), dt.time(9, 0))   # 08:30: chỉ việc hồ sơ (không quét)
EOD_SUMMARY_AT = dt.time(14, 50)
EOD_OOS_AT = dt.time(14, 55)       # (D) ghi vni_day/ret_close mỗi ca ⇒ bộ OOS thật
EOD_OOS_ALERT_AT = dt.time(14, 58) # tới giờ này vẫn chưa ghi được ⇒ cảnh báo sức khoẻ
QUOTE_ERR_ALERT = 0.5              # tỉ lệ lỗi lấy giá trong 1 lượt quét ⇒ cảnh báo sức khoẻ
HEALTH_ALERT_EVERY_MIN = 60        # cảnh báo sức khoẻ cùng loại tối đa 1 lần/60'
VNI_MAX_AGE_MIN = 5                # bar VNINDEX cuối cũ hơn ⇒ coi như không đọc được (DNSE cache theo URL)
OPEN_GRACE_MIN = 2                 # DNSE chỉ phát bar 1 phút SAU khi phút đó đóng (đo 08/10)
HOLD_NOTE = ("MẶC ĐỊNH GIỮ — hệ thống KHÔNG tự bán; muốn bán anh ra lệnh rõ qua kênh đặt lệnh "
             "thường. Không trả lời = GIỮ")


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
        n = now.replace(tzinfo=None)
        grace = dt.timedelta(minutes=OPEN_GRACE_MIN)
        # 09:15 + vài phút đầu: chưa có bar nào là BÌNH THƯỜNG, không phải nguồn hỏng ⇒ _scan không cảnh báo
        self.vni_pending_open = not bars and \
            dt.timedelta(0) <= n - n.replace(hour=9, minute=15, second=0, microsecond=0) < grace
        self.vni_note = None if bars else "không có bar 1 phút nào"
        if bars:
            # nghỉ trưa / sau 14:30 không có bar mới — so với mốc cuối phiên đang mở, không với `now`
            ref_t = n
            if dt.time(11, 30) <= n.time() < (dt.datetime.combine(n.date(), dt.time(13)) + grace).time():
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


# ============================================================== báo + dispatch
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


def dd_prompt(dos, kind, note_cmd, now):
    """Prompt dispatch cho 1 bước hồ sơ DD khủng hoảng (quick = ngày 1 / daily / final)."""
    tk, tr = dos["ticker"], dos["trigger"]
    held = ", ".join(f"{a} {h['qty']}cp ({h['book']})" for a, h in dos["holdings"].items()) or "không giữ"
    n = E.dd_day(dt.date.fromisoformat(dos["t0"][:10]), now.date())
    common = (f"[CRISIS-DD {tk} — hồ sơ {dos['id']}] Mã {tk} kích hoạt cổng giá lúc {dos['t0'][:16]} ICT: "
              f"{tr['reason']} (ret {tr['ret']*100:+.1f}%, VNINDEX {(tr['vni_ret'] or 0)*100:+.1f}%). Đang giữ: "
              f"{held}. Quyết định user 2026-11-01: KHÔNG tự bán; DD dạng khủng hoảng trong 7 ngày, user quyết "
              f"bán, mặc định GIỮ. Hồ sơ: {dos['dir']}/DOSSIER.md (đọc các mục trước). ")
    if kind == "quick":
        task = ("Việc NGÀY 1 — TÓM TẮT NHANH: (1) gọi Agent(subagent_type='legal-vn') đọc tin pháp lý 7 ngày "
                f"gần nhất về {tk} (khởi tố, thanh tra, xử phạt UBCKNN, đình chỉ/hạn chế giao dịch); (2) tự tìm "
                "tin DN (CBTT, giao dịch nội bộ/cổ đông lớn, bán giải chấp), BCTC/KQKD gần nhất, tin ngành; "
                "(3) viết bản tóm tắt nhanh: chuyện gì xảy ra, có dính pháp nhân/tài sản lõi không, câu hỏi "
                "còn mở cần theo dõi các ngày tới. Không có tin thì nói thẳng 'chưa thấy tin'. ")
    elif kind == "daily":
        task = (f"Việc NGÀY {n}/{E.DD_WINDOW_DAYS} — CẬP NHẬT: tìm tin MỚI kể từ mục trước trong hồ sơ "
                "(legal-vn cho pháp lý; CBTT, BCTC, ngành), trả lời các câu hỏi còn mở. Nếu có SỰ KIỆN LỚN "
                "(khởi tố pháp nhân/lãnh đạo chủ chốt, gian lận BCTC, mất khả năng thanh toán, đình chỉ giao "
                "dịch, KQKD sụp) thêm cờ --major-event để hệ thống xin báo cáo kết luận ngay. ")
    else:
        task = ("Việc BÁO CÁO KẾT LUẬN: tổng hợp toàn bộ hồ sơ, kết luận đúng 1 nhãn — BROKEN (= GÃY: pháp lý "
                "dính pháp nhân/tài sản lõi, gian lận, KQKD sụp, mất khả năng thanh toán) / NOISE (= NHIỄU: "
                "không có tin, tin cá nhân không dính lõi, cả ngành) / UNCLEAR (= CHƯA RÕ); nêu bằng chứng + "
                "nguồn, rủi ro nếu giữ, điều gì sẽ đổi kết luận. Đây là tư liệu để USER QUYẾT, không phải lệnh. ")
    return (common + task + "Viết chi tiết (có nguồn, link) ra 1 file .md rồi GHI bằng đúng lệnh: "
            f"{note_cmd} --summary 'TÓM TẮT ≤600 ký tự' --detail-file <file.md>"
            + (" --label LABEL" if kind == "final" else "")
            + ". KHÔNG đặt/huỷ/sửa lệnh, KHÔNG sửa plan, KHÔNG đề xuất bán tự động.")


def dispatch_argv(prompt, kind, dispatch_bin=DISPATCH):
    """argv THẬT gửi dispatch.sh (selfcheck chạy đúng argv này vào stub). --retries 0 ⇒ 1 lần hết giờ
    = đúng 1 lỗi ở circuit."""
    return [dispatch_bin, "Taylor", prompt, "--bg", "--thread", "trading_daily",
            "--timeout", str(DD_JOB_TIMEOUT_S[kind]), "--retries", "0", "--model", "opus", "--effort", "medium"]


def dispatch_dd(dos, kind, note_cmd, now, dry=False, dispatch_bin=DISPATCH):
    """→ (job | "DRY" | "issued" | None, info). None = dispatch HỎNG (info = lỗi thật)."""
    prompt = dd_prompt(dos, kind, note_cmd, now)
    if dry:
        return "DRY", prompt
    env = dict(os.environ, DISPATCH_FROM=DISPATCH_FROM_ID)
    try:
        r = subprocess.run(dispatch_argv(prompt, kind, dispatch_bin),
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
    """State NGÀY (ca kích hoạt trong ngày + outbox). Ca KHÔNG carry sang phiên sau: phần sống qua
    nhiều ngày là hồ sơ DD (crisis_dd/). Chỉ tin chưa gửi xong của phiên trước được gửi nốt."""
    st = _read_json(state_path(state_dir, day))
    if st:
        return st
    st = {"date": day.isoformat(), "last_scan": None, "cases": {}, "outbox": []}
    prev = _read_json(state_path(state_dir, prev_trading_day(day)))
    st["outbox"] = [m for m in ((prev or {}).get("outbox") or []) if m.get("left")
                    and m.get("attempts", 0) < NOTIFY_MAX_ATTEMPTS]
    return st


# -------------------------------------------------------------- hồ sơ DD khủng hoảng
def dd_root(state_dir):
    return os.path.join(state_dir, DD_DIR_NAME)


def dd_dir(state_dir, did):
    return os.path.join(dd_root(state_dir), did)


def dd_json(state_dir, did):
    return os.path.join(dd_dir(state_dir, did), "dossier.json")


def load_dossiers(state_dir, status=None):
    root = dd_root(state_dir)
    out = []
    for did in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        d = _read_json(dd_json(state_dir, did))
        if d and (status is None or d.get("status") == status):
            out.append(d)
    return out


def open_dossier_for(state_dir, tk):
    for d in load_dossiers(state_dir, "OPEN"):
        if d["ticker"] == tk:
            return d
    return None


def save_dossier(state_dir, dos):
    _atomic_json(dd_json(state_dir, dos["id"]), dos)


def create_dossier(state_dir, case):
    """Idempotent theo id = MÃ_ngàyT0. Watcher ghi dossier.json; DOSSIER.md + notes/ là của agent."""
    did = f"{case['ticker']}_{case['t0'][:10]}"
    d = _read_json(dd_json(state_dir, did))
    if d:
        return d
    p = dd_dir(state_dir, did)
    os.makedirs(os.path.join(p, "notes"), exist_ok=True)
    d = {"id": did, "dir": p, "ticker": case["ticker"], "t0": case["t0"], "trigger": case["trigger"],
         "t0_quote": case.get("t0_quote"), "holdings": case["holdings"], "status": "OPEN", "jobs": {},
         "relayed": [], "reminders": [], "daily_requested": [], "retriggers": [], "final_requested": None,
         "major_event": None, "conclusion": None, "default": "HOLD"}
    md = os.path.join(p, "DOSSIER.md")
    if not os.path.exists(md):
        with open(md, "w", encoding="utf-8") as f:
            f.write(f"# Hồ sơ DD khủng hoảng — {case['ticker']} (mở {case['t0'][:16]} ICT)\n\n"
                    f"Kích hoạt: {case['trigger']['reason']} (ret {case['trigger']['ret']*100:+.1f}%).\n"
                    f"Quyết định user 2026-11-01: KHÔNG tự bán; thu thập tin 7 ngày; user quyết bán, "
                    f"MẶC ĐỊNH GIỮ.\n\n")
    save_dossier(state_dir, d)
    return d


def note_name(kind, day_n):
    return {"quick": "quick.json", "final": "final.json"}.get(kind, f"daily_d{day_n}.json")


def read_notes(state_dir, did):
    nd = os.path.join(dd_dir(state_dir, did), "notes")
    out = []
    for fn in sorted(os.listdir(nd)) if os.path.isdir(nd) else []:
        if fn.endswith(".json"):
            n = _read_json(os.path.join(nd, fn))
            if n:
                out.append({**n, "file": fn})
    return out


# ============================================================== 1 nhịp
class Deps:
    """Gói phụ thuộc ngoài — selfcheck thay bằng giả."""

    def __init__(self, market, notifier, state_dir, dispatch=True, accounts=None, universe=None, nav=nav_info,
                 dispatch_watch=False, dispatch_bin=DISPATCH, job_status=job_status, budget_s=RUN_BUDGET_S):
        self.market, self.notifier, self.state_dir = market, notifier, state_dir
        self.dispatch_watch, self.dispatch = dispatch_watch, dispatch
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
    for k in ("scans", "triggers", "market_wide", "market_wide_relabel", "dispatches", "dispatch_fail",
              "dispatch_skipped", "dd_dispatches", "dd_notes", "dd_reminders", "dd_concluded", "quotes",
              "quote_errors", "notify_fail"):
        s.setdefault(k, 0)
    for k in ("alt_cur", "alt_rel"):
        s.setdefault(k, [])
    return s


# -------------------------------------------------------------- hộp thư đi (at-least-once)
def enqueue(st, msg, channels=("discord", "telegram"), subject=None, mention=False, key=None, now=None):
    """Xếp 1 tin vào hộp thư đi trong state. Caller PHẢI ghi state trước khi flush_outbox gửi.
    key: chống xếp trùng."""
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
        lines.append(f"  • {lab}: {h['qty']:,}cp ≈ {val/1e6:,.1f}tr"
                     + (f" = {val/nav*100:.1f}% NAV (NAV {str(nav_at)[:16]})" if nav else "")
                     + (f", lãi/lỗ {pnl:+.1f}% (giá vốn {h['cost']:,.0f})" if pnl is not None else "")
                     + f", book {h['book']}" + (" ⚠️ book KHÔNG xác định" if h["book"] == E.UNKNOWN else "")
                     + (f" ⛔ {h['no_auto_sell']}" if h.get("no_auto_sell") else ""))
    return "\n".join(lines) or "  • không giữ (watchlist / lệnh mua)"


def open_case(tk, u, tr, q, now, deps, st):
    """Ghi ca kích hoạt vào state NGÀY — KHÔNG tác động ngoài (hồ sơ/dispatch/tin T0 làm ở _pending_work
    sau khi state đã lên đĩa)."""
    day = now.date()
    case = {"ticker": tk, "t0": _iso(now), "trigger": tr, "exchange": q.get("exchange"),
            "exchange_known": q.get("exchange_known"), "holdings": u["holdings"], "watch": u.get("watch"),
            "deferred_buys": [], "t0_quote": {k: q.get(k) for k in ("last", "ref", "floor")},
            "t0_pending": True}
    for b in u["buys"]:
        try:
            live = deps.market.open_buys(b["account_id"], tk)
        except Exception as e:      # noqa: BLE001
            live = [{"error": str(e)}]
        case["deferred_buys"].append({**b, "live_orders": live,
                                      "would": "HUỶ lệnh đã ra sàn" if live else "GỠ khỏi plan trước khi bot đặt"})
    case["watch_only"] = not case["holdings"] and not case["deferred_buys"]
    existing = open_dossier_for(deps.state_dir, tk)
    if case["watch_only"] and not deps.dispatch_watch:
        case["status"], case["need_dossier"] = "NO_POSITION", False
    elif existing:
        case["status"], case["need_dossier"], case["dossier"] = "DD_EXISTING", False, existing["id"]
    else:
        case["status"], case["need_dossier"] = "DD_OPEN", True
    st["cases"][tk] = case
    _stats(st)["triggers"] += 1
    log_event(deps.state_dir, day, "TRIGGER", now=now, ticker=tk, trigger=tr, quote=q,
              holdings=case["holdings"], deferred_buys=case["deferred_buys"], status=case["status"])
    return case


def _t0_msg(case, deps):
    tk, tr, q = case["ticker"], case["trigger"], case.get("t0_quote") or {}
    t0 = _p(case["t0"])
    buys = "".join(f"\n  🛑 lệnh MUA {b['account']} {b.get('qty')}cp ({b.get('book')}) ⇒ bản live sẽ "
                   f"{b['would']} (shadow: CHỈ ghi log)" for b in case["deferred_buys"])
    inv = case.get("investigation") or {}
    if case["status"] == "NO_POSITION":
        dd = "  ℹ️ chỉ watchlist (không giữ, không lệnh mua) ⇒ KHÔNG mở hồ sơ DD"
    elif case["status"] == "DD_EXISTING":
        dd = (f"  📂 hồ sơ DD khủng hoảng {case['dossier']} ĐANG MỞ ⇒ ghi lần kích hoạt này vào hồ sơ, "
              f"không mở hồ sơ mới")
    elif inv.get("job"):
        dd = (f"  📂 MỞ HỒ SƠ DD KHỦNG HOẢNG {case.get('dossier')} (7 ngày; job ngày 1 {inv['job']}: tóm tắt "
              f"nhanh legal-vn + tin DN/BCTC/ngành). Nhắc anh ngày 3 và 6; hết 7 ngày ⇒ báo cáo kết luận.")
    else:
        dd = (f"  📂 mở hồ sơ {case.get('dossier')} nhưng ⚠️⚠️ KHÔNG dispatch được tóm tắt ngày 1 — "
              f"{inv.get('skipped') or inv.get('note') or '?'}. ANH CẦN TỰ XEM TIN {tk}.")
    return (f"🚨 CỔNG GIÁ TRONG PHIÊN — {tk} {t0:%H:%M}: {tr['reason']}\n"
            f"  giá {_fmt(q.get('last'))} (TC {_fmt(q.get('ref'))}, sàn {_fmt(q.get('floor'))}) | VNINDEX "
            f"{(tr['vni_ret'] or 0)*100:+.1f}%" + (" ⚠️ không đọc được VNINDEX" if tr["vni_missing"] else "")
            + f"\n{_fmt_hold(case, deps, q)}{buys}\n{dd}\n  ⇒ {HOLD_NOTE}.")


def _dispatch_gate(st, deps, new=True, key=None):
    if deps.dispatch is None:
        return False, "chạy với --no-dispatch"
    if st.get("dispatch_halted"):
        return False, f"dispatch đã DỪNG tới hết hôm nay: {st['dispatch_halted']}"
    s = _stats(st)
    if new:
        if s["dispatches"] >= MAX_DISPATCH_PER_DAY:
            return False, f"đã đủ trần {MAX_DISPATCH_PER_DAY} hồ sơ mới/ngày"
        if (st.get("dispatch_by_scan") or {}).get(key, 0) >= MAX_DISPATCH_PER_SCAN:
            return False, f"đã đủ trần {MAX_DISPATCH_PER_SCAN} hồ sơ mới/lượt quét"
    elif s["dd_dispatches"] >= MAX_DD_DISPATCH_PER_DAY:
        return False, f"đã đủ trần {MAX_DD_DISPATCH_PER_DAY} dispatch cập nhật hồ sơ/ngày"
    return True, ""


def _note_cmd(deps, did, kind):
    return (f"{sys.executable} {os.path.abspath(__file__)} dd-note --dossier {did} --kind {kind} "
            f"--state-dir {deps.state_dir}")


def _dd_dispatch(st, deps, now, dos, kind, jkey, day_n=1):
    """Dispatch at-most-once 1 bước hồ sơ: cờ vào dossier.json TRƯỚC khi gọi. → job | None."""
    day = now.date()
    dos["jobs"][jkey] = {"kind": kind, "day": day_n, "dispatch_attempted_at": _iso(now)}
    save_dossier(deps.state_dir, dos)
    job, info = dispatch_dd(dos, kind, _note_cmd(deps, dos["id"], kind), now, dry=not deps.dispatch,
                            dispatch_bin=deps.dispatch_bin)
    dos["jobs"][jkey].update({"job": job, "note": None if job else info})
    save_dossier(deps.state_dir, dos)
    if not job:
        _stats(st)["dispatch_fail"] += 1
    log_event(deps.state_dir, day, "DD_DISPATCH", now=now, dossier=dos["id"], step=kind, key=jkey, job=job,
              info=info[:3000])
    return job


def _case_value(case):
    last = (case.get("t0_quote") or {}).get("last") or 0
    return sum(h["qty"] for h in case["holdings"].values()) * last


def _pending_work(st, deps, now):
    """Ca MỚI: tạo hồ sơ + dispatch ngày 1 (at-most-once) rồi xếp tin T0 — vị thế lớn trước."""
    day = now.date()
    for tk, case in sorted(st["cases"].items(), key=lambda kv: -_case_value(kv[1])):
        if not (case.get("need_dossier") or case.get("t0_pending")):
            continue
        if deps.over_budget():
            log_event(deps.state_dir, day, "BUDGET", now=now, where="pending_work", ticker=tk)
            return
        if case.get("need_dossier"):
            dos = create_dossier(deps.state_dir, case)
            case["dossier"] = dos["id"]
            jq = dos["jobs"].get("quick")
            if jq is None:
                ok, why = _dispatch_gate(st, deps, new=True, key=case["t0"])
                if not ok:
                    case["investigation"] = {"skipped": why}
                    dos["jobs"]["quick"] = {"kind": "quick", "skipped": why}
                    save_dossier(deps.state_dir, dos)
                    _stats(st)["dispatch_skipped"] += 1
                    log_event(deps.state_dir, day, "DISPATCH_SKIPPED", now=now, ticker=tk, why=why)
                else:
                    _stats(st)["dispatches"] += 1
                    dbs = st.setdefault("dispatch_by_scan", {})
                    dbs[case["t0"]] = dbs.get(case["t0"], 0) + 1
                    _save(deps, day, st)
                    job = _dd_dispatch(st, deps, now, dos, "quick", "quick")
                    case["investigation"] = {"job": job, "note": dos["jobs"]["quick"].get("note")}
            elif not jq.get("job") and not jq.get("note") and not jq.get("skipped"):
                jq["note"] = ("tiến trình bị cắt giữa lúc dispatch — không xác nhận được job; KHÔNG "
                              "dispatch lại (at-most-once)")
                save_dossier(deps.state_dir, dos)
                case["investigation"] = {"note": jq["note"]}
                _stats(st)["dispatch_fail"] += 1
                log_event(deps.state_dir, day, "DISPATCH_UNCERTAIN", now=now, ticker=tk, note=jq["note"])
            else:
                case["investigation"] = {k: jq.get(k) for k in ("job", "note", "skipped")}
            case["need_dossier"] = False
            _save(deps, day, st)
        if case.get("t0_pending"):
            if case["status"] == "DD_EXISTING":
                dos = _read_json(dd_json(deps.state_dir, case["dossier"]))
                if dos and not any(r.get("t0") == case["t0"] for r in dos["retriggers"]):
                    dos["retriggers"].append({"t0": case["t0"], "trigger": case["trigger"]})
                    save_dossier(deps.state_dir, dos)
            enqueue(st, _t0_msg(case, deps), ("discord", "telegram", "email"), subject=f"Cổng giá {tk}",
                    mention=True, now=now)
            case["t0_pending"] = False
            case["t0_notified"] = True
            _save(deps, day, st)


def _relay_note(st, dos, n, now):
    tk = dos["ticker"]
    kind = n.get("kind")
    body = (n.get("summary") or "")[:600]
    path = f"{dos['dir']}/DOSSIER.md"
    if kind == "final":
        lab = n.get("label")
        enqueue(st, f"📋 KẾT LUẬN HỒ SƠ DD KHỦNG HOẢNG {tk} ({dos['id']}): **{E.VERDICT_VN.get(lab, lab)}**\n"
                    f"  {body}\n  Hồ sơ: {path}\n  ⇒ ANH QUYẾT. {HOLD_NOTE}.",
                ("discord", "telegram", "email"), subject=f"Kết luận DD khủng hoảng {tk}", mention=True, now=now)
    elif kind == "quick":
        enqueue(st, f"📂 DD khủng hoảng {tk} — TÓM TẮT NHANH NGÀY 1:\n  {body}\n  Hồ sơ: {path}\n  ⇒ {HOLD_NOTE}.",
                ("discord", "telegram", "email"), subject=f"DD khủng hoảng {tk} ngày 1", mention=True, now=now)
    elif n.get("major_event"):
        enqueue(st, f"⚠️ DD khủng hoảng {tk} — SỰ KIỆN LỚN (ngày {n.get('day')}):\n  {body}\n  ⇒ đã xin báo "
                    f"cáo kết luận sớm. Hồ sơ: {path}. {HOLD_NOTE}.",
                ("discord", "telegram"), mention=True, now=now)
    else:
        enqueue(st, f"📂 DD khủng hoảng {tk} ngày {n.get('day')}/{E.DD_WINDOW_DAYS}: {body[:300]} (hồ sơ {path}) — mặc định GIỮ",
                ("discord",), now=now)


def _dossier_tick(st, deps, now):
    """Mọi hồ sơ OPEN: chuyển tiếp ghi chú mới · kiểm job chết · nhắc ngày 3/6 · dispatch cập nhật/kết luận.
    Không có nhánh nào hành động lên lệnh/vị thế."""
    day = now.date()
    s = _stats(st)
    for dos in load_dossiers(deps.state_dir, "OPEN"):
        if deps.over_budget():
            log_event(deps.state_dir, day, "BUDGET", now=now, where="dossier_tick", dossier=dos["id"])
            return
        tk, changed = dos["ticker"], False
        # 1) ghi chú mới của agent ⇒ báo
        for n in read_notes(deps.state_dir, dos["id"]):
            if n["file"] in dos["relayed"]:
                continue
            dos["relayed"].append(n["file"])
            s["dd_notes"] += 1
            if n.get("major_event") and not dos.get("major_event"):
                dos["major_event"] = {"at": n.get("at"), "day": n.get("day"), "summary": (n.get("summary") or "")[:300]}
            if n.get("kind") == "final":
                dos["status"] = "CONCLUDED"
                dos["conclusion"] = {"label": n.get("label"), "source": "agent", "at": n.get("at")}
                s["dd_concluded"] += 1
            _relay_note(st, dos, n, now)
            log_event(deps.state_dir, day, "DD_NOTE", now=now, dossier=dos["id"], note=n["file"],
                      label=n.get("label"), major_event=bool(n.get("major_event")))
            changed = True
        # 2) job chết mà không có ghi chú tương ứng
        have = {n["file"] for n in read_notes(deps.state_dir, dos["id"])}
        for jk, j in dos["jobs"].items():
            job = j.get("job")
            if not job or job in ("DRY", "issued") or j.get("job_dead"):
                continue
            want = "final.json" if j["kind"] == "final" else ("quick.json" if j["kind"] == "quick"
                                                              else f"daily_d{j.get('day')}.json")
            if want in have:
                continue
            js = deps.job_status(job)
            if js not in JOB_DEAD:
                continue
            j["job_dead"] = js
            changed = True
            if STOP_DISPATCH_AFTER_TIMEOUT and not st.get("dispatch_halted"):
                st["dispatch_halted"] = f"job hồ sơ {job} ({tk}, {j['kind']}) kết thúc '{js}' không ghi chú"
            log_event(deps.state_dir, day, "JOB_DEAD", now=now, dossier=dos["id"], job=job, step=j["kind"], status=js)
            if j["kind"] == "final":
                dos["status"] = "CONCLUDED"
                dos["conclusion"] = {"label": E.UNCLEAR, "source": "no_agent", "at": _iso(now)}
                s["dd_concluded"] += 1
                enqueue(st, f"📋 KẾT LUẬN HỒ SƠ {tk} ({dos['id']}): **{E.VERDICT_VN[E.UNCLEAR]}** — job kết luận "
                            f"{job} kết thúc '{js}' KHÔNG có báo cáo ⇒ ANH CẦN TỰ XEM hồ sơ {dos['dir']}/DOSSIER.md. "
                            f"{HOLD_NOTE}.", ("discord", "telegram", "email"), subject=f"Kết luận DD {tk}",
                        mention=True, now=now)
            else:
                enqueue(st, f"⚠️ Hồ sơ DD {tk}: job {j['kind']} {job} kết thúc '{js}' KHÔNG ghi chú ⇒ thiếu "
                            f"{'tóm tắt ngày 1' if j['kind'] == 'quick' else 'cập nhật ngày ' + str(j.get('day'))}; "
                            f"dừng dispatch tới hết hôm nay. ANH CẦN TỰ XEM TIN {tk}. {HOLD_NOTE}.",
                        mention=True, now=now)
        if changed:
            save_dossier(deps.state_dir, dos)
            _save(deps, day, st)
        # 3) lịch: nhắc / cập nhật / kết luận
        n_day = E.dd_day(dt.date.fromisoformat(dos["t0"][:10]), day)
        for act in E.dd_due(dos, day):
            if act.startswith("remind:"):
                last = (read_notes(deps.state_dir, dos["id"]) or [{}])[-1]
                dos["reminders"].append(act)
                save_dossier(deps.state_dir, dos)
                s["dd_reminders"] += 1
                enqueue(st, f"⏰ NHẮC — hồ sơ DD khủng hoảng {tk} ngày {n_day}/{E.DD_WINDOW_DAYS} (mốc {act[7:]}) "
                            f"CÒN MỞ. Mới nhất: {(last.get('summary') or 'chưa có ghi chú')[:300]}\n  Hồ sơ: "
                            f"{dos['dir']}/DOSSIER.md\n  ⇒ ANH QUYẾT. {HOLD_NOTE}.",
                        ("discord", "telegram"), mention=True, key=f"dd:{dos['id']}:{act}", now=now)
                log_event(deps.state_dir, day, "DD_REMIND", now=now, dossier=dos["id"], mark=act, dd_day=n_day)
                continue
            ok, why = _dispatch_gate(st, deps, new=False)
            if act == "final":
                dos["final_requested"] = {"at": _iso(now), "why": "sự kiện lớn" if dos.get("major_event") and
                                          n_day <= E.DD_WINDOW_DAYS else f"hết {E.DD_WINDOW_DAYS} ngày",
                                          "skipped": None if ok else why}
            else:
                dos["daily_requested"].append(day.isoformat())
            save_dossier(deps.state_dir, dos)
            if not ok:
                _stats(st)["dispatch_skipped"] += 1
                log_event(deps.state_dir, day, "DISPATCH_SKIPPED", now=now, dossier=dos["id"], step=act, why=why)
                if act == "final":
                    dos["status"] = "CONCLUDED"
                    dos["conclusion"] = {"label": E.UNCLEAR, "source": "no_dispatch", "at": _iso(now)}
                    save_dossier(deps.state_dir, dos)
                    s["dd_concluded"] += 1
                    enqueue(st, f"📋 HỒ SƠ DD {tk} ({dos['id']}) tới hạn kết luận nhưng KHÔNG dispatch được "
                                f"({why}) ⇒ **{E.VERDICT_VN[E.UNCLEAR]}**; ANH CẦN TỰ XEM {dos['dir']}/DOSSIER.md. "
                                f"{HOLD_NOTE}.", ("discord", "telegram", "email"),
                            subject=f"Kết luận DD {tk}", mention=True, now=now)
                else:
                    health_alert(st, "dd_dispatch", f"không dispatch được cập nhật hồ sơ {tk} ngày {n_day}: {why}",
                                 now, deps)
                continue
            s["dd_dispatches"] += 1
            _save(deps, day, st)
            jkey = "final" if act == "final" else f"daily:{day.isoformat()}"
            _dd_dispatch(st, deps, now, dos, act, jkey, day_n=n_day)
        _save(deps, day, st)


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
    if not (vl and vr) and vr and getattr(deps.market, "vni_pending_open", False):
        log_event(deps.state_dir, day, "VNI_PENDING_OPEN", now=now, vni=[vl, vr])
    elif not (vl and vr):
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
    # (A) nhật ký kích hoạt trong ngày cho cửa sổ trượt — chỉ kích hoạt đo được idio (có VNINDEX)
    tlog = st.setdefault("trigger_log", [])
    for tk, u, tr, q in hits:
        if not tr["vni_missing"]:
            tlog.append({"ticker": tk, "at": _iso(now), "at_floor": tr["at_floor"]})
    win_reason = E.window_market_wide_reason([{**e, "at": _p(e["at"])} for e in tlog], now) if hits else None
    reason = E.market_wide_reason([h[2] for h in hits]) or win_reason
    opened = []
    if reason:
        _market_wide(st, now, deps, hits, reason)
        if win_reason:
            _relabel_market_wide(st, now, deps, win_reason)
    else:
        lone = []
        for h in hits:
            if h[2].get("individual"):
                opened.append(h[0])
                open_case(*h, now, deps, st)
            else:
                lone.append(h)
        if lone:            # (B) chạm sàn không đủ điều kiện ca riêng ⇒ nhánh gộp (chỉ báo)
            _market_wide(st, now, deps, lone, "chạm sàn không đủ điều kiện mở ca riêng", lone=True)
    st["last_scan"] = _iso(now)
    log_event(deps.state_dir, day, "SCAN", now=now, n_universe=len(uni), triggered=opened,
              market_wide=reason, vni=[vl, vr], quote_errors=n_err)
    _save(deps, day, st)
    return opened


def _market_wide(st, now, deps, hits, reason, lone=False):
    """Nhánh gộp: KHÔNG mở ca/hồ sơ, KHÔNG dispatch, KHÔNG tự hành động — chỉ ghi + báo mã MỚI.
    `lone` = (B) mã chạm sàn không đủ điều kiện ca riêng trong lượt KHÔNG có biến động chung."""
    day, s = now.date(), _stats(st)
    mw = st.setdefault("market_wide", {})
    new = [h for h in hits if h[0] not in mw]
    for tk, u, tr, q in hits:
        mw.setdefault(tk, {"first": _iso(now), "reason": reason, "ret": tr["ret"], "idio": tr["idio"],
                           "vni_ret": tr["vni_ret"], "at_floor": tr["at_floor"],
                           "not_individual": E.not_individual_reason(tr),
                           "held": {lab: h["qty"] for lab, h in u["holdings"].items()}})
    log_event(deps.state_dir, day, "MARKET_WIDE", now=now, reason=reason,
              tickers=[h[0] for h in hits], new=[h[0] for h in new],
              not_individual={h[0]: E.not_individual_reason(h[2]) for h in hits if not h[2].get("individual")})
    if not new:
        return
    s["market_wide"] += 1
    rows = "\n".join(
        f"  • {tk} {tr['ret']*100:+.1f}%" + (" CHẠM SÀN" if tr["at_floor"] else "")
        + (f" [{E.not_individual_reason(tr)}]" if not tr.get("individual") else "")
        + ("".join(f" | giữ {lab} {h['qty']:,}cp" for lab, h in u["holdings"].items()) or " | không giữ")
        + (" | có lệnh MUA trong plan" if u["buys"] else "") for tk, u, tr, q in new)
    if lone and not any(h[2].get("floor_mw") for h in new):
        head = f"⚠️ CHẠM SÀN — KHÔNG MỞ CA RIÊNG ({reason}), {now:%H:%M}: {len(new)} mã"
        tail = "luật chạm sàn: chỉ mở ca riêng khi idio đạt ngưỡng và VNINDEX > −2%"
    else:
        head = (f"🌐 CẢNH BÁO GỘP — CẢ THỊ TRƯỜNG ({reason}), {now:%H:%M}: {len(new)} mã mới kích hoạt "
                f"(tổng {len(hits)} lượt này)")
        tail = (f"mã sẽ được xét lại riêng khi cửa sổ {E.MARKET_WIDE_WINDOW_MIN}' giao dịch không còn đạt "
                f"ngưỡng gộp")
    enqueue(st, f"{head}\n{rows}\n  ⇒ KHÔNG mở hồ sơ DD từng mã, KHÔNG tự hành động; {tail}. "
                f"Anh tự đánh giá; {HOLD_NOTE}.", mention=True, now=now)


def _relabel_market_wide(st, now, deps, reason):
    """(A) Ca RIÊNG đã mở trong cửa sổ trượt, nay cửa sổ đạt ngưỡng gộp ⇒ gắn nhãn cả thị trường cho ca
    + hồ sơ DD (ngữ cảnh cho agent/user). Không có hành động nào khác (không còn đường bán để dừng)."""
    day = now.date()
    rows = []
    for tk, c in st["cases"].items():
        t0 = _p(c["t0"])
        if c.get("market_wide") or not E.in_window(t0, now):
            continue
        c["market_wide"] = {"at": _iso(now), "reason": reason}
        dos = _read_json(dd_json(deps.state_dir, c["dossier"])) if c.get("dossier") else None
        if dos and not dos.get("market_wide"):
            dos["market_wide"] = c["market_wide"]
            save_dossier(deps.state_dir, dos)
        rows.append((tk, t0))
    if not rows:
        return
    _stats(st)["market_wide_relabel"] += len(rows)
    log_event(deps.state_dir, day, "MARKET_WIDE_RELABEL", now=now, reason=reason,
              cases={tk: {"t0": _iso(t0)} for tk, t0 in rows})
    enqueue(st, f"🌐 GẮN NHÃN CẢ THỊ TRƯỜNG cho ca đã mở riêng ({reason}):\n" + "\n".join(
        f"  • {tk} (T0 {t0:%H:%M}) — hồ sơ DD vẫn tiếp tục, ghi nhận bối cảnh chung" for tk, t0 in rows)
        + f"\n  ⇒ {HOLD_NOTE}.", mention=True, now=now)


def _eod_oos(st, now, deps):
    """(D) Từ EOD_OOS_AT: ghi 1 dòng EOD_OOS/ngày với vni_day + ret_close (giá lúc ghi / TC) cho mọi
    ca + mã gộp ⇒ ca live tích luỹ thành bộ OOS thật (chấm T+k sau từ giá ngày). At-least-once: bị
    cắt giữa log và lưu state ⇒ có thể lặp dòng — dedupe theo (ngày, mã) khi đọc. UPCOM khớp liên tục
    tới 15:00 ⇒ giá 14:55 CHƯA phải giá đóng cửa (`close_final` = False) — chấm lại bằng giá ngày BQ.
    Thêm (2026-11-01): mã có hồ sơ DD đang mở (kích hoạt ngày trước) cũng được ghi (kind "dossier")."""
    if now.time() < EOD_OOS_AT or st.get("eod_oos_logged"):
        return
    day = now.date()
    vl, vr = deps.market.vni(now)
    vni_day = (vl / vr - 1) if (vl and vr) else None
    rows = []
    mw = st.get("market_wide") or {}
    dossiers = {d["ticker"]: d for d in load_dossiers(deps.state_dir, "OPEN")}
    order = list(st["cases"]) + [t for t in mw if t not in st["cases"]]
    order += [t for t in dossiers if t not in order]
    for tk in order:
        if deps.over_budget():
            log_event(deps.state_dir, day, "BUDGET", now=now, where="eod_oos", ticker=tk)
            return
        q = deps.market.quote(tk)
        last, ref = q.get("last"), q.get("ref")
        row = {"ticker": tk, "exchange": q.get("exchange"), "last": last, "ref": ref,
               "ret_close": (last / ref - 1) if (last and ref and not q.get("error")) else None,
               "close_final": (q.get("exchange") or "HOSE").upper() != "UPCOM"}
        c = st["cases"].get(tk)
        if c is not None:
            tr = c.get("trigger") or {}
            row.update({"kind": "case", "t0": c["t0"], "trig_ret": tr.get("ret"), "trig_idio": tr.get("idio"),
                        "trig_vni": tr.get("vni_ret"), "at_floor": tr.get("at_floor"),
                        "market_wide": c.get("market_wide"), "status": c.get("status"), "dossier": c.get("dossier"),
                        "holdings": {lab: h.get("qty") for lab, h in (c.get("holdings") or {}).items()}})
        elif tk in mw:
            m = mw[tk]
            row.update({"kind": "market_wide", "t0": m.get("first"), "trig_ret": m.get("ret"),
                        "trig_idio": m.get("idio"), "trig_vni": m.get("vni_ret"), "at_floor": m.get("at_floor"),
                        "market_wide": {"reason": m.get("reason")}, "not_individual": m.get("not_individual"),
                        "holdings": m.get("held")})
        else:
            d = dossiers[tk]
            tr = d.get("trigger") or {}
            row.update({"kind": "dossier", "t0": d["t0"], "dossier": d["id"], "trig_ret": tr.get("ret"),
                        "dd_day": E.dd_day(dt.date.fromisoformat(d["t0"][:10]), day),
                        "holdings": {lab: h.get("qty") for lab, h in (d.get("holdings") or {}).items()}})
        rows.append(row)
    log_event(deps.state_dir, day, "EOD_OOS", now=now, vni_day=vni_day, vni=[vl, vr], close_asof=_iso(now),
              rows=rows)
    st["eod_oos_logged"] = _iso(now)


def _eod_summary(st, now, deps):
    if now.time() < EOD_SUMMARY_AT or st.get("eod_summary_sent"):
        return
    s = _stats(st)
    crashes = 0
    p = os.path.join(deps.state_dir, f"shadow_{now.date().isoformat()}.jsonl")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            crashes = sum(1 for x in f if '"kind": "CRASH"' in x)
    n_open = len(load_dossiers(deps.state_dir, "OPEN"))
    st["eod_summary_sent"] = _iso(now)
    enqueue(st, f"📊 Tóm tắt intraday-watch {now:%d/%m}: {s['scans']} lượt quét · {s['triggers']} kích "
                f"hoạt · {s['market_wide']} cảnh báo gộp · {s['market_wide_relabel']} ca riêng gắn nhãn gộp sau · "
                f"hồ sơ DD: {s['dispatches']} mở mới ({s['dispatch_fail']} lỗi dispatch, {s['dispatch_skipped']} bị "
                f"chặn), {s['dd_dispatches']} cập nhật/kết luận, {s['dd_notes']} ghi chú, {s['dd_reminders']} nhắc, "
                f"{s['dd_concluded']} kết luận, {n_open} đang mở · ngưỡng tương đối {len(s['alt_rel'])} mã vs hiện "
                f"hành {len(s['alt_cur'])} mã · lỗi giá {s['quote_errors']}/{s['quotes']} · lỗi gửi tin "
                f"{s['notify_fail']} · crash {crashes}"
                + (f" · dispatch DỪNG: {st['dispatch_halted']}" if st.get("dispatch_halted") else ""),
            ("discord",), now=now)


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
    """08:25-08:59: CHỈ việc hồ sơ DD (nhắc ngày 3/6, cập nhật, kết luận) + gửi nốt tin tồn. Không quét."""
    day = now.date()
    st = load_state(deps.state_dir, day)
    _stats(st)
    _save(deps, day, st)
    flush_outbox(st, deps, now)
    _dossier_tick(st, deps, now)
    _save(deps, day, st)
    flush_outbox(st, deps, now)
    _save(deps, day, st)
    return {"open_dossiers": [d["id"] for d in load_dossiers(deps.state_dir, "OPEN")]}


def _run_locked(now, deps):
    from trading_bot.vn_market import session_phase
    day = now.date()
    hp, _ = session_phase(now)
    st = load_state(deps.state_dir, day)
    _stats(st)
    flush_outbox(st, deps, now)                       # tin tồn từ lượt bị cắt
    opened = _scan(now, deps, st) if _scan_due(now, st.get("last_scan"), hp) else []
    _pending_work(st, deps, now)
    _dossier_tick(st, deps, now)
    _eod_oos(st, now, deps)
    if now.time() >= EOD_OOS_ALERT_AT and not st.get("eod_oos_logged"):
        health_alert(st, "eod_oos", f"chưa ghi được EOD_OOS (vni_day/ret_close) lúc {now:%H:%M} — hết ngân sách "
                                    f"hoặc lỡ tick từ {EOD_OOS_AT:%H:%M} ⇒ ngày này thiếu dữ liệu OOS", now, deps)
    _eod_summary(st, now, deps)
    _save(deps, day, st)
    flush_outbox(st, deps, now)
    _save(deps, day, st)
    return {"opened": opened, "open_dossiers": [d["id"] for d in load_dossiers(deps.state_dir, "OPEN")]}


# ============================================================== CLI
def cmd_dd_note(a, now=None):
    """Agent ghi 1 bước hồ sơ: notes/<kind>.json (GHI-MỘT-LẦN) + nối chi tiết vào DOSSIER.md."""
    now = now or _now()
    p = dd_dir(a.state_dir, a.dossier)
    if not os.path.isdir(p):
        sys.exit(f"không có hồ sơ {p}")
    if a.kind not in ("quick", "daily", "final"):
        sys.exit(f"kind phải là quick|daily|final, nhận {a.kind}")
    if a.kind == "final" and a.label not in (E.BROKEN, E.NOISE, E.UNCLEAR):
        sys.exit(f"final cần --label BROKEN|NOISE|UNCLEAR, nhận {a.label}")
    t0 = dt.date.fromisoformat(a.dossier.rsplit("_", 1)[1])
    n = E.dd_day(t0, now.date())
    np_ = os.path.join(p, "notes", note_name(a.kind, n))
    if os.path.exists(np_):
        print(f"đã có {np_} — giữ bản đầu (không ghi đè)")
        return
    detail = ""
    if a.detail_file:
        with open(a.detail_file, encoding="utf-8") as f:
            detail = f.read()
    with open(os.path.join(p, "DOSSIER.md"), "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        head = {"quick": "Ngày 1 — tóm tắt nhanh", "daily": f"Ngày {n} — cập nhật",
                "final": f"KẾT LUẬN: {E.VERDICT_VN.get(a.label, '')}"}[a.kind]
        f.write(f"\n## {head} ({now:%Y-%m-%d %H:%M} ICT)" + (" — ⚠️ SỰ KIỆN LỚN" if a.major_event else "")
                + f"\n\n{a.summary[:1500]}\n\n{detail}\n")
    os.makedirs(os.path.dirname(np_), exist_ok=True)
    _atomic_json(np_, {"kind": a.kind, "day": n, "summary": a.summary[:1500], "label": a.label if a.kind == "final"
                       else None, "major_event": bool(a.major_event), "at": _iso(now)})
    print(f"ghi {np_}")


def main(argv=None, market_factory=None, notifier=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--no-dispatch", action="store_true")
    r.add_argument("--dry-notify", action="store_true")
    r.add_argument("--dispatch-watch", action="store_true",
                   help="mở hồ sơ DD cả mã chỉ-watchlist (mặc định: chỉ báo)")
    r.add_argument("--state-dir", default=STATE_DIR)
    v = sub.add_parser("dd-note")
    v.add_argument("--dossier", required=True)
    v.add_argument("--kind", required=True)
    v.add_argument("--summary", required=True)
    v.add_argument("--label")
    v.add_argument("--major-event", action="store_true")
    v.add_argument("--detail-file")
    v.add_argument("--state-dir", default=STATE_DIR)
    s = sub.add_parser("status")
    s.add_argument("--date")
    s.add_argument("--state-dir", default=STATE_DIR)
    a = ap.parse_args(argv)
    if a.cmd == "dd-note":
        return cmd_dd_note(a)
    if a.cmd == "status":
        d = dt.date.fromisoformat(a.date) if a.date else _now().date()
        print(json.dumps({"state": _read_json(state_path(a.state_dir, d), {}),
                          "open_dossiers": load_dossiers(a.state_dir, "OPEN")}, ensure_ascii=False, indent=1))
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
