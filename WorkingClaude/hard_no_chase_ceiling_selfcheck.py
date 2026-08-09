# -*- coding: utf-8 -*-
"""Self-check cho TRẦN GIÁ MUA TUYỆT ĐỐI `PlannedOrder.hard_no_chase_ceiling_vnd`.

Cơ chế cần chứng minh (dispatch Taylor_20260809_123917, luật entry-window LAG V2.4):
lệnh mua BÁM giá đang chào thật trên thị trường (q.ask, đọc lại mỗi chu kỳ) NHƯNG
KHÔNG BAO GIỜ đặt trên `hard_no_chase_ceiling_vnd` (= entry_anchor_price), ở MỌI bước.

Ca kiểm (§4 của dispatch):
  A. Regression — không đặt trần → hành vi CŨ nguyên vẹn (buy + sell).
  B. Giá thị trường DƯỚI trần → đặt BÁM giá chào thật, KHÔNG neo ngược xuống xa.
  C. Giá thị trường TRÊN trần → giá đặt clamp đúng tại trần (không thể khớp trên trần).
  D. Trần thắng cả khi trần đuổi % (kể cả chase_cap_vol_scale nới tay) muốn vượt.
  E. Sàn phiên đã > trần → KHÔNG đặt lệnh (None), có journal HARD_CEILING_BLOCK.
  F. ATC-remainder-buy bật → lệnh có trần KHÔNG đi đường ATC (ATC không đặt được giá).
  G. "Slide": ask đổi qua từng chu kỳ → giá đặt đổi theo, luôn ≤ trần.
  H. Trần không rò sang lệnh BÁN; giá trị rác → fail-safe về hành vi cũ.

Chạy: python hard_no_chase_ceiling_selfcheck.py   (exit 0 = pass)
"""
import datetime as dt
import glob
import os
import sys

# §5b coding_guidelines: chặn _publish_bot_event ghi lên bus THẬT — phải đặt TRƯỚC
# khi bất kỳ Executor nào được dựng.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

from trading_bot.config import DEFAULTS, EXEC_DIR          # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan       # noqa: E402
from trading_bot.executor import Executor                  # noqa: E402

# Executor.__init__ nạp state.json theo (account, plan_date) mặc định TRƯỚC khi test kịp
# đổi hướng — file cũ cùng tag làm hỏng state khởi đầu (xem ghost_order_selfcheck.py TAG).
TAG = "selfcheck-hardceiling"
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(_f)

# Dựng đúng ca thật DRI 2026-08-10: UPCOM (tick 100đ), anchor 13.000đ, thị trường 13.100–13.200.
SYM = "DRI"
ANCHOR = 13_000.0
REF_CLOSE = 13_000.0          # ref_price = giá tham chiếu THẬT (không còn neo anchor/1,04)
FLOOR = 11_900.0              # sàn UPCOM −15% quanh ref (chỉ cần < anchor cho ca thường)
CEIL_BAND = 14_900.0


class FakeQuote:
    def __init__(self, last, bid, ask, floor=FLOOR, ceiling=CEIL_BAND,
                 exchange="UPCOM", day_volume=3_000_000):
        self.symbol = SYM; self.exchange = exchange
        self.last = last; self.ref = REF_CLOSE; self.bid = bid; self.ask = ask
        self.floor = floor; self.ceiling = ceiling; self.day_volume = day_volume

    def ok(self):
        return self.last is not None or self.ref is not None


class FakeBroker:
    name = "fake"

    def __init__(self, quote):
        self.quote = quote; self.placed = []; self._oid = 0
        self.cash = 10_000_000_000

    def get_quote(self, sym):
        return self.quote

    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        self._oid += 1
        self.placed.append(dict(symbol=symbol, qty=qty, side=side, price=price,
                                type=order_type))
        return f"OID{self._oid}"

    def cancel_order(self, oid):
        pass

    def poll_orders(self):
        return {}

    def get_cash(self):
        return self.cash

    def get_max_buy_qty(self, symbol, price, loan_package_id=None):
        return 1_000_000


