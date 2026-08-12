# -*- coding: utf-8 -*-
"""Self-check P1 — trần no-chase ĐỘNG (`anchor × (1+τ)`) trong discretionary_accumulation.py.

Context (job Taylor_20260812_095213, nghiên cứu Taylor_20260812_091343): trần cố định 20.000đ
duyệt 2026-07-23 cho TV1 hết đúng từ 2026-08-11 khi giá lên 20.200-20.500 ⇒ 0cp khớp dưới trần
trên tổng 39.500cp phiên 08-12. Không cơ chế nào phát hiện.

BẤT BIẾN của file này (§24 coding_guidelines — trần cứng vẫn là lưới an toàn cuối):
  • MẶC ĐỊNH TẮT ⇒ band giá và order sinh ra PHẢI byte-identical với trước.
  • Không có đường nào FAIL-OPEN: thiếu cờ / thiếu cận trên tuyệt đối / thiếu-rác giá anchor /
    τ ngoài dải ⇒ rơi về band CỐ ĐỊNH, không bao giờ rơi về "không có trần".
  • resting_limit ≤ no_chase_ceiling trong MỌI nhánh (bất biến no-chase).
  • Mọi ca "trần động mở khoá được lệnh" đều có CA CHỨNG MINH NGƯỢC: bỏ trần động ra thì
    executor THẬT SỰ không đặt được lệnh nào (`_limit_price` trả None).

Run: /home/trido/thanhdt/wc_venv/bin/python dynamic_no_chase_ceiling_selfcheck.py  (exit 0 = pass)
"""
import copy
import os
import sys

# §5b: bất kỳ selfcheck nào chạm Executor phải chặn `_publish_bot_event` ghi lên bus THẬT.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.discretionary_accumulation import (  # noqa: E402
    compute_session_order, resolve_price_band, validate_state,
    DYNAMIC_CEILING_TAU_DEFAULT, DYNAMIC_CEILING_TAU_MAX)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


# State TV1 THẬT (data/trade_plans/discretionary/state_TV1_SpaceX.json, rút gọn phần engine đọc).
BASE = {
    "ticker": "TV1", "account": "SpaceX", "status": "active", "lot_size": 100,
    "target_qty": 2000, "baseline_qty_before_program": 0,
    "price_band": {"resting_limit": 19900, "no_chase_ceiling": 20000},
    "adv_ref_vnd": 701_000_000, "per_session_cap_pct_adv": 0.1,
    "opportunistic": {"k": 2.0, "m": 2.0},
}
# Giá 5 phiên gần nhất của TV1 quanh 08-12 (đơn vị VND, cũ→mới) — dùng làm anchor.
ANCHORS = [19900.0, 20000.0, 20100.0, 20300.0, 20500.0]     # mean = 20.160
MEAN = sum(ANCHORS) / len(ANCHORS)


def st(**over):
    s = copy.deepcopy(BASE)
    for k, v in over.items():
        if k == "price_band":
            s["price_band"].update(v)
        else:
            s[k] = v
    return s


def band(state, anchors=ANCHORS, latest=20500.0):
    return resolve_price_band(state, anchors, latest)


# ---------------------------------------------------------------- A. MẶC ĐỊNH = hành vi cũ
c, r, info = resolve_price_band(BASE)                       # không truyền anchor gì cả
check("A1 mặc định (không anchor, không cờ): trần = band cố định",
      (c, r) == (20000.0, 19900.0) and info["mode"] == "fixed", f"{c}/{r}/{info['mode']}")
c, r, info = band(BASE)                                     # có anchor nhưng KHÔNG bật cờ
check("A2 có anchor nhưng cờ TẮT: vẫn band cố định (cờ là điều kiện cần)",
      (c, r) == (20000.0, 19900.0) and info["mode"] == "fixed", f"{c}/{r}")

o_off, d_off = compute_session_order(BASE, 0, 1_500_000_000, 20500, "2099-01-01", "2099-01-01T00:00:00")
o_ref, d_ref = compute_session_order(BASE, 0, 1_500_000_000, 20500, "2099-01-01", "2099-01-01T00:00:00",
                                     anchor_prices=ANCHORS)
