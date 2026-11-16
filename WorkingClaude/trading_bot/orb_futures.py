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
  • KHÔNG BAO GIỜ giữ qua đêm: sau 14:29 vẫn còn vị thế ⇒ đặt lại lệnh đóng mỗi 30s; 14:45 còn
                vị thế ⇒ cảnh báo ĐỎ cho user đóng tay.
  • Tín hiệu = 0 ⇒ không vào.

CHẾ ĐỘ: `orb_futures.enabled` (khóa CẤP PROFILE trong secrets/trading_bot_accounts.json, KHÔNG nằm
trong `overrides` để khỏi đụng config.py) MẶC ĐỊNH False ⇒ DRY-RUN: đọc giá thật DNSE, chạy đủ máy
trạng thái, ghi lệnh DỰ KIẾN + khớp giả lập vào journal, KHÔNG gọi place/cancel. Chỉ user bật.

AN TOÀN (coding_guidelines §5/§5b/§12/§16/§27)
  • fcntl.flock không chặn: tiến trình thứ 2 thoát ngay (cron watchdog gọi lại an toàn).
  • data/BOT_STOP ⇒ không đặt BẤT KỲ lệnh nào (kể cả lệnh đóng) + báo động mỗi chu kỳ khi có vị thế.
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

TERMINAL = ("CLOSED", "FLAT", "SKIPPED", "PAUSED")


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
            cfg["enabled"] = cfg.get("enabled") is True        # chỉ đúng literal true mới bật
            return p, cfg
    raise SystemExit(f"[orb_fut] không có account '{account}' trong {path}")


def default_notify(msg):
    """Discord Trading Daily (+ Telegram cho báo động). Bị chặn trong test mode."""
    if test_mode():
        sink = os.environ.get("MIKE_BOT_TEST_EVENT_SINK")
        if sink:
            with open(sink, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"notify": msg}, ensure_ascii=False) + "\n")
        return
    p = os.path.join(MIKE_BIN, "notify_thread.sh")
    if os.path.isfile(p):
        try:
            subprocess.run([p, msg, "trading_daily"], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=60)
        except Exception as ex:                                     # noqa: BLE001
            print(f"[orb_fut] notify lỗi: {ex}", file=sys.stderr)


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
    return rows_of(client.positions(account_id, market_type="DERIVATIVE"), "positions", "data")


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
    return rows_of(client.orders(account_id, market_type="DERIVATIVE"), "orders", "data")


def order_fill(client, account_id, oid):
    """(filled_qty, avg_price, status) — đọc từ order_detail của broker (§27 khớp thật)."""
    r = client.order_detail(account_id, oid, market_type="DERIVATIVE")
    r = r.get("order", r) if isinstance(r, dict) else r
    q = fnum(qget(r, "fillQuantity", "filledQuantity", "cumQty", "matchedQuantity")) or 0.0
    px = fnum(qget(r, "averagePrice", "avgPrice", "fillPrice", "matchPrice"))
    st = str(qget(r, "orderStatus", "status", default=""))
    return int(q), px, st