def make_exec(orders, quote, cfg_over=None):
    cfg = dict(DEFAULTS); cfg.update(cfg_over or {}); cfg["mode"] = "paper"
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account=TAG,
                     created_at="2099-01-01T00:00:00")
    ex = Executor(plan, FakeBroker(quote), cfg)
    # `chase_cap_vol_scale_enabled` mặc định True ⇒ __init__ nạp rvol_20d THẬT của mã từ
    # cache BQ local. Đo 2026-08-09: DRI rvol=0,0153 ⇒ trần đuổi 3,06% chứ không phải 1,5%
    # — số này ĐỔI theo ngày, để nguyên thì test tự vô hiệu theo thời gian (§23 hệ luận 1:
    # selfcheck không assert lên trạng thái SỐNG). Xoá cache, ca nào cần thì tự bơm vào.
    ex._gap_ref.clear()
    return ex


def buy_order(ceiling=None, ref=REF_CLOSE, qty=3000, oid="BUY-DRI-LAG-01"):
    return PlannedOrder(id=oid, ticker=SYM, side="buy", qty=qty, ref_price=ref,
                        book="LAG", play_type="LAG_HI",
                        hard_no_chase_ceiling_vnd=ceiling)


fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


NOW = dt.datetime(2099, 1, 1, 9, 30, 0)

# ───────────────────────────────────── A. Regression: không trần → hành vi CŨ
print("A. Không đặt trần → hành vi cũ nguyên vẹn")
q_up = FakeQuote(last=13_100, bid=13_000, ask=13_100)
o_noceil = buy_order(ceiling=None)
ex = make_exec([o_noceil], q_up)
px_a = ex._limit_price(o_noceil, q_up, cross=True)
# cũ: cap = ref×(1+1,5%) = 13.195 → round down tick 100 = 13.100; ask 13.100 → min = 13.100
check("A1 buy không trần vẫn đặt tại ask (13.100)", px_a == 13_100, f"px={px_a}")
check("A2 _hard_buy_ceiling(None) = None", Executor._hard_buy_ceiling(o_noceil) is None)
o_sell = PlannedOrder(id="SELL-01", ticker=SYM, side="sell", qty=1000, ref_price=REF_CLOSE)
px_sell_before = ex._limit_price(o_sell, q_up, cross=True)
check("A3 lệnh bán không đổi (đặt tại bid)", px_sell_before == 13_000, f"px={px_sell_before}")

# ───────────────────────────────────── B. Giá DƯỚI trần → BÁM giá chào thật
print("B. Thị trường DƯỚI trần → bám giá đang chào, không neo ngược xa")
q_low = FakeQuote(last=12_600, bid=12_500, ask=12_600)
o_b = buy_order(ceiling=ANCHOR)
ex_b = make_exec([o_b], q_low)
px_b = ex_b._limit_price(o_b, q_low, cross=True)
check("B1 đặt ĐÚNG ask 12.600 (bám thị trường, rẻ hơn trần)", px_b == 12_600, f"px={px_b}")
check("B2 và < trần anchor", px_b < ANCHOR)
# Điều cơ chế CŨ không làm được: neo ref=anchor/1,04=12.500 thì trần đuổi TĨNH (1,5%,
# mặc định khi thiếu rvol) chỉ tới 12.687 → làm tròn xuống bước giá UPCOM = 12.600. Thị
# trường chào 12.900 — VẪN DƯỚI anchor 13.000, lẽ ra mua được — mà lệnh cũ không với tới.
q_mid = FakeQuote(last=12_900, bid=12_800, ask=12_900)
o_new = buy_order(ceiling=ANCHOR)
px_new = make_exec([o_new], q_mid)._limit_price(o_new, q_mid, cross=True)
o_old = buy_order(ceiling=None, ref=ANCHOR / 1.04)
px_old = make_exec([o_old], q_mid)._limit_price(o_old, q_mid, cross=True)
check("B3 giá chào 12.900 (≤anchor): cơ chế MỚI với tới, cơ chế CŨ không",
      px_new == 12_900 and px_old < px_new, f"cũ={px_old} vs mới={px_new}")
check("B4 cả hai đều ≤ anchor (cũ an toàn nhưng bỏ lỡ)",
      px_new <= ANCHOR and px_old <= ANCHOR)

