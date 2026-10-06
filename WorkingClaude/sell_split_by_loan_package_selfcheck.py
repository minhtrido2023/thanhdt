#!/usr/bin/env python3
"""sell_split_by_loan_package_selfcheck.py — lệnh BÁN trải nhiều gói vay phải TÁCH theo gói.

Sự cố 2026-10-06 (ZaloPay 0001743768, PARKMERGE-SELL-BID): bán 27 BID, positions THẬT lúc
09:15:01 (`data/execution_logs/dnse_raw_2026-10-06.jsonl`, kind=positions) có 2 deal:
gói 1258 tradeQuantity=20, gói 1826 tradeQuantity=7. Bot gửi MỘT lệnh 27@1258 ⇒ DNSE HTTP 400
"Trade quantity not enough" ×5 ⇒ PLACE_FAIL_STOPPED. DNSE KHÔNG khớp một phần theo gói.

Fix: executor hỏi `DNSEBroker.plan_sell_leg` ⇒ không gói nào đủ ⇒ đặt CHÂN ĐẦU (≤ sellable
một gói, mang `sell_loan_package_id` = gói đó) như một lệnh con BÌNH THƯỜNG; chân kế tiếp
tính lại ở vòng sau trên positions mới (đi ngay nếu chân trước khớp đủ).

Nhóm ca:
  A  ca BID THẬT          27 = 20@1258 + 7@1826, không PLACE_FAIL, parent DONE
  B  BYTE-IDENTICAL       mọi ca CÓ gói đủ: lời gọi DNSE + log place_order + journal + state
                           GIỐNG HỆT code TRƯỚC fix (BASE_REV, chạy thật trong subprocess)
  C  lô chẵn+lẻ trải gói   150/30 bán 180 ⇒ 100 + 50 + 30, mọi lệnh hợp lệ lô; property 5.000 ca
  D  kill giữa 2 chân     restart không bán trùng (state có chân 1 / ghost-guard khi chưa kịp ghi)
  E  positions lỗi        không tách, đường cũ (gói default) + log có lỗi thật
  F  ATC                  1 chân lô chẵn ở 1 gói; không gói nào ≥1 lô ⇒ bỏ ATC, journal 1 lần
  G  ranh giới            đòn bẩy CAPIT không tách; broker không hỗ trợ / MagicMock không tách;
                           sell_loan_package_id sai ngữ cảnh ⇒ ValueError; tick-retry giữ gói

Mô phỏng DNSE (FakeClient): lệnh bán bị từ chối CẢ lệnh nếu qty > tradeQuantity của ĐÚNG gói
gửi lên (đo được 10-06). Đặt lệnh bán KHÔNG giữ tradeQuantity — nó chỉ giảm khi KHỚP (đo được:
LPB SpaceX 2026-09-29, VPB ZaloPay 2026-07-15 trong dnse_raw); huỷ lệnh không đổi gì.
`stale_positions=True` ⇒ positions() trả ảnh chụp CŨ tới khi gọi `refresh()` (fill đã thấy ở
poll lệnh nhưng positions chưa cập nhật) — DNSE vẫn kiểm theo số THẬT.

Chạy: python3 sell_split_by_loan_package_selfcheck.py [--mutations]
  (không mạng; SELLSPLIT_CODE_ROOT=<dir> = import trading_bot từ thư mục khác — dùng nội bộ
  cho so sánh BASE_REV và mutation)
"""
import copy
import csv
import datetime as dt
import glob
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")   # §5b — chặn _publish_bot_event ra bus THẬT

WC_ROOT = os.path.dirname(os.path.abspath(__file__))
CODE_ROOT = os.environ.get("SELLSPLIT_CODE_ROOT") or WC_ROOT
os.environ.setdefault("TRADING_BOT_RUNTIME_ROOT", WC_ROOT)
for _p in (WC_ROOT, CODE_ROOT):
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

from trading_bot.brokers import DNSEBroker, OrderUpdate, Quote  # noqa: E402
from trading_bot.config import EXEC_DIR, load_config  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan  # noqa: E402
from dnse_api import DNSEError  # noqa: E402

# Code TRƯỚC fix (parent của branch). Ghim cứng, KHÔNG dùng merge-base: sau khi merge, merge-base
# chính là bản fix ⇒ so "mới với mới" sẽ xanh vô nghĩa.
BASE_REV = "e829f429"
TAG = "selfcheck-sellsplit"
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(_f)

FAILS = []