def order_dead(status):
    s = status.lower()
    if "partial" in s:
        return False
    return any(k in s for k in ("cancel", "reject", "fill", "expire"))


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

    # ---- persistence
    def _load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, encoding="utf-8") as f:
                return json.load(f)
        return {"date": str(self.day), "account": self.account, "mode": self.mode, "stage": "INIT",
                "known_oids": [], "contracts": CONTRACTS, "stop_pct": STOP_PCT}

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
        body = {"account": self.account, "mode": self.mode, "date": str(self.day), "msg": msg}
        body.update(payload or {})
        self.raw("alert", body)
        self.publish(level, f"orb_futures_{topic}", body)
        self.notify(f"{'🔴' if level == 'error' else 'ℹ️'} **ORB VN30F {self.account} [{self.mode}]** — {msg}")

    def pause(self, reason, **kw):
        self.stage("PAUSED", pause_reason=reason, **kw)
        self.journal("PAUSED", note=reason)
        self.alert("paused", f"PAUSED: {reason}. Bot KHÔNG đặt thêm lệnh — cần người kiểm tra.")

    # ---- guards
    def bot_stopped(self):
        return os.path.exists(self.bot_stop_file)

    def reconcile(self):
        """Broker là nguồn sự thật. True = khớp state; False = đã PAUSE."""
        try:
            pos = broker_positions(self.c, self.acc)
            ords = broker_orders(self.c, self.acc)
        except Exception as ex:                                     # noqa: BLE001
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
        net = 0.0
        for p in pos:
            q = position_qty(p)
            if q is None:
                self.pause("có dòng vị thế phái sinh không đọc được số lượng (schema chưa xác minh)",
                           positions=pos)
                return False
            net += q
        if not self.live:
            return True                                             # DRY: broker không có lệnh của ta
        expect = self.state.get("sig", 0) * CONTRACTS if self.state["stage"] in ("OPEN", "EXIT_PENDING",
                                                                                  "EXIT_PLACED") else 0
        if self.state["stage"] in ("ENTRY_PLACED",):
            return True                                             # đang chờ khớp — check ở bước fill
        if abs(net - expect) > 1e-9:
            self.pause(f"vị thế broker {net:+.0f} HĐ ≠ state kỳ vọng {expect:+d} HĐ", positions=pos)
            return False
        return True

    # ---- order primitives (DRY ⇒ giả lập, KHÔNG gọi broker)
    def _place(self, side, price, purpose):
        """Ghi intent → đặt → ghi oid ngay (§5). Trả oid."""
        self.stage(f"{purpose}_PENDING", **{f"{purpose.lower()}_intent": {"side": side, "price": price,
                                                                           "ts": self.now().isoformat()}})
        if not self.live:
            oid = f"DRY-{purpose}-{self.day}"
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
        self.stage(f"{purpose}_PLACED", **{f"{purpose.lower()}_oid": oid})
        return oid

    def _fill(self, oid, side, sim_px):
        if not self.live:
            return CONTRACTS, sim_px, "DRY_FILLED"
        q, px, st = order_fill(self.c, self.acc, oid)
        self.raw("order_detail", {"oid": oid, "filled": q, "avg": px, "status": st})
        return q, px, st

    def _cancel(self, oid):
        if self.live:
            r = self.c.cancel_order(self.acc, oid, market_type="DERIVATIVE")
            self.raw("cancel_order", {"oid": oid, "resp": r})
        self.journal("CANCEL", oid=oid)

    # ---- stages
    def step_entry(self, t):
        if t.time() < ENTRY_OPEN:
            return
        if t.time() > ENTRY_DEADLINE:
            self.stage("SKIPPED", skip_reason="lỡ cửa sổ vào lệnh 09:31–09:40")
            self.journal("SKIP", note=self.state["skip_reason"])
            self.alert("skip", "BỎ phiên: lỡ cửa sổ vào lệnh 09:31–09:40.", level="status")
            return
        sig, info = compute_signal(bars_today(self.c, self.day), strict=t.time() < dt.time(9, 33))
        if sig is None:
            if t.time() >= dt.time(9, 33):           # cho feed 2 phút; sau đó bỏ phiên
                self.stage("SKIPPED", skip_reason=f"dữ liệu tín hiệu không đủ: {info}")
                self.journal("SKIP", note=self.state["skip_reason"])
                self.alert("skip", f"BỎ phiên: {info}", level="status")
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
                self.stage("SKIPPED", skip_reason=f"sức mua phái sinh không đủ (qmax={qmax:g})")
                self.journal("SKIP", note=self.state["skip_reason"])
                self.alert("funding", f"BỎ phiên — ký quỹ phái sinh KHÔNG đủ cho {CONTRACTS} HĐ "
                           f"(ppse qmax={qmax:g}). Xem cảnh báo nộp ký quỹ.")
                return
        if not self.reconcile():
            return
        lim = round_tick(px * (1 + sig * ENTRY_SLIP_CAP))
        lim = min(max(lim, floor_ or lim), ceil_ or lim)
        oid = self._place(side, lim, "ENTRY")
        self._await_entry(oid, side, px)

    def _await_entry(self, oid, side, sim_px):
        t0 = self.now()                                  # đồng hồ tiêm được (test), không monotonic
        while True:
            q, fpx, st = self._fill(oid, side, sim_px)
            if q >= CONTRACTS:
                return self._opened(oid, side, fpx)
            if order_dead(st) or (self.now() - t0).total_seconds() > ORDER_FILL_WAIT_S:
                if not order_dead(st):
                    self._cancel(oid)
                    self.sleep(2)
                q, fpx, st = self._fill(oid, side, sim_px)
                if q >= CONTRACTS:
                    return self._opened(oid, side, fpx)
                if q > 0:                       # không thể với 1 HĐ — nhưng không đoán
                    return self.pause(f"lệnh vào {oid} khớp lẻ {q}/{CONTRACTS}")
                self.stage("SKIPPED", skip_reason=f"lệnh vào {oid} không khớp ({st})")
                self.journal("SKIP", oid=oid, note=self.state["skip_reason"])
                self.alert("skip", f"BỎ phiên: lệnh vào không khớp trong {ORDER_FILL_WAIT_S}s, đã huỷ.",
                           level="status")
                return
            self.sleep(POLL_S)

    def _opened(self, oid, side, fpx):
        sig = self.state["sig"]
        stop = round_tick(fpx * (1 - sig * STOP_PCT))
        self.stage("OPEN", entry_px=fpx, stop_px=stop, filled_total=CONTRACTS * sig,
                   entry_ts=self.now().isoformat())
        self.journal("FILL", side, oid, CONTRACTS, fpx, note=f"entry; stop={stop}")
        self.publish("status", "orb_futures_entry", {"account": self.account, "mode": self.mode,
                     "contract": self.state["contract"], "side": side, "px": fpx, "stop": stop})
        self.notify(f"📈 **ORB VN30F {self.account} [{self.mode}]** VÀO {'LONG' if sig > 0 else 'SHORT'} "
                    f"{CONTRACTS} HĐ {self.state['contract']} @ {fpx} (OR {self.state['signal']['or_ret']:+.2%}). "
                    f"Stop thảm hoạ {stop} (±{STOP_PCT:.1%}); thoát 14:29.")

    def step_open(self, t):
        if t.time() >= EXIT_AT:
            return self._exit("TIME", t)
        if LUNCH[0] <= t.time() < LUNCH[1]:
            return
        px, _ = last_trade_px(self.c, self.state["contract"])
        if px is None:
            return
        sig, stop = self.state["sig"], self.state["stop_px"]
        if (sig > 0 and px <= stop) or (sig < 0 and px >= stop):
            self.state["stop_trigger_px"] = px
            return self._exit("STOP", t)

    def _exit(self, reason, t):
        sig = self.state["sig"]
        side = "sell" if sig > 0 else "buy"
        # Đóng = LO ngược chiều ở giá sàn (đóng long) / trần (đóng short) — theo docs DNSE
        # "đóng vị thế": khớp ở giá tốt nhất hiện có, không phải ở sàn/trần.
        price = self.state["floor"] if sig > 0 else self.state["ceiling"]
        if not self.reconcile():
            return
        self.state["exit_reason"] = reason
        px_now, _ = last_trade_px(self.c, self.state["contract"])
        oid = self._place(side, price, "EXIT")
        self._await_exit(oid, side, px_now or self.state["entry_px"])

    def _await_exit(self, oid, side, sim_px):
        t0 = self.now()                                  # đồng hồ tiêm được (test), không monotonic
        while True:
            q, fpx, st = self._fill(oid, side, sim_px)
            if q >= CONTRACTS:
                return self._closed(oid, side, fpx)
            if self.now().time() >= SESSION_END:
                return self.alert("overnight", f"⛔ 14:45 VẪN CÒN VỊ THẾ {self.state['contract']} "
                                  f"(lệnh đóng {oid} {st}) — USER ĐÓNG TAY NGAY. Bot không giữ qua đêm.")
            if order_dead(st) or (self.now() - t0).total_seconds() > EXIT_RETRY_S:
                if not order_dead(st):
                    self._cancel(oid); self.sleep(2)
                q, fpx, st = self._fill(oid, side, sim_px)
                if q >= CONTRACTS:
                    return self._closed(oid, side, fpx)
                self.stage("OPEN")                      # đặt lại ở chu kỳ sau (reconcile trước)
                return
            self.sleep(POLL_S)

    def _closed(self, oid, side, fpx):
        sig, epx = self.state["sig"], self.state["entry_px"]
        pts = sig * (fpx - epx)
        gross = pts * MULT * CONTRACTS
        self.stage("CLOSED", exit_px=fpx, exit_ts=self.now().isoformat(), filled_total=0,
                   pnl_points=round(pts, 2), pnl_gross_vnd=round(gross))
        self.journal("FILL", side, oid, CONTRACTS, fpx,
                     note=f"exit {self.state['exit_reason']}; pnl_gross={gross:.0f}VND")
        self.publish("finding" if self.state["exit_reason"] == "STOP" else "status", "orb_futures_exit",
                     {"account": self.account, "mode": self.mode, "reason": self.state["exit_reason"],
                      "entry": epx, "exit": fpx, "pnl_gross_vnd": round(gross)})
        self.notify(f"{'🛑' if self.state['exit_reason'] == 'STOP' else '🏁'} **ORB VN30F {self.account} "
                    f"[{self.mode}]** THOÁT ({self.state['exit_reason']}) @ {fpx}; vào {epx} ⇒ "
                    f"{pts:+.1f} điểm = {gross / 1e6:+,.2f}tr gộp (CHƯA trừ phí/thuế).")

    def resume_check(self):
        """Khởi động lại giữa chừng: _PENDING không oid ⇒ PAUSE; _PLACED ⇒ chờ khớp tiếp, KHÔNG đặt lại."""
        s = self.state["stage"]
        if s in ("ENTRY_PENDING", "EXIT_PENDING"):
            self.pause(f"khởi động lại ở {s}: không biết lệnh đã gửi broker chưa")
            return False
        if s == "ENTRY_PLACED":
            self._await_entry(self.state["entry_oid"], "buy" if self.state["sig"] > 0 else "sell",
                              self.state.get("last_px_at_entry"))
        elif s == "EXIT_PLACED":
            self._await_exit(self.state["exit_oid"], "sell" if self.state["sig"] > 0 else "buy",
                             self.state.get("entry_px"))
        return True

    # ---- main loop
    def run(self, once=False):
        with open(self.lock_file, "a+") as lf:
            try:
                fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print("[orb_fut] tiến trình khác đang giữ khoá — thoát."); return "LOCKED"
            if self.state["stage"] in TERMINAL:
                print(f"[orb_fut] state {self.state['stage']} — không làm gì."); return self.state["stage"]
            if not self.resume_check():
                return self.state["stage"]
            if self.state["stage"] == "INIT" and not self.reconcile():
                return self.state["stage"]
            while True:
                t = self.now()
                s = self.state["stage"]
                if s in TERMINAL:
                    return s
                if self.bot_stopped():
                    last = self.state.get("bot_stop_alert_ts")
                    if s == "OPEN" and (not last or (t - dt.datetime.fromisoformat(last)).total_seconds() >= 300):
                        self.state["bot_stop_alert_ts"] = t.isoformat(); self.save()
                        self.alert("bot_stop", "data/BOT_STOP đang bật VÀ còn vị thế mở — bot KHÔNG đặt lệnh "
                                   "đóng. User tự xử lý.")
                    else:
                        self.stage("SKIPPED", skip_reason="data/BOT_STOP")
                        self.journal("SKIP", note="BOT_STOP")
                    if once or s != "OPEN":
                        return self.state["stage"]
                elif s == "INIT":
                    self.step_entry(t)
                elif s == "OPEN":
                    self.step_open(t)
                else:                                   # stage lạ/kẹt (vd _PENDING) ⇒ không bao giờ quay vô hạn
                    self.pause(f"stage bất thường trong vòng lặp: {s}")
                    return self.state["stage"]
                if t.time() >= SESSION_END:
                    if self.state["stage"] == "OPEN":
                        self.alert("overnight", "⛔ 14:45 còn vị thế ORB — USER ĐÓNG TAY NGAY.")
                    return self.state["stage"]
                if once:
                    return self.state["stage"]
                self.sleep(POLL_S)