# ───────────────────────────────────── C. Giá TRÊN trần → clamp đúng tại trần
print("C. Thị trường TRÊN trần → clamp tại trần, không thể khớp trên anchor")
q_hi = FakeQuote(last=13_200, bid=13_100, ask=13_200)
o_c = buy_order(ceiling=ANCHOR)
ex_c = make_exec([o_c], q_hi)
px_c = ex_c._limit_price(o_c, q_hi, cross=True)
check("C1 giá đặt == trần 13.000 (không phải ask 13.200)", px_c == ANCHOR, f"px={px_c}")
check("C2 giá đặt ≤ trần (bất biến)", px_c <= ANCHOR)
# LO mua ở 13.000 trong khi ask 13.200 → không khớp ngay; chỉ khớp nếu ai đó chào xuống
# ≤13.000. Đó ĐÚNG là ý định: không bao giờ trả giá trên anchor.
check("C3 giá đặt < ask hiện tại (nằm chờ, không mua đuổi)", px_c < q_hi.ask)

# ───────────────────────────────────── D. Trần thắng trần-đuổi-% (kể cả vol-scale nới)
print("D. Trần tuyệt đối thắng mọi trần đuổi % (kể cả chase_cap_vol_scale nới tay)")
o_d = buy_order(ceiling=ANCHOR, ref=13_400)      # ref cao hơn anchor → cap% = 13.601
ex_d = make_exec([o_d], q_hi)
px_d = ex_d._limit_price(o_d, q_hi, cross=True)
check("D1 ref_price CAO hơn trần vẫn bị clamp về trần", px_d == ANCHOR, f"px={px_d}")
# chase_cap_vol_scale bật + rvol lớn → cap% nới tới ceil 4% = 13.936 (nếu không có trần)
ex_d2 = make_exec([o_d], q_hi, {"chase_cap_vol_scale_enabled": True})
ex_d2._gap_ref[SYM] = {"rvol_20d": 0.05}         # k=2 → 10% → clamp về ceil 4%
check("D2 _buy_chase_pct đã thật sự nới tới ceil 4%",
      abs(ex_d2._buy_chase_pct(SYM) - 0.04) < 1e-9, f"pct={ex_d2._buy_chase_pct(SYM)}")
q_d = FakeQuote(last=13_900, bid=13_800, ask=13_900)
px_d2 = ex_d2._limit_price(o_d, q_d, cross=True)
check("D3 vol-scale nới +4% vẫn KHÔNG vượt trần", px_d2 == ANCHOR, f"px={px_d2}")
# chứng minh ngược lại: BỎ trần thì đúng cấu hình đó CÓ đẩy vượt anchor
o_d_noceil = buy_order(ceiling=None, ref=13_400)
ex_d3 = make_exec([o_d_noceil], q_d, {"chase_cap_vol_scale_enabled": True})
ex_d3._gap_ref[SYM] = {"rvol_20d": 0.05}
px_d3 = ex_d3._limit_price(o_d_noceil, q_d, cross=True)
check("D4 (chứng minh trần thật sự chặn) BỎ trần → cùng cấu hình đặt TRÊN anchor",
      px_d3 > ANCHOR, f"px_không_trần={px_d3} > anchor={ANCHOR}")

# ───────────────────────────────────── E. Sàn phiên > trần → KHÔNG đặt lệnh
print("E. Sàn phiên đã trên trần → không đặt lệnh (None) + journal HARD_CEILING_BLOCK")
q_gap = FakeQuote(last=15_000, bid=15_000, ask=15_100, floor=14_500, ceiling=16_000)
o_e = buy_order(ceiling=ANCHOR)
ex_e = make_exec([o_e], q_gap)
px_e = ex_e._limit_price(o_e, q_gap, cross=True)
check("E1 trả None (không có giá hợp lệ ≤ trần)", px_e is None, f"px={px_e}")
# nếu KHÔNG có guard cuối, `max(px, q.floor)` sẽ đẩy giá lên 14.500 > anchor → mua trên anchor
o_e_noceil = buy_order(ceiling=None, ref=REF_CLOSE)
px_e2 = make_exec([o_e_noceil], q_gap)._limit_price(o_e_noceil, q_gap, cross=True)
check("E2 (chứng minh lỗ hổng có thật) không trần → q.floor đẩy giá lên trên anchor",
      px_e2 is not None and px_e2 > ANCHOR, f"px={px_e2}")
ex_e._place_slices(NOW, "MORNING")
check("E3 _place_slices KHÔNG đặt lệnh nào", len(ex_e.broker.placed) == 0,
      str(ex_e.broker.placed))
jlines = "".join(open(ex_e.journal_file, encoding="utf-8").readlines()) \
    if os.path.exists(ex_e.journal_file) else ""