check("A3 order sinh ra GIỐNG HỆT khi truyền/không truyền anchor lúc cờ tắt",
      o_off == o_ref, "khác nhau!" if o_off != o_ref else "")
check("A4 order mặc định giữ đúng trần cũ 20.000 / ref 19.900",
      o_off["hard_no_chase_ceiling_vnd"] == 20000 and o_off["ref_price"] == 19900,
      f"{o_off['hard_no_chase_ceiling_vnd']}/{o_off['ref_price']}")

# ---------------------------------------------------------------- B. BẬT nhưng thiếu điều kiện
ON = {"enabled": True, "tau": 0.03, "sessions": 5}
c, r, info = band(st(dynamic_ceiling=ON))
check("B1 bật cờ nhưng THIẾU price_band.max_no_chase_ceiling ⇒ fail-safe band cố định",
      (c, r) == (20000.0, 19900.0) and info["mode"] == "fixed_failsafe",
      info.get("reason", ""))

CAPPED = st(dynamic_ceiling=ON, price_band={"max_no_chase_ceiling": 22000})
for nm, anchors, latest in [
        ("B2 chỉ 4 giá anchor (cần 5)", ANCHORS[:4], 20500.0),
        ("B3 anchor có phần tử None", [19900, None, 20100, 20300, 20500], 20500.0),
        ("B4 anchor có phần tử ≤0", [19900, 0, 20100, 20300, 20500], 20500.0),
        ("B5 anchor sai ĐƠN VỊ (nghìn đồng)", [19.9, 20.0, 20.1, 20.3, 20.5], 20500.0),
        ("B6 anchor lệch >2× giá mới nhất", [19900, 20000, 20100, 20300, 99000], 20500.0),
        ("B7 anchor rỗng", [], 20500.0),
        ("B8 anchor toàn bool (isinstance(True,int) là bẫy thật)", [True] * 5, 20500.0)]:
    c, r, info = resolve_price_band(CAPPED, anchors, latest)
    check(f"{nm} ⇒ fail-safe band cố định",
          (c, r) == (20000.0, 19900.0) and info["mode"] == "fixed_failsafe", info.get("reason", ""))

for nm, tau in [("B9 tau=0", 0), ("B10 tau âm", -0.03), ("B11 tau>10%", 0.5),
                ("B12 tau chuỗi", "3%"), ("B13 tau=True", True)]:
    c, r, info = band(st(dynamic_ceiling={"enabled": True, "tau": tau},
                         price_band={"max_no_chase_ceiling": 22000}))
    check(f"{nm} ⇒ fail-safe band cố định", (c, r) == (20000.0, 19900.0), f"{c}/{r}")

for nm, n in [("B14 sessions=0", 0), ("B15 sessions=99", 99), ("B16 sessions=2.5", 2.5)]:
    c, r, info = band(st(dynamic_ceiling={"enabled": True, "tau": 0.03, "sessions": n},
                         price_band={"max_no_chase_ceiling": 22000}))
    check(f"{nm} ⇒ fail-safe band cố định", (c, r) == (20000.0, 19900.0), f"{c}/{r}")

for nm, val in [("B17 max cap = 0", 0), ("B18 max cap âm", -1), ("B19 max cap chuỗi", "22000"),
                ("B20 max cap = True", True)]:
    c, r, info = band(st(dynamic_ceiling=ON, price_band={"max_no_chase_ceiling": val}))
    check(f"{nm} ⇒ fail-safe band cố định", (c, r) == (20000.0, 19900.0), f"{c}/{r}")

c, r, info = band(st(dynamic_ceiling={"enabled": "yes", "tau": 0.03},
                     price_band={"max_no_chase_ceiling": 22000}))
check("B21 enabled='yes' (truthy nhưng KHÔNG phải True) ⇒ vẫn TẮT — cờ phải là bool True",
      (c, r) == (20000.0, 19900.0) and info["mode"] == "fixed", info.get("reason", ""))

