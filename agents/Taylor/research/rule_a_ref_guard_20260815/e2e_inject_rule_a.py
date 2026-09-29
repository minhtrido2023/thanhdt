"""E2E OFFLINE: chuỗi inject → engine → lệnh, với `dynamic_ceiling.ceiling_rule = "A"`.

Việc 2, job Taylor_20260815_022340. Selfcheck đơn vị đã khoá từng mắt xích riêng
(`anchor_prices_for(with_dates=True)` ở G18, `resolve_price_band`/`compute_session_order` ở
`discretionary_rule_a_selfcheck.py`). Cái CHƯA ai khoá là 3 dòng NỐI chúng trong
`discretionary_accumulation_inject.py` — và đó đúng là chỗ đã hỏng thật: attempt 1 thêm tham số
`with_dates` cùng docstring nhưng KHÔNG return ngày và KHÔNG sửa caller, nên lật state sang
luật A sẽ ra fail-safe CÂM (trần rơi về band cố định 20.000, không ai được báo).

Test này chạy `process_account()` THẬT, offline hoàn toàn (broker/NAV/fill đều là stub, plan +
state ghi vào thư mục tạm), và đòi lệnh chèn ra mang ĐÚNG provenance luật A.
"""
import copy
import datetime as dt
import json
import os
import sys
import tempfile
from zoneinfo import ZoneInfo

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
import discretionary_accumulation_inject as inj          # noqa: E402
from trading_bot.no_chase_ceiling import resolve_buy_ceiling, rule_a_ceiling   # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
PLAN_DATE = "2026-08-17"
fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def bar_ts(y, m, d):
    return int(dt.datetime(y, m, d, 9, 0, tzinfo=ICT).timestamp())


# Nến TV1 THẬT tới 2026-08-14 (feed trả đơn vị NGHÌN — đúng hình dạng payload DNSE).
BARS = [("2026-08-10", 20.0), ("2026-08-11", 20.0), ("2026-08-12", 20.3),
        ("2026-08-13", 20.3), ("2026-08-14", 20.1)]
RAW = {"t": [bar_ts(*map(int, d.split("-"))) for d, _ in BARS],
       "c": [c for _, c in BARS],
       "o": [0] * 5, "h": [0] * 5, "l": [0] * 5, "v": [0] * 5}

STATE = {
    "ticker": "TV1", "account": "SpaceX", "status": "active", "lot_size": 100,
    "target_qty": 2300, "baseline_qty_before_program": 0,
    "price_band": {"resting_limit": 19900, "no_chase_ceiling": 20000,
                   "max_no_chase_ceiling": 25000},
    "adv_ref_vnd": 720_000_000, "per_session_cap_pct_adv": 0.1,
    "opportunistic": {"k": 2.0, "m": 2.0},
    "dynamic_ceiling": {"enabled": True, "tau": 0.03, "sessions": 5, "ceiling_rule": "A"},
    "ledger": [],
}


class _Client:
    def ohlc(self, symbol, resolution="1D", **q):
        return RAW


class _Broker:
    client = _Client()


def run_case(state, label):
    """→ order dict đã chèn vào plan (hoặc None), chạy process_account() thật."""
    tmp = tempfile.mkdtemp(prefix="rulea_e2e_")
    state_path = os.path.join(tmp, "state_TV1_SpaceX.json")
    json.dump(state, open(state_path, "w"), ensure_ascii=False)
    plan_path = os.path.join(tmp, f"plan_SpaceX_{PLAN_DATE}.json")
    json.dump({"plan_date": PLAN_DATE, "account": "SpaceX", "orders": []},
              open(plan_path, "w"), ensure_ascii=False)

    orig = {k: getattr(inj, k) for k in
            ("load_active_states", "broker_filled_qty", "prev_session_market",
             "load_active_nav", "gate_injected_order", "PLAN_DIR")}
    inj.load_active_states = lambda acc: ([(state_path, copy.deepcopy(state))], [])
    inj.broker_filled_qty = lambda *a, **k: (0, _Broker())
    inj.prev_session_market = lambda *a, **k: (1_500_000_000, 20_100.0)
    inj.load_active_nav = lambda *a, **k: (973_647_205.0, {"reason": "stub"})
    # Cổng tiền là mối quan tâm KHÁC (§P0) — trung hoà để test này chỉ nói về trần giá.
    # Chữ ký thật: (order, plan, broker, account_mode, lot_size) → (order|None, record).
    inj.gate_injected_order = lambda order, *a, **k: (
        order, {"action": "PASS", "reason": "stub — cổng tiền ngoài phạm vi test trần giá"})
    inj.PLAN_DIR = tmp
    try:
        # `now` thật: sau 14:45 ngày 08-14 ⇒ cả 5 bar đều là phiên ĐÃ ĐÓNG.
        rc = inj.process_account("SpaceX", PLAN_DATE, dry_run=False)
    finally:
        for k, v in orig.items():
            setattr(inj, k, v)
    plan = json.load(open(plan_path))
    orders = [o for o in plan.get("orders", []) if o.get("ticker") == "TV1"]
    print(f"    [{label}] rc={rc}, {len(orders)} lệnh TV1")
    return orders[0] if orders else None