# ------------------------------------------------------------------ funding / plan block
def funding_status(client, account_id, *, target_vnd=100_000_000):
    """Ký quỹ phái sinh đủ cho 1 HĐ chưa? Pure-ish: chỉ READ.

    Cần TỐI THIỂU = ký quỹ ban đầu 1 HĐ (gói vay thật) + lỗ khi chạm stop + đệm 1 stop nữa cho gap.
    Đích = 100tr (sleeve user chốt). Field `derivative.*` của balances: ngữ nghĩa CHƯA XÁC MINH
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
    min_req = im + 2 * STOP_PCT * notional
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
    """Khối markdown cho plan report T+1 — LUẬT duyệt trước, KHÔNG có lệnh cụ thể."""
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
                     f"{float(f['initial_rate']):.2%} = {tr(f['im_vnd'])}; tối thiểu (KQ + 2×stop) {tr(f['min_required_vnd'])}; "
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
    live = ocfg["enabled"] and prof.get("mode") == "live"
    if live and not c.has_trading_token():
        default_notify(f"🔴 **ORB VN30F {a.account} [LIVE]** — không có trading-token DNSE (run_bot 09:05 "
                       "lẽ ra đã tạo) ⇒ BỎ phiên.")
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
            default_notify(f"✅ ORB VN30F {account}: ký quỹ phái sinh đã đủ.")
            prev["ok_sent"] = True
    else:
        default_notify("🥚 " + plan_block(account, client, account_id, enabled, fund=f).split("\n")[-1])
        prev["alerted"] = True
    tmp = st_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(prev | {"last": f["status"]}, fh)
    os.replace(tmp, st_path)
    return 0


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        sys.exit(main())
