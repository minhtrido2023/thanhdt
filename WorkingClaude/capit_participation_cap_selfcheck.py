# -*- coding: utf-8 -*-
"""Regression self-check for the CAPIT hybrid participation-cap (ADV20 floor + realized ceiling).

Context (2 vòng R&D đã CONFIRMED trước khi code này ra đời):
  - Taylor_20260721_043923 (chẩn đoán) — verify_20260721_050105.log
  - Taylor_20260721_050720 (market-impact test) — verify_20260721_052922.log
  - mike/agents/Taylor/research/capit_participation_cap_marketimpact.md

Vấn đề: guard pacing cũ trong Executor._child_qty (executor.py) dùng `max_participation ×
q.day_volume` REAL-TIME. Sáng 2026-07-21 NCT có phiên mỏng bất thường (<1000cp tới 11:29) →
10% × day_volume < 1 lô → return 0 → lệnh CAPIT bị WAIT_QUOTA OAN dù NCT thực chất thanh khoản
(ADV20 ~2,18 tỷ/ngày). Sửa (CHỈ cho lệnh CAPIT): đổi CƠ SỞ pacing sang ADV20 causal (đảo ngược
cap_vnd=X·ADV20·D trong golive_v23_status.json) + THÊM trần phụ 30% KL khớp lũy kế THẬT để fleet
không thành đa số một phiên mỏng. allowance = min(ADV20-floor, 30%-realized-ceiling).

Non-CAPIT: GIỮ NGUYÊN 100% guard cũ (10% day_volume real-time). Đây là bất biến regression
quan trọng nhất — test D so sánh new vs old byte-cho-byte trên nhiều input.

Run: python capit_participation_cap_selfcheck.py   (exit 0 = all pass)
"""
import glob
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.plan import PlannedOrder, TradePlan  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.config import load_config, EXEC_DIR  # noqa: E402
from trading_bot.vn_market import round_lot, LOT  # noqa: E402

# Xoá fixture cũ để chạy lặp không nhiễm state (cùng pattern ghost_order_selfcheck.py).
TAG = "selfcheck-capit-cap"
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(f)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


class FakeQuote:
    """_child_qty chỉ đọc q.day_volume; đủ để test pacing guard."""
    def __init__(self, day_volume):
        self.day_volume = day_volume

    def ok(self):
        return True


class _NullBroker:
    name = "null"

    def get_quote(self, *a, **k):
        raise AssertionError("get_quote không nên bị gọi trong self-check này")

    def place_order(self, *a, **k):
        raise AssertionError("place_order không nên bị gọi trong self-check này")


def make_executor(tmpdir, orders, shared=None):
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=orders,
                     account=TAG, created_at="2099-01-01T00:00:00")
    cfg = load_config()
    cfg["mode"] = "paper"
    ex = Executor(plan, _NullBroker(), cfg, shared=shared if shared is not None else {})
    ex.state_file = os.path.join(tmpdir, "state.json")
    ex.journal_file = os.path.join(tmpdir, "journal.csv")
    return ex


def old_child_qty(cfg, shared, o, ps, q, px):
    """Bản _child_qty TRƯỚC thay đổi (nguyên văn logic guard cũ) — dùng làm ground-truth
    cho regression test non-CAPIT + fail-safe CAPIT-thiếu-ADV20."""
    remaining = o.qty - ps["filled"]
    if 0 < remaining < LOT:
        return remaining
    by_value = int(cfg["max_child_value"] / px) if px else remaining
    qty = min(remaining, by_value)
    if q.day_volume:
        fleet_filled = shared.get(o.ticker, 0)
        allowance = int(cfg["max_participation"] * q.day_volume) - fleet_filled
        if allowance < LOT:
            return 0
        qty = min(qty, allowance)
    qty = round_lot(qty)
    if qty < LOT <= remaining and remaining * (px or 0) <= cfg["max_child_value"]:
        qty = round_lot(remaining)
    return qty


def ps_for(ex, o):
    return ex.state["parents"][o.id]


# NCT thật (data/golive_v23_status.json 2026-07-21): total cap 435.558.000, x=0.10, d=2.0
# → ADV20_vnd = 435558000 / (0.1*2) = 2.177.790.000. px ~94.000 (lệnh thật 500cp = 47M).
NCT_TOTAL_CAP = 435_558_000
NCT_ADV20_VND = NCT_TOTAL_CAP / (0.10 * 2.0)   # = 2_177_790_000
NCT_PX = 94_000

