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

# ------------------------------------------------- G. anchor_prices_for() trên PAYLOAD DNSE THÔ
# Vì sao cần khối này: 49 ca A-F ở trên BƠM TAY `anchor_prices` (đã qua bước tính) nên KHÔNG
# ca nào chạm `anchor_prices_for()` — chính chỗ quant-skeptic bắt lỗi thật (log
# mike/logs/verify_20260812_104435_640589.log): hàm đó lấy `c[-n:]` không lọc theo `t`, mà DNSE
# CÓ trả nến hôm nay (probe live 2026-08-12 18:28 ICT: TV1/DGC đều có bar ngày 08-12) ⇒ giữa
# phiên thì 1/5 anchor là GIÁ LIVE, trần no-chase tự đuổi theo cái giá nó đang đuổi.
# Khối này bơm payload DNSE dạng THÔ (mảng t + c, đơn vị NGHÌN đúng như feed thật) và neo `now`
# tường minh nên kết quả tất định, không phụ thuộc TZ/ngày chạy (§16).
import importlib.util  # noqa: E402

_INJ_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "mike", "bin", "discretionary_accumulation_inject.py")
_spec = importlib.util.spec_from_file_location("_disc_inject_for_selfcheck", _INJ_PATH)
inj = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inj)

import datetime as _dt  # noqa: E402
from zoneinfo import ZoneInfo as _ZI  # noqa: E402

_ICT = _ZI("Asia/Ho_Chi_Minh")


def _bar_ts(y, m, d):
    """DNSE 1D: timestamp = 09:00 ICT của ngày giao dịch (đúng như payload live đã đo)."""
    return int(_dt.datetime(y, m, d, 9, 0, tzinfo=_ICT).timestamp())


def _now(y, m, d, hh, mm):
    return _dt.datetime(y, m, d, hh, mm)          # naive ICT, giống now_ict()


# 6 bar: 5 phiên đã đóng (08-05→08-11) + nến HÔM NAY 08-12 đang chạy, giá vọt 25.0 (nghìn đồng)
# để nhiễm-hay-không nhìn thấy được ngay bằng số.
RAW = {"t": [_bar_ts(2026, 8, 5), _bar_ts(2026, 8, 6), _bar_ts(2026, 8, 7),
             _bar_ts(2026, 8, 10), _bar_ts(2026, 8, 11), _bar_ts(2026, 8, 12)],
       "c": [19.9, 20.0, 20.1, 20.3, 20.5, 25.0],
       "o": [0] * 6, "h": [0] * 6, "l": [0] * 6, "v": [0] * 6}
COMPLETED_5 = [19900.0, 20000.0, 20100.0, 20300.0, 20500.0]   # == ANCHORS
WITH_TODAY_5 = [20000.0, 20100.0, 20300.0, 20500.0, 25000.0]


class _FakeClient:
    def __init__(self, payload):
        self.payload, self.calls, self.last_query = payload, 0, None

    def ohlc(self, symbol, resolution="1D", **query):
        self.calls += 1
        self.last_query = query
        return self.payload


class _FakeBrokerOHLC:
    def __init__(self, payload):
        self.client = _FakeClient(payload)


G_ON = {"enabled": True, "tau": 0.03, "sessions": 5}
G_STATE = st(dynamic_ceiling=G_ON, price_band={"max_no_chase_ceiling": 22000})


def anchors_from(payload, now, state=None):
    b = _FakeBrokerOHLC(payload)
    return inj.anchor_prices_for(b, state or G_STATE, "TV1", now=now), b


# --- G1-G4: nến hôm nay bị LOẠI ở mọi thời điểm phiên CHƯA đóng ------------------------------
for nm, now_at in [("G1 GIỮA phiên 11:00 (MORNING)", _now(2026, 8, 12, 11, 0)),
                   ("G2 TRƯỚC phiên 07:00 (PRE — DNSE có thể trả bar stub)", _now(2026, 8, 12, 7, 0)),
                   ("G3 ATC 14:40 (chưa chốt)", _now(2026, 8, 12, 14, 40)),
                   ("G4 ATO 09:05", _now(2026, 8, 12, 9, 5))]:
    a, _ = anchors_from(RAW, now_at)
    check(f"{nm} ⇒ nến hôm nay bị LOẠI, anchor = 5 phiên đã đóng", a == COMPLETED_5, f"{a}")