# ---------------------------------------------------------------- C. Trần động ăn — số học đúng
S = st(dynamic_ceiling=ON, price_band={"max_no_chase_ceiling": 22000})
c, r, info = band(S)
exp_c = int(MEAN * 1.03)                        # 20.764
exp_r = int(min(c, 19900 * c / 20000))          # kéo theo cùng tỉ lệ
check("C1 trần động = floor(mean(5 phiên) × 1,03)", c == exp_c, f"{c} vs {exp_c}")
check("C2 resting kéo theo ĐÚNG tỉ lệ band đã duyệt (19.900/20.000)", r == exp_r, f"{r} vs {exp_r}")
check("C3 resting ≤ trần (bất biến no-chase)", r <= c, f"{r}/{c}")
check("C4 trần động CAO HƠN trần cố định trong ca TV1 (nếu không thì P1 vô nghĩa)",
      c > 20000, f"{c}")
check("C5 info khai báo đủ để audit", info["mode"] == "dynamic" and info["anchor_vnd"] == round(MEAN, 2)
      and info["tau"] == 0.03 and info["sessions"] == 5 and not info["capped_by_max"], f"{info}")

# cận trên tuyệt đối phải CẮT
c2, r2, info2 = band(st(dynamic_ceiling=ON, price_band={"max_no_chase_ceiling": 20300}))
check("C6 cận trên tuyệt đối user duyệt CẮT trần động", c2 == 20300 and info2["capped_by_max"] is True,
      f"{c2}")
check("C7 bị cắt thì resting cũng theo (≤ trần)", r2 <= c2, f"{r2}/{c2}")

# luật ĐỐI XỨNG: anchor đi xuống thì trần HẠ
low = [18000.0, 18100.0, 18000.0, 17900.0, 18000.0]
c3, r3, info3 = resolve_price_band(S, low, 18000.0)
check("C8 anchor đi XUỐNG ⇒ trần HẠ (luật đối xứng, mua rẻ hơn — không phải lỗi)",
      c3 < 20000 and info3["mode"] == "dynamic", f"{c3}")
check("C9 hạ trần vẫn giữ resting ≤ trần", r3 <= c3, f"{r3}/{c3}")

# chỉ N phần tử CUỐI được dùng
c4, _, info4 = resolve_price_band(S, [1e9] + ANCHORS, 20500.0)   # phần tử rác ở ĐẦU, ngoài cửa sổ
check("C10 chỉ `sessions` phần tử CUỐI được dùng (phần tử cũ ngoài cửa sổ không ảnh hưởng)",
      c4 == exp_c, f"{c4} vs {exp_c}")

# ---------------------------------------------------------------- D. Order sinh ra khi bật
o_on, d_on = compute_session_order(S, 0, 1_500_000_000, 20500, "2099-01-01",
                                   "2099-01-01T00:00:00", anchor_prices=ANCHORS)
check("D1 order mang trần ĐỘNG", o_on["hard_no_chase_ceiling_vnd"] == exp_c,
      f"{o_on['hard_no_chase_ceiling_vnd']}")
check("D2 ref_price = resting động (executor tính cap = ref×(1+chase) nên KHÔNG được để đứng yên)",
      o_on["ref_price"] == exp_r, f"{o_on['ref_price']}")
check("D3 ref_price ≤ trần trong order thật", o_on["ref_price"] <= o_on["hard_no_chase_ceiling_vnd"])
check("D4 decision ghi lại luật để audit",
      d_on["price_band_rule"]["mode"] == "dynamic"
      and o_on["accumulation_program"]["price_band_rule"]["mode"] == "dynamic")
check("D5 note công bố trần động cho người đọc plan", "TRẦN ĐỘNG" in o_on["note"])
check("D6 qty vẫn tuân cap %ADV (P1 KHÔNG được đụng sizing)",
      o_on["qty"] == o_ref["qty"] or o_on["qty"] > 0, f"{o_on['qty']} vs {o_ref['qty']}")

# ---------------------------------------------------------------- E. validate_state không đổi
def raises_value_error(fn):
    try:
        fn()
        return False
    except ValueError:
        return True


check("E1 validate_state vẫn chặn resting > ceiling (bất biến cũ nguyên vẹn)",
      raises_value_error(lambda: validate_state(st(price_band={"resting_limit": 21000}))))
check("E2 state TV1 thật vẫn hợp lệ", validate_state(BASE) is True)
check("E3 validate_state KHÔNG biết gì về trần động (nó chỉ gác band cố định đã duyệt)",
      validate_state(st(dynamic_ceiling=ON, price_band={"max_no_chase_ceiling": 22000})) is True)

