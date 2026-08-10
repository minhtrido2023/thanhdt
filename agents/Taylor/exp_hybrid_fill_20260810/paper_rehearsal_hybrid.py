# -*- coding: utf-8 -*-
"""Paper rehearsal của lịch HYBRID — job Taylor_20260810_034544.

Mục tiêu HẸP (đúng như dispatch mục 3): chứng minh CƠ CHẾ chạy được trên PaperBroker THẬT —
lệnh ra đúng lịch block, đủ KL, KHÔNG có PLACE_FAIL/reject. KHÔNG đo edge bps (edge đã có
bằng chứng từ 663 phiên backtest; PaperBroker khớp 100% tại giá đặt nên không thể sinh dữ
liệu fill thật — xem `research/fill_timing_checkpoint_20260804.md`).

Chạy phiên mô phỏng 09:00 → 14:30 (bước 1 phút, đồng hồ bơm vào — không phụ thuộc giờ chạy
thật, nên chạy được bất kỳ lúc nào, kể cả cuối tuần).

Chạy: python3 mike/agents/Taylor/exp_hybrid_fill_20260810/paper_rehearsal_hybrid.py
"""
import datetime as dt
import glob
import os
import sys

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")          # §5b — không ghi bus thật
_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", ".."))
sys.path.insert(0, _ROOT)

from trading_bot.brokers import PaperBroker                # noqa: E402
from trading_bot.config import DATA_DIR, DEFAULTS, EXEC_DIR  # noqa: E402
from trading_bot.executor import Executor                  # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan       # noqa: E402

TAG = "rehearsal-hybridft"
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(f)
_PAPER_STATE = os.path.join(DATA_DIR, f"bot_paper_{TAG}.json")
if os.path.exists(_PAPER_STATE):          # tài khoản ảo bền qua phiên → phải dựng lại sạch
    os.remove(_PAPER_STATE)

PX = 20_000.0
ORDERS = [
    PlannedOrder(id="B1", ticker="AAA", side="buy", qty=5000, ref_price=PX,
                 book="LAG", play_type="LAG_HI"),
    PlannedOrder(id="S1", ticker="BBB", side="sell", qty=4000, ref_price=PX,
                 book="BAL", play_type="PARK"),
]


class RehearsalBroker(PaperBroker):
    """PaperBroker thật + quote tĩnh (không có feed sống trong rehearsal)."""

    class Q:
        def __init__(self, sym):
            self.symbol = sym; self.exchange = "HOSE"
            self.last = self.ref = self.bid = self.ask = PX
            self.floor = PX * 0.93; self.ceiling = PX * 1.07
            self.day_volume = 5_000_000

        def ok(self):
            return True

    def get_quote(self, symbol):
        return self.Q(symbol)


def main():
    cfg = dict(DEFAULTS)
    cfg.update({"mode": "paper", "fill_timing_hybrid_enabled": True,
                "gap_adaptive_enabled": False, "extreme_regime_enabled": False})
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                     strategy_version="0", state=3, state_name="NEUTRAL", nav_basis={},
                     orders=ORDERS, account=TAG, created_at="2099-01-01T00:00:00")
    br = RehearsalBroker(init_cash=2_000_000_000, label=TAG).connect()
    br.state["positions"]["BBB"] = 4000        # có hàng để bán (tài khoản ảo dựng sạch ở trên)
    br._save()
    ex = Executor(plan, br, cfg)

    timeline = []
    t = dt.datetime(2099, 1, 1, 9, 0)
    end = dt.datetime(2099, 1, 1, 14, 30)
    while t <= end:
        phase = "MORNING" if t.time() < dt.time(11, 30) else "AFTERNOON"
        ex.step(t, phase, cont=True)
        for o in plan.orders:
            for c in ex.state["parents"][o.id]["children"]:
                key = (o.id, c["oid"])
                if key not in {(a, b) for a, b, _, _ in timeline}:
                    timeline.append((o.id, c["oid"], t.strftime("%H:%M"), c["qty"]))
        t += dt.timedelta(minutes=1)

    print(f"{'order':6} {'giờ đặt':8} {'KL':>7}")
    for oid, _c, hhmm, qty in timeline:
        print(f"{oid:6} {hhmm:8} {qty:7,}")

    # ---- kiểm tra ----
    fails = []
    jf = ex.journal_file
    jtxt = open(jf, encoding="utf-8").read() if os.path.exists(jf) else ""
    for bad in ("PLACE_FAIL", "NO_QUOTE", "WAIT_CASH", "WAIT_QUOTA", "WAIT_T2_SETTLEMENT"):
        n = jtxt.count(bad)
        print(f"  journal {bad}: {n}")
        if n:
            fails.append(f"{bad}×{n}")

    buy_blocks = {"11:00", "11:15", "13:00", "13:15", "13:30"}
    sell_blocks = {"09:15", "09:30", "09:45", "10:00"}
    b_times = [hhmm for oid, _c, hhmm, _q in timeline if oid == "B1"]
    s_times = [hhmm for oid, _c, hhmm, _q in timeline if oid == "S1"]
    b_qty = sum(q for oid, _c, _h, q in timeline if oid == "B1")
    s_qty = sum(q for oid, _c, _h, q in timeline if oid == "S1")

    def chk(name, cond, detail=""):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    chk("BUY: mọi lệnh con đặt ĐÚNG trong 5 block đã lên lịch",
        set(b_times) <= buy_blocks, f"{b_times}")
    chk("BUY: dùng đủ 5 block (trải, không gom)", len(set(b_times)) == 5, f"{sorted(set(b_times))}")
    chk("BUY: tổng KL đã đặt = KL lệnh", b_qty == 5000, f"{b_qty}")
    chk("SELL: mọi lệnh con đặt ĐÚNG trong 4 block đã lên lịch",
        set(s_times) <= sell_blocks, f"{s_times}")
    chk("SELL: dùng đủ 4 block (KHÔNG gom tại mở cửa)", len(set(s_times)) == 4,
        f"{sorted(set(s_times))}")
    chk("SELL: tổng KL đã đặt = KL lệnh", s_qty == 4000, f"{s_qty}")
    chk("mọi parent DONE cuối phiên",
        all(ex.state["parents"][o.id]["done"] for o in plan.orders))

    print("\n" + "=" * 56)
    if fails:
        print(f"❌ REHEARSAL FAIL: {fails}")
        return 1
    print("✅ REHEARSAL PASS — lệnh ra đúng lịch block, đủ KL, 0 reject")
    return 0


if __name__ == "__main__":
    sys.exit(main())