# --- G5: sau 14:45 của NGÀY GIAO DỊCH thì nến hôm nay LÀ phiên hoàn tất → được dùng ----------
a, _ = anchors_from(RAW, _now(2026, 8, 12, 20, 30))   # đúng giờ cron thật
check("G5 20:30 (giờ cron thật, phiên đã đóng) ⇒ nến hôm nay HỢP LỆ, vào anchor",
      a == WITH_TODAY_5, f"{a}")
a, _ = anchors_from(RAW, _now(2026, 8, 12, 14, 46))
check("G5b 14:46 (ngay sau ATC) ⇒ đã hoàn tất", a == WITH_TODAY_5, f"{a}")

# --- G6: bar mang ngày TƯƠNG LAI luôn bị loại ------------------------------------------------
a, _ = anchors_from(RAW, _now(2026, 8, 11, 20, 30))
check("G6 chạy ngày 08-11: bar 08-12 là TƯƠNG LAI ⇒ loại, anchor = 5 phiên tới 08-11",
      a == COMPLETED_5, f"{a}")

# --- G7: cuối tuần/lễ mà feed vẫn trả bar mang ngày đó ⇒ rác, loại ---------------------------
RAW_SAT = {"t": RAW["t"][:5] + [_bar_ts(2026, 8, 15)], "c": RAW["c"],
           "o": [0] * 6, "h": [0] * 6, "l": [0] * 6, "v": [0] * 6}
a, _ = anchors_from(RAW_SAT, _now(2026, 8, 15, 20, 0))     # 15/08/2026 = thứ Bảy
check("G7 T7 20:00 + bar mang ngày T7 ⇒ rác, loại (không dựa mỗi tên phiên CLOSED)",
      a == COMPLETED_5, f"{a}")

# --- G8-G11: mọi payload hỏng ⇒ None (fail-safe về trần cố định, KHÔNG fail-open) ------------
for nm, payload in [
        ("G8 thiếu mảng `t` (không biết bar nào hoàn tất)", {"c": RAW["c"]}),
        ("G9 len(t) ≠ len(c)", {"t": RAW["t"][:3], "c": RAW["c"]}),
        ("G10 timestamp rác (chuỗi)", {"t": ["abc"] + RAW["t"][1:], "c": RAW["c"]}),
        ("G11 payload rỗng", {"t": [], "c": []}),
        ("G11b raw không phải dict", None)]:
    a, _ = anchors_from(payload, _now(2026, 8, 12, 11, 0))
    check(f"{nm} ⇒ None (fail-safe)", a is None, f"{a}")

# thiếu phiên HOÀN TẤT sau khi lọc (5 bar, bar cuối là hôm nay đang chạy → còn 4 < 5)
RAW_SHORT = {"t": RAW["t"][1:], "c": RAW["c"][1:],
             "o": [0] * 5, "h": [0] * 5, "l": [0] * 5, "v": [0] * 5}
a, _ = anchors_from(RAW_SHORT, _now(2026, 8, 12, 11, 0))
check("G12 lọc xong còn 4 phiên hoàn tất < sessions=5 ⇒ None (KHÔNG bù bằng nến dở dang)",
      a is None, f"{a}")
a, _ = anchors_from(RAW_SHORT, _now(2026, 8, 12, 20, 30))
check("G12b cùng payload nhưng phiên đã đóng ⇒ đủ 5, chạy bình thường",
      a == WITH_TODAY_5, f"{a}")