check("E4 có journal HARD_CEILING_BLOCK (phân biệt với NO_QUOTE/WAIT_CASH)",
      "HARD_CEILING_BLOCK" in jlines)

# ───────────────────────────────────── F. ATC không được lách trần
print("F. ATC-remainder-buy: lệnh có trần KHÔNG đi đường ATC")
o_f = buy_order(ceiling=ANCHOR)
ex_f = make_exec([o_f], q_hi, {"atc_remainder_buy": True})
ex_f._atc_sweep()
check("F1 không có lệnh ATC nào được đặt", len(ex_f.broker.placed) == 0,
      str(ex_f.broker.placed))
o_f2 = buy_order(ceiling=None)
ex_f2 = make_exec([o_f2], q_hi, {"atc_remainder_buy": True})
ex_f2._atc_sweep()
check("F2 (regression) lệnh KHÔNG trần vẫn quét ATC như cũ",
      len(ex_f2.broker.placed) == 1 and ex_f2.broker.placed[0]["type"] == "ATC",
      str(ex_f2.broker.placed))

# ───────────────────────────────────── G. Slide: ask đổi → giá đặt đổi theo, luôn ≤ trần
print("G. Slide theo giá đang khớp qua từng chu kỳ, trần giữ nguyên ở mọi bước")
o_g = buy_order(ceiling=ANCHOR)
seq = [(12_400, 12_400), (12_800, 12_800), (13_100, 13_000), (12_900, 12_900),
       (13_500, 13_000)]
slide = []
for ask, want in seq:
    q_g = FakeQuote(last=ask, bid=ask - 100, ask=ask)
    px_g = make_exec([o_g], q_g)._limit_price(o_g, q_g, cross=True)
    slide.append((ask, px_g))
    check(f"G ask={ask:,} → đặt {want:,}", px_g == want, f"px={px_g}")
check("G_all mọi bước đều ≤ trần", all(p <= ANCHOR for _, p in slide), str(slide))
check("G_track có ít nhất 3 mức giá đặt KHÁC nhau (thật sự bám, không đứng yên)",
      len({p for _, p in slide}) >= 3, str(sorted({p for _, p in slide})))

# ───────────────────────────────────── H. Không rò sang lệnh bán; giá trị rác fail-safe
print("H. Không rò sang SELL; giá trị rác → fail-safe hành vi cũ")
o_h_sell = PlannedOrder(id="SELL-02", ticker=SYM, side="sell", qty=1000,
                        ref_price=REF_CLOSE, hard_no_chase_ceiling_vnd=ANCHOR)
check("H1 _hard_buy_ceiling bỏ qua lệnh bán", Executor._hard_buy_ceiling(o_h_sell) is None)
px_h = make_exec([o_h_sell], q_up)._limit_price(o_h_sell, q_up, cross=True)
check("H2 giá bán không đổi so với trước khi có trần", px_h == px_sell_before,
      f"{px_h} vs {px_sell_before}")
for bad in (0, -5, None, "", "abc"):
    o_bad = buy_order(ceiling=bad)
    check(f"H3 trần rác {bad!r} → None (không nới, không crash)",
          Executor._hard_buy_ceiling(o_bad) is None)
    px_bad = make_exec([o_bad], q_up)._limit_price(o_bad, q_up, cross=True)
    check(f"H4 trần rác {bad!r} → giá y hệt hành vi cũ", px_bad == px_a, f"px={px_bad}")

# ───────────────────────────────────── I. load_plan: giữ field + tự suy từ entry_anchor_price
print("I. load_plan() giữ field và TỰ SUY trần từ entry_anchor_price")
import dataclasses  # noqa: E402
import json         # noqa: E402
from trading_bot.config import PLAN_DIR  # noqa: E402
from trading_bot.plan import load_plan   # noqa: E402

check("I1 hard_no_chase_ceiling_vnd nằm trong dataclasses.fields(PlannedOrder)",
      "hard_no_chase_ceiling_vnd" in {f.name for f in dataclasses.fields(PlannedOrder)})