# ---------------------------------------------------------------- F. CHỨNG MINH NGƯỢC ở executor
# Không đủ nếu chỉ nói "trần cao hơn". Phải chứng minh: với trần CỐ ĐỊNH, executor THẬT SỰ
# không đặt được lệnh trong đúng điều kiện thị trường 2026-08-12 (ask 20.300, sàn/trần phiên
# quanh đó) — và với trần ĐỘNG thì đặt được, mà vẫn KHÔNG BAO GIỜ vượt trần.
from trading_bot.plan import PlannedOrder, TradePlan  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.config import load_config  # noqa: E402


class Q:
    def __init__(self, last, bid, ask, ceiling, floor):
        self.last, self.bid, self.ask = last, bid, ask
        self.ceiling, self.floor, self.exchange = ceiling, floor, "UPCOM"
        self.ref, self.day_volume, self.symbol = last, 39500, "TV1"

    def ok(self):
        return True


class _NullBroker:
    name = "null"

    def get_quote(self, *a, **k):
        raise AssertionError("không dùng broker trong test này")


def _px(hard, ref):
    o = PlannedOrder(id="F", ticker="TV1", side="buy", qty=2000, ref_price=ref,
                     book="DISCRETIONARY_SPECIAL", hard_no_chase_ceiling_vnd=hard)
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=[o],
                     account="selfcheck-p1-ceiling", created_at="2099-01-01T00:00:00")
    cfg = load_config()
    cfg["mode"] = "paper"
    ex = Executor(plan, _NullBroker(), cfg, shared={})
    # Thị trường 2026-08-12: giá chạy 20.200-20.500, sàn phiên đã trên trần cũ 20.000.
    return ex._limit_price(o, Q(last=20300, bid=20200, ask=20300, ceiling=23000, floor=20100),
                           cross=True), o


px_fixed, _ = _px(20000, 19900)
px_dyn, o_dyn = _px(exp_c, exp_r)
check("F1 [CHỨNG MINH NGƯỢC] trần CỐ ĐỊNH 20.000 ⇒ executor KHÔNG đặt được lệnh nào (None) "
      "— đúng chữ ký thất bại thật 08-12", px_fixed is None, f"px={px_fixed}")
check("F2 trần ĐỘNG ⇒ đặt được lệnh", px_dyn is not None and px_dyn > 0, f"px={px_dyn}")
check("F3 giá đặt KHÔNG BAO GIỜ vượt trần động (lưới an toàn §24 còn nguyên)",
      px_dyn is not None and px_dyn <= exp_c, f"px={px_dyn} vs trần {exp_c}")
check("F4 giá đặt cũng ≤ ref×(1+chase) — P1 KHÔNG đụng logic đuổi giá",
      px_dyn is not None and px_dyn <= exp_r * 1.041, f"px={px_dyn}, ref={exp_r}")

# Trần động cao nhưng THỊ TRƯỜNG còn cao hơn nữa ⇒ vẫn phải từ chối đặt (không đuổi vô hạn).
o2 = PlannedOrder(id="G", ticker="TV1", side="buy", qty=2000, ref_price=exp_r,
                  book="DISCRETIONARY_SPECIAL", hard_no_chase_ceiling_vnd=exp_c)
plan2 = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                  strategy_version="0", state=3, state_name="NEUTRAL",
                  nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=[o2],
                  account="selfcheck-p1-ceiling2", created_at="2099-01-01T00:00:00")
cfg2 = load_config()
cfg2["mode"] = "paper"
ex2 = Executor(plan2, _NullBroker(), cfg2, shared={})
px_far = ex2._limit_price(o2, Q(last=25000, bid=24900, ask=25000, ceiling=27000, floor=24800),
                          cross=True)
check("F5 thị trường vượt CẢ trần động ⇒ vẫn KHÔNG đặt (thà lỡ phiên còn hơn mua trên trần)",
      px_far is None, f"px={px_far}")

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ tất cả PASS — P1 mặc định byte-identical, mọi nhánh hỏng đều fail-safe về trần cố định.")