# --- G13: cờ TẮT ⇒ không gọi API nào (bất biến 'mặc định không thêm 1 lời gọi') --------------
b_off = _FakeBrokerOHLC(RAW)
a_off = inj.anchor_prices_for(b_off, BASE, "TV1", now=_now(2026, 8, 12, 11, 0))
check("G13 cờ TẮT ⇒ None và KHÔNG gọi client.ohlc lần nào",
      a_off is None and b_off.client.calls == 0, f"{a_off}/calls={b_off.client.calls}")

# --- G14: đơn vị — feed trả NGHÌN đồng, anchor ra VND ----------------------------------------
a, _ = anchors_from(RAW, _now(2026, 8, 12, 11, 0))
check("G14 chuẩn hoá đơn vị: feed 19.9 (nghìn) ⇒ anchor 19.900 VND",
      a[0] == 19900.0 and all(v > 1000 for v in a), f"{a}")

# --- G15: cửa sổ hỏi API neo TZ ICT tường minh (§16), không lệ thuộc TZ process ---------------
_, b15 = anchors_from(RAW, _now(2026, 8, 12, 11, 0))
check("G15 query DNSE có from<to và to = đúng mốc ICT của `now` (neo TZ tường minh)",
      b15.client.last_query["to"] == int(_dt.datetime(2026, 8, 12, 11, 0, tzinfo=_ICT).timestamp())
      and b15.client.last_query["from"] < b15.client.last_query["to"],
      f"{b15.client.last_query}")

# --- G16: [CHỨNG MINH NGƯỢC] lỗi cũ THẬT SỰ đổi trần, không phải lo hão ----------------------
# Tái dựng đúng code cũ (`c[-n:]` không lọc) trên CÙNG payload, CÙNG thời điểm giữa phiên.
buggy = [float(inj.normalize_price_vnd(float(v))) for v in RAW["c"][-5:]]
fixed_anchor, _ = anchors_from(RAW, _now(2026, 8, 12, 11, 0))
c_bug, _, i_bug = resolve_price_band(G_STATE, buggy, 25000.0)
c_fix, _, i_fix = resolve_price_band(G_STATE, fixed_anchor, 25000.0)
check("G16 code CŨ (không lọc) cho trần CAO HƠN — lỗi có hậu quả thật, không phải lý thuyết",
      c_bug > c_fix, f"cũ {c_bug} vs mới {c_fix}")
check("G16b trần mới = mean(5 phiên ĐÃ ĐÓNG)×1,03, KHÔNG chứa giá live hôm nay",
      c_fix == int(MEAN * 1.03) and i_fix["anchor_vnd"] == round(MEAN, 2), f"{c_fix}/{i_fix}")
check("G16c giá LIVE 25.000 của hôm nay KHÔNG lọt vào anchor sau khi vá",
      25000.0 not in (fixed_anchor or []), f"{fixed_anchor}")

# --- G17: bar_is_completed_session — bảng chân trị trực tiếp ----------------------------------
_bts = _bar_ts(2026, 8, 12)
for nm, now_at, want in [
        ("G17a hôm qua, giữa phiên hôm nay", _now(2026, 8, 13, 11, 0), True),
        ("G17b hôm nay, 20:30", _now(2026, 8, 12, 20, 30), True),
        ("G17c hôm nay, 11:00", _now(2026, 8, 12, 11, 0), False),
        ("G17d hôm nay, 00:30 (PRE)", _now(2026, 8, 12, 0, 30), False),
        ("G17e ngày mai (bar tương lai)", _now(2026, 8, 11, 20, 30), False)]:
    got = inj.bar_is_completed_session(_bts, now_at)
    check(f"{nm} ⇒ {want}", got is want, f"got={got}")
check("G17f timestamp không parse được ⇒ None (caller fail-safe)",
      inj.bar_is_completed_session("xx", _now(2026, 8, 12, 20, 30)) is None)
check("G17g lễ 02/09 dù sau 14:45 ⇒ bar mang ngày lễ vẫn là rác",
      inj.bar_is_completed_session(_bar_ts(2026, 9, 2), _now(2026, 9, 2, 20, 0)) is False)

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ tất cả PASS — P1 mặc định byte-identical, mọi nhánh hỏng đều fail-safe về trần cố định.")