def check(cond, msg):
    print(("  OK  " if cond else " FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


# ─────────────────────────────── mô phỏng DNSE ───────────────────────────────
def _row(symbol, lp, q, acc="0001743768"):
    return {"symbol": symbol, "status": "OPEN", "loanPackageId": lp, "openQuantity": q,
            "tradeQuantity": q, "accountNo": acc}


class FakeClient:
    def __init__(self, rows, default_lp, raise_positions=False, tick_fail_once=False,
                 pkg_ids=None, stale_positions=False):
        self.loan_package_id = default_lp
        self.rows = [dict(r) for r in rows]
        self.stale = [dict(r) for r in rows] if stale_positions else None
        self.accepted = []
        self.raise_positions = raise_positions
        self.tick_fail_once = tick_fail_once
        self.pkg_ids = pkg_ids or [default_lp]
        self.calls = []
        self.book = {}
        self.n_positions = 0

    def positions(self, account_id):
        self.n_positions += 1
        if self.raise_positions:
            raise RuntimeError("simulated positions timeout")
        src = self.stale if self.stale is not None else self.rows
        return {"positions": [dict(r) for r in src]}

    def refresh(self):
        if self.stale is not None:
            self.stale = [dict(r) for r in self.rows]

    def loan_packages(self, account_id, market_type="STOCK", symbol=None):
        return {"loanPackages": [{"id": i, "type": "M"} for i in self.pkg_ids]}

    def _deal(self, symbol, lp):
        return next((r for r in self.rows if r["symbol"] == symbol
                     and str(r["loanPackageId"]) == str(lp)), None)

    def place_order(self, account_id, symbol, qty, side, order_type="LO", price=None,
                    loan_package_id=None):
        self.calls.append({"symbol": symbol, "qty": qty, "side": side, "order_type": order_type,
                           "price": price, "loan_package_id": loan_package_id})
        if self.tick_fail_once:
            self.tick_fail_once = False
            raise DNSEError("HTTP 400: Invalid price lot", status=400)
        if side == "sell":
            d = self._deal(symbol, loan_package_id)
            if d is None:
                raise DNSEError("HTTP 400: deal not found", status=400)
            if qty > d["tradeQuantity"]:
                raise DNSEError("HTTP 400: Trade quantity not enough", status=400)
            # KHÔNG trừ tradeQuantity ở đây: DNSE chỉ trừ khi KHỚP (xem fill).
        self.accepted.append((symbol, qty, loan_package_id, order_type, side))
        oid = str(9000 + len(self.calls))
        self.book[oid] = {"symbol": symbol, "qty": qty, "filled": 0, "status": "New",
                          "lp": loan_package_id, "side": side}
        return {"id": int(oid), "symbol": symbol, "quantity": qty}

    def fill(self, oid, n=None):
        o = self.book[oid]
        n = o["qty"] if n is None else n
        o["filled"] = n
        o["status"] = "Filled" if n >= o["qty"] else "PartiallyFilled"
        if o["side"] == "sell":
            d = self._deal(o["symbol"], o["lp"])
            d["openQuantity"] -= n
            d["tradeQuantity"] -= n

    def kill(self, oid):
        self.book[oid]["status"] = "Canceled"


def make_quote(symbol, px=34550):
    q = Quote.__new__(Quote)
    q.raw = {}
    q.symbol = symbol
    q.exchange = "HOSE"
    q.exchange_known = True
    q.last = q.ref = px
    q.ceiling = px * 1.07
    q.floor = px * 0.93
    q.bid = px - 50
    q.ask = px + 50
    q.day_volume = None
    return q


class StubDNSE(DNSEBroker):
    """DNSEBroker THẬT (place_order / plan_sell_leg / resolve / get_positions) trên FakeClient;
    chỉ thay quote / tiền / sổ lệnh / huỷ."""
    name = "dnse"

    def get_quote(self, symbol, *a, **k):
        return make_quote(symbol)

    def get_cash(self):
        return 10 ** 12

    def get_max_buy_qty(self, *a, **k):
        return 10 ** 9

    def poll_orders(self):
        return {oid: OrderUpdate(oid, o["status"], o["filled"], 34550,
                                 raw={"symbol": o["symbol"]})
                for oid, o in self.client.book.items()}

    def cancel_order(self, oid):
        self.client.kill(str(oid))
        return {}


def make_broker(client, default_lp):
    b = StubDNSE.__new__(StubDNSE)
    b.account_id = "0001743768"
    b.label = "ZaloPay"
    b.client = client
    b._loan_package_id = default_lp
    b._loan_pkg_cache = {}
    b._lever_pkg_cache = {}
    b.raw_log = []
    b._log_raw = lambda kind, payload: b.raw_log.append((kind, copy.deepcopy(payload)))
    return b


NOW = dt.datetime(2099, 1, 1, 9, 20)


def make_exec(tmp, orders, broker):
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=orders,
                     account=TAG, created_at="2099-01-01T00:00:00")
    cfg = load_config()
    cfg["mode"] = "paper"
    cfg["fill_timing_hybrid_enabled"] = False      # đo đường bán, không đo lịch HYBRID
    cfg["order_book_shadow_enabled"] = False
    ex = Executor(plan, broker, cfg, shared={})
    ex.state_file = os.path.join(tmp, "state.json")
    ex.journal_file = os.path.join(tmp, "journal.csv")
    return ex


def cycle(ex, now, atc=False):
    """Đúng thứ tự `Executor.step()`: poll → sync_fills → ghost → positions → cancel_stale →
    place_slices | atc_sweep."""
    updates = ex.broker.poll_orders()
    ex._sync_fills(updates)
    ghosts = ex._ghost_tickers(updates)
    try:
        positions = ex.broker.get_positions()
    except Exception:
        positions = None                      # step(): POSITIONS_FAIL ⇒ positions=None
    if atc:
        ex._atc_sweep(ghosts, positions)
    else:
        ex._cancel_stale(now)
        ex._place_slices(now, "MORNING", ghosts, positions)
    ex._save_state()


def journal(ex):
    if not os.path.exists(ex.journal_file):
        return []
    with open(ex.journal_file, encoding="utf-8") as f:
        return [r[1:] for r in csv.reader(f) if len(r) > 1 and r[1] != "event"]


def sells(cl):
    return [(c["qty"], c["loan_package_id"]) for c in cl.calls if c["side"] == "sell"]


def trace(ex, b, cl):
    """Mọi thứ đi ra khỏi bot: lời gọi DNSE, log place_order + resolve, journal, state."""
    return {"calls": cl.calls,
            "place_log": [p for k, p in b.raw_log if k == "place_order"],
            "resolve_log": [p for k, p in b.raw_log if k == "sell_loan_package_resolve"],
            "journal": journal(ex),
            "children": [{k: v for k, v in c.items() if k != "ts"}
                         for ps in ex.state["parents"].values() for c in ps["children"]]}


# ─────────────────────── kịch bản dùng cho cả code mới lẫn BASE_REV ───────────────────────
def scen(rows, default_lp, orders, steps, **client_kw):
    with tempfile.TemporaryDirectory() as tmp:
        cl = FakeClient(rows, default_lp, **client_kw)
        b = make_broker(cl, default_lp)
        ex = make_exec(tmp, orders, b)
        for st in steps:
            st(ex, cl)
        return trace(ex, b, cl)


def _c(now, atc=False):
    return lambda ex, cl: cycle(ex, now, atc)


def _fill_last(ex, cl):
    live = [k for k, o in cl.book.items() if o["status"] == "New"]
    if live:                                  # BASE_REV: mọi lệnh bị từ chối ⇒ không có gì khớp
        cl.fill(live[-1])


SO = lambda q, t="BID", **kw: PlannedOrder(id=f"SELL-{t}", ticker=t, side="sell", qty=q,  # noqa: E731
                                            ref_price=34550, **kw)

UNCHANGED = {
    # SpaceX THẬT 10-06 09:15:00: BID 1841:75, bán 75 (gói default đủ, 1 gói)
    "U1_spacex_bid_75": lambda: scen([_row("BID", 1841, 75, "0002023347")], 1841, [SO(75)],
                                     [_c(NOW), _fill_last, _c(NOW + dt.timedelta(minutes=9))]),
    # ZaloPay 09-29 fixture: BID 1258:300 · 1826:100, bán 100 ⇒ default đủ
    "U2_default_sufficient": lambda: scen([_row("BID", 1258, 300), _row("BID", 1826, 100)], 1258,
                                          [SO(100)], [_c(NOW)]),
    # MBB 1258:2 · 1826:400, bán 400 ⇒ chỉ 1826 đủ (tie-break non-default)
    "U3_nondefault_sufficient": lambda: scen([_row("MBB", 1258, 2), _row("MBB", 1826, 400)], 1258,
                                             [SO(400, "MBB")], [_c(NOW)]),
    # HPG chỉ ở 1826, bán 300 qua 2 vòng (bán lỗi 9-29 nay đúng — không đổi)
    "U4_single_pkg_multi_cycle": lambda: scen([_row("HPG", 1826, 500)], 1258, [SO(300, "HPG")],
                                              [_c(NOW), _fill_last,
                                               _c(NOW + dt.timedelta(minutes=9))]),
    # Lệnh MUA không đụng đường bán
    "U5_buy": lambda: scen([], 1258, [PlannedOrder(id="BUY-1", ticker="BID", side="buy",
                                                   qty=200, ref_price=34550)], [_c(NOW)]),
    # Đòn bẩy CAPIT (loan_package_id=1840) bán khi KHÔNG gói nào đủ ⇒ KHÔNG tách, đường cũ
    "U6_lever_insufficient": lambda: scen([_row("BID", 1258, 20), _row("BID", 1826, 7)], 1258,
                                          [SO(27, loan_package_id=1840)], [_c(NOW)],
                                          pkg_ids=[1258, 1840]),
    # ATC có gói đủ ⇒ y hệt
    "U7_atc_sufficient": lambda: scen([_row("BID", 1258, 300), _row("BID", 1826, 100)], 1258,
                                      [SO(200)], [_c(NOW, atc=True)]),
    # Gói đủ nhưng lệnh vượt tổng sellable ⇒ cap T+2 cũ quyết, y hệt
    "U8_partial_sellable": lambda: scen([_row("VCB", 1258, 100), _row("VCB", 1826, 200)], 1258,
                                        [SO(200, "VCB")], [_c(NOW)]),
}
# positions lỗi: lệnh đi ra y hệt, NHƯNG có thêm 1 bản ghi log ⇒ so mọi thứ trừ resolve_log
UNCHANGED_EXCEPT_LOG = {
    "E1_positions_error": lambda: scen([_row("BID", 1258, 20), _row("BID", 1826, 7)], 1258,
                                       [SO(27)], [_c(NOW)], raise_positions=True),
}
INCIDENT = lambda: scen([_row("BID", 1826, 7), _row("BID", 1258, 20)], 1258, [SO(27)],  # noqa: E731
                        [_c(NOW), _fill_last, _c(NOW + dt.timedelta(seconds=20)), _fill_last,
                         _c(NOW + dt.timedelta(seconds=40))])


def all_traces():
    out = {k: f() for k, f in {**UNCHANGED, **UNCHANGED_EXCEPT_LOG}.items()}
    out["INCIDENT"] = INCIDENT()
    return out


if "--trace-json" in sys.argv:
    print("@@TRACE@@" + json.dumps(all_traces(), ensure_ascii=False, default=str))
    sys.exit(0)


def base_traces():
    """Chạy CHÍNH các kịch bản trên brokers.py + executor.py của BASE_REV (subprocess)."""
    top = subprocess.run(["git", "-C", WC_ROOT, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True).stdout.strip()
    prefix = os.path.relpath(WC_ROOT, top)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(os.path.join(WC_ROOT, "trading_bot"), os.path.join(tmp, "trading_bot"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        for f in ("brokers.py", "executor.py"):
            src = subprocess.run(["git", "-C", top, "show", f"{BASE_REV}:{prefix}/trading_bot/{f}"],
                                 capture_output=True, text=True, check=True).stdout
            with open(os.path.join(tmp, "trading_bot", f), "w", encoding="utf-8") as fh:
                fh.write(src)
        env = dict(os.environ, SELLSPLIT_CODE_ROOT=tmp)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--trace-json"],
                           capture_output=True, text=True, env=env, timeout=300)
        line = next((ln for ln in r.stdout.splitlines() if ln.startswith("@@TRACE@@")), None)
        if line is None:
            raise RuntimeError(f"BASE trace lỗi rc={r.returncode}: {r.stderr[-2000:]}")
        return json.loads(line[len("@@TRACE@@"):])


def mutations():
    """Bắn từng đột biến vào bản sao trading_bot/, chạy lại selfcheck — phải ĐỎ."""
    E, B = "executor.py", "brokers.py"
    muts = [
        ("M01 executor không truyền gói chân tách", E,
         "loan_package_id=getattr(o, \"loan_package_id\", None),\n"
         "                                              **place_kw)",
         "loan_package_id=getattr(o, \"loan_package_id\", None))"),
        ("M02 broker bỏ qua sell_loan_package_id", B,
         "lp = (sell_loan_package_id if sell_loan_package_id is not None\n"
         "                  else self._resolve_sell_loan_package_id(symbol, qty))",
         "lp = self._resolve_sell_loan_package_id(symbol, qty)"),
        ("M03 plan_sell_leg luôn None", B,
         "        lp, q = legs[0]\n", "        return None\n        lp, q = legs[0]\n"),
        ("M04 chân không làm tròn lô", B,
         "                q = round_lot(q)   #", "                q = q   #"),
        ("M05 bỏ đi-ngay sau chân khớp đủ", E,
         "if since < interval and ps[\"children\"] and not self._split_leg_completed(ps):",
         "if since < interval and ps[\"children\"]:"),
        ("M06 đi-ngay không cần khớp đủ", E,
         "return c.get(\"sell_lp\") is not None and c.get(\"filled\", 0) >= c[\"qty\"]",
         "return c.get(\"sell_lp\") is not None"),
        ("M07 'có gói đủ' dùng > thay >=", B,
         "any(v[\"sellable\"] >= need for v in by_pkg.values())",
         "any(v[\"sellable\"] > need for v in by_pkg.values())"),
        ("M08 positions lỗi không log", B,
         "\"rule\": \"TÁCH: LỖI-đọc-positions → không tách (hành vi cũ)\",",
         "\"rule\": None,"),
        ("M09 ATC không tách", E,
         "            leg = self._sell_split_leg(o, remaining)\n",
         "            leg = None\n"),
        ("M10 ATC skip journal mỗi vòng (bỏ cờ noted)", E,
         "        if ps.get(\"atc_split_skip_noted\"):\n            return\n",
         ""),
        ("M11 tách cả lệnh đòn bẩy", E,
         "if o.side != \"sell\" or getattr(o, \"loan_package_id\", None) is not None:\n"
         "            return None\n        fn = getattr(self.broker, \"plan_sell_leg\"",
         "if o.side != \"sell\":\n"
         "            return None\n        fn = getattr(self.broker, \"plan_sell_leg\""),
        ("M12 bỏ kiểm kiểu kết quả", E,
         "if not (isinstance(leg, tuple) and len(leg) == 2 and isinstance(leg[0], int)\n"
         "                and leg[1] is not None):",
         "if not leg:"),
        ("M13 child không ghi sell_lp", E,
         "                child[\"sell_lp\"] = sell_lp     #",
         "                pass     #"),
        ("M14 tick-retry rơi mất gói", E,
         "                                          **(place_kw or {}))", "                                          )"),
        ("M15 bỏ chặn sell_loan_package_id sai ngữ cảnh", B,
         "if sell_loan_package_id is not None and (side != \"sell\" or loan_package_id is not None):",
         "if False:"),
        ("M16 executor bỏ kiểm lô chân", E,
         "if not (0 < lq < qty) or (lq >= LOT and lq % LOT):", "if not (0 < lq):"),
        ("M17 chân chọn gói NHỎ nhất", B,
         "v = max(cands, key=lambda x: (x[1], str(x[0])))",
         "v = min(cands, key=lambda x: (x[1], str(x[0])))"),
        ("M18 log place_order luôn có khoá mới", B,
         "        if sell_loan_package_id is not None:   # khoá chỉ có ở chân tách",
         "        if True:   # khoá chỉ có ở chân tách"),
        ("M19 child luôn mang sell_lp", E,
         "            if sell_lp is not None:\n                child[\"sell_lp\"] = sell_lp",
         "            if True:\n                child[\"sell_lp\"] = sell_lp"),
        ("M20 log tách thiếu kế hoạch", B,
         "\"split_plan\": [[i, n] for i, n in legs],", "\"split_plan\": None,"),
        ("M21 place thành công không reset streak", E,
         "            ps[\"place_fail_streak\"] = 0\n            ps[\"place_fail_note\"] = \"\"\n"
         "            self.shared[o.ticker]",
         "            self.shared[o.ticker]"),
        ("M22 ATC quyết sau khi huỷ LO (bỏ kiểm trước huỷ)", E,
         "            if c and o.side == \"sell\":\n                # Quyết định TRƯỚC",
         "            if False:\n                # Quyết định TRƯỚC"),
        ("M23 plan_sell_leg lỗi không journal", E,
         "            self._journal(\"SPLIT_LEG_ERROR\", o, qty=qty, note=(",
         "            (lambda *a, **k: None)(qty, note=("),
        ("M24 ATC skip lại đặt cờ vĩnh viễn", E,
         "        ps[\"atc_split_skip_noted\"] = True\n",
         "        ps[\"atc_split_skip_noted\"] = True\n        ps[\"atc_unsupported\"] = True\n"),
    ]
    killed, survived = [], []
    for name, f, old, new in muts:
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(os.path.join(WC_ROOT, "trading_bot"), os.path.join(tmp, "trading_bot"),
                            ignore=shutil.ignore_patterns("__pycache__"))
            path = os.path.join(tmp, "trading_bot", f)
            src = open(path, encoding="utf-8").read()
            n = src.count(old)
            if n != 1:
                print(f" FAIL mutation {name}: pattern xuất hiện {n} lần (phải đúng 1)")
                survived.append(name + " [pattern]")
                continue
            open(path, "w", encoding="utf-8").write(src.replace(old, new))
            env = dict(os.environ, SELLSPLIT_CODE_ROOT=tmp)
            r = subprocess.run([sys.executable, os.path.abspath(__file__)], capture_output=True,
                               text=True, env=env, timeout=600)
            # Chết phải vì một check FAIL cụ thể, không phải vì crash/import lỗi — mutant làm
            # vỡ cú pháp sẽ "giết" mọi test mà không chứng minh test nào đo đúng điều gì.
            fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith(" FAIL ")]
            ok_kill = r.returncode == 1 and bool(fails)
            (killed if ok_kill else survived).append(name)
            print(f"  {'KILLED ' if ok_kill else 'SURVIVE'} {name}"
                  + (f"  ← {fails[0][:110]}" if fails else f"  (rc={r.returncode}, không có FAIL)"))
    print(f"mutation: {len(killed)}/{len(muts)} bị giết; sống sót: {survived}")
    return not survived


if "--mutations" in sys.argv:
    sys.exit(0 if mutations() else 1)

# ═════════════════════════════════ A. ca BID THẬT ═════════════════════════════════
print("=== A. BID ZaloPay 10-06: 1258:20 · 1826:7, bán 27 ===")
new = all_traces()
t = new["INCIDENT"]
got = [(c["qty"], c["loan_package_id"]) for c in t["calls"]]
check(got == [(20, 1258), (7, 1826)], f"2 lệnh con 20@1258 + 7@1826 (thực tế {got})")
check(not any(r[0].startswith("PLACE_FAIL") for r in t["journal"]),
      "không PLACE_FAIL / PLACE_FAIL_STOPPED")
check(any(r[0] == "DONE" for r in t["journal"]), "parent DONE sau 2 chân khớp")
places = [r for r in t["journal"] if r[0] == "PLACE"]
# Chân 2: sau khi chân 1 khớp, gói 1826 (7) ĐỦ cho phần còn lại 7 ⇒ KHÔNG còn là ca tách ⇒ đi
# ĐƯỜNG CŨ (_resolve_sell_loan_package_id ⇒ 1826). Chỉ chân 1 mang dấu tách.
check(len(places) == 2 and "tách gói vay 1258" in places[0][-1] and "tách" not in places[1][-1],
      f"journal PLACE: chân 1 ghi 'tách gói vay 1258', chân 2 đường thường ({[r[-1] for r in places]})")
check([c.get("sell_lp") for c in t["children"]] == [1258, None],
      f"state: chân 1 mang sell_lp=1258, chân 2 không ({[c.get('sell_lp') for c in t['children']]})")
pl = t["place_log"]
check(len(pl) == 2 and pl[0].get("sell_split_leg") is True and pl[0]["loan_package_id_sent"] == 1258
      and "sell_split_leg" not in pl[1] and pl[1]["loan_package_id_sent"] == 1826,
      "log place_order: chân 1 sell_split_leg=True @1258; chân 2 không khoá mới @1826")
check(len(t["resolve_log"]) == 2 and t["resolve_log"][1].get("rule") == "sellable-lớn-nhất"
      and t["resolve_log"][1].get("any_pkg_covers_qty") is True,
      f"chân 2 qua resolve cũ, có gói đủ ({t['resolve_log'][1:]})")
r0 = t["resolve_log"][0] if t["resolve_log"] else {}
check(r0.get("split_plan") == [[1258, 20], [1826, 7]] and r0.get("leg_now") == [1258, 20]
      and r0.get("split_uncovered") == 0 and r0.get("rule", "").startswith("TÁCH"),
      f"log sell_loan_package_resolve ghi KẾ HOẠCH TÁCH đầy đủ ({r0})")
ts = [r for r in t["journal"] if r[0] == "PLACE"]
check(len(ts) == 2, "chân 2 đi NGAY chu kỳ 20s sau khi chân 1 khớp đủ (không chờ 8')")

# Counter-proof: cùng fixture trên CODE CŨ ⇒ đúng sự cố (27@1258 bị từ chối)
base = base_traces()
bt = base["INCIDENT"]
bgot = [(c["qty"], c["loan_package_id"]) for c in bt["calls"]]
check(bgot and all(x == (27, 1258) for x in bgot)
      and any("Trade quantity not enough" in r[-1] for r in bt["journal"]),
      f"counter-proof BASE_REV {BASE_REV}: 27@1258 ⇒ 'Trade quantity not enough' ({bgot[:2]}…)")

# Chân 1 CHƯA khớp ⇒ không đặt chân 2 (1 lệnh mở / parent)
with tempfile.TemporaryDirectory() as tmp:
    cl = FakeClient([_row("BID", 1258, 20), _row("BID", 1826, 7)], 1258)
    b = make_broker(cl, 1258)
    ex = make_exec(tmp, [SO(27)], b)
    cycle(ex, NOW)
    cycle(ex, NOW + dt.timedelta(seconds=20))
    check(sells(cl) == [(20, 1258)], f"chân 1 còn mở ⇒ KHÔNG đặt chân 2 ({sells(cl)})")
    # khớp 1 phần rồi bị huỷ ⇒ KHÔNG đi-ngay (giữ nhịp 8' như cũ — chặn bão đặt lại)
    oid = list(cl.book)[0]
    cl.fill(oid, 10)
    cl.kill(oid)
    cycle(ex, NOW + dt.timedelta(seconds=40))
    check(sells(cl) == [(20, 1258)], f"chân khớp THIẾU rồi chết ⇒ chờ slice_interval ({sells(cl)})")
    cycle(ex, NOW + dt.timedelta(minutes=9))
    check(sells(cl) == [(20, 1258), (10, 1258)],
          f"hết interval ⇒ chân kế = 10@1258 (17 còn: 1258:10 lớn nhất) ({sells(cl)})")

# ═══════════════════════════ B. BYTE-IDENTICAL khi có gói đủ ═══════════════════════════
print(f"=== B. ca CÓ gói đủ: y hệt code BASE_REV {BASE_REV} ===")
for k in UNCHANGED:
    same = new[k] == base[k]
    diff = "" if same else {f: (new[k][f], base[k][f]) for f in new[k] if new[k][f] != base[k][f]}
    check(same and new[k]["calls"], f"{k}: calls+log+journal+state giống hệt ({diff})")
for k in UNCHANGED_EXCEPT_LOG:
    same = all(new[k][f] == base[k][f] for f in ("calls", "place_log", "journal", "children"))
    check(same and new[k]["calls"], f"{k}: lệnh đi ra/journal/state giống hệt (log resolve thêm 1)")

# ═══════════════════════════ C. lô chẵn+lẻ trải gói ═══════════════════════════
print("=== C. lô: 1258:150 · 1826:30, bán 180 ===")
with tempfile.TemporaryDirectory() as tmp:
    cl = FakeClient([_row("BID", 1258, 150), _row("BID", 1826, 30)], 1258)
    b = make_broker(cl, 1258)
    ex = make_exec(tmp, [SO(180)], b)
    t0 = NOW
    for i in range(6):
        cycle(ex, t0)
        if cl.book and cl.book[list(cl.book)[-1]]["status"] == "New":
            cl.fill(list(cl.book)[-1])
        t0 += dt.timedelta(minutes=9)
    s = sells(cl)
    check(s == [(100, 1258), (50, 1258), (30, 1826)], f"100@1258 → 50@1258 → 30@1826 ({s})")
    check(all(q % 100 == 0 or q < 100 for q, _ in s), "mọi lệnh hợp lệ lô (bội 100 hoặc lẻ <100)")
    check(sum(q for q, _ in s) == 180 and ex.state["parents"]["SELL-BID"]["done"],
          "đủ 180, parent DONE, không lệnh vượt")

with tempfile.TemporaryDirectory() as tmp:
    # 1258(default):120 · 1826:150, bán 200 ⇒ chân 1 = 100@1826 (gói LỚN nhất, KHÔNG phải
    # gói default dù default cũng đủ 100 — chân mang đúng gói kế hoạch đã chọn)
    cl = FakeClient([_row("BID", 1258, 120), _row("BID", 1826, 150)], 1258)
    b = make_broker(cl, 1258)
    ex = make_exec(tmp, [SO(200)], b)
    cycle(ex, NOW)
    _fill_last(ex, cl)
    cycle(ex, NOW + dt.timedelta(seconds=20))
    check(sells(cl) == [(100, 1826), (100, 1258)],
          f"200 chẵn trải 120/150 ⇒ 100@1826 (tách) rồi 100@1258 (gói đủ, đường cũ) ({sells(cl)})")

B_ = DNSEBroker._sell_split_legs
check(B_([(1258, 60), (1826, 50)], 100) == [(1258, 60), (1826, 40)], "100 trên 60/50 ⇒ 60 + 40 lẻ")
check(B_([(1258, 150), (1826, 120)], 200) == [(1258, 100), (1826, 100)],
      "200 trên 150/120 ⇒ 100 + 100 (KHÔNG 150+50 trộn lô)")
rng = random.Random(20261006)
bad = []
for _ in range(5000):
    pk = [(1000 + i, rng.choice([rng.randint(1, 99), rng.randint(1, 30) * 100,
                                 rng.randint(100, 2000)])) for i in range(rng.randint(1, 4))]
    need = rng.choice([rng.randint(1, 99), rng.randint(1, 30) * 100])
    legs = B_(pk, need)
    used = {}
    for i, q in legs:
        used[i] = used.get(i, 0) + q
    ok = (all(q > 0 and (q % 100 == 0 or q < 100) for _, q in legs)
          and all(used[i] <= dict(pk)[i] for i in used)
          and sum(q for _, q in legs) == min(need, sum(s for _, s in pk)))
    if not ok:
        bad.append((pk, need, legs))
check(not bad, f"property 5.000 ca: lô hợp lệ, ≤ sellable từng gói, tổng = min(cần, có) ({bad[:2]})")

# ═══════════════════════════ D. kill giữa 2 chân ═══════════════════════════
print("=== D. kill giữa 2 chân — chạy lại KHÔNG bán trùng ===")


def resume(tmp, b):
    ex = make_exec(tmp, [SO(27)], b)
    ex.state = ex._load_state()
    return ex


with tempfile.TemporaryDirectory() as tmp:
    cl = FakeClient([_row("BID", 1258, 20), _row("BID", 1826, 7)], 1258)
    b = make_broker(cl, 1258)
    cycle(make_exec(tmp, [SO(27)], b), NOW)           # chân 1 đặt + state ghi ⇒ KILL
    _fill_last(None, cl)                              # chân 1 khớp trong lúc bot chết
    ex2 = resume(tmp, b)
    check(len(ex2.state["parents"]["SELL-BID"]["children"]) == 1, "D1 resume thấy chân 1 trong state")
    cycle(ex2, NOW + dt.timedelta(seconds=20))
    cycle(ex2, NOW + dt.timedelta(seconds=40))
    check(sells(cl) == [(20, 1258), (7, 1826)], f"D1 restart: chỉ đặt chân 2 = 7@1826 ({sells(cl)})")
    _fill_last(None, cl)
    ex3 = resume(tmp, b)                              # kill lần 2 sau khi chân 2 khớp
    for i in range(3):
        cycle(ex3, NOW + dt.timedelta(minutes=10 + 9 * i))
    check(sum(q for q, _ in sells(cl)) == 27 and ex3.state["parents"]["SELL-BID"]["done"],
          f"D2 tổng bán đúng 27, DONE, không lệnh thêm ({sells(cl)})")

for label, fill in (("chân 1 còn mở", False), ("chân 1 đã khớp", True)):
    with tempfile.TemporaryDirectory() as tmp:
        cl = FakeClient([_row("BID", 1258, 20), _row("BID", 1826, 7)], 1258)
        b = make_broker(cl, 1258)
        ex = make_exec(tmp, [SO(27)], b)
        with mock.patch.object(Executor, "_save_state", lambda self: None):
            ex._place_slices(NOW, "MORNING", set(), b.get_positions())   # KILL trước khi ghi
        if fill:
            _fill_last(None, cl)
        ex2 = resume(tmp, b)
        cycle(ex2, NOW + dt.timedelta(seconds=20))
        cycle(ex2, NOW + dt.timedelta(minutes=9))
        check(sells(cl) == [(20, 1258)] and not ex2.state["parents"]["SELL-BID"]["children"],
              f"D3 kill sau place TRƯỚC save ({label}) ⇒ ghost-guard chặn, không lệnh mới ({sells(cl)})")

with tempfile.TemporaryDirectory() as tmp:
    cl = FakeClient([_row("BID", 1258, 20), _row("BID", 1826, 7)], 1258)
    b = make_broker(cl, 1258)
    ex = make_exec(tmp, [SO(27)], b)
    cycle(ex, NOW)
    _fill_last(None, cl)
    ex._sync_fills(b.poll_orders())
    ex._save_state()
    with mock.patch.object(Executor, "_save_state", lambda self: None):
        ex._place_slices(NOW + dt.timedelta(seconds=20), "MORNING", set(), b.get_positions())
    ex2 = resume(tmp, b)                              # chân 2 đã ở DNSE, state không biết
    cycle(ex2, NOW + dt.timedelta(minutes=9))
    check(sells(cl) == [(20, 1258), (7, 1826)],
          f"D4 kill sau chân 2 place TRƯỚC save ⇒ ghost-guard chặn, không đặt lại ({sells(cl)})")

# ═══════════════════════════ E. positions lỗi ═══════════════════════════
print("=== E. positions lỗi ⇒ không tách, hành vi cũ ===")
e = new["E1_positions_error"]
check([(c["qty"], c["loan_package_id"]) for c in e["calls"]] == [(27, 1258)],
      f"lệnh đi ra = gói default như cũ ({e['calls']})")
rules = [r.get("rule") or "" for r in e["resolve_log"]]
check(any(r.startswith("TÁCH: LỖI-đọc-positions") for r in rules)
      and any("simulated positions timeout" in (r.get("error") or "") for r in e["resolve_log"]),
      f"log resolve có bản ghi TÁCH-lỗi kèm lỗi thật ({rules})")

# ═══════════════════════════ F. ATC ═══════════════════════════
print("=== F. ATC ===")
with tempfile.TemporaryDirectory() as tmp:
    cl = FakeClient([_row("BID", 1258, 120), _row("BID", 1826, 120)], 1258)
    b = make_broker(cl, 1258)
    ex = make_exec(tmp, [SO(240)], b)
    cycle(ex, NOW, atc=True)
    s = [(c["qty"], c["loan_package_id"], c["order_type"]) for c in cl.calls]
    check(s == [(100, 1826, "ATC")], f"ATC 200 trên 120/120 ⇒ 1 chân 100@1826 ATC ({s})")
    check(ex.state["parents"]["SELL-BID"]["children"][0].get("sell_lp") == 1826,
          "ATC child mang sell_lp")
with tempfile.TemporaryDirectory() as tmp:
    cl = FakeClient([_row("BID", 1258, 60), _row("BID", 1826, 50)], 1258)
    b = make_broker(cl, 1258)
    ex = make_exec(tmp, [SO(110)], b)
    for i in range(3):
        cycle(ex, NOW, atc=True)
    ev = [r[0] for r in journal(ex)]
    check(cl.calls == [] and ev.count("ATC_SPLIT_SKIP") == 1,
          f"không gói nào ≥1 lô ⇒ KHÔNG đặt ATC, journal ATC_SPLIT_SKIP đúng 1 lần ({ev})")

# ═══════════════════════════ G. ranh giới ═══════════════════════════
print("=== G. ranh giới ===")
u6 = new["U6_lever_insufficient"]["calls"]
check(len(u6) == 1 and u6[0]["qty"] == 27, f"đòn bẩy CAPIT: không tách ({u6})")

with tempfile.TemporaryDirectory() as tmp:
    mb = mock.MagicMock()
    mb.get_quote.side_effect = lambda s, *a, **k: make_quote(s)
    mb.get_cash.return_value = 10 ** 12
    mb.place_order.return_value = "OID-1"
    ex = make_exec(tmp, [SO(27)], mb)
    try:
        ex._place_slices(NOW, "MORNING", set(), {"BID": {"total": 27, "sellable": 27}})
        kw = mb.place_order.call_args
    except Exception as e:                   # Mock lọt qua kiểm kiểu ⇒ executor ném ⇒ FAIL rõ
        print(f"    executor NÉM {type(e).__name__}: {e}")
        kw = None
    check(kw is not None and kw[0][1] == 27 and "sell_loan_package_id" not in kw[1],
          f"MagicMock broker (plan_sell_leg = Mock) ⇒ không tách ({kw})")


class _NoSplit:
    def plan_sell_leg(self, s, q):
        return (20, 1258)


with tempfile.TemporaryDirectory() as tmp:
    ex = make_exec(tmp, [SO(27)], _NoSplit())
    check(ex._sell_split_leg(SO(27), 27) == (20, 1258), "_sell_split_leg nhận tuple hợp lệ")
    ex.broker.plan_sell_leg = lambda s, q: (120, 1258)
    check(ex._sell_split_leg(SO(200), 200) is None, "chân trộn lô (120) bị executor từ chối")
    ex.broker.plan_sell_leg = lambda s, q: (27, 1258)
    check(ex._sell_split_leg(SO(27), 27) is None, "chân = cả lệnh ⇒ không phải tách ⇒ None")

cl = FakeClient([_row("BID", 1258, 20)], 1258)
b = make_broker(cl, 1258)
for kw, label in (({"side": "buy"}, "lệnh MUA"), ({"side": "sell", "loan_package_id": 1840},
                                                   "kèm đòn bẩy")):
    try:
        b.place_order("BID", 20, price=34550, sell_loan_package_id=1258, **kw)
        check(False, f"sell_loan_package_id + {label} phải ValueError")
    except ValueError:
        check(cl.calls == [], f"sell_loan_package_id + {label} ⇒ ValueError, không gọi DNSE")
check(b.plan_sell_leg("BID", 20) is None, "plan_sell_leg: gói đủ ĐÚNG BẰNG qty ⇒ None (đường cũ)")

with tempfile.TemporaryDirectory() as tmp:
    # 1258(default):120 · 1826:150, bán 200 ⇒ chân 100@1826. Nếu retry rơi mất gói, resolve cũ
    # sẽ chọn 1258 (default đủ 100) ⇒ phân biệt được.
    cl = FakeClient([_row("BID", 1258, 120), _row("BID", 1826, 150)], 1258, tick_fail_once=True)
    b = make_broker(cl, 1258)
    b.get_quote = lambda s, *a, **k: make_quote(s, 34600)   # bid 34550: lệch bước giá HNX ⇒ retry
    ex = make_exec(tmp, [SO(200)], b)
    cycle(ex, NOW)
    s = sells(cl)
    pl = [p for k, p in b.raw_log if k == "place_order"]
    check(s == [(100, 1826), (100, 1826)] and any(r[0] == "TICK_RETRY_OK" for r in journal(ex))
          and pl and pl[-1].get("sell_split_leg") is True
          and ex.state["parents"]["SELL-BID"]["children"][0].get("sell_lp") == 1826,
          f"tick-retry giữ đúng chân + gói ({s})")

# ═══════════════════════════ H. vòng 2 (arch-review NB-1/3/4/5) ═══════════════════════════
print("=== H. vòng 2 ===")
# NB-3: đặt lệnh thành công reset chuỗi lỗi cấu trúc của parent
with tempfile.TemporaryDirectory() as tmp:
    cl = FakeClient([_row("BID", 1258, 20), _row("BID", 1826, 7)], 1258)
    b = make_broker(cl, 1258)
    ex = make_exec(tmp, [SO(27)], b)
    ps = ex.state["parents"]["SELL-BID"]
    ps["place_fail_streak"], ps["place_fail_note"] = 4, "HTTP 400: Trade quantity not enough"
    cycle(ex, NOW)
    check(sells(cl) == [(20, 1258)] and ps["place_fail_streak"] == 0 and ps["place_fail_note"] == ""
          and not ps.get("place_blocked"),
          f"NB-3 place thành công ⇒ streak reset ({ps.get('place_fail_streak')}, {sells(cl)})")

# NB-4: ATC không đặt được ⇒ KHÔNG huỷ LO, KHÔNG cờ vĩnh viễn, journal 1 lần, thử lại sau
with tempfile.TemporaryDirectory() as tmp:
    cl = FakeClient([_row("BID", 1258, 60), _row("BID", 1826, 50)], 1258)
    b = make_broker(cl, 1258)
    ex = make_exec(tmp, [SO(110)], b)
    cycle(ex, NOW)                                    # LO chân 60@1258 đang mở
    lo = next(iter(cl.book))
    for _ in range(3):
        cycle(ex, NOW, atc=True)
    ps = ex.state["parents"]["SELL-BID"]
    ev = [r[0] for r in journal(ex)]
    check(cl.book[lo]["status"] == "New" and cl.accepted == [("BID", 60, 1258, "LO", "sell")]
          and ev.count("ATC_SPLIT_SKIP") == 1 and not ps.get("atc_unsupported")
          and not ps["atc_sent"],
          f"NB-4 ATC bỏ ⇒ LO còn nguyên, không cờ vĩnh viễn, journal 1 lần ({ev}, {cl.accepted})")
    with tempfile.TemporaryDirectory() as tmp2:   # _atc_sweep TRẦN (không save ké của cycle())
        cl2 = FakeClient([_row("BID", 1258, 60), _row("BID", 1826, 50)], 1258)
        b2 = make_broker(cl2, 1258)
        ex2 = make_exec(tmp2, [SO(110)], b2)
        ex2._atc_sweep(set(), b2.get_positions())
        try:
            with open(ex2.state_file, encoding="utf-8") as fh:
                on_disk = json.load(fh)["parents"]["SELL-BID"]
        except FileNotFoundError:                 # không save ⇒ không có file ⇒ FAIL rõ
            on_disk = {}
        check(on_disk.get("atc_split_skip_noted") is True and not on_disk.get("atc_unsupported"),
              "NB-4 cờ noted ghi xuống state.json ngay trong _atc_sweep, không cờ vĩnh viễn")
    for r in cl.rows:                                  # sau đó gói 1258 đủ lô chẵn ⇒ ATC đi được
        if r["loanPackageId"] == 1258:
            r["tradeQuantity"] = r["openQuantity"] = 300
    cycle(ex, NOW, atc=True)
    check(("BID", 100, 1258, "ATC", "sell") in cl.accepted and cl.book[lo]["status"] == "Canceled",
          f"NB-4 vòng sau positions đổi ⇒ thử lại: huỷ LO + đặt ATC ({cl.accepted})")

# NB-5: plan_sell_leg ném ⇒ rơi về hành vi cũ NHƯNG có journal lý do
class _Boom:
    def plan_sell_leg(self, s, q):
        raise RuntimeError("positions boom")


with tempfile.TemporaryDirectory() as tmp:
    ex = make_exec(tmp, [SO(27)], _Boom())
    try:
        r = ex._sell_split_leg(SO(27), 27)
    except Exception as e:                   # ném ra ngoài ⇒ FAIL rõ, không phải crash
        r = f"NÉM {type(e).__name__}"
    j = [x for x in journal(ex) if x[0] == "SPLIT_LEG_ERROR"]
    check(r is None and len(j) == 1 and "positions boom" in j[0][-1],
          f"NB-5 plan_sell_leg ném ⇒ None + journal SPLIT_LEG_ERROR kèm lý do ({r}, {j})")

# NB-1: fill đã thấy ở poll lệnh nhưng positions CHƯA cập nhật ⇒ chỉ 400 + retry, không bán vượt
with tempfile.TemporaryDirectory() as tmp:
    cl = FakeClient([_row("BID", 1258, 20), _row("BID", 1826, 7)], 1258, stale_positions=True)
    b = make_broker(cl, 1258)
    ex = make_exec(tmp, [SO(27)], b)
    cycle(ex, NOW)
    _fill_last(None, cl)                              # chân 1 khớp; positions vẫn ảnh cũ (20/7)
    cycle(ex, NOW + dt.timedelta(seconds=20))         # ảnh cũ ⇒ chọn 1258 cho 7cp ⇒ DNSE 400
    ev = [r[0] for r in journal(ex)]
    check(cl.accepted == [("BID", 20, 1258, "LO", "sell")] and "PLACE_FAIL" in ev,
          f"NB-1 positions cũ ⇒ lệnh bị 400 (không khớp thêm), không bán vượt ({cl.accepted})")
    cl.refresh()
    cycle(ex, NOW + dt.timedelta(seconds=40))
    tot = sum(a[1] for a in cl.accepted)
    check([(a[1], a[2]) for a in cl.accepted] == [(20, 1258), (7, 1826)] and tot == 27,
          f"NB-1 positions mới ⇒ retry đúng chân 7@1826, tổng đặt 27 ({cl.accepted})")

print()
if FAILS:
    print(f"FAIL {len(FAILS)}:")
    for m in FAILS:
        print("  - " + m)
    sys.exit(1)
print("ALL OK")