print(__doc__.splitlines()[0])
print("=" * 78)

print("\n1. state BẬT luật A ⇒ lệnh phải mang provenance và trần neo phiên 08-14")
o_a = run_case(STATE, "rule_a")
check("E2E-1 có lệnh được chèn", isinstance(o_a, dict))
if isinstance(o_a, dict):
    expect = int(rule_a_ceiling(20_100.0, 0.03)[0])       # close 08-14 = 20.100 → 20.703
    check("E2E-2 trần = floor(close 2026-08-14 × 1,03) = 20.703",
          int(o_a["hard_no_chase_ceiling_vnd"]) == expect == 20_703,
          f"{o_a['hard_no_chase_ceiling_vnd']}")
    check("E2E-3 provenance khai ĐÚNG phiên đã đóng gần nhất (08-14), KHÔNG phải mean-5",
          o_a.get("ceiling_rule") == "A" and o_a.get("ceiling_anchor_date") == "2026-08-14"
          and float(o_a.get("ceiling_anchor_price")) == 20_100.0,
          f"{o_a.get('ceiling_rule')}/{o_a.get('ceiling_anchor_date')}/"
          f"{o_a.get('ceiling_anchor_price')}")
    c_rt, i_rt = resolve_buy_ceiling(dict(o_a, side="buy"), plan_date=PLAN_DATE)
    check("E2E-4 load_plan (resolve_buy_ceiling) TÁI LẬP đúng trần — KHÔNG fail-closed",
          i_rt.get("mode") == "rule_a" and int(c_rt) == expect, f"{i_rt.get('mode')}/{c_rt}")
    # ĐÂY là bài test bắt được lỗi thật của attempt 1: nếu 3 dòng nối ở inject.py chưa wire,
    # engine fail-safe câm và trần rơi về 20.000 — lệnh vẫn ra, vẫn trông hợp lệ.
    check("E2E-5 KHÔNG rơi về band cố định 20.000 (fail-safe CÂM — lỗi thật của attempt 1)",
          int(o_a["hard_no_chase_ceiling_vnd"]) != 20_000)

print("\n2. state KHÔNG khai ceiling_rule ⇒ mean-5 y như hôm nay (đối chứng)")
st_old = copy.deepcopy(STATE)
st_old["dynamic_ceiling"].pop("ceiling_rule")
o_o = run_case(st_old, "mean-5")
check("E2E-6 có lệnh được chèn", isinstance(o_o, dict))
if isinstance(o_o, dict):
    mean5 = sum(c for _, c in BARS) / len(BARS) * 1000.0        # 20.140
    check("E2E-7 trần = floor(mean5 × 1,03) = 20.744 (đúng trần plan LIVE 08-17 thật)",
          int(o_o["hard_no_chase_ceiling_vnd"]) == int(mean5 * 1.03) == 20_744,
          f"{o_o['hard_no_chase_ceiling_vnd']}")
    check("E2E-8 KHÔNG mang nhãn luật A (nhánh cũ sạch, không provenance rơi vãi)",
          "ceiling_rule" not in o_o,
          f"{[k for k in o_o if k.startswith('ceiling_')]}")
    check("E2E-9 luật A CAO hơn mean-5 đúng chênh lệch đã báo cáo",
          isinstance(o_a, dict)
          and int(o_a["hard_no_chase_ceiling_vnd"]) - int(o_o["hard_no_chase_ceiling_vnd"]) == -41,
          f"{int(o_a['hard_no_chase_ceiling_vnd']) - int(o_o['hard_no_chase_ceiling_vnd']):+}đ "
          f"(08-17: giá đóng cuối THẤP hơn mean-5 ⇒ luật A siết, đúng tính đối xứng)")

print("\n" + "=" * 78)
if fails:
    print(f"❌ FAIL {len(fails)}: {fails}")
    sys.exit(1)
print("✅ ALL PASS — chuỗi inject→engine→lệnh chạy đúng luật A end-to-end (offline).")
