# -*- coding: utf-8 -*-
"""ORB intraday VN30F — đường thực thi LIVE cho sleeve SpaceX (job Taylor_20261116_162132).

TÁCH BIỆT HOÀN TOÀN với `Executor` cổ phiếu: không import executor.py, không dùng chung state/
journal của nó. Paper `orb_pt.py` vẫn chạy song song làm đối chứng — module này KHÔNG đổi alpha.

LUẬT (user duyệt 16/11/2026 23:20 ICT, decided_by: user)
  • Tín hiệu  = sign(close bar 1m cuối ≤09:30 / close bar 09:00 − 1) trên VN30F1M — y hệt orb_pt.py.
  • Vào lệnh  = sau 09:30 (cửa sổ 09:31:00–09:40:00; trễ hơn ⇒ BỎ phiên), ĐÚNG 1 hợp đồng.
  • Thoát     = 14:29:00 (bar cuối phiên liên tục; 14:30–14:45 là ATC). Nghiên cứu: Sharpe 14:29
                vs 14:30 = 1,57 vs 1,58 (orb_fiinx_vn30f1m_20260925/README §2) — không đáng kể.
  • Stop thảm hoạ = ±2,5% từ GIÁ KHỚP vào (chọn theo tần suất chạm ≤3%, KHÔNG theo PnL —
                agents/Taylor/research/orb_futures_stop_20261116/). Bot giám sát `latest_trade`.
  • KHÔNG BAO GIỜ giữ qua đêm: sau 14:29 vẫn còn vị thế ⇒ đặt lại lệnh đóng mỗi 30s (sau khi lệnh trước
                CHẮC chết); từ 14:45 KHÔNG đặt lệnh nữa, chỉ cảnh báo ĐỎ cho user đóng tay.
  • Tín hiệu = 0 ⇒ không vào.

CHẾ ĐỘ: `orb_futures.enabled` (khóa CẤP PROFILE trong secrets/trading_bot_accounts.json, KHÔNG nằm
trong `overrides` để khỏi đụng config.py) MẶC ĐỊNH False ⇒ DRY-RUN: đọc giá thật DNSE, chạy đủ máy
trạng thái, ghi lệnh DỰ KIẾN + khớp giả lập vào journal, KHÔNG gọi place/cancel. Chỉ user bật.

AN TOÀN (coding_guidelines §5/§5b/§12/§16/§27)
  • fcntl.flock không chặn: tiến trình thứ 2 thoát ngay (cron watchdog gọi lại an toàn).
  • data/BOT_STOP ⇒ không vào lệnh mới. Đang có vị thế: VẪN đặt lệnh ĐÓNG (stop/14:29) vì user chốt
    ORB_CLOSE_ALLOWED_UNDER_BOT_STOP = True (2026-11-17); hằng số False ⇒ chỉ theo dõi + báo ĐỎ lặp cho user đóng tay.
  • Mọi lần chạy, kể cả trạng thái kết thúc: đọc READ-ONLY positions phái sinh; còn vị thế ⇒ báo ĐỎ lặp.
  • Trạng thái lệnh: chỉ Cancelled/Rejected/Expired + khớp 0 mới là CHẾT; PendingCancel/lạ = SỐNG ⇒
    không đặt lệnh đóng thứ 2 khi lệnh đóng trước chưa chắc chết; lệnh vào không chắc chết ⇒ PAUSED.
  • Vòng giám sát try/except: lỗi thoáng qua ⇒ thử lại; 3 lỗi liên tiếp ⇒ báo ĐỎ. Không đặt lệnh ≥14:45.
  • Trước MỌI lệnh: đối chiếu positions + sổ lệnh phái sinh SỐNG của broker. Vị thế/lệnh không có
    trong state ⇒ PAUSED + báo bus/Discord, không đoán.
  • Ghi intent (…_PENDING) TRƯỚC khi gọi place_order, ghi oid NGAY SAU. Khởi động lại thấy _PENDING
    không có oid ⇒ PAUSED (không biết lệnh đã đi chưa) — KHÔNG đặt lại.
  • State ghi atomic tmp+os.replace. Fill lấy từ order_detail của broker (khớp thật), không suy.
  • Raw log `orb_futures_raw_<date>.jsonl` có account_no cấp cao nhất (§12).
  • Mọi mốc giờ neo Asia/Ho_Chi_Minh tường minh (§16) — đồng hồ là datetime AWARE.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import datetime as dt
import fcntl
import json
import os
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
WC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("ORB_FUT_DATA_DIR") or os.path.join(WC_ROOT, "data")
ACCOUNTS_FILE = os.environ.get("ORB_FUT_ACCOUNTS_FILE") or os.path.join(WC_ROOT, "secrets",
                                                                         "trading_bot_accounts.json")
MIKE_BIN = os.path.join(WC_ROOT, "mike", "bin")

# ---- luật (đổi bất kỳ hằng số nào dưới đây = đổi luật user đã duyệt) ----
CONTRACTS = 1                      # user chốt ĐÚNG 1 HĐ
STOP_PCT = 0.025                   # stop thảm hoạ — research/orb_futures_stop_20261116
SIGNAL_SYMBOL = "VN30F1M"          # chuỗi liên tục DNSE ohlc type=derivative (= VCI, 30/30 phiên)
OR_START, OR_END = "09:00", "09:30"
ENTRY_OPEN = dt.time(9, 31, 5)          # bar 09:30 đã đóng
ENTRY_DEADLINE = dt.time(9, 40, 0)
EXIT_AT = dt.time(14, 29, 0)
SESSION_END = dt.time(14, 45, 0)
LUNCH = (dt.time(11, 30), dt.time(13, 0))
MULT = 100_000                     # VND / điểm
TICK = 0.1
ENTRY_SLIP_CAP = 0.003             # lệnh vào = LO marketable, giá trần ±0,3% so với giá khớp gần nhất
FEED_XCHECK_TOL = 0.005            # |latest_trade HĐ / close bar VN30F1M − 1| > 0,5% ⇒ nghi lệch HĐ/roll
ORDER_FILL_WAIT_S = 60
EXIT_RETRY_S = 30
POLL_S = 5

# ---- an toàn (vòng 2 arch-review 16/11) ----
# Kill-switch BOT_STOP khi đang có vị thế mở: False = bot KHÔNG đặt bất kỳ lệnh nào, kể cả lệnh ĐÓNG giảm
# rủi ro, chỉ báo ĐỎ lặp lại cho user đóng tay. True = vẫn cho đặt lệnh ĐÓNG (stop/14:29), không bao giờ
# cho lệnh VÀO. USER CHỐT True 2026-11-17 11:35 ICT (decided_by: user); đổi lại = quyết định của user.
ORB_CLOSE_ALLOWED_UNDER_BOT_STOP = True   # user chốt 2026-11-17 11:35 ICT: BOT_STOP cho phép bot tự đặt lệnh ĐÓNG (KHÔNG cho vào lệnh)
ALERT_REPEAT_S = 60                # báo lặp (BOT_STOP+vị thế, còn vị thế sau 14:29…): tối đa 1 lần/60s/tiến trình;
                                   # mỗi lần watchdog gọi lại = 1 lần báo mới
WATCH_ERR_ALERT_N = 3              # ≥N lỗi liên tiếp trong vòng giám sát ⇒ báo ĐỎ, tối đa 1 tin/ALERT_REPEAT_S (N-b)
CANCEL_CONFIRM_TRIES = 3           # sau huỷ: đọc lại tối đa 3 lần × 2s; vẫn chưa CHẮC chết ⇒ coi là sống
TERMINAL_CONFIRM_TRIES = 3         # R2 vòng 4: vừa sang trạng thái kết thúc ⇒ đọc positions tối đa 3 lần × 2s;
                                   # chỉ báo "BROKER CÒN" khi MỌI lần đọc đều còn (positions có thể trễ order_detail)
WORST_DAY_PCT = 0.0946             # phiên tệ nhất lịch sử không stop (≈ 1 ngày khoá trần/sàn) — research stop
MIN_MARGIN_FLOOR_VND = 55_000_000  # sàn ký quỹ tối thiểu (quant-skeptic 16/11): 43,3tr cũ − 17,4tr ⇒ < KQ duy trì

TERMINAL = ("CLOSED", "FLAT", "SKIPPED", "PAUSED")
DEAD_NOFILL = {"cancelled", "canceled", "rejected", "expired"}   # khớp TUYỆT ĐỐI sau chuẩn hoá — KHÔNG chứa-chuỗi
                                                                 # ('PendingCancel' chứa 'cancel' nhưng còn SỐNG)


class SchemaError(RuntimeError):
    """Phản hồi broker thiếu khoá mong đợi — KHÔNG được coi là rỗng."""


class OrderRefused(RuntimeError):
    """Lớp chặn cuối trong _place (BOT_STOP / sau 14:45)."""


# ------------------------------------------------------------------ helpers
def qget(d, *names, default=None):
    if not isinstance(d, dict):
        return default
    low = {str(k).lower(): v for k, v in d.items()}
    for n in names:
        v = low.get(n.lower())
        if v not in (None, "", "null"):
            return v
    return default


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def round_tick(p):
    return round(round(p / TICK) * TICK, 1)


def rows_of(r, *keys):
    if isinstance(r, list):
        return r
    if isinstance(r, dict):
        for k in keys:
            if isinstance(r.get(k), list):
                return r[k]
    return []


def rows_strict(r, *keys):
    """Như rows_of nhưng THIẾU khoá mong đợi ⇒ SchemaError (M2: không coi 'không đọc được' là 'rỗng')."""
    if isinstance(r, list):
        return r
    if isinstance(r, dict):
        for k in keys:
            if isinstance(r.get(k), list):
                return r[k]
    raise SchemaError(f"phản hồi thiếu khoá {list(keys)}: {str(r)[:200]}")


def test_mode():
    return os.environ.get("MIKE_BOT_TEST_MODE") == "1" or bool(os.environ.get("PYTEST_CURRENT_TEST"))


def load_profile(account, path=None):
    """Profile account + khoá `orb_futures` (mặc định {"enabled": False})."""
    path = path or ACCOUNTS_FILE
    with open(path, encoding="utf-8") as f:
        accs = json.load(f).get("accounts", [])
    for p in accs:
        if p.get("label") == account:
            cfg = dict(p.get("orb_futures") or {})
            cfg["sleeve_enabled"] = cfg.get("enabled") is True   # chỉ đúng literal true mới bật
            cfg["account_enabled"] = p.get("enabled") is True     # m2: account tắt ⇒ ORB tắt theo
            cfg["enabled"] = cfg["sleeve_enabled"] and cfg["account_enabled"]
            return p, cfg
    raise SystemExit(f"[orb_fut] không có account '{account}' trong {path}")


def default_notify(msg, red=False):
    """Discord Trading Daily; red=True thêm Telegram (đường độc lập bridge). Bị chặn trong test mode.

    M3: KHÔNG nuốt lỗi — đọc exit code từng kênh, in stderr khi rc≠0; trả True nếu ≥1 kênh rc==0."""
    if test_mode():
        sink = os.environ.get("MIKE_BOT_TEST_EVENT_SINK")
        if sink:
            with open(sink, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"notify": msg, "red": red}, ensure_ascii=False) + "\n")
        return True
    chans = [("notify_thread.sh", [msg, "trading_daily"])]
    if red:
        chans.append(("notify_telegram.sh", [msg]))
    ok = False
    for script, args in chans:
        p = os.path.join(MIKE_BIN, script)
        if not os.path.isfile(p):
            print(f"[orb_fut] notify: thiếu {p}", file=sys.stderr)
            continue
        try:
            r = subprocess.run([p, *args], capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                ok = True
            else:
                print(f"[orb_fut] notify {script} rc={r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}",
                      file=sys.stderr)
        except Exception as ex:                                     # noqa: BLE001
            print(f"[orb_fut] notify {script} lỗi: {ex!r}", file=sys.stderr)
    if not ok:
        print(f"[orb_fut] ⛔ MỌI kênh báo đều thất bại — nội dung: {msg}", file=sys.stderr)
    return ok


def default_publish(event_type, topic, payload):
    """Bus fleet (fire-and-forget). Cùng guard test-mode như executor._publish_bot_event (§5b)."""
    if test_mode():
        sink = os.environ.get("MIKE_BOT_TEST_EVENT_SINK")
        if sink:
            with open(sink, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"event_type": event_type, "topic": topic,
                                     "payload": payload}, ensure_ascii=False) + "\n")
        return
    p = os.path.join(MIKE_BIN, "append_event.sh")
    if os.path.isfile(p):
        try:
            subprocess.Popen([p, "Mafee", event_type, topic, json.dumps(payload, ensure_ascii=False)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        except Exception:                                           # noqa: BLE001
            pass


# ------------------------------------------------------------------ signal
def bars_today(client, day):
    """Bar 1m VN30F1M hôm nay từ DNSE (§6 same-day: DNSE, KHÔNG BQ). [(hm, o, h, l, c)]."""
    f = int(dt.datetime.combine(day, dt.time(8, 59), ICT).timestamp())
    t = int(dt.datetime.combine(day, dt.time(14, 46), ICT).timestamp())
    r = client.ohlc(SIGNAL_SYMBOL, resolution="1", bar_type="derivative", **{"from": f, "to": t})
    out = []
    for i, ts in enumerate(r.get("t") or []):
        b = dt.datetime.fromtimestamp(ts, ICT)
        if b.date() != day:
            continue
        out.append((b.strftime("%H:%M"), float(r["o"][i]), float(r["h"][i]),
                    float(r["l"][i]), float(r["c"][i])))
    return sorted(out)


def compute_signal(bars, strict=True):
    """Đúng logic orb_pt.py. Trả (sig, info) hoặc (None, lý do) khi dữ liệu không đủ tin.

    strict=True: bắt buộc có bar 09:30 (đúng như backtest). Sau 09:33 caller nới về ≥09:25
    (cùng mức chịu của orb_pt.py: 'bar cuối ≤09:30' bất kể là phút nào)."""
    op = [b for b in bars if b[0] <= OR_END]
    if len(op) < 10:
        return None, f"thiếu bar OR ({len(op)} < 10)"
    if op[0][0] > "09:05":
        return None, f"bar đầu tiên {op[0][0]} > 09:05 — không có bar mở cửa"
    if strict and op[-1][0] != OR_END:
        return None, f"chưa có bar {OR_END} (bar cuối {op[-1][0]})"
    if op[-1][0] < "09:25":
        return None, f"bar cuối ≤09:30 là {op[-1][0]} (feed trễ)"
    c0, entry_ref = op[0][4], op[-1][4]
    orr = entry_ref / c0 - 1
    sig = (orr > 0) - (orr < 0)
    return sig, {"c0": c0, "or_close": entry_ref, "or_ret": orr, "or_last_hm": op[-1][0], "n_or": len(op)}


# ------------------------------------------------------------------ broker facts
def resolve_contract(client, max_pages=5):
    """HĐ đang là VN30F1M theo DNSE (mã KRX vd 41I1GB000). Không thấy ⇒ None."""
    for page in range(1, max_pages + 1):
        r = client.instruments(market_id="DVX", limit=100, page=page)
        rows = rows_of(r, "data")
        for x in rows:
            if x.get("symbolType") == "VN30F1M" and x.get("securityGroupId") == "FU":
                return x["symbol"]
        if len(rows) < 100:
            break
    return None


def secdef_g1(client, symbol):
    rows = rows_of(client.secdef(symbol), "data")
    for x in rows:
        if x.get("boardId") == "G1":
            return x
    return rows[0] if rows else None


def last_trade_px(client, symbol):
    rows = rows_of(client.latest_trade(symbol), "trades")
    for x in rows:
        if x.get("boardId") == "G1":
            return fnum(x.get("matchPrice")), x.get("time")
    return None, None


def derivative_package(client, account_id):
    """Gói vay phái sinh duy nhất. 0 hoặc >1 gói ⇒ None (không đoán)."""
    pk = rows_of(client.loan_packages(account_id, market_type="DERIVATIVE"), "loanPackages")
    return pk[0] if len(pk) == 1 else None


def broker_positions(client, account_id):
    return rows_strict(client.positions(account_id, market_type="DERIVATIVE"), "positions", "data")


def position_qty(row):
    """Số HĐ mở có dấu (+long/−short). Schema phái sinh CHƯA XÁC MINH (positions đang rỗng) ⇒ không
    parse được = None, caller coi là KHÔNG RÕ (fail-safe)."""
    q = fnum(qget(row, "openQuantity", "netQuantity", "quantity", "totalQuantity", "openQty"))
    if q is None:
        return None
    side = str(qget(row, "side", "positionSide", default="")).upper()
    if side in ("NS", "SHORT", "SELL", "S"):
        q = -abs(q)
    return q


def broker_orders(client, account_id):
    return rows_strict(client.orders(account_id, market_type="DERIVATIVE"), "orders", "data")


def net_position(rows):
    """Tổng HĐ có dấu; dòng nào không parse được ⇒ None (KHÔNG RÕ, fail-safe)."""
    net = 0.0
    for p in rows:
        q = position_qty(p)
        if q is None:
            return None
        net += q
    return net


def order_fill(client, account_id, oid):
    """(filled_qty, avg_price, status) — đọc từ order_detail của broker (§27 khớp thật)."""
    r = client.order_detail(account_id, oid, market_type="DERIVATIVE")
    r = r.get("order", r) if isinstance(r, dict) else r
    q = fnum(qget(r, "fillQuantity", "filledQuantity", "cumQty", "matchedQuantity")) or 0.0
    px = fnum(qget(r, "averagePrice", "avgPrice", "fillPrice", "matchPrice"))
    st = str(qget(r, "orderStatus", "status", default=""))
    return int(q), px, st


def order_state(qty, status):
    """FILLED | PARTIAL | DEAD (chắc chắn Cancelled/Rejected/Expired VÀ khớp 0) | ALIVE.
    ALIVE gồm cả PendingCancel, New, PendingNew, trạng thái rỗng/lạ, 'Filled' mà khớp 0 — tức là
    MỌI thứ không CHẮC chết đều coi là còn sống (B2)."""
    if qty >= CONTRACTS:
        return "FILLED"
    if qty > 0:
        return "PARTIAL"
    s = "".join(ch for ch in str(status).lower() if ch.isalpha())
    return "DEAD" if s in DEAD_NOFILL else "ALIVE"


# ------------------------------------------------------------------ executor
class OrbFutures:
    def __init__(self, client, account, account_id, live, *, clock=None, sleep=None,
                 notify=None, publish=None, data_dir=None):
        self.c, self.account, self.acc = client, account, account_id
        self.live = bool(live)
        self.mode = "LIVE" if self.live else "DRY"
        self.clock = clock or (lambda: dt.datetime.now(ICT))
        self.sleep = sleep or time.sleep
        self.notify = notify or default_notify
        self.publish = publish or default_publish
        self.dir = os.path.join(data_dir or DATA_DIR, "orb_futures")
        os.makedirs(self.dir, exist_ok=True)
        self.bot_stop_file = os.path.join(data_dir or DATA_DIR, "BOT_STOP")
        self.day = self.clock().astimezone(ICT).date()
        sfx = "" if self.live else "_dry"
        self.state_file = os.path.join(self.dir, f"state_{account}_{self.day}{sfx}.json")
        self.journal_file = os.path.join(self.dir, f"journal_{account}{sfx}.csv")
        self.raw_file = os.path.join(self.dir, f"orb_futures_raw_{self.day}.jsonl")
        self.lock_file = os.path.join(self.dir, f"lock_{account}")
        self.state = self._load()
        self.err_n = 0                                   # lỗi liên tiếp trong vòng giám sát (B4)
        self._last_alert = {}                            # khoá → datetime, chống spam báo lặp

    # ---- persistence
    def _load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, encoding="utf-8") as f:
                return json.load(f)
        return {"date": str(self.day), "account": self.account, "mode": self.mode, "stage": "INIT",
                "known_oids": [], "exit_oids": [], "contracts": CONTRACTS, "stop_pct": STOP_PCT}

    def save(self):
        tmp = f"{self.state_file}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.state_file)

    def raw(self, kind, payload):
        with open(self.raw_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": self.now().isoformat(timespec="seconds"), "account": self.account,
                                "account_no": self.acc, "mode": self.mode, "kind": kind,
                                "payload": payload}, ensure_ascii=False, default=str) + "\n")

    def journal(self, event, side="", oid="", qty="", price="", note=""):
        new = not os.path.exists(self.journal_file)
        with open(self.journal_file, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
                            "filled_total", "book", "play_type", "note"])
            w.writerow([self.now().isoformat(timespec="seconds"), event, f"ORB-{self.day}",
                        self.state.get("contract", ""), side, oid, qty, price,
                        self.state.get("filled_total", ""), "ORB_FUT", self.mode, note])

    def now(self):
        return self.clock().astimezone(ICT)

    def stage(self, s, **kw):
        self.state["stage"] = s
        self.state.update(kw)
        self.save()

    # ---- alerts
    def alert(self, topic, msg, level="error", payload=None):
        """level=error ⇒ ĐỎ: bus + Discord + Telegram (M3). level=status ⇒ bus + Discord."""
        body = {"account": self.account, "mode": self.mode, "date": str(self.day), "msg": msg}
        body.update(payload or {})
        self.raw("alert", body)
        self.publish(level, f"orb_futures_{topic}", body)
        ok = self.notify(f"{'🔴' if level == 'error' else 'ℹ️'} **ORB VN30F {self.account} [{self.mode}]** — {msg}",
                         red=(level == "error"))
        if ok is False:
            self.raw("notify_failed", {"topic": topic, "msg": msg})

    def alert_repeat(self, key, topic, msg, force=False):
        """Báo ĐỎ lặp lại, tối đa 1 lần / ALERT_REPEAT_S / khoá trong 1 tiến trình (force = bỏ chặn)."""
        t, last = self.now(), self._last_alert.get(key)
        if force or last is None or (t - last).total_seconds() >= ALERT_REPEAT_S:
            self._last_alert[key] = t
            self.alert(topic, msg)

    def pause(self, reason, **kw):
        self.stage("PAUSED", pause_reason=reason, **kw)
        self.journal("PAUSED", note=reason)
        self.alert("paused", f"PAUSED: {reason}. Bot KHÔNG đặt thêm lệnh — cần người kiểm tra.")

    def _skip(self, reason, msg=None, topic="skip", level="status"):
        self.stage("SKIPPED", skip_reason=reason)
        self.journal("SKIP", note=reason)
        self.alert(topic, msg or f"BỎ phiên: {reason}", level=level)

    # ---- guards
    def bot_stopped(self):
        return os.path.exists(self.bot_stop_file)

    def watch_broker(self, why, confirm_tries=1):
        """B2 — READ-ONLY positions phái sinh. Phẳng ⇒ True. Còn vị thế / không đọc được (LIVE) ⇒ báo ĐỎ.
        Gọi ở MỌI lần chạy kể cả trạng thái kết thúc (SKIPPED/PAUSED/CLOSED/FLAT).
        N-a: DRY (cờ TẮT) ⇒ chỉ ghi raw log + stdout, KHÔNG Telegram/Discord/bus — vị thế phái sinh lúc DRY
        là của user (giữ tay), bot không có lệnh nào trên broker nên không được spam.
        confirm_tries>1 (R2 vòng 4): còn vị thế ⇒ đọc lại sau 2s, tối đa confirm_tries lần; phẳng ở BẤT KỲ lần nào
        ⇒ True; chỉ báo khi MỌI lần đọc đều còn. Lỗi đọc ⇒ báo ĐỎ NGAY như cũ (không chờ đọc lại)."""
        for i in range(max(1, confirm_tries)):
            if i:
                self.sleep(2)
            try:
                pos = broker_positions(self.c, self.acc)
            except Exception as ex:                                 # noqa: BLE001
                self.raw("watch_err", repr(ex))
                if self.live:
                    self.alert_repeat("watch_err", "watch", f"KHÔNG đọc được positions phái sinh ({why}): {ex!r}"[:300]
                                      + " — không xác nhận được TK phẳng, cần người kiểm tra.")
                    return False
                return True
            net = net_position(pos)
            self.raw("watch", {"why": why, "stage": self.state["stage"], "positions": pos, "net": net, "try": i + 1})
            if net is not None and abs(net) <= 1e-9:
                return True
        if not self.live:                                  # N-a
            if net is None or abs(net) > 1e-9:
                self.raw("watch_dry_position", {"why": why, "net": net})
                print(f"[orb_fut] DRY: broker có vị thế phái sinh net={net} ({why}) — chỉ ghi log, không báo.")
                return False
            return True
        if net is None:
            self.alert_repeat("watch_unk", "watch", f"dòng vị thế phái sinh không đọc được số lượng ({why}, "
                              f"state {self.state['stage']}) — cần người kiểm tra.")
            return False
        if abs(net) > 1e-9:
            self.alert_repeat("watch_open", "open_position",
                              f"⛔ BROKER CÒN {net:+.0f} HĐ PHÁI SINH trong khi state = {self.state['stage']} ({why}). "
                              "Bot KHÔNG tự đặt lệnh ở trạng thái này — USER ĐÓNG TAY trên app DNSE.")
            return False
        return True

    def reconcile(self):
        """Broker là nguồn sự thật. True = khớp state; False = đã PAUSE."""
        try:
            pos = broker_positions(self.c, self.acc)
            ords = broker_orders(self.c, self.acc)
        except Exception as ex:                                     # noqa: BLE001 — gồm SchemaError (M2)
            if self.live:
                self.pause(f"không đọc được positions/orders phái sinh: {ex!r}"[:300])
                return False
            self.raw("reconcile_err_dry", repr(ex)); return True
        self.raw("reconcile", {"positions": pos, "orders": ords})
        known = set(self.state.get("known_oids", []))
        foreign = [o for o in ords if str(qget(o, "id", "orderId")) not in known]
        if foreign:
            self.pause(f"sổ lệnh phái sinh có {len(foreign)} lệnh KHÔNG do ORB đặt",
                       foreign_orders=foreign)
            return False
        net = net_position(pos)
        if net is None:
            self.pause("có dòng vị thế phái sinh không đọc được số lượng (schema chưa xác minh)",
                       positions=pos)
            return False
        if not self.live:
            return True                                             # DRY: broker không có lệnh của ta
        if self.state["stage"] in ("ENTRY_PLACED",):
            return True                                             # đang chờ khớp — check ở bước fill
        expect = self.state.get("sig", 0) * CONTRACTS if self.state["stage"] in ("OPEN", "EXIT_PENDING",
                                                                                  "EXIT_PLACED") else 0
        if abs(net - expect) > 1e-9:
            self.pause(f"vị thế broker {net:+.0f} HĐ ≠ state kỳ vọng {expect:+d} HĐ", positions=pos)
            return False
        return True

    # ---- order primitives (DRY ⇒ giả lập, KHÔNG gọi broker)
    def _place(self, side, price, purpose):
        """Ghi intent → đặt → ghi oid ngay (§5). Trả oid. Lớp chặn CUỐI: BOT_STOP / ≥14:45 ⇒ OrderRefused."""
        if self.bot_stopped() and not (purpose == "EXIT" and ORB_CLOSE_ALLOWED_UNDER_BOT_STOP):
            raise OrderRefused(f"BOT_STOP — từ chối đặt lệnh {purpose}")
        if self.now().time() >= SESSION_END:
            raise OrderRefused(f"≥{SESSION_END} — từ chối đặt lệnh {purpose}")
        self.stage(f"{purpose}_PENDING", **{f"{purpose.lower()}_intent": {"side": side, "price": price,
                                                                           "ts": self.now().isoformat()}})
        if not self.live:
            oid = f"DRY-{purpose}-{self.day}-{len(self.state.get('known_oids', []))}"
            self.journal(f"DRY_PLACE_{purpose}", side, oid, CONTRACTS, price)
        else:
            pk = self.state["loan_package_id"]
            r = self.c.place_order(self.acc, self.state["contract"], qty=CONTRACTS, side=side,
                                   order_type="LO", price=price, market_type="DERIVATIVE",
                                   loan_package_id=pk)
            oid = str(qget(r, "id", "orderId", "orderid", default=""))
            self.raw("place_order", {"purpose": purpose, "side": side, "price": price, "resp": r})
            if not oid:
                self.pause(f"place_order {purpose} không trả id: {r}")
                raise RuntimeError("no oid")
            self.journal(f"PLACE_{purpose}", side, oid, CONTRACTS, price)
        self.state.setdefault("known_oids", []).append(oid)
        if purpose == "EXIT":
            self.state.setdefault("exit_oids", []).append(oid)
        self.stage(f"{purpose}_PLACED", **{f"{purpose.lower()}_oid": oid})
        return oid

    def _fill(self, oid, sim_px):
        if not self.live:
            return CONTRACTS, sim_px, "DRY_FILLED"
        q, px, st = order_fill(self.c, self.acc, oid)
        self.raw("order_detail", {"oid": oid, "filled": q, "avg": px, "status": st})
        return q, px, st

    def _cancel(self, oid):
        if self.live:
            try:
                r = self.c.cancel_order(self.acc, oid, market_type="DERIVATIVE")
                self.raw("cancel_order", {"oid": oid, "resp": r})
            except Exception as ex:                                 # noqa: BLE001 — trạng thái đọc lại ở bước sau
                self.raw("cancel_err", {"oid": oid, "err": repr(ex)})
        self.journal("CANCEL", oid=oid)

    def _settle_after_cancel(self, oid, sim_px):
        """Huỷ rồi đọc lại tới khi CHẮC: (kind, q, px, st). kind ∈ FILLED/PARTIAL/DEAD/ALIVE."""
        self._cancel(oid)
        q, px, st = 0, None, ""
        for _ in range(CANCEL_CONFIRM_TRIES):
            self.sleep(2)
            q, px, st = self._fill(oid, sim_px)
            k = order_state(q, st)
            if k != "ALIVE":
                return k, q, px, st
        return "ALIVE", q, px, st

    def _px_or_estimate(self, fpx, purpose, fallback):
        """B3: order_detail thiếu averagePrice ⇒ KHÔNG crash: ước = giá khớp gần nhất (LTP) → fallback
        (giá lệnh), gắn cờ *_px_estimated + báo ĐỎ."""
        if fpx is not None:
            return fpx, False
        try:
            ltp, _ = last_trade_px(self.c, self.state["contract"])
        except Exception:                                           # noqa: BLE001
            ltp = None
        est = ltp if ltp is not None else fallback
        self.alert("fill_px_missing", f"lệnh {purpose} đã KHỚP nhưng broker không trả giá khớp — dùng giá ƯỚC "
                   f"{est} ({'LTP' if ltp is not None else 'giá lệnh'}); stop/PnL theo giá ước, cần đối soát email khớp.")
        return est, True

    # ---- stages
    def step_entry(self, t):
        if t.time() < ENTRY_OPEN:
            return
        if t.time() > ENTRY_DEADLINE:
            return self._skip("lỡ cửa sổ vào lệnh 09:31–09:40")
        sig, info = compute_signal(bars_today(self.c, self.day), strict=t.time() < dt.time(9, 33))
        if sig is None:
            if t.time() >= dt.time(9, 33):           # cho feed 2 phút; sau đó bỏ phiên
                self._skip(f"dữ liệu tín hiệu không đủ: {info}")
            return
        self.state.update(sig=sig, signal=info)
        self.journal("SIGNAL", note=json.dumps(info))
        if sig == 0:
            self.stage("FLAT")
            self.notify(f"ℹ️ **ORB VN30F {self.account} [{self.mode}]** — OR = 0 ⇒ KHÔNG vào lệnh hôm nay.")
            return
        contract = resolve_contract(self.c)
        sd = secdef_g1(self.c, contract) if contract else None
        px, px_t = last_trade_px(self.c, contract) if contract else (None, None)
        if not contract or not sd or px is None:
            return self.pause(f"không xác định được HĐ/secdef/giá (contract={contract}, px={px})")
        if str(sd.get("symbolTradingSanctionStatusCode", "NRM")) != "NRM":
            return self.pause(f"HĐ {contract} trạng thái giao dịch {sd.get('symbolTradingSanctionStatusCode')}")
        dev = px / info["or_close"] - 1
        if abs(dev) > FEED_XCHECK_TOL:
            return self.pause(f"giá {contract} {px} lệch close VN30F1M {info['or_close']} {dev:+.2%} "
                              f"(>{FEED_XCHECK_TOL:.1%}) — nghi lệch HĐ/roll")
        ceil_, floor_ = fnum(sd.get("ceilingPrice")), fnum(sd.get("floorPrice"))
        pk = derivative_package(self.c, self.acc)
        side = "buy" if sig > 0 else "sell"
        self.state.update(contract=contract, ceiling=ceil_, floor=floor_, last_px_at_entry=px,
                          loan_package_id=(pk or {}).get("id"),
                          margin_rate_init=(pk or {}).get("initialRate"))
        if self.live:
            if pk is None:
                return self.pause("không có đúng 1 gói vay phái sinh")
            pp = self.c.ppse(self.acc, contract, px, market_type="DERIVATIVE", loan_package_id=pk["id"])
            self.raw("ppse", pp)
            qmax = fnum(qget(pp, "qmaxBuy" if sig > 0 else "qmaxSell")) or 0
            if qmax < CONTRACTS:
                return self._skip(f"sức mua phái sinh không đủ (qmax={qmax:g})", topic="funding", level="error",
                                  msg=f"BỎ phiên — ký quỹ phái sinh KHÔNG đủ cho {CONTRACTS} HĐ "
                                      f"(ppse qmax={qmax:g}). Xem cảnh báo nộp ký quỹ.")
        if not self.reconcile():
            return
        lim = round_tick(px * (1 + sig * ENTRY_SLIP_CAP))
        lim = min(max(lim, floor_ or lim), ceil_ or lim)
        oid = self._place(side, lim, "ENTRY")
        self._await_entry(oid, side, px)

    def _await_entry(self, oid, side, sim_px):
        t0 = self.now()                                  # đồng hồ tiêm được (test), không monotonic
        while True:
            q, fpx, st = self._fill(oid, sim_px)
            k = order_state(q, st)
            if k == "ALIVE" and (self.now() - t0).total_seconds() > ORDER_FILL_WAIT_S:
                k, q, fpx, st = self._settle_after_cancel(oid, sim_px)
                if k == "ALIVE":
                    return self.pause(f"lệnh vào {oid} đã gửi huỷ nhưng trạng thái '{st}' chưa CHẮC chết "
                                      "(PendingCancel/không rõ) — coi như CÒN SỐNG", live_entry_oid=oid)
            if k == "FILLED":
                return self._opened(oid, side, fpx)
            if k == "PARTIAL":                           # không thể với 1 HĐ — nhưng không đoán
                return self.pause(f"lệnh vào {oid} khớp lẻ {q}/{CONTRACTS}")
            if k == "DEAD":
                return self._skip(f"lệnh vào {oid} không khớp ({st}, khớp 0)",
                                  msg=f"BỎ phiên: lệnh vào không khớp trong {ORDER_FILL_WAIT_S}s ({st}).")
            self.sleep(POLL_S)

    def _opened(self, oid, side, fpx):
        sig = self.state["sig"]
        fpx, est = self._px_or_estimate(fpx, "VÀO", (self.state.get("entry_intent") or {}).get("price"))
        stop = round_tick(fpx * (1 - sig * STOP_PCT))
        self.stage("OPEN", entry_px=fpx, stop_px=stop, filled_total=CONTRACTS * sig,
                   entry_ts=self.now().isoformat(), fill_px_estimated=est)
        self.journal("FILL", side, oid, CONTRACTS, fpx, note=f"entry; stop={stop}" + ("; px ƯỚC" if est else ""))
        self.publish("status", "orb_futures_entry", {"account": self.account, "mode": self.mode,
                     "contract": self.state["contract"], "side": side, "px": fpx, "stop": stop,
                     "fill_px_estimated": est})
        self.notify(f"📈 **ORB VN30F {self.account} [{self.mode}]** VÀO {'LONG' if sig > 0 else 'SHORT'} "
                    f"{CONTRACTS} HĐ {self.state['contract']} @ {fpx}{' (ƯỚC)' if est else ''} "
                    f"(OR {self.state['signal']['or_ret']:+.2%}). Stop thảm hoạ {stop} (±{STOP_PCT:.1%}); thoát 14:29.")

    def _stop_hit(self, px):
        sig, stop = self.state["sig"], self.state["stop_px"]
        return px is not None and ((sig > 0 and px <= stop) or (sig < 0 and px >= stop))

    def step_open(self, t):
        if LUNCH[0] <= t.time() < LUNCH[1]:
            return
        if self.state.get("exit_reason"):                # đã quyết thoát (stop/time) ⇒ tiếp tục thoát
            return self._exit(self.state["exit_reason"], t)
        if t.time() >= EXIT_AT:
            return self._exit("TIME", t)
        px, _ = last_trade_px(self.c, self.state["contract"])
        if self._stop_hit(px):
            self.state["stop_trigger_px"] = px
            return self._exit("STOP", t)

    def _exit(self, reason, t):
        if t.time() >= SESSION_END:                       # M1: hết phiên — chỉ báo, KHÔNG đặt lệnh
            return self.alert_repeat("overnight", "overnight", f"⛔ ≥14:45 VẪN CÒN VỊ THẾ {self.state.get('contract')} "
                                     "— bot KHÔNG đặt lệnh sau phiên. USER ĐÓNG TAY NGAY.")
        sig = self.state["sig"]
        side = "sell" if sig > 0 else "buy"
        self.state["exit_reason"] = reason
        self.save()
        # B2: MỌI lệnh đóng trước đó phải CHẮC chết + khớp 0 trước khi đặt lệnh mới (PendingCancel = sống)
        for prev in self.state.get("exit_oids", []):
            q, fpx, st = self._fill(prev, self.state.get("entry_px"))
            k = order_state(q, st)
            if k == "FILLED":
                return self._closed(prev, side, fpx)
            if k != "DEAD":
                return self.alert_repeat(f"exit_alive_{prev}", "exit_wait",
                                         f"lệnh đóng trước {prev} trạng thái '{st}' khớp {q} — chưa CHẮC chết ⇒ "
                                         "KHÔNG đặt lệnh đóng mới (chống đóng kép/đảo vị thế). Thử lại chu kỳ sau.")
        if not self.reconcile():
            return
        # Đóng = LO ngược chiều ở giá sàn (đóng long) / trần (đóng short) — theo docs DNSE
        # "đóng vị thế": khớp ở giá tốt nhất hiện có, không phải ở sàn/trần.
        price = self.state["floor"] if sig > 0 else self.state["ceiling"]
        px_now, _ = last_trade_px(self.c, self.state["contract"])
        oid = self._place(side, price, "EXIT")
        self._await_exit(oid, side, px_now or self.state["entry_px"])

    def _await_exit(self, oid, side, sim_px):
        t0 = self.now()                                  # đồng hồ tiêm được (test), không monotonic
        while True:
            q, fpx, st = self._fill(oid, sim_px)
            k = order_state(q, st)
            if k == "FILLED":
                return self._closed(oid, side, fpx)
            if k == "PARTIAL":
                return self.pause(f"lệnh đóng {oid} khớp lẻ {q}/{CONTRACTS}")
            if self.now().time() >= SESSION_END:
                return self.alert_repeat("overnight", "overnight", f"⛔ 14:45 VẪN CÒN VỊ THẾ {self.state['contract']} "
                                         f"(lệnh đóng {oid} {st}) — USER ĐÓNG TAY NGAY. Bot không giữ qua đêm.")
            if k == "DEAD":
                self.stage("OPEN")                       # _exit chu kỳ sau xác minh lại rồi mới đặt
                return
            if (self.now() - t0).total_seconds() > EXIT_RETRY_S:
                if self.bot_stopped() and not ORB_CLOSE_ALLOWED_UNDER_BOT_STOP:
                    return                               # BOT_STOP: giữ lệnh đóng đang sống, không huỷ/đặt lại
                k, q, fpx, st = self._settle_after_cancel(oid, sim_px)
                if k == "FILLED":
                    return self._closed(oid, side, fpx)
                self.stage("OPEN")                       # DEAD ⇒ đặt lại; ALIVE ⇒ _exit chờ nó chết
                return
            self.sleep(POLL_S)

    def _closed(self, oid, side, fpx):
        sig, epx = self.state["sig"], self.state["entry_px"]
        fpx, est = self._px_or_estimate(fpx, "ĐÓNG", None)
        if fpx is None:
            return self.pause(f"lệnh đóng {oid} đã khớp nhưng không có giá khớp lẫn LTP — cần đối soát",
                              filled_total=0)
        pts = sig * (fpx - epx)
        gross = pts * MULT * CONTRACTS
        self.stage("CLOSED", exit_px=fpx, exit_ts=self.now().isoformat(), filled_total=0,
                   pnl_points=round(pts, 2), pnl_gross_vnd=round(gross), exit_px_estimated=est)
        reason = self.state.get("exit_reason", "?")
        self.journal("FILL", side, oid, CONTRACTS, fpx,
                     note=f"exit {reason}; pnl_gross={gross:.0f}VND" + ("; px ƯỚC" if est else ""))
        self.publish("finding" if reason == "STOP" else "status", "orb_futures_exit",
                     {"account": self.account, "mode": self.mode, "reason": reason,
                      "entry": epx, "exit": fpx, "pnl_gross_vnd": round(gross), "exit_px_estimated": est})
        self.notify(f"{'🛑' if reason == 'STOP' else '🏁'} **ORB VN30F {self.account} "
                    f"[{self.mode}]** THOÁT ({reason}) @ {fpx}{' (ƯỚC)' if est else ''}; vào {epx} ⇒ "
                    f"{pts:+.1f} điểm = {gross / 1e6:+,.2f}tr gộp (CHƯA trừ phí/thuế).")

    def _bot_stop_cycle(self, t, s):
        """B1 — BOT_STOP khi có vị thế (OPEN/EXIT_PLACED): KHÔNG vào mới; theo dõi tiếp; báo ĐỎ lặp."""
        if s == "EXIT_PLACED":                           # lệnh đóng đặt TRƯỚC khi bật BOT_STOP: chỉ đọc khớp
            q, fpx, st = self._fill(self.state["exit_oid"], self.state.get("entry_px"))
            if order_state(q, st) == "FILLED":
                return self._closed(self.state["exit_oid"], "sell" if self.state["sig"] > 0 else "buy", fpx)
        if ORB_CLOSE_ALLOWED_UNDER_BOT_STOP:
            self.alert_repeat("bot_stop", "bot_stop", "data/BOT_STOP đang bật VÀ còn vị thế mở — chế độ cho phép "
                              "ĐÓNG: bot vẫn đóng khi chạm stop/14:29, KHÔNG vào lệnh mới.")
            return self.step_open(t) if s == "OPEN" else self._await_exit(
                self.state["exit_oid"], "sell" if self.state["sig"] > 0 else "buy", self.state.get("entry_px"))
        px = None
        with contextlib.suppress(Exception):
            px, _ = last_trade_px(self.c, self.state["contract"])
        hit = self._stop_hit(px)
        late = t.time() >= EXIT_AT
        first_hit = (hit or late) and not self.state.get("bot_stop_hit_alerted")
        if first_hit:
            self.state["bot_stop_hit_alerted"] = True; self.save()
        tail = (f" GIÁ {px} ĐÃ CHẠM STOP {self.state['stop_px']}." if hit else "") + \
               (" ĐÃ QUA 14:29 (giờ thoát)." if late else "")
        self.alert_repeat("bot_stop", "bot_stop",
                          f"⛔ VỊ THẾ MỞ {self.state['sig'] * CONTRACTS:+d} HĐ {self.state['contract']}, "
                          f"BOT_STOP đang bật — bot KHÔNG đặt lệnh (kể cả lệnh đóng). CẦN USER ĐÓNG TAY.{tail}",
                          force=first_hit)

    # ---- main loop
    def run(self, once=False):
        with open(self.lock_file, "a+") as lf:
            try:
                fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print("[orb_fut] tiến trình khác đang giữ khoá — thoát."); return "LOCKED"
            self.state = self._load()                       # m1: đọc lại SAU khi có khoá
            if self.state["stage"] in TERMINAL:
                self.watch_broker("chạy lại ở trạng thái kết thúc")   # B2: kể cả kết thúc vẫn nhìn broker
                print(f"[orb_fut] state {self.state['stage']} — không đặt lệnh."); return self.state["stage"]
            if self.state["stage"] == "INIT" and not self.reconcile():
                return self.state["stage"]
            while True:
                t = self.now()
                s = self.state["stage"]
                if s in TERMINAL:
                    return s
                if t.time() >= SESSION_END:
                    if s != "INIT":
                        self.alert_repeat("overnight", "overnight", f"⛔ ≥14:45 còn vị thế ORB (state {s}) — "
                                          "USER ĐÓNG TAY NGAY. Bot không đặt lệnh sau phiên.")
                    else:
                        self._skip("chạy sau phiên")
                    self.watch_broker("sau 14:45")
                    return self.state["stage"]
                try:
                    if s in ("ENTRY_PENDING", "EXIT_PENDING"):
                        self.pause(f"stage {s}: không biết lệnh đã tới broker chưa (khởi động lại / lỗi giữa "
                                   "intent và oid) — KHÔNG đặt lại")
                    elif self.bot_stopped() and s in ("OPEN", "EXIT_PLACED"):
                        self._bot_stop_cycle(t, s)
                    elif self.bot_stopped() and s == "INIT":
                        self._skip("data/BOT_STOP")
                    elif s == "INIT":
                        self.step_entry(t)
                    elif s == "ENTRY_PLACED":            # resume: chờ oid cũ, KHÔNG đặt lại (huỷ được kể cả BOT_STOP)
                        self._await_entry(self.state["entry_oid"], "buy" if self.state["sig"] > 0 else "sell",
                                          self.state.get("last_px_at_entry"))
                    elif s == "EXIT_PLACED":
                        self._await_exit(self.state["exit_oid"], "sell" if self.state["sig"] > 0 else "buy",
                                         self.state.get("entry_px"))
                    elif s == "OPEN":
                        self.step_open(t)
                    else:                               # stage lạ ⇒ không bao giờ quay vô hạn
                        self.pause(f"stage bất thường trong vòng lặp: {s}")
                    self.err_n = 0
                    self._last_alert.pop("loop_err", None)   # minor vòng 4: hồi phục ⇒ đợt lỗi sau báo ngay
                except OrderRefused as ex:
                    self.raw("order_refused", repr(ex))
                    self.alert_repeat("refused", "refused", f"lệnh bị chặn: {ex}")
                except Exception as ex:                 # noqa: BLE001 — B4: lỗi thoáng qua ⇒ thử lại chu kỳ sau
                    self.err_n += 1
                    self.raw("loop_err", {"n": self.err_n, "stage": self.state["stage"], "err": repr(ex)})
                    if self.err_n >= WATCH_ERR_ALERT_N:  # N-b: ≤1 tin / ALERT_REPEAT_S (khoá riêng), không mỗi N lỗi
                        self.alert_repeat("loop_err", "watch_err", f"{self.err_n} lỗi LIÊN TIẾP trong vòng giám sát "
                                          f"(stage {self.state['stage']}): {ex!r}"[:300] + " — bot vẫn thử lại; nếu "
                                          "đang có vị thế, stop có thể KHÔNG được giám sát.")
                if self.state["stage"] == "OPEN" and t.time() >= dt.time(14, 30):
                    self.alert_repeat("late_open", "late_open", (   # N-c: nội dung đúng khi BOT_STOP chặn cả lệnh đóng
                        "⚠️ đã qua 14:29 mà vị thế ORB vẫn MỞ, BOT_STOP đang bật — bot KHÔNG đặt lệnh nào, "
                        "cần user đóng tay." if self.bot_stopped() and not ORB_CLOSE_ALLOWED_UNDER_BOT_STOP else
                        "⚠️ đã qua 14:29 mà vị thế ORB vẫn MỞ — bot đang đặt lại lệnh đóng; nếu tới 14:45 chưa "
                        "đóng ⇒ user đóng tay."))
                if self.state["stage"] in TERMINAL:     # R2: vừa kết thúc TRONG tiến trình này ⇒ nhìn broker ngay
                    if self.live:                       # (khớp ngầm không được im lặng tới lần watchdog sau)
                        self.watch_broker(f"vừa chuyển sang {self.state['stage']}", TERMINAL_CONFIRM_TRIES)
                    return self.state["stage"]
                if once:
                    return self.state["stage"]
                self.sleep(POLL_S)


# ------------------------------------------------------------------ funding / plan block
def funding_status(client, account_id, *, target_vnd=100_000_000):
    """Ký quỹ phái sinh đủ cho 1 HĐ chưa? Pure-ish: chỉ READ.

    TỐI THIỂU = max(55tr; KQ ban đầu 1 HĐ + 2×lỗ chạm stop; KQ DUY TRÌ + 1 phiên tệ nhất lịch sử 9,46%).
    Lý do sàn 55tr (quant-skeptic 16/11): 1 ngày khoá trần/sàn ≈ −17,4tr kéo mức cũ 43,3tr xuống ~25,9tr <
    KQ duy trì 32,6tr ⇒ bị gọi KQ/thanh lý. Đích = 100tr (sleeve user chốt) — KHUYẾN NGHỊ nộp đủ 100tr. Field `derivative.*` của balances: ngữ nghĩa CHƯA XÁC MINH
    (TK đang 0 hết) ⇒ ước tiền ký quỹ = remainSecure + usedSecure + pendingSecure, gắn nhãn.
    """
    bal = client.balances(account_id)
    der = bal.get("derivative") or {}
    egg = fnum((bal.get("egg") or {}).get("totalValue"))
    pk = derivative_package(client, account_id)
    contract = resolve_contract(client)
    sd = secdef_g1(client, contract) if contract else None
    ref = fnum((sd or {}).get("basicPrice"))
    if not pk or not ref:
        return {"status": "UNVERIFIED", "why": "thiếu gói vay/giá tham chiếu", "contract": contract}
    notional = ref * MULT * CONTRACTS
    im = notional * float(pk.get("initialRate"))
    mm_rate = fnum(pk.get("maintenanceRate")) or float(pk.get("initialRate"))
    min_req = max(MIN_MARGIN_FLOOR_VND, im + 2 * STOP_PCT * notional, notional * (mm_rate + WORST_DAY_PCT))
    cash_est = sum(fnum(der.get(k)) or 0.0 for k in ("remainSecure", "usedSecure", "pendingSecure"))
    pp = client.ppse(account_id, contract, ref, market_type="DERIVATIVE", loan_package_id=pk["id"])
    qb, qs = fnum(qget(pp, "qmaxBuy")) or 0, fnum(qget(pp, "qmaxSell")) or 0
    ok = cash_est >= min_req and qb >= CONTRACTS and qs >= CONTRACTS
    short = 0.0 if ok else max(target_vnd - cash_est, min_req - cash_est, 0.0)
    short = -(-short // 100_000) * 100_000
    return {"status": "FUNDED" if ok else "SHORT", "contract": contract, "ref": ref, "notional": notional,
            "initial_rate": pk.get("initialRate"), "maintenance_rate": pk.get("maintenanceRate"),
            "im_vnd": im, "min_required_vnd": min_req, "target_vnd": target_vnd,
            "der_cash_est_vnd": cash_est, "der_fields": der, "qmax_buy": qb, "qmax_sell": qs,
            "short_vnd": short, "egg_vnd": egg,
            "fee_per_contract_side_dnse": _dnse_fee(pk), "fields_semantics_verified": False}


def _dnse_fee(pk):
    tf = (pk.get("tradingFee") or {}).get("progressTradingFee") or []
    for b in tf:
        if b.get("fromQuantity", 0) <= CONTRACTS <= b.get("toQuantity", 0):
            return b.get("fee")
    return None


def plan_block(account, client, account_id, enabled, fund=None):
    """Khối markdown cho plan report T+1 — LUẬT duyệt trước, KHÔNG có lệnh cụ thể.
    N1: cờ TẮT ⇒ CHỈ 1 dòng trạng thái, không đọc broker, KHÔNG in 'CẦN NỘP KÝ QUỸ'."""
    if not enabled:
        return ("**ORB sleeve (VN30F): TẮT/DRY** — bot chỉ chạy mô phỏng (đọc giá, không gửi lệnh); "
                "KHÔNG cần nộp ký quỹ phái sinh.")
    tr = lambda v: f"{v / 1e6:,.1f}tr"                       # noqa: E731
    lines = [f"**ORB futures sleeve (VN30F) — {'LIVE' if enabled else 'DRY-RUN (cờ TẮT, không gửi lệnh)'}**",
             f"Luật duyệt trước: {CONTRACTS} HĐ VN30F1M · tín hiệu sign(OR 09:00–09:30) · vào 09:31–09:40 · "
             f"thoát 14:29 · stop thảm hoạ ±{STOP_PCT:.1%} từ giá khớp · không giữ qua đêm · OR=0 ⇒ đứng ngoài. "
             "Hướng long/short chỉ biết sau 09:30 — bot báo Trading Daily khi vào/thoát."]
    try:
        f = fund or funding_status(client, account_id)
    except Exception as ex:                                  # noqa: BLE001 — fail-open cho plan report
        return "\n".join(lines + [f"⚠️ Không kiểm được ký quỹ phái sinh ({ex!r})"[:200]])
    if f["status"] == "UNVERIFIED":
        lines.append(f"⚠️ Ký quỹ phái sinh: KHÔNG KIỂM ĐƯỢC ({f['why']}).")
    else:
        lines.append(f"HĐ {f['contract']} tham chiếu {f['ref']:g} ⇒ notional {tr(f['notional'])}; ký quỹ ban đầu "
                     f"{float(f['initial_rate']):.2%} = {tr(f['im_vnd'])}; tối thiểu {tr(f['min_required_vnd'])} (sàn 55tr: KQ duy trì + 1 phiên khoá trần/sàn); "
                     f"đích sleeve {tr(f['target_vnd'])}. Tiền phái sinh ước {tr(f['der_cash_est_vnd'])} "
                     f"(ngữ nghĩa field chưa xác minh), ppse qmax mua/bán {f['qmax_buy']:g}/{f['qmax_sell']:g}.")
        if f["status"] == "SHORT":
            egg = f.get("egg_vnd")
            lines.append(f"🥚 **CẦN NỘP KÝ QUỸ PHÁI SINH ≥ {tr(f['short_vnd'])} trước 09:25** "
                         f"(Trứng vàng hiện {tr(egg) if egg is not None else '?'}). Làm TAY trên app DNSE: "
                         "Trứng vàng → tiền cơ sở → Nộp ký quỹ phái sinh (DNSE OpenAPI không có API chuyển). "
                         "Chưa nộp ⇒ ORB BỎ phiên, cổ phiếu không bị ảnh hưởng.")
    return "\n".join(lines)


# ------------------------------------------------------------------ CLI
def make_client(profile):
    sys.path.insert(0, WC_ROOT)
    from trading_bot.brokers import get_dnse_client
    return get_dnse_client(profile.get("credentials_file"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account", default="SpaceX")
    ap.add_argument("--once", action="store_true", help="1 chu kỳ rồi thoát")
    ap.add_argument("--plan-block", action="store_true", help="in khối plan report rồi thoát")
    ap.add_argument("--funding-alert", action="store_true",
                    help="nhắc nộp ký quỹ (chỉ khi cờ BẬT và thiếu; 1 lần báo 'đủ'/ngày)")
    a = ap.parse_args(argv)
    prof, ocfg = load_profile(a.account)
    acc = prof.get("account_id")
    c = make_client(prof)
    if a.plan_block:
        print(plan_block(a.account, c, acc, ocfg["enabled"])); return 0
    if a.funding_alert:
        return funding_alert(a.account, c, acc, ocfg["enabled"])
    if not ocfg["account_enabled"]:
        print(f"[orb_fut] account {a.account} enabled≠true ⇒ ORB tắt theo (chạy DRY).")
    live = ocfg["enabled"] and prof.get("mode") == "live"
    if live and not c.has_trading_token():
        default_notify(f"🔴 **ORB VN30F {a.account} [LIVE]** — không có trading-token DNSE (run_bot 09:05 "
                       "lẽ ra đã tạo) ⇒ BỎ phiên.", red=True)
        return 2
    wd = c.working_dates()
    today = dt.datetime.now(ICT).date()
    if str(today) not in (wd.get("workingDates") or []):
        print(f"[orb_fut] {today} không phải ngày giao dịch (DNSE working-dates)."); return 0
    print(OrbFutures(c, a.account, acc, live).run(once=a.once))
    return 0


def funding_alert(account, client, account_id, enabled, data_dir=None):
    if not enabled:
        print("[orb_fut] cờ TẮT — không nhắc ký quỹ."); return 0
    d = os.path.join(data_dir or DATA_DIR, "orb_futures")
    os.makedirs(d, exist_ok=True)
    today = dt.datetime.now(ICT).date()
    st_path = os.path.join(d, f"funding_alert_{account}_{today}.json")
    f = funding_status(client, account_id)
    prev = {}
    if os.path.exists(st_path):
        with open(st_path, encoding="utf-8") as fh:
            prev = json.load(fh)
    if f["status"] == "FUNDED":
        if prev.get("alerted") and not prev.get("ok_sent"):
            prev["ok_sent"] = default_notify(f"✅ ORB VN30F {account}: ký quỹ phái sinh đã đủ.", red=True)
    else:
        ok = default_notify("🥚 " + plan_block(account, client, account_id, enabled, fund=f).split("\n")[-1],
                            red=True)
        prev["alerted"] = prev.get("alerted") or ok          # M3: gửi hỏng ⇒ không latch, lần sau nhắc lại
    tmp = st_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(prev | {"last": f["status"]}, fh)
    os.replace(tmp, st_path)
    return 0


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        sys.exit(main())