# ---------------------------------------------------------------- Test A: unblock thin morning
with tempfile.TemporaryDirectory() as tmp:
    o = PlannedOrder(id="CAP-A", ticker="NCT", side="buy", qty=500, ref_price=NCT_PX, book="CAPIT")
    ex = make_executor(tmp, [o])
    ex._capit_adv20_vnd = {"NCT": NCT_ADV20_VND}          # inject ADV20 basis
    cfg, shared, ps = ex.cfg, ex.shared, ps_for(ex, o)
    q_thin = FakeQuote(day_volume=500)                    # phiên mỏng bất thường như NCT sáng nay

    old = old_child_qty(cfg, shared, o, ps, q_thin, NCT_PX)
    new = ex._child_qty(o, ps, q_thin, NCT_PX)
    check("A1 OLD guard CHẶN oan trên phiên mỏng (return 0 = WAIT_QUOTA)", old == 0,
          f"old={old}")
    check("A2 NEW cho phép mua (qty>0, hết WAIT_QUOTA oan)", new > 0, f"new={new}")
    # ADV20-floor = int(0.10*2.177.790.000/94000)=2316; ceil=int(0.30*500)=150; min=150 → round_lot=100
    check("A3 NEW = 100 (min(floor=2316, ceil=150)=150 → round_lot lô 100)", new == 100,
          f"new={new}")

# ---------------------------------------------------------------- Test B: trần phụ 30% cắt đúng
with tempfile.TemporaryDirectory() as tmp:
    o = PlannedOrder(id="CAP-B", ticker="NCT", side="buy", qty=5000, ref_price=NCT_PX, book="CAPIT")
    ex = make_executor(tmp, [o])
    ex._capit_adv20_vnd = {"NCT": NCT_ADV20_VND}
    cfg, ps = ex.cfg, ps_for(ex, o)
    q = FakeQuote(day_volume=1000)      # ADV20-floor=2316 lớn hơn; ceil=int(0.30*1000)=300 BIND
    new = ex._child_qty(o, ps, q, NCT_PX)
    # by_value=int(200M/94000)=2127; floor=2316; ceil=300 → allowance=min(2316,300)=300 → cut đúng 300
    check("B1 trần phụ cắt xuống ĐÚNG 30% cumulative day_volume", new == 300,
          f"new={new} (kỳ vọng 300 = 0.30*1000)")
    check("B2 KHÔNG vượt trần phụ (new < ADV20-floor pacing 2127)", new < 2127,
          f"new={new}")

# ---------------------------------------------------------------- Test C: ADV20-floor bind (mua theo ADV20)
with tempfile.TemporaryDirectory() as tmp:
    # Tên tổng hợp thanh khoản mỏng theo 20 phiên: ADV20 nhỏ, nhưng hôm nay tape lớn.
    o = PlannedOrder(id="CAP-C", ticker="THIN", side="buy", qty=5000, ref_price=10_000, book="CAPIT")
    ex = make_executor(tmp, [o])
    ex._capit_adv20_vnd = {"THIN": 100_000_000}    # ADV20_vnd nhỏ
    cfg, ps = ex.cfg, ps_for(ex, o)
    q = FakeQuote(day_volume=1_000_000)            # tape hôm nay dày → ceil lỏng
    new = ex._child_qty(o, ps, q, 10_000)
    # floor=int(0.10*100M/10000)=1000; ceil=int(0.30*1e6)=300000 → allowance=min=1000 (ADV20 BIND)
    check("C1 ADV20-floor bind khi tape dày (pacing theo ADV20, không theo realized)", new == 1000,
          f"new={new} (kỳ vọng 1000 = 0.10*ADV20/px)")

# ---------------------------------------------------------------- Test D: REGRESSION non-CAPIT byte-identical
with tempfile.TemporaryDirectory() as tmp:
    o_bal = PlannedOrder(id="BAL-D", ticker="FPT", side="buy", qty=5000, ref_price=20_000, book="BAL")
    o_sell = PlannedOrder(id="SELL-D", ticker="FPT", side="sell", qty=5000, ref_price=20_000, book="CAPIT")
    ex = make_executor(tmp, [o_bal, o_sell])
    ex._capit_adv20_vnd = {"FPT": 5_000_000_000}   # dù có ADV20, non-CAPIT phải PHỚT LỜ nó
    cfg, shared = ex.cfg, ex.shared
    regression_ok = True
    detail = ""
    for (o, px) in [(o_bal, 20_000), (o_sell, 20_000)]:
        ps = ps_for(ex, o)
        for dv in [0, 50, 500, 1000, 100_000, 5_000_000]:
            for filled in [0, 100, 3000]:
                ps["filled"] = filled
                q = FakeQuote(day_volume=dv)
                new = ex._child_qty(o, ps, q, px)
                old = old_child_qty(cfg, shared, o, ps, q, px)
                if new != old:
                    regression_ok = False
                    detail = f"{o.id} dv={dv} filled={filled}: new={new} old={old}"
                    break
            if not regression_ok:
                break
        ps["filled"] = 0
        if not regression_ok:
            break
    # o_bal = book BAL (non-CAPIT); o_sell = book CAPIT nhưng side=sell → _is_capit_buy False → guard cũ
    check("D non-CAPIT (BAL buy + CAPIT SELL) hành vi Y HỆT code cũ mọi input", regression_ok,
          detail or "48 tổ hợp dv×filled×order khớp new==old")

