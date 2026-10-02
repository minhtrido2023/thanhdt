#!/usr/bin/env python3
"""Self-check: BÁN TRỌN LÔ LẺ khi THOÁT HẾT (user duyệt 2026-10-02 15:24 ICT, job Taylor_20261002_082525).

Ca gốc: SpaceX VIX 220cp, park target 0% ⇒ plan chỉ bán 200 (PARKMERGE-SELL-VIX), 20cp lẻ kẹt vì
`compute_park_trim` round_lot() + `merge_park_orders` ép bội 100. Quy tắc mới (`full_exit_qty`):
lệnh BÁN mà phần còn lại của book sau lệnh là 0 < còn lại < 1 lô và toàn bộ book bán được ngay
(≤ sellable) ⇒ bán TOÀN BỘ (1 order qty=220; executor tự tách 200 + 20).

Phủ: L1 compute_park_trim · L2 compute_jit_unpark · merge_park_orders (+ bất biến I4).

Chạy:
    python3 mike/bin/oddlot_full_exit_selfcheck.py             # các ca
    python3 mike/bin/oddlot_full_exit_selfcheck.py --mutations # + mutation test (mọi mutant phải chết)
    python3 mike/bin/oddlot_full_exit_selfcheck.py --all-tz    # + ma trận TZ (env -u TZ, ICT, UTC, NY, Tokyo)
Không mạng, không BQ, không DNSE: mọi nguồn (adv/giá/rổ/state/ex_map) bơm tay.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

_MUT = os.environ.get("ODDLOT_MUT_DIR")          # chỉ runner --mutations đặt biến này
BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)
import wc_paths  # noqa: E402
WC = wc_paths.find_wc_root(__file__)
sys.path.insert(0, WC)
if _MUT:
    # Nạp bản mutant TRƯỚC vào sys.modules: chèn sys.path không đủ vì mỗi module tự
    # `sys.path.insert(0, bin/)` lúc import ⇒ bản thật sẽ che lại bản mutant.
    import importlib.util
    for _fn in os.listdir(_MUT):
        _spec = importlib.util.spec_from_file_location(_fn[:-3], os.path.join(_MUT, _fn))
        _mod = importlib.util.module_from_spec(_spec)
        sys.modules[_fn[:-3]] = _mod
        _spec.loader.exec_module(_mod)

import compute_park_trim as cpt                 # noqa: E402
import compute_jit_unpark as cju                # noqa: E402
import merge_park_orders as mpo                 # noqa: E402
from trading_bot.plan import LAG_ADV_PCT        # noqa: E402
from trading_bot.vn_market import LOT           # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


ASOF = "2026-10-02"
PX = {"VIX": 20_000, "AAA": 10_000, "BBB": 50_000, "VPB": 20_000}
DEBT = 50e6


# ═════════════════════════════════════════════════════════ L1 fixtures
def l1_holdings(qtys, sellable=None, broker=None):
    lots = [{"ticker": t, "qty": q, "market_price": PX[t], "mv_vnd": q * PX[t], "price": PX[t],
             "entry_date": "2026-09-01", "source": "j1", "book": "PARK"} for t, q in qtys.items()]
    bpos = {t: {"qty": (broker or {}).get(t, q), "market_price": PX[t],
                "sellable": (sellable or {}).get(t, (broker or {}).get(t, q))}
            for t, q in qtys.items()}
    return {"account_label": "TEST", "asof": ASOF, "park_lots": lots, "broker_positions": bpos,
            "park_mv_vnd": sum(l["mv_vnd"] for l in lots), "cash_available_vnd": 0.0,
            "cash_total_vnd": DEBT, "cash_debt_vnd": DEBT, "cash_dividend_receiving_vnd": 0.0,
            "egg_assets_vnd": 0.0, "cash_basis": "total_cash",
            "reconcile": {"ok": True, "mismatches": []},
            "unverified_tickers": [], "excluded_tickers": []}


def adv_for_cap_shares(tk_shares):
    """adv_fn sao cho trần per-name = đúng N cổ phiếu (share=1)."""
    def _f(tk, asof):
        n = tk_shares.get(tk)
        return ((1e15 if n is None else n * PX[tk] / LAG_ADV_PCT), asof, None)
    return _f


def run_l1(qtys, target=0.0, basket=None, sellable=None, adv_fn=None, broker=None):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"state": 3, "state_name": "NEUTRAL", "date": ASOF,
                   "etf_park_frac": target}, f)
    old = cpt.STATE_FILE
    cpt.STATE_FILE = path
    try:
        return cpt.compute_trim(
            "TEST", ASOF, target, holdings=l1_holdings(qtys, sellable, broker),
            share_override=1.0, adv_fn=adv_fn or adv_for_cap_shares({}),
            day_cap_override=1e15, basket_override=basket or {"AAA": 1.0},
            price_fn=lambda tk: (PX.get(tk), None), excluded_dividend_config_override=[])
    finally:
        cpt.STATE_FILE = old
        os.unlink(path)


def order(r, tk):
    return next((o for o in r.get("orders", []) if o["ticker"] == tk), None)


def qty_of(r, tk):
    o = order(r, tk)
    return None if o is None else o["qty"]


print("=== oddlot full-exit selfcheck ===")
print("-- L1 compute_park_trim --")
r = run_l1({"VIX": 220})
check("L1-1 VIX 220 target0 ⇒ 1 order qty=220", qty_of(r, "VIX") == 220
      and len([o for o in r["orders"] if o["ticker"] == "VIX"]) == 1, qty_of(r, "VIX"))
o = order(r, "VIX") or {}
check("L1-1b order mang full_exit + odd_lot_qty=20 + qty_lot_part=200",
      o.get("full_exit") is True and o.get("odd_lot_qty") == 20 and o.get("qty_lot_part") == 200, o)
check("L1-1c value_vnd/FIFO theo qty 220", o.get("value_vnd") == 220 * PX["VIX"]
      and sum(f["qty"] for f in o.get("fifo_lots", [])) == 220)

r = run_l1({"VIX": 200})
o = order(r, "VIX") or {}
check("L1-2 VIX 200 ⇒ 200, KHÔNG có khoá full_exit (shape cũ)",
      o.get("qty") == 200 and "full_exit" not in o and "odd_lot_qty" not in o, o.get("qty"))

r = run_l1({"VIX": 20})
check("L1-3 VIX 20 (chỉ lô lẻ, hết hẳn) ⇒ 20", qty_of(r, "VIX") == 20
      and (order(r, "VIX") or {}).get("full_exit") is True, (r["decision"], r.get("blocked")))

# trim một phần: AAA 1050 @10k, target 0,5 ⇒ tgt 525cp ⇒ want 525 ⇒ lô 500 ⇒ còn 550 ≥ 1 lô
r = run_l1({"AAA": 1050}, target=0.5, basket={"AAA": 1.0})
o = order(r, "AAA") or {}
check("L1-4 trim một phần (còn ≥1 lô) ⇒ 500, không bán lẻ",
      o.get("qty") == 500 and "full_exit" not in o, (r["decision"], o.get("qty")))

r = run_l1({"VIX": 220}, adv_fn=adv_for_cap_shares({"VIX": 150}))
o = order(r, "VIX") or {}
check("L1-5 ADV-cap binding (trần 150cp) ⇒ 100 lô chẵn, KHÔNG kèm lẻ",
      o.get("qty") == 100 and "full_exit" not in o, o.get("qty"))
r = run_l1({"VIX": 520}, adv_fn=adv_for_cap_shares({"VIX": 350}))
check("L1-5b ADV-cap binding (520cp, trần 350) ⇒ 300, không lẻ", qty_of(r, "VIX") == 300)
r = run_l1({"VIX": 220}, adv_fn=adv_for_cap_shares({"VIX": 205}))
check("L1-5c trần cho đủ MỌI lô chẵn (205cp) ⇒ 220 (lẻ đi kèm lệnh hoàn tất thoát hết)",
      qty_of(r, "VIX") == 220)

r = run_l1({"VIX": 220}, sellable={"VIX": 120})
o = order(r, "VIX") or {}
check("L1-6 sellable 120 < book 220 ⇒ 100, không lẻ (không vượt sellable)",
      o.get("qty") == 100 and "full_exit" not in o, o.get("qty"))
r = run_l1({"VIX": 220}, sellable={"VIX": 219})
check("L1-6b sellable 219 < book 220 ⇒ 200 (min sellable)", qty_of(r, "VIX") == 200)
r = run_l1({"VIX": 20}, sellable={"VIX": 0})
check("L1-6c sellable 0 ⇒ KHÔNG lệnh (book 20 chưa về)", qty_of(r, "VIX") is None)

# helper thuần — gọi qua _fe: mutant làm vỡ hàm (TypeError…) phải FAIL CÓ TÊN, không crash cả script
def _fe(*a):
    try:
        return cpt.full_exit_qty(*a)
    except Exception as e:
        return f"{type(e).__name__}: {e}"


check("H-1 full_exit_qty(200,220,220)=(220,True)", _fe(200, 220, 220) == (220, True))
check("H-2 full_exit_qty(200,200,200)=(200,False)", _fe(200, 200, 200) == (200, False))
check("H-3 full_exit_qty(100,220,220)=(100,False) — còn 120 ≥ 1 lô",
      _fe(100, 220, 220) == (100, False))
check("H-4 full_exit_qty(200,220,219)=(200,False) — book > sellable",
      _fe(200, 220, 219) == (200, False))
check("H-5 full_exit_qty(200,220,220,230)=(200,False) — broker 230 > sellable 220 (B1)",
      _fe(200, 220, 220, 230) == (200, False))
check("H-6 full_exit_qty(200,220,220,220)=(220,True) — broker<=sellable",
      _fe(200, 220, 220, 220) == (220, True))

# B3(i): book 300, trần ADV 250cp ⇒ 200 (rest=100 = 1 lô, KHÔNG < 1 lô) — giết `rest <= LOT`
r = run_l1({"VIX": 300}, adv_fn=adv_for_cap_shares({"VIX": 250}))
o = order(r, "VIX") or {}
check("B3-i book 300, trần ADV 250cp ⇒ 200, KHÔNG full_exit",
      o.get("qty") == 200 and "full_exit" not in o, o.get("qty"))
# B3(iv): VIX 220/220, broker = book = sellable ⇒ 220 thoát hết
r = run_l1({"VIX": 220}, broker={"VIX": 220}, sellable={"VIX": 220})
o = order(r, "VIX") or {}
check("B3-iv broker 220 <= sellable 220 ⇒ 220 có full_exit",
      o.get("qty") == 220 and o.get("full_exit") is True, o.get("qty"))
# B1: PARK 330 nhưng broker 930 > sellable 900 ⇒ KHÔNG kèm lẻ (suất sellable thuộc LAG 600)
r = run_l1({"VPB": 330}, broker={"VPB": 930}, sellable={"VPB": 900})
o = order(r, "VPB") or {}
check("B3-iii-a PARK 330 + broker 930 > sellable 900 ⇒ PARK 300, không lẻ",
      o.get("qty") == 300 and "full_exit" not in o, o.get("qty"))

# ═════════════════════════════════════════════════════════ L2 fixtures
print("-- L2 compute_jit_unpark --")


def l2_holdings(tk, qty, px, sellable=None, broker=None):
    q1 = (qty // 2 // LOT) * LOT
    lots = [{"ticker": tk, "book": "PARK", "play_type": "NEUTRAL_park", "entry_date": f"2026-0{6+i}-15",
             "qty": q, "price": px, "source": f"lot{i}", "market_price": px, "mv_vnd": q * px}
            for i, q in enumerate((q1, qty - q1)) if q > 0]
    return {"account_label": "SC", "asof": ASOF, "park_lots": lots, "lots": lots,
            "broker_positions": {tk: {"qty": qty if broker is None else broker, "market_price": px,
                                      "sellable": qty if sellable is None else sellable}},
            "park_mv_vnd": qty * px, "cash_available_vnd": 0.0, "egg_assets_vnd": 0.0,
            "excluded_tickers": [], "unverified_tickers": [],
            "reconcile": {"ok": True, "mismatches": []}}


BUY = {"id": "BUY-ZZZ", "ticker": "ZZZ", "side": "buy", "qty": 1200, "ref_price": 10_000,
       "book": "LAG", "play_type": "LAG_HI", "priority": 10}          # 12tr


def run_l2(qty, sellable=None):
    return cju.compute_jit_unpark(
        "SC", asof=ASOF, orders=[dict(BUY)], holdings=l2_holdings("BBB", qty, PX["BBB"], sellable),
        share_override=1.0, adv_fn=lambda tk, a: (1e15, a, None), day_cap_override=1e15)


r2 = run_l2(250)
o = order(r2, "BBB") or {}
check("L2-1 PARK 250 @50k, cần ~240cp ⇒ hết lô chẵn ⇒ bán 250 kèm lẻ 50",
      o.get("qty") == 250 and o.get("full_exit") is True and o.get("odd_lot_qty") == 50, o.get("qty"))
amd = (r2.get("buy_amendments") or [{}])[0]
check("L2-1b lệnh MUA không đổi cỡ (qty_final == qty_plan 1200)",
      amd.get("qty_final") == 1200, amd)
r2 = run_l2(1250)
o = order(r2, "BBB") or {}
check("L2-2 PARK 1250 ⇒ bội lô, không lẻ (còn ≥1 lô)",
      o.get("qty", 1) % LOT == 0 and "full_exit" not in o, o.get("qty"))
r2 = run_l2(250, sellable=220)
o = order(r2, "BBB") or {}
check("L2-3 sellable 220 < book 250 ⇒ 200, không lẻ", o.get("qty") == 200 and "full_exit" not in o,
      o.get("qty"))
def run_l2_l1used(qty, sellable, used, broker=None):
    return cju.compute_jit_unpark(
        "SC", asof=ASOF, orders=[dict(BUY)],
        holdings=l2_holdings("BBB", qty, PX["BBB"], sellable, broker),
        share_override=1.0, adv_fn=lambda tk, a: (1e15, a, None), day_cap_override=1e15,
        l1_result={"orders": [{"ticker": "BBB", "qty": used, "value_vnd": used * PX["BBB"]}]})


# B3(ii): book 320, L1 đã dùng 100 ⇒ book_left 220
o = order(run_l2_l1used(320, 320, 100), "BBB") or {}
check("B3-ii-a L2 book 320, L1 dùng 100, sellable 320 ⇒ 220 có full_exit",
      o.get("qty") == 220 and o.get("full_exit") is True, o.get("qty"))
o = order(run_l2_l1used(320, 300, 100), "BBB") or {}
check("B3-ii-b L2 book 320, L1 dùng 100, sellable 300 ⇒ 200 không lẻ",
      o.get("qty") == 200 and "full_exit" not in o, o.get("qty"))
o = order(run_l2_l1used(320, 320, 100, broker=420), "BBB") or {}
check("B3-ii-c L2 broker 420 > sellable 320 ⇒ 200 không lẻ (B1 ở L2)",
      o.get("qty") == 200 and "full_exit" not in o, o.get("qty"))

r2 = cju.compute_jit_unpark(
    "SC", asof=ASOF, orders=[dict(BUY)], holdings=l2_holdings("BBB", 250, PX["BBB"]),
    share_override=1.0, adv_fn=lambda tk, a: (1e15, a, None), day_cap_override=1e15,
    l1_result={"orders": [{"ticker": "BBB", "qty": 250, "value_vnd": 250 * PX["BBB"]}]})
check("L2-4 L1 đã giữ chỗ 250 (thoát hết) ⇒ L2 KHÔNG bán thêm BBB", order(r2, "BBB") is None)

# ═════════════════════════════════════════════════════════ merge
print("-- merge_park_orders --")


def l1_art(orders):
    return {"decision": "TRIM", "reconcile_ok": True, "orders": orders}


def l2_art(orders):
    return {"decision": "JIT", "reconcile_ok": True, "orders": orders, "buy_amendments": []}


def sell(tk, qty, sellable, full_exit=False, extra=None):
    o = {"ticker": tk, "side": "sell", "qty": qty, "ref_price": PX[tk], "sellable": sellable}
    if full_exit:
        o["full_exit"] = True
    o.update(extra or {})
    return o


BUY_ORDER = {"id": "BUY-AAA", "ticker": "AAA", "side": "buy", "qty": 500, "ref_price": 10_000,
             "book": "LAG", "play_type": "LAG_HI", "priority": 10}


def merge(l1=None, l2=None, extra_orders=()):
    plan = {"plan_date": ASOF, "orders": [dict(BUY_ORDER)] + [dict(x) for x in extra_orders]}
    return mpo.merge_park_orders(plan, l1, l2, ex_map={})


def gen(p, tk):
    return next((o for o in p["orders"] if o.get("merge_owner") == mpo.OWNER
                 and o["ticker"] == tk), None)


p, rep = merge(l1_art([sell("VIX", 220, 220, True)]))
g = gen(p, "VIX") or {}
check("M-1 L1 full_exit 220 ⇒ 1 lệnh PARKMERGE qty=220, full_exit, odd 20, status OK",
      rep["status"] == "OK" and g.get("qty") == 220 and g.get("full_exit") is True
      and g.get("odd_lot_qty") == 20, (rep["status"], g.get("qty"), rep["errors"]))
check("M-1b bất biến I4 PASS với lệnh full_exit lẻ",
      all(c["ok"] for c in rep["invariants"] if c["name"].startswith("I4")))
check("M-1c lệnh MUA byte-identical", next(o for o in p["orders"] if o["id"] == "BUY-AAA")
      == BUY_ORDER)

p, rep = merge(l1_art([sell("VIX", 200, 200)]))
g = gen(p, "VIX") or {}
check("M-2 L1 200 ⇒ 200, không khoá full_exit", g.get("qty") == 200 and "full_exit" not in g)

p, rep = merge(l1_art([sell("VIX", 220, 220, False)]))
check("M-3 qty lẻ KHÔNG khai full_exit ⇒ làm tròn xuống 200", (gen(p, "VIX") or {}).get("qty") == 200)

p, rep = merge(l1_art([sell("VIX", 220, None, True)]))
check("M-4 full_exit nhưng sellable KHÔNG biết ⇒ làm tròn xuống 200",
      (gen(p, "VIX") or {}).get("qty") == 200)

foreign = {"id": "SELL-VIX-AUTOEXIT-LAG", "ticker": "VIX", "side": "sell", "qty": 100,
           "ref_price": PX["VIX"], "book": "LAG", "play_type": "LAG_AUTO_EXIT", "priority": 1,
           "sellable": 220}
p, rep = merge(l1_art([sell("VIX", 220, 220, True)]), extra_orders=[foreign])
g = gen(p, "VIX") or {}
check("M-5 lệnh khác chiếm 100/220 ⇒ L1 bị CẮT ⇒ 100 (bội lô, không lẻ), Σ ≤ sellable",
      rep["status"] == "OK" and g.get("qty") == 100 and "full_exit" not in g,
      (rep["status"], g.get("qty")))

p, rep = merge(l1_art([sell("VIX", 100, 220)]), l2_art([sell("VIX", 120, 220, True)]))
g = gen(p, "VIX") or {}
check("M-6 L1 100 + L2 120 full_exit (sellable 220) ⇒ cộng dồn 220, giữ lẻ 20",
      g.get("qty") == 220 and g.get("full_exit") is True and g.get("odd_lot_qty") == 20,
      (rep["status"], g.get("qty")))
p, rep = merge(l1_art([sell("VIX", 220, 220, True)]), l2_art([sell("VIX", 100, 220)]))
g = gen(p, "VIX") or {}
check("M-7 L1 220 full_exit + L2 100 vượt sellable 220 ⇒ cắt, Σ ≤ 220, không lẻ",
      rep["status"] == "OK" and (g.get("qty") or 0) <= 220 and (g.get("qty") or 0) % LOT == 0,
      (rep["status"], g.get("qty")))

foreign2 = dict(foreign, sellable=320)
p, rep = merge(l1_art([sell("VIX", 200, 320)]), l2_art([sell("VIX", 120, 320, True)]),
               extra_orders=[foreign2])
g = gen(p, "VIX") or {}
check("M-8 L1 bị CẮT (lệnh khác chiếm 100/320) ⇒ book PARK không còn thoát hết ⇒ lẻ của L2 "
      "bị làm tròn: 100+100=200, không lẻ",
      rep["status"] == "OK" and g.get("qty") == 200 and "full_exit" not in g,
      (rep["status"], g.get("qty")))

inv = mpo._check_invariants(
    [{"id": "X", "ticker": "VIX", "side": "sell", "qty": 220, "merge_owner": mpo.OWNER,
      "sellable": 220}], {}, [])
check("I4-a lệnh merge lẻ KHÔNG có full_exit ⇒ I4 báo lỗi",
      not next(c for c in inv["checks"] if c["name"].startswith("I4"))["ok"])
inv = mpo._check_invariants(
    [{"id": "X", "ticker": "VIX", "side": "sell", "qty": 220, "merge_owner": mpo.OWNER,
      "sellable": 219, "full_exit": True}], {}, [])
check("I2-a full_exit 220 > sellable 219 ⇒ I2 FAIL (chặn)", any("I2" in f for f in inv["failed"]))

# B3(iii): ca VPB tích hợp — L1 → merge → auto_exit_inject._cap_sellable, đúng thứ tự cron
import auto_exit_inject as aei                  # noqa: E402
r1 = run_l1({"VPB": 330}, broker={"VPB": 930}, sellable={"VPB": 900})
p, rep_ = merge(r1)
g = gen(p, "VPB") or {}
used_q, warn = aei._cap_sellable(p, "VPB", 600, {"VPB": {"sellable": 900}}, "LAG")
check("B3-iii-b VPB: PARK 330 + LAG 600 + sellable 900 ⇒ merge 300, LAG giữ 600 không CAP",
      g.get("qty") == 300 and "full_exit" not in g and used_q == 600 and warn is None,
      (g.get("qty"), used_q, warn))

# ═════════════════════════════════════════ NON-BLOCKING vòng 2: 2 lệnh MUA rút cùng 1 mã PARK
print("-- L2: 2 lệnh MUA cùng rút 1 mã PARK (sold_qty) --")


def run_l2_two_buys(qty, sellable, broker):
    b1 = dict(BUY, id="BUY-Z1", qty=1000)            # 10tr ⇒ 200cp BBB @50k
    b2 = dict(BUY, id="BUY-Z2", ticker="ZZY", qty=500, priority=9)   # 5tr ⇒ 100cp
    return cju.compute_jit_unpark(
        "SC", asof=ASOF, orders=[b1, b2],
        holdings=l2_holdings("BBB", qty, PX["BBB"], sellable, broker),
        share_override=1.0, adv_fn=lambda tk, a: (1e15, a, None), day_cap_override=1e15)


r2 = run_l2_two_buys(350, 350, 350)
bq = [o["qty"] for o in r2.get("orders", []) if o["ticker"] == "BBB"]
fe = [o.get("full_exit") is True for o in r2.get("orders", []) if o["ticker"] == "BBB"]
check("SQ-1 book=sellable=broker 350, MUA1 rút 200 rồi MUA2 rút 100 ⇒ lệnh 2 thoát hết 150 "
      "(200 + 150 = 350)", bq == [200, 150] and fe == [False, True], (bq, fe))
r2 = run_l2_two_buys(350, 300, 350)
bq = [o["qty"] for o in r2.get("orders", []) if o["ticker"] == "BBB"]
check("SQ-2 sellable 300 < book 350: MUA2 chỉ còn 100 sellable ⇒ 100, KHÔNG kèm lẻ (Σ ≤ sellable)",
      bq == [200, 100] and sum(bq) <= 300, bq)

# X4: nhánh mặc định broker_left=None ⇒ = book_left (không được làm hỏng H-1)
_h7 = _fe(200, 220, 220, None)
check("H-7 full_exit_qty(200,220,220,None)=(220,True) — mặc định broker_left = book_left",
      _h7 == (220, True), _h7)

# ═════════════════════════════════ BLOCKING vòng 3: nguồn sellable LIVE == JSONL (bản ghi THẬT)
print("-- park_holdings: sellable live == jsonl trên bản ghi positions THẬT 2026-10-02 --")
import park_holdings as ph                      # noqa: E402
import trading_bot.brokers as tbb               # noqa: E402

FIX = json.load(open(os.path.join(BIN, "fixtures", "dnse_positions_eod_20261002.json"),
                     encoding="utf-8"))
ACCT_NO = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
REC = {r["account_no"]: r for r in FIX["records"]}


class _FakeDNSEClient:
    def __init__(self, payload):
        self._p = payload

    def positions(self, account_id):
        return json.loads(json.dumps(self._p))

    def balances(self, account_no):
        return {}


def snap_live(label, payload, module=ph):
    """Nhánh LIVE THẬT của read_broker_snapshot (DNSEBroker.get_positions thật) với client giả trả
    payload thô; KHÔNG ghi _log_raw, KHÔNG mạng (need_price=False)."""
    old_conn, old_today = tbb.DNSEBroker.connect, module.today_ict

    def _connect(self):
        self.client = _FakeDNSEClient(payload)
        self._raw_log = None
        return self
    tbb.DNSEBroker.connect = _connect
    module.today_ict = lambda: ASOF
    try:
        return module.read_broker_snapshot(label, ACCT_NO[label], ASOF, need_price=False)[0]
    finally:
        tbb.DNSEBroker.connect, module.today_ict = old_conn, old_today


def snap_jsonl(label, rec):
    d = tempfile.mkdtemp(prefix="oddlot_raw_")
    try:
        with open(os.path.join(d, f"dnse_raw_{ASOF}.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        old_today = ph.today_ict
        ph.today_ict = lambda: "2099-01-01"          # ép nhánh jsonl (asof quá khứ)
        try:
            return ph.read_broker_snapshot(label, ACCT_NO[label], ASOF, exec_dir=d,
                                           need_price=False)[0]
        finally:
            ph.today_ict = old_today
    finally:
        shutil.rmtree(d, ignore_errors=True)


LIVE, RAW = {}, {}
for label, acct_no in ACCT_NO.items():
    rec = REC[acct_no]
    try:
        LIVE[label] = snap_live(label, rec["payload"])
    except SystemExit as e:                       # fail-closed trên bản ghi THẬT = lỗi, FAIL có tên
        LIVE[label] = {}
        print(f"  live SystemExit: {e}")
    RAW[label] = snap_jsonl(label, rec)
    sl = {t: (v["qty"], v["sellable"]) for t, v in LIVE[label].items()}
    sr = {t: (v["qty"], v["sellable"]) for t, v in RAW[label].items()}
    diff = {t: (sl.get(t), sr.get(t)) for t in set(sl) | set(sr) if sl.get(t) != sr.get(t)}
    check(f"LR-1 {label}: (qty, sellable) live == jsonl cho MỌI mã ({len(sr)} mã, ts {rec['ts']})",
          not diff and len(sr) > 0, diff)
    # Bằng chứng lỗi có sẵn brokers.py:729-731 (thông tin, KHÔNG phải assertion: nếu user vá
    # brokers.py thì số này về 0 và selfcheck vẫn xanh).
    gp = {t: v["sellable"] for t, v in tbb.DNSEBroker.get_positions(
        type("B", (), {"client": _FakeDNSEClient(rec["payload"]), "account_id": acct_no,
                       "_log_raw": lambda *a: None})()).items()}
    bad = {t: (gp[t], sr[t][1]) for t in gp if t in sr and gp[t] != sr[t][1]}
    print(f"  info — {label}: DNSEBroker.get_positions() sellable ≠ tradeQuantity ở {len(bad)} mã "
          f"(get_positions, thô): {bad}")

# Giá trị TUYỆT ĐỐI (live == jsonl không đủ: cả hai cùng sai vẫn bằng nhau) — đọc từ bản ghi thật
EXP = {"ZaloPay": {"VIB": (19, 0), "BID": (27, 0), "MSB": (40, 0), "VPB": (312, 0),
                   "MBB": (52, 2), "HDB": (59, 59), "VIX": (5, 5)},
       "SpaceX": {"VIB": (47, 0), "TPB": (30, 0), "BID": (75, 0), "MBB": (275, 0),
                  "MSB": (100, 0), "VPB": (286, 0), "VIX": (20, 20), "DRI": (3700, 3700)}}
for label, exp in EXP.items():
    got = {t: (LIVE[label].get(t, {}).get("qty"), LIVE[label].get(t, {}).get("sellable"))
           for t in exp}
    check(f"LR-2 {label}: sellable = Σ tradeQuantity THÔ (0 giữ nguyên 0), qty = Σ openQuantity",
          got == exp, {t: (got[t], exp[t]) for t in exp if got[t] != exp[t]})
check("LR-2b mã PENDING_CLOSE open 0 (SCL/ACB) KHÔNG có trong vị thế",
      not ({"SCL", "ACB"} & (set(LIVE["ZaloPay"]) | set(RAW["ZaloPay"]))))

# Tổng hợp nhiều loan-package (không có ca trade>0 nhiều dòng trong dữ liệu thật ⇒ ca dựng thêm)
_agg = ph.aggregate_position_rows(
    [{"symbol": "AAA", "openQuantity": 120, "tradeQuantity": 50, "marketPrice": 10_000},
     {"symbol": "AAA", "openQuantity": 80, "tradeQuantity": 30, "marketPrice": None},
     {"symbol": "AAA", "openQuantity": 40, "tradeQuantity": 40, "status": "CLOSED"},
     {"symbol": "AAA", "openQuantity": 9, "tradeQuantity": 9, "accountNo": "OTHER"}], "X")
check("LR-3 gộp 2 loan-package: qty 200, sellable 50+30=80, bỏ CLOSED + account khác",
      _agg == {"AAA": {"qty": 200, "sellable": 80, "broker_market_price": 10_000.0}}, _agg)

# Payload dạng lạ (qty chỉ ở khoá dự phòng `quantity`) ⇒ live FAIL-CLOSED, không đoán sellable
try:
    snap_live("ZaloPay", {"positions": [{"symbol": "AAA", "quantity": 100, "tradeQuantity": 0,
                                         "accountNo": ACCT_NO["ZaloPay"]}]})
    _lr4 = "không chặn"
except SystemExit as e:
    _lr4 = "fail-closed" if "fail-closed" in str(e) else f"SystemExit khác: {e}"
check("LR-4 qty get_positions ≠ qty chuẩn hoá ⇒ live SystemExit fail-closed", _lr4 == "fail-closed",
      _lr4)

# Từ vị thế THẬT đi tiếp L1 → L2 → merge: mã tradeQuantity=0 KHÔNG được full_exit ở cả 2 đường
print("-- tradeQuantity=0 (bản ghi thật) ⇒ KHÔNG full_exit ở L1 / L2 / merge, cả live lẫn jsonl --")


def _h_from_snapshot(snap, tickers, px=20_000):
    lots = [{"ticker": t, "qty": snap[t]["qty"], "market_price": px, "mv_vnd": snap[t]["qty"] * px,
             "price": px, "entry_date": "2026-09-01", "source": "j1", "book": "PARK",
             "play_type": "NEUTRAL_park"} for t in tickers]
    return {"account_label": "TEST", "asof": ASOF, "park_lots": lots, "lots": lots,
            "broker_positions": {t: dict(snap[t], market_price=px) for t in tickers},
            "park_mv_vnd": sum(l["mv_vnd"] for l in lots), "cash_available_vnd": 0.0,
            "cash_total_vnd": DEBT, "cash_debt_vnd": DEBT, "cash_dividend_receiving_vnd": 0.0,
            "egg_assets_vnd": 0.0, "cash_basis": "total_cash",
            "reconcile": {"ok": True, "mismatches": []},
            "unverified_tickers": [], "excluded_tickers": []}


ZERO = {"ZaloPay": ["VIB", "BID", "MSB", "VPB", "MBB"],
        "SpaceX": ["VIB", "TPB", "BID", "MBB", "MSB", "VPB"]}
for label, tks in ZERO.items():
    for src_name, snap in (("live", LIVE[label]), ("jsonl", RAW[label])):
        if not all(t in snap for t in tks):
            check(f"TQ0-L1 {label}/{src_name}: snapshot thiếu mã", False, sorted(set(tks) - set(snap)))
            continue
        for t in tks:
            PX.setdefault(t, 20_000)
        old = cpt.STATE_FILE
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"state": 3, "state_name": "NEUTRAL", "date": ASOF, "etf_park_frac": 0.0}, f)
        cpt.STATE_FILE = path
        try:
            r1 = cpt.compute_trim("TEST", ASOF, 0.0, holdings=_h_from_snapshot(snap, tks),
                                  share_override=1.0, adv_fn=adv_for_cap_shares({}),
                                  day_cap_override=1e15, basket_override={"AAA": 1.0},
                                  price_fn=lambda tk: (20_000, None),
                                  excluded_dividend_config_override=[])
        finally:
            cpt.STATE_FILE = old
            os.unlink(path)
        fe1 = {o["ticker"]: o["qty"] for o in r1.get("orders", []) if o.get("full_exit")}
        over1 = {o["ticker"]: (o["qty"], snap[o["ticker"]]["sellable"])
                 for o in r1.get("orders", []) if o["qty"] > snap[o["ticker"]]["sellable"]}
        check(f"TQ0-L1 {label}/{src_name}: KHÔNG full_exit + Σ ≤ sellable cho mã tradeQuantity thấp",
              not fe1 and not over1, (fe1, over1))
        buy = dict(BUY, qty=100_000)                 # cần 1 tỷ ⇒ L2 vét mọi thứ bán được
        r2 = cju.compute_jit_unpark("TEST", asof=ASOF, orders=[buy],
                                    holdings=_h_from_snapshot(snap, tks), share_override=1.0,
                                    adv_fn=lambda tk, a: (1e15, a, None), day_cap_override=1e15)
        fe2 = {o["ticker"]: o["qty"] for o in r2.get("orders", []) if o.get("full_exit")}
        over2 = {o["ticker"]: (o["qty"], snap[o["ticker"]]["sellable"])
                 for o in r2.get("orders", []) if o["qty"] > snap[o["ticker"]]["sellable"]}
        check(f"TQ0-L2 {label}/{src_name}: KHÔNG full_exit + Σ ≤ sellable cho mã tradeQuantity thấp",
              not fe2 and not over2, (fe2, over2))
        pm, rm = merge(r1, dict(r2, decision="JIT", reconcile_ok=True))
        gm = {o["ticker"]: o["qty"] for o in pm["orders"]
              if o.get("merge_owner") == mpo.OWNER and o["ticker"] in tks}
        check(f"TQ0-M {label}/{src_name}: merge KHÔNG sinh lệnh bán vượt sellable / lô lẻ",
              all(q <= snap[t]["sellable"] and q % LOT == 0 for t, q in gm.items())
              and rm["status"] in ("OK", "NOOP", "NO_CHANGE", "SKIP"), (gm, rm["status"]))

print(f"\n{len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAILED: " + "; ".join(FAIL))

# ═════════════════════════════════════════════════════════ mutation runner
MUTANTS = [
    # (tên, file, chuỗi gốc, chuỗi mutant, assertion PHẢI fail)
    ("M_invert_full_exit", "compute_park_trim.py",
     "if 0 < rest < LOT and book_left <= sellable_left and broker_left <= sellable_left:",
     "if not (0 < rest < LOT) and book_left <= sellable_left:", "L1-1 VIX 220"),
    ("M_drop_sellable_min", "compute_park_trim.py",
     "if 0 < rest < LOT and book_left <= sellable_left and broker_left <= sellable_left:",
     "if 0 < rest < LOT:", "H-4 full_exit_qty(200,220,219)"),
    ("M_drop_lot_bound", "compute_park_trim.py",
     "if 0 < rest < LOT and book_left <= sellable_left and broker_left <= sellable_left:",
     "if 0 < rest and book_left <= sellable_left and broker_left <= sellable_left:",
     "L1-5 ADV-cap binding"),
    ("M_lot_le", "compute_park_trim.py", "if 0 < rest < LOT and book_left <= sellable_left and broker_left <= sellable_left:",
     "if 0 < rest <= LOT and book_left <= sellable_left and broker_left <= sellable_left:",
     "B3-i book 300"),
    ("M_drop_broker_cond", "compute_park_trim.py", "if 0 < rest < LOT and book_left <= sellable_left and broker_left <= sellable_left:",
     "if 0 < rest < LOT and book_left <= sellable_left:", "B3-iii-a PARK 330"),
    ("M_l1_broker_not_passed", "compute_park_trim.py",
     "int(bpos.get(tk, {}).get(\"qty\", d[\"qty\"])))", "d[\"qty\"])", "B3-iii-a PARK 330"),
    ("M_l2_drop_used_book", "compute_jit_unpark.py",
     "d[\"qty\"] - used_q - d[\"sold_qty\"],", "d[\"qty\"] - d[\"sold_qty\"],",
     "B3-ii-a L2 book 320"),
    ("M_l2_drop_used_sellable", "compute_jit_unpark.py",
     "d[\"sellable\"] - used_q - d[\"sold_qty\"],", "d[\"sellable\"] - d[\"sold_qty\"],",
     "B3-ii-b L2 book 320"),
    ("M_l2_drop_used_broker", "compute_jit_unpark.py",
     "d[\"broker_qty\"] - used_q - d[\"sold_qty\"])", "d[\"broker_qty\"] - d[\"sold_qty\"])",
     "B3-ii-a L2 book 320"),
    ("M_l2_broker_ignored", "compute_jit_unpark.py",
     "d[\"broker_qty\"] - used_q - d[\"sold_qty\"])", "d[\"qty\"] - used_q - d[\"sold_qty\"])",
     "B3-ii-c L2 broker 420"),
    ("M_drop_adv_cap", "compute_park_trim.py",
     "sell_vnd = min(want_vnd, cap_i)", "sell_vnd = want_vnd", "L1-5 ADV-cap binding"),
    ("M_l1_no_call", "compute_park_trim.py",
     "qty, full_exit = full_exit_qty(qty_lot, d[\"qty\"], sellable,",
     "qty, full_exit = qty_lot, False; _x = (qty_lot, d[\"qty\"], sellable,", "L1-1 VIX 220"),
    ("M_l1_min_sellable_removed", "compute_park_trim.py",
     "qty = min(qty, d[\"qty\"], sellable)", "qty = min(qty, d[\"qty\"])", "L1-6 sellable 120"),
    ("M_l2_no_call", "compute_jit_unpark.py",
     "q, full_exit = full_exit_qty(q_lot,", "q, full_exit = q_lot, False; _x = (q_lot,",
     "L2-1 PARK 250"),
    ("M_l2_ignore_sellable", "compute_jit_unpark.py",
     "d[\"sellable\"] - used_q - d[\"sold_qty\"],", "10**9,", "L2-3 sellable 220"),
    ("M_merge_ignore_flag", "merge_park_orders.py",
     "if d[k] % LOT and keep_odd and k[-2:] in d[\"full_exit\"]:",
     "if d[k] % LOT and keep_odd:", "M-3 qty lẻ KHÔNG khai full_exit"),
    ("M_merge_ignore_cut", "merge_park_orders.py",
     "keep_odd = (d[\"sellable\"] is not None and not d[\"cut_L1\"] and not d[\"cut_L2\"])",
     "keep_odd = (d[\"sellable\"] is not None)", "M-8 L1 bị CẮT"),
    ("M_merge_ignore_unknown_sellable", "merge_park_orders.py",
     "keep_odd = (d[\"sellable\"] is not None and not d[\"cut_L1\"] and not d[\"cut_L2\"])",
     "keep_odd = (not d[\"cut_L1\"] and not d[\"cut_L2\"])", "M-4 full_exit nhưng sellable"),
    ("M_merge_never_keep_odd", "merge_park_orders.py",
     "if d[k] % LOT and keep_odd and k[-2:] in d[\"full_exit\"]:",
     "if False:", "M-1 L1 full_exit 220"),
    ("M_merge_I4_accepts_any_odd", "merge_park_orders.py",
     "or (_i(o.get(\"qty\")) % LOT != 0 and o.get(\"full_exit\") is not True))]",
     "or False)]", "I4-a lệnh merge lẻ"),
    # ── vòng 2 NON-BLOCKING: sold_qty (2 MUA cùng rút 1 mã) + nhánh mặc định broker_left=None
    ("X11_l2_book_no_sold", "compute_jit_unpark.py",
     "d[\"qty\"] - used_q - d[\"sold_qty\"],", "d[\"qty\"] - used_q,", "SQ-1 book=sellable=broker"),
    ("X12_l2_sellable_no_sold", "compute_jit_unpark.py",
     "d[\"sellable\"] - used_q - d[\"sold_qty\"],", "d[\"sellable\"] - used_q,", "SQ-2 sellable 300"),
    ("X13_l2_broker_no_sold", "compute_jit_unpark.py",
     "d[\"broker_qty\"] - used_q - d[\"sold_qty\"])", "d[\"broker_qty\"] - used_q)",
     "SQ-1 book=sellable=broker"),
    ("X14_l2_sold_not_accumulated", "compute_jit_unpark.py",
     "d[\"sold_qty\"] += q\n", "pass\n", "SQ-1 book=sellable=broker"),
    ("X4_default_broker_too_big", "compute_park_trim.py",
     "        broker_left = book_left\n", "        broker_left = book_left + LOT\n",
     "H-7 full_exit_qty(200,220,220,None)"),
    ("X4b_default_branch_removed", "compute_park_trim.py",
     "    if broker_left is None:\n        broker_left = book_left\n", "",
     "H-7 full_exit_qty(200,220,220,None)"),
    # ── vòng 3 BLOCKING: nguồn sellable live vs jsonl (park_holdings)
    ("R1_live_sellable_from_get_positions", "park_holdings.py",
     "\"market_price\": 0.0, \"sellable\": d[\"sellable\"],",
     "\"market_price\": 0.0, \"sellable\": raw_pos[sym].get(\"sellable\", d[\"qty\"]),",
     "TQ0-L1 ZaloPay/live"),
    ("R1b_live_sellable_from_get_positions_lr", "park_holdings.py",
     "\"market_price\": 0.0, \"sellable\": d[\"sellable\"],",
     "\"market_price\": 0.0, \"sellable\": raw_pos[sym].get(\"sellable\", d[\"qty\"]),",
     "LR-1 ZaloPay"),
    ("R2_norm_or_total", "park_holdings.py",
     "sellable = int(p.get(\"tradeQuantity\") or 0)", "sellable = int(p.get(\"tradeQuantity\") or q)",
     "LR-2 ZaloPay"),
    ("R3_norm_no_sellable_sum", "park_holdings.py",
     "            sellable += prev[\"sellable\"]\n", "            pass\n", "LR-3 gộp 2 loan-package"),
    ("R4_norm_no_qty_sum", "park_holdings.py",
     "            q += prev[\"qty\"]\n", "            pass\n", "LR-1 ZaloPay"),
    ("R5_norm_keep_closed", "park_holdings.py",
     "        if str(p.get(\"status\", \"OPEN\")).upper() == \"CLOSED\":\n            continue\n",
     "", "LR-3 gộp 2 loan-package"),
    ("R6_norm_no_account_filter", "park_holdings.py",
     "        if str(p.get(\"accountNo\") or account_no) != str(account_no):\n            continue\n",
     "", "LR-3 gộp 2 loan-package"),
    ("R7_live_no_qty_crosscheck", "park_holdings.py",
     "if _bq != _aq:", "if False:", "LR-4 qty get_positions"),
    ("R8_jsonl_sellable_eq_qty", "park_holdings.py",
     "\"market_price\": d[\"broker_market_price\"] or 0.0,\n                         \"sellable\": d[\"sellable\"],",
     "\"market_price\": d[\"broker_market_price\"] or 0.0,\n                         \"sellable\": d[\"qty\"],",
     "LR-1 ZaloPay"),
]


def run_mutations():
    killed, survived = [], []
    for name, fname, a, b, must in MUTANTS:
        src = open(os.path.join(BIN, fname), encoding="utf-8").read()
        if src.count(a) != 1:
            survived.append(f"{name}: chuỗi gốc xuất hiện {src.count(a)} lần (mutant không áp được)")
            continue
        d = tempfile.mkdtemp(prefix="oddlot_mut_")
        try:
            with open(os.path.join(d, fname), "w", encoding="utf-8") as f:
                f.write(src.replace(a, b))
            env = dict(os.environ, ODDLOT_MUT_DIR=d, WC_ROOT=WC)
            pr = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env,
                                capture_output=True, text=True, timeout=300)
            out = pr.stdout + pr.stderr
            hit = any(line.strip().startswith(f"FAIL — {must}") for line in out.splitlines())
            (killed if (pr.returncode != 0 and hit) else survived).append(
                f"{name} (rc={pr.returncode}, '{must}' FAIL={hit})")
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print(f"\n=== MUTATION: {len(killed)}/{len(MUTANTS)} bị giết bằng assertion có tên ===")
    for k in killed:
        print("  KILLED  " + k)
    for s in survived:
        print("  SURVIVED " + s)
    return not survived


def run_tz():
    variants = [("env -u TZ", None), ("Asia/Ho_Chi_Minh", "Asia/Ho_Chi_Minh"), ("UTC", "UTC"),
                ("America/New_York", "America/New_York"), ("Asia/Tokyo", "Asia/Tokyo")]
    ok = True
    for label, tz in variants:
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        if tz:
            env["TZ"] = tz
        pr = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env,
                            capture_output=True, text=True, timeout=300)
        tail = [l for l in pr.stdout.splitlines() if "PASS /" in l]
        print(f"  TZ={label:18s} rc={pr.returncode} {tail[-1] if tail else '?'}")
        ok &= pr.returncode == 0
    return ok


if __name__ == "__main__":
    ok = not FAIL
    if not _MUT and "--mutations" in sys.argv:
        ok &= run_mutations()
    if not _MUT and "--all-tz" in sys.argv:
        ok &= run_tz()
    sys.exit(0 if ok else 1)
