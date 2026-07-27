# -*- coding: utf-8 -*-
"""Self-check: mở rộng hybrid ADV20-floor + realized-ceiling từ CAPIT sang DISCRETIONARY_SPECIAL.

Context (job Taylor_20260727_072910): TV1 (book=DISCRETIONARY_SPECIAL) lại kẹt WAIT_QUOTA suốt
phiên 2026-07-27 — đúng lỗi NCT tuần trước. Fix hybrid ADV20-floor + realized-ceiling tuần trước
CHỈ áp cho book=="CAPIT" (_is_capit_buy) nên TV1 rơi vào nhánh `elif q.day_volume` cũ (trần theo
%KL khớp thật trong ngày — sai công cụ cho tên thanh khoản mỏng/không đều như TV1).

Fix: _adv20_basis_for(o) route ADV20 theo book — CAPIT lấy từ golive_v23_status.json (không đổi),
DISCRETIONARY_SPECIAL lấy adv_ref_vnd từ state file riêng state_<TICKER>_<account>.json (tổng quát,
không hardcode TV1). Nhánh hybrid trong _child_qty dùng chung cho cả 2 book; trần phụ 30% realized
dùng chung capit_realized_participation_ceiling (cùng ngữ nghĩa "không thành đa số một phiên mỏng").

Bất biến regression: CAPIT hành vi Y HỆT (chạy lại capit_participation_cap_selfcheck.py). File này
lo phần DISCRETIONARY_SPECIAL + fail-safe.

Run: python discretionary_participation_cap_selfcheck.py   (exit 0 = all pass)
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
# Tag DUY NHẤT cho file này — KHÔNG dùng chung với selfcheck khác (bài học §7 coding_guidelines).
TAG = "selfcheck-disc-cap"
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


def make_executor(tmpdir, orders, account=TAG, shared=None):
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=orders,
                     account=account, created_at="2099-01-01T00:00:00")
    cfg = load_config()
    cfg["mode"] = "paper"
    ex = Executor(plan, _NullBroker(), cfg, shared=shared if shared is not None else {})
    ex.state_file = os.path.join(tmpdir, "state.json")
    ex.journal_file = os.path.join(tmpdir, "journal.csv")
    return ex


def old_child_qty(cfg, shared, o, ps, q, px):
    """Bản _child_qty TRƯỚC thay đổi (guard cũ %KL-ngày) — ground-truth cho fail-safe/regression."""
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


def write_state(dirpath, ticker, account, adv_ref_vnd, extra=None):
    """Tạo state file DISCRETIONARY_SPECIAL theo đúng convention state_<TICKER>_<account>.json."""
    os.makedirs(dirpath, exist_ok=True)
    d = {"schema": "low_liquidity_discretionary_accumulation_state_v1",
         "ticker": ticker, "account": account, "book": "DISCRETIONARY_SPECIAL",
         "status": "active"}
    if adv_ref_vnd is not None:
        d["adv_ref_vnd"] = adv_ref_vnd
    if extra:
        d.update(extra)
    p = os.path.join(dirpath, f"state_{ticker}_{account}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f)
    return p


# TV1 thật (state_TV1_SpaceX.json): adv_ref_vnd = 701.000.000, resting_limit 19.900.
TV1_ADV20_VND = 701_000_000
TV1_PX = 19_900

# ---------------------------------------------------------------- Test A: TV1 hết WAIT_QUOTA oan
# Phiên KL ngày THẤP nhưng ADV20 đủ → guard cũ chặn oan, hybrid cho mua (yêu cầu (a) dispatch).
with tempfile.TemporaryDirectory() as tmp:
    disc_dir = os.path.join(tmp, "disc")
    write_state(disc_dir, "TV1", "SpaceX", TV1_ADV20_VND)
    o = PlannedOrder(id="DISC-A", ticker="TV1", side="buy", qty=200, ref_price=TV1_PX,
                     book="DISCRETIONARY_SPECIAL")
    ex = make_executor(tmp, [o], account="SpaceX")
    # loader đọc từ base_dir test thay vì WORKDIR thật
    ex._disc_adv20_vnd = ex._load_discretionary_adv20_basis(base_dir=disc_dir)
    check("A0 loader đọc adv_ref_vnd đúng từ state file convention", ex._disc_adv20_vnd == {"TV1": float(TV1_ADV20_VND)},
          f"{ex._disc_adv20_vnd}")
    cfg, shared, ps = ex.cfg, ex.shared, ps_for(ex, o)
    q_thin = FakeQuote(day_volume=500)     # phiên mỏng bất thường (10%×500=50 < lô → guard cũ return 0)

    old = old_child_qty(cfg, shared, o, ps, q_thin, TV1_PX)
    new = ex._child_qty(o, ps, q_thin, TV1_PX)
    check("A1 OLD guard %KL-ngày CHẶN oan trên phiên mỏng (return 0 = WAIT_QUOTA)", old == 0, f"old={old}")
    check("A2 NEW cho phép mua (qty>0, hết WAIT_QUOTA oan cho TV1)", new > 0, f"new={new}")
    # floor=int(0.10*701M/19900)=3522; ceil=int(0.30*500)=150; by_value=int(200M/19900)=10050;
    # qty=min(remaining=200, by_value)=200; allowance=min(3522,150)=150 → qty=min(200,150)=150 → round_lot=100
    check("A3 NEW = 100 (min(floor=3522, ceil=150)=150 → round_lot lô 100)", new == 100, f"new={new}")

# ---------------------------------------------------------------- Test B: trần phụ 30% realized cắt đúng
with tempfile.TemporaryDirectory() as tmp:
    disc_dir = os.path.join(tmp, "disc")
    write_state(disc_dir, "TV1", "SpaceX", TV1_ADV20_VND)
    o = PlannedOrder(id="DISC-B", ticker="TV1", side="buy", qty=5000, ref_price=TV1_PX,
                     book="DISCRETIONARY_SPECIAL")
    ex = make_executor(tmp, [o], account="SpaceX")
    ex._disc_adv20_vnd = ex._load_discretionary_adv20_basis(base_dir=disc_dir)
    cfg, ps = ex.cfg, ps_for(ex, o)
    q = FakeQuote(day_volume=1000)    # floor=3522 lớn hơn; ceil=int(0.30*1000)=300 BIND
    new = ex._child_qty(o, ps, q, TV1_PX)
    check("B1 trần phụ 30% realized cắt xuống ĐÚNG 300 (=0.30*1000)", new == 300, f"new={new}")
    check("B2 KHÔNG vượt ADV20-floor 3522", new < 3522, f"new={new}")

# ---------------------------------------------------------------- Test C: ADV20-floor bind khi tape dày
with tempfile.TemporaryDirectory() as tmp:
    disc_dir = os.path.join(tmp, "disc")
    write_state(disc_dir, "TV1", "SpaceX", TV1_ADV20_VND)
    o = PlannedOrder(id="DISC-C", ticker="TV1", side="buy", qty=50000, ref_price=TV1_PX,
                     book="DISCRETIONARY_SPECIAL")
    ex = make_executor(tmp, [o], account="SpaceX")
    ex._disc_adv20_vnd = ex._load_discretionary_adv20_basis(base_dir=disc_dir)
    cfg, ps = ex.cfg, ps_for(ex, o)
    q = FakeQuote(day_volume=10_000_000)   # tape dày → ceil lỏng, floor bind
    new = ex._child_qty(o, ps, q, TV1_PX)
    # floor=int(0.10*701M/19900)=3522; by_value=int(200M/19900)=10050; ceil=int(0.30*1e7)=3e6
    # allowance=min(3522, 3e6)=3522 → qty=min(remaining=50000, 10050, 3522)=3522 → round_lot=3500
    check("C1 ADV20-floor bind khi tape dày → 3500 (round_lot của 3522)", new == 3500, f"new={new}")

# ---------------------------------------------------------------- Test D: fail-safe thiếu adv_ref_vnd
# (c) state file tồn tại NHƯNG thiếu/sai adv_ref_vnd → lùi guard cũ.
with tempfile.TemporaryDirectory() as tmp:
    disc_dir = os.path.join(tmp, "disc")
    write_state(disc_dir, "TV1", "SpaceX", None)          # thiếu adv_ref_vnd
    o = PlannedOrder(id="DISC-D", ticker="TV1", side="buy", qty=5000, ref_price=TV1_PX,
                     book="DISCRETIONARY_SPECIAL")
    ex = make_executor(tmp, [o], account="SpaceX")
    ex._disc_adv20_vnd = ex._load_discretionary_adv20_basis(base_dir=disc_dir)
    check("D0 loader bỏ qua ticker thiếu adv_ref_vnd → {}", ex._disc_adv20_vnd == {}, f"{ex._disc_adv20_vnd}")
    cfg, shared, ps = ex.cfg, ex.shared, ps_for(ex, o)
    for dv in [0, 500, 100_000]:
        q = FakeQuote(day_volume=dv)
        new = ex._child_qty(o, ps, q, TV1_PX)
        old = old_child_qty(cfg, shared, o, ps, q, TV1_PX)
        check(f"D1 dv={dv}: fail-safe = guard cũ (không mua vô hạn)", new == old, f"new={new} old={old}")

    # adv_ref_vnd âm/0 cũng bị loại (không tạo ADV20 rác)
    write_state(disc_dir, "TV1", "SpaceX", -5)
    check("D2 adv_ref_vnd âm → bỏ qua (loader {})",
          ex._load_discretionary_adv20_basis(base_dir=disc_dir) == {})
    write_state(disc_dir, "TV1", "SpaceX", 0)
    check("D3 adv_ref_vnd=0 → bỏ qua (loader {})",
          ex._load_discretionary_adv20_basis(base_dir=disc_dir) == {})

# ---------------------------------------------------------------- Test E: DISCRETIONARY_SPECIAL KHÔNG có state file
# (d) order phát sinh thủ công, không đăng ký playbook (không có state file) → guard cũ, KHÔNG crash.
with tempfile.TemporaryDirectory() as tmp:
    disc_dir = os.path.join(tmp, "disc")   # rỗng — không tạo state file nào
    os.makedirs(disc_dir, exist_ok=True)
    o = PlannedOrder(id="DISC-E", ticker="XYZ", side="buy", qty=5000, ref_price=10_000,
                     book="DISCRETIONARY_SPECIAL")
    ex = make_executor(tmp, [o], account="SpaceX")
    ex._disc_adv20_vnd = ex._load_discretionary_adv20_basis(base_dir=disc_dir)
    check("E0 loader không crash khi thiếu file → {}", ex._disc_adv20_vnd == {}, f"{ex._disc_adv20_vnd}")
    cfg, shared, ps = ex.cfg, ex.shared, ps_for(ex, o)
    for dv in [0, 500, 100_000]:
        q = FakeQuote(day_volume=dv)
        new = ex._child_qty(o, ps, q, 10_000)     # KHÔNG crash
        old = old_child_qty(cfg, shared, o, ps, q, 10_000)
        check(f"E1 dv={dv}: DISCRETIONARY_SPECIAL không state → guard cũ, không crash", new == old,
              f"new={new} old={old}")

# ---------------------------------------------------------------- Test F: base dir không tồn tại → {}
with tempfile.TemporaryDirectory() as tmp:
    o = PlannedOrder(id="DISC-F", ticker="TV1", side="buy", qty=200, ref_price=TV1_PX,
                     book="DISCRETIONARY_SPECIAL")
    ex = make_executor(tmp, [o], account="SpaceX")
    m = ex._load_discretionary_adv20_basis(base_dir=os.path.join(tmp, "does_not_exist"))
    check("F1 base_dir không tồn tại → {} (không crash)", m == {}, f"{m}")
    # plan không có DISCRETIONARY_SPECIAL buy → {} (short-circuit)
    o_non = PlannedOrder(id="BAL-F", ticker="FPT", side="buy", qty=500, ref_price=20_000, book="BAL")
    ex_non = make_executor(tmp, [o_non], account="SpaceX")
    disc_dir = os.path.join(tmp, "disc2")
    write_state(disc_dir, "FPT", "SpaceX", 5_000_000_000)
    check("F2 plan không có DISCRETIONARY_SPECIAL buy → {} (short-circuit)",
          ex_non._load_discretionary_adv20_basis(base_dir=disc_dir) == {})

# ---------------------------------------------------------------- Test G: routing _adv20_basis_for
with tempfile.TemporaryDirectory() as tmp:
    disc_dir = os.path.join(tmp, "disc")
    write_state(disc_dir, "TV1", "SpaceX", TV1_ADV20_VND)
    o_disc = PlannedOrder(id="G-DISC", ticker="TV1", side="buy", qty=200, ref_price=TV1_PX,
                          book="DISCRETIONARY_SPECIAL")
    o_disc_sell = PlannedOrder(id="G-DISC-SELL", ticker="TV1", side="sell", qty=200, ref_price=TV1_PX,
                               book="DISCRETIONARY_SPECIAL")
    o_bal = PlannedOrder(id="G-BAL", ticker="FPT", side="buy", qty=500, ref_price=20_000, book="BAL")
    ex = make_executor(tmp, [o_disc, o_disc_sell, o_bal], account="SpaceX")
    ex._disc_adv20_vnd = ex._load_discretionary_adv20_basis(base_dir=disc_dir)
    ex._capit_adv20_vnd = {"TV1": 999}   # phải bị PHỚT LỜ cho DISCRETIONARY buy (route theo book)
    check("G1 _adv20_basis_for(DISC buy) → adv_ref_vnd (KHÔNG lẫn nguồn CAPIT)",
          ex._adv20_basis_for(o_disc) == float(TV1_ADV20_VND), f"{ex._adv20_basis_for(o_disc)}")
    check("G2 _adv20_basis_for(DISC SELL) → None (chỉ buy mới ADV20-paced)",
          ex._adv20_basis_for(o_disc_sell) is None)
    check("G3 _adv20_basis_for(BAL buy) → None (không phải ADV20-paced)",
          ex._adv20_basis_for(o_bal) is None)

# ---------------------------------------------------------------- Test H: regression non-DISCRETIONARY byte-identical
with tempfile.TemporaryDirectory() as tmp:
    disc_dir = os.path.join(tmp, "disc")
    write_state(disc_dir, "TV1", "SpaceX", TV1_ADV20_VND)
    o_bal = PlannedOrder(id="H-BAL", ticker="FPT", side="buy", qty=5000, ref_price=20_000, book="BAL")
    o_lag = PlannedOrder(id="H-LAG", ticker="MBB", side="buy", qty=5000, ref_price=25_000, book="LAG")
    ex = make_executor(tmp, [o_bal, o_lag], account="SpaceX")
    # dù có state file TV1, các order non-DISCRETIONARY phải PHỚT LỜ ADV20 và chạy guard cũ
    ex._disc_adv20_vnd = {"FPT": 9e9, "MBB": 9e9}   # cố tình nhồi để chắc chắn bị bỏ qua
    cfg, shared = ex.cfg, ex.shared
    regression_ok, detail = True, ""
    for (o, px) in [(o_bal, 20_000), (o_lag, 25_000)]:
        ps = ps_for(ex, o)
        for dv in [0, 50, 500, 1000, 100_000, 5_000_000]:
            for filled in [0, 100, 3000]:
                ps["filled"] = filled
                q = FakeQuote(day_volume=dv)
                new = ex._child_qty(o, ps, q, px)
                old = old_child_qty(cfg, shared, o, ps, q, px)
                if new != old:
                    regression_ok, detail = False, f"{o.id} dv={dv} filled={filled}: new={new} old={old}"
                    break
            if not regression_ok:
                break
        ps["filled"] = 0
        if not regression_ok:
            break
    check("H non-DISCRETIONARY (BAL/LAG buy) hành vi Y HỆT code cũ mọi input", regression_ok,
          detail or "36 tổ hợp dv×filled×order khớp new==old")

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ ALL PASS — DISCRETIONARY_SPECIAL hybrid participation-cap (ADV20 floor + 30% realized ceiling)")
sys.exit(0)