# ---------------------------------------------------------------- Test E: fail-safe CAPIT thiếu ADV20
with tempfile.TemporaryDirectory() as tmp:
    o = PlannedOrder(id="CAP-E", ticker="NCT", side="buy", qty=5000, ref_price=NCT_PX, book="CAPIT")
    ex = make_executor(tmp, [o])
    ex._capit_adv20_vnd = {}                       # artifact hỏng/stale → không có ADV20 cho mã
    cfg, shared, ps = ex.cfg, ex.shared, ps_for(ex, o)
    q = FakeQuote(day_volume=100_000)
    new = ex._child_qty(o, ps, q, NCT_PX)
    old = old_child_qty(cfg, shared, o, ps, q, NCT_PX)
    check("E1 CAPIT thiếu ADV20 → fail-safe về guard realtime cũ (không mua vô hạn)", new == old,
          f"new={new} old={old}")

    # E2: CAPIT có ADV20 nhưng px=0 → không chia cho 0, lùi về guard cũ (dùng day_volume)
    ex._capit_adv20_vnd = {"NCT": NCT_ADV20_VND}
    new0 = ex._child_qty(o, ps, q, 0)
    old0 = old_child_qty(cfg, shared, o, ps, q, 0)
    check("E2 CAPIT px=0 → không crash, hành vi = guard cũ", new0 == old0, f"new={new0} old={old0}")

    # E3: CAPIT có ADV20, day_volume=0 (halt) → chỉ ADV20-floor, KHÔNG mua vô hạn (bị order-size chặn)
    q_halt = FakeQuote(day_volume=0)
    o.qty = 500
    ps["filled"] = 0
    new_halt = ex._child_qty(o, ps, q_halt, NCT_PX)
    # floor=int(0.10*2.177.790.000/94000)=2316; remaining=500; by_value=2127; qty=min(500,2127)=500;
    # allowance=2316 → qty=min(500,2316)=500 → round_lot=500. Bị order-size chặn ở 500, KHÔNG vô hạn.
    check("E3 CAPIT halt (day_volume=0) → chỉ ADV20-floor, bị order-size chặn (=500, không vô hạn)",
          new_halt == 500, f"new={new_halt}")

# ---------------------------------------------------------------- Test F: loader fail-safe + đúng giá trị
with tempfile.TemporaryDirectory() as tmp:
    o = PlannedOrder(id="CAP-F", ticker="NCT", side="buy", qty=500, ref_price=NCT_PX, book="CAPIT")
    ex = make_executor(tmp, [o])
    good = {
        "signal_date": "2099-01-01",
        "capit_adv_caps_total": {"NCT": NCT_TOTAL_CAP, "PVT": 9_440_511_000},
        "capit_adv_x": 0.1, "capit_adv_d": 2.0,
    }

    def write(d):
        p = os.path.join(tmp, "st.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f)
        return p

    m = ex._load_capit_adv20_basis(status_path=write(good))
    check("F1 loader trả ADV20_vnd đúng = total/(x*d)",
          abs(m.get("NCT", 0) - NCT_ADV20_VND) < 1 and abs(m.get("PVT", 0) - 9_440_511_000/0.2) < 1,
          f"NCT={m.get('NCT')}")

    bad_date = dict(good, signal_date="2000-01-01")
    check("F2 signal_date artifact ≠ plan → {} (artifact cũ, fail-safe)",
          ex._load_capit_adv20_basis(status_path=write(bad_date)) == {})

    no_total = {k: v for k, v in good.items() if k != "capit_adv_caps_total"}
    check("F3 thiếu capit_adv_caps_total → {}",
          ex._load_capit_adv20_basis(status_path=write(no_total)) == {})

    bad_xd = dict(good, capit_adv_x=0)
    check("F4 capit_adv_x=0 → {} (không chia cho 0)",
          ex._load_capit_adv20_basis(status_path=write(bad_xd)) == {})

    check("F5 file không tồn tại → {} (không crash)",
          ex._load_capit_adv20_basis(status_path=os.path.join(tmp, "nope.json")) == {})

    # F6: plan KHÔNG có lệnh CAPIT buy → {} kể cả khi file hợp lệ (short-circuit, không đọc file)
    o_non = PlannedOrder(id="BAL-F", ticker="FPT", side="buy", qty=500, ref_price=20_000, book="BAL")
    ex_non = make_executor(tmp, [o_non])
    check("F6 plan không có CAPIT buy → {} (short-circuit)",
          ex_non._load_capit_adv20_basis(status_path=write(good)) == {})

    # F7: cap âm/0/None trong total bị bỏ qua (không tạo ADV20 rác)
    dirty = dict(good, capit_adv_caps_total={"NCT": NCT_TOTAL_CAP, "BAD": 0, "NEG": -5, "NUL": None})
    m2 = ex._load_capit_adv20_basis(status_path=write(dirty))
    check("F7 total có 0/âm/None → chỉ giữ mã hợp lệ",
          set(m2.keys()) == {"NCT"}, f"keys={sorted(m2.keys())}")

# ---------------------------------------------------------------- self-check 0 VND (non-CAPIT bất biến)
# Test D ở trên đã chứng minh non-CAPIT byte-identical → không đổi qty/giá lệnh non-CAPIT hiện có.

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ ALL PASS — CAPIT hybrid participation-cap (ADV20 floor + 30% realized ceiling)")
sys.exit(0)