def _mk_plan_file(orders):
    """Ghi 1 plan tạm để kiểm ĐÚNG đường load_plan() thật (không giả lập)."""
    path = os.path.join(PLAN_DIR, f"plan_{TAG}_2099-01-02.json")
    json.dump({"plan_date": "2099-01-02", "signal_date": "2099-01-01", "strategy": "tst",
               "strategy_version": "0", "state": 3, "state_name": "NEUTRAL",
               "nav_basis": {}, "account": TAG, "orders": orders},
              open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return path


_p = _mk_plan_file([
    # (a) generator CHỈ ghi entry_anchor_price (đúng hiện trạng plan 08-10) → phải tự suy ra trần
    {"id": "BUY-A", "ticker": "DRI", "side": "buy", "qty": 3000, "ref_price": 13000.0,
     "entry_anchor_price": 13000.0},
    # (b) generator ghi trần CHẶT HƠN anchor → giữ cái chặt hơn, không được nới lên anchor
    {"id": "BUY-B", "ticker": "POW", "side": "buy", "qty": 1000, "ref_price": 13400.0,
     "entry_anchor_price": 13400.0, "hard_no_chase_ceiling_vnd": 13000.0},
    # (c) lệnh BÁN có anchor (vô nghĩa) → không được sinh trần
    {"id": "SELL-C", "ticker": "SCL", "side": "sell", "qty": 500, "ref_price": 24200.0,
     "entry_anchor_price": 24200.0},
    # (d) anchor rác → fail-safe, không trần, không crash
    {"id": "BUY-D", "ticker": "SSI", "side": "buy", "qty": 100, "ref_price": 24450.0,
     "entry_anchor_price": "n/a"},
])
_loaded = {x.id: x for x in load_plan("2099-01-02", account=TAG).orders}
check("I2 (a) chỉ có entry_anchor_price → tự suy trần = anchor",
      _loaded["BUY-A"].hard_no_chase_ceiling_vnd == 13_000.0,
      str(_loaded["BUY-A"].hard_no_chase_ceiling_vnd))
check("I3 (b) trần generator CHẶT HƠN anchor → giữ chặt hơn (không nới)",
      _loaded["BUY-B"].hard_no_chase_ceiling_vnd == 13_000.0,
      str(_loaded["BUY-B"].hard_no_chase_ceiling_vnd))
check("I4 (c) lệnh BÁN không sinh trần",
      _loaded["SELL-C"].hard_no_chase_ceiling_vnd is None)
check("I5 (d) anchor rác → None, không crash",
      _loaded["BUY-D"].hard_no_chase_ceiling_vnd is None)
os.remove(_p)

# I6 — BẤT BIẾN trên MỌI plan thật đang có trong repo: lệnh mua nào mang
# entry_anchor_price thì sau load_plan() PHẢI có trần cứng ≤ anchor. Assert lên quan hệ,
# KHÔNG lên rổ mã/số đếm của một ngày cụ thể (§23 hệ luận 1) — plan đổi mỗi ngày mà test
# vẫn đúng. Không có plan nào mang anchor → bỏ qua, không phải FAIL.
import re  # noqa: E402
_checked = 0
for _f in sorted(glob.glob(os.path.join(PLAN_DIR, "plan_*.json"))):
    _m = re.match(r"plan_(.+)_(\d{4}-\d{2}-\d{2})\.json$", os.path.basename(_f))
    if not _m:
        continue
    try:
        _raw = json.load(open(_f, encoding="utf-8"))
        _anch = {o["ticker"]: float(o["entry_anchor_price"]) for o in _raw.get("orders", [])
                 if o.get("side") == "buy" and isinstance(o.get("entry_anchor_price"), (int, float))}
        if not _anch:
            continue
        _pl = load_plan(_m.group(2), account=_m.group(1))
        for _o in _pl.orders:
            if _o.side != "buy" or _o.ticker not in _anch:
                continue
            _checked += 1
            check(f"I6 {os.path.basename(_f)} {_o.ticker}: trần cứng ≤ anchor {_anch[_o.ticker]:,.0f}",
                  bool(_o.hard_no_chase_ceiling_vnd) and _o.hard_no_chase_ceiling_vnd <= _anch[_o.ticker],
                  f"trần={_o.hard_no_chase_ceiling_vnd}")
    except Exception as _e:      # plan cũ schema khác → không phải lỗi của cơ chế này
        print(f"  [skip] {os.path.basename(_f)}: {_e}")
print(f"  (I6 đã kiểm {_checked} lệnh mua mang anchor trên plan thật)")

for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(_f)

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ TẤT CẢ PASS")
