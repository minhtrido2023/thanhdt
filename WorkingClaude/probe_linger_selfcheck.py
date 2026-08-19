# -*- coding: utf-8 -*-
"""Self-check cho PROBE HARNESS paper (probe_linger_min / probe_tick_log).

Bối cảnh: checkpoint 2026-08-19 (mike/agents/Taylor/research/paper_gates_checkpoint_20260819.md)
đo được bằng chứng của EXTREME gate là MỘT CHIỀU vì hai lý do CẤU TRÚC của harness:
  (A) 0/242 dòng PLACE nằm trong extreme_band — nhưng 3 phiên giá THỰC SỰ vào band SAU khi
      executor đã tắt; không có dữ liệu tại-thời-điểm để nói chắc.
  (B) executor sống trung vị 20 GIÂY ⇒ px_hist không bao giờ đủ 0,7×dip_window_min ⇒ `_r15`
      trả None ⇒ trigger (ii) fail-safe False vì cấu trúc, không vì thị trường lành tính.

Bộ này kiểm ĐÚNG hai thứ đó, và — quan trọng hơn — kiểm rằng harness KHÔNG chạm gate:
  A. LIVE / cờ tắt / cấu hình rác  → đường cũ byte-identical, không dòng log nào, phiên vẫn
     kết thúc ngay khi khớp xong.
  B. PAPER + cờ bật               → phiên sống thêm, KHÔNG đặt lệnh, px_hist tiếp tục dài ra,
     r15 chuyển từ None sang tính được, tick log ghi đúng band-proximity.
  C. Cách ly gate                 → chuỗi quyết định của `_extreme_regime` GIỐNG HỆT dù probe
     harness bật hay tắt.

Chạy: python3 probe_linger_selfcheck.py   (exit 0 = pass hết)
Chạy lại dưới `env -u TZ` và `TZ=America/New_York` — mọi mốc giờ ở đây phải bất biến theo TZ.
"""
import datetime as dt
import glob
import os
import sys

# §5b coding_guidelines: selfcheck chạm Executor PHẢI chặn kênh bus TRƯỚC khi dựng Executor.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

from trading_bot.config import DEFAULTS, EXEC_DIR
from trading_bot.plan import PlannedOrder, TradePlan
from trading_bot.executor import Executor

TAG = "selfcheck-probe"
# Executor.__init__ nạp state.json theo (account, plan_date) NGAY khi dựng, trước khi test kịp
# chuyển hướng — file sót lại từ lần chạy trước làm hỏng lần này một cách IM LẶNG. Ở đây nó cắn
# thật: px_hist cũ (mốc 09:50) khiến `_record_prices` thấy mẫu "mới hơn now" ⇒ bỏ qua mọi chu kỳ
# ⇒ không dòng tick log nào. Glob phải là `{TAG}*` (KHÔNG phải `{TAG}_*`): mọi ca dưới đây dùng
# tag CÓ HẬU TỐ (`selfcheck-probe-r15`…), dạng `{TAG}_*` không khớp cái nào.
for _pat in (f"exec_{TAG}*", f"probe_ticks_{TAG}*"):
    for _f in glob.glob(os.path.join(EXEC_DIR, _pat)):
        os.remove(_f)

REF = 50_000.0
FLOOR = round(REF * 0.93, -1)
CEIL = round(REF * 1.07, -1)
NOW0 = dt.datetime(2099, 1, 1, 9, 30, 0)


class FakeQuote:
    def __init__(self, last, floor=FLOOR, ceiling=CEIL, ref=REF):
        self.symbol = "TST"; self.exchange = "HOSE"
        self.last = last; self.ref = ref
        self.bid = last; self.ask = last
        self.floor = floor; self.ceiling = ceiling; self.day_volume = 5_000_000
    def ok(self):
        return self.last is not None or self.ref is not None


class FakeBroker:
    name = "fake"
    def __init__(self, quotes):
        self.quotes = quotes; self.placed = []; self._oid = 0
        self.polls = 0; self.cash = 10_000_000_000
    def get_quote(self, sym):
        return self.quotes.get(sym)
    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        self._oid += 1
        self.placed.append(dict(symbol=symbol, qty=qty, side=side, price=price))
        return f"OID{self._oid}"
    def cancel_order(self, oid):
        pass
    def poll_orders(self):
        self.polls += 1
        return {}
    def get_positions(self):
        return {}
    def get_cash(self):
        return self.cash


def make_exec(cfg_over, tag=TAG, last=REF, floor=FLOOR):
    cfg = dict(DEFAULTS)
    cfg["fill_timing_hybrid_enabled"] = False   # cô lập 1 biến (§23 hệ luận 1)
    cfg["mode"] = "paper"
    cfg.update(cfg_over)
    o = PlannedOrder(id="BUY-TST-01", ticker="TST", side="buy", qty=10_000, ref_price=REF)
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=[o], account=tag,
                     created_at="2099-01-01T00:00:00")
    q = FakeQuote(last=last, floor=floor)
    ex = Executor(plan, FakeBroker({"TST": q}), cfg)
    ex.probe_tick_file = os.path.join(EXEC_DIR, f"probe_ticks_{tag}_run.csv")
    if os.path.exists(ex.probe_tick_file):
        os.remove(ex.probe_tick_file)
    return ex, o, q


def mark_done(ex):
    for p in ex.state["parents"].values():
        p["done"] = True


fails = []
def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


# ============================================================ A. REGRESSION — cờ phải câm
print("A. LIVE / cờ tắt / cấu hình rác → hành vi CŨ nguyên vẹn")

ex, o, q = make_exec({"mode": "live", "probe_linger_min": 30}, tag=TAG + "-live")
check("A1 mode=live ⇒ harness TẮT dù probe_linger_min=30", ex._probe_linger_on() is False)
mark_done(ex)
check("A2 mode=live ⇒ step() vẫn kết thúc phiên ngay khi khớp xong",
      ex.step(NOW0, "MORNING", True) is True)
check("A3 mode=live ⇒ KHÔNG sinh file tick log", not os.path.exists(ex.probe_tick_file))

# Cổng LIVE fail-safe: cấu hình THIẾU khoá phải = gate BẬT (paper-only), không mở toang.
ex, o, q = make_exec({"mode": "live", "probe_linger_min": 30}, tag=TAG + "-nokey")
ex.cfg.pop("probe_linger_live_gate", None)
check("A4 thiếu khoá probe_linger_live_gate ⇒ vẫn paper-only (fail-safe .get(...,True))",
      ex._probe_linger_on() is False)

# Ca quant-skeptic 2026-08-19 chỉ ra là CHƯA ĐƯỢC PHỦ: cờ cổng bị đặt False TƯỜNG MINH trên
# một account LIVE. Bản đầu viết `live_gate and mode != "paper"` ⇒ ca này BẬT harness trên live
# chỉ bằng MỘT dòng override. Sau khi tách chốt, `mode` được kiểm vô điều kiện.
ex, o, q = make_exec({"mode": "live", "probe_linger_min": 30,
                      "probe_linger_live_gate": False}, tag=TAG + "-livebypass")
check("A4b cổng đặt False TƯỜNG MINH trên account LIVE ⇒ VẪN tắt (mode kiểm vô điều kiện)",
      ex._probe_linger_on() is False)
mark_done(ex)
check("A4c ⇒ step() vẫn kết thúc phiên ngay, không linger trên live",
      ex.step(NOW0, "MORNING", True) is True)

# Trên PAPER, cờ False = TẮT HẲN harness (ngữ nghĩa cố ý khác fill_timing_live_gate — xem
# docstring `_probe_linger_on`): không có đường nào biến nó thành "mở sang live".
ex, o, q = make_exec({"probe_linger_min": 30, "probe_linger_live_gate": False},
                     tag=TAG + "-papergate")
check("A4d paper + cổng False ⇒ tắt hẳn harness (kill-switch, KHÔNG phải mở live)",
      ex._probe_linger_on() is False)

ex, o, q = make_exec({"probe_linger_min": 0}, tag=TAG + "-off")
check("A5 probe_linger_min=0 ⇒ TẮT dù đang paper", ex._probe_linger_on() is False)
mark_done(ex)
check("A6 probe_linger_min=0 ⇒ step() kết thúc phiên ngay",
      ex.step(NOW0, "MORNING", True) is True)

ex, o, q = make_exec({"probe_linger_min": "ba-muoi"}, tag=TAG + "-junk")
check("A7 probe_linger_min rác ⇒ TẮT, không raise", ex._probe_linger_on() is False)

# Nhánh cũ của _record_prices: parent done thì KHÔNG lấy mẫu khi harness tắt.
ex, o, q = make_exec({"probe_linger_min": 0}, tag=TAG + "-nosample")
mark_done(ex)
ex._record_prices(NOW0, "MORNING")
check("A8 harness TẮT ⇒ parent done KHÔNG được lấy mẫu (hành vi cũ)",
      not ex.state.get("px_hist", {}).get("TST"))

# ============================================================ B. PAPER — cơ chế chạy
print("B. PAPER + probe_linger_min=30 (cơ chế)")

ex, o, q = make_exec({"probe_linger_min": 30}, tag=TAG + "-on")
check("B1 paper + min>0 ⇒ harness BẬT", ex._probe_linger_on() is True)
mark_done(ex)
s1 = ex.step(NOW0, "MORNING", True)
check("B2 all_done nhưng còn cửa sổ ⇒ step() trả False (giữ phiên sống)", s1 is False)
until = ex.state.get("_probe_linger_until")
check("B3 mốc kết thúc = now + 30' đóng dấu vào state",
      until == (NOW0 + dt.timedelta(minutes=30)).isoformat(timespec="seconds"), f"until={until}")
check("B4 KHÔNG đặt lệnh nào trong linger", ex.broker.placed == [],
      f"placed={ex.broker.placed}")
check("B5 parent ĐÃ done vẫn được lấy mẫu giá", bool(ex.state["px_hist"].get("TST")))

# Mốc không tự gia hạn: gọi lại sau 10' vẫn giữ nguyên `until` (bền qua restart giữa phiên).
ex.step(NOW0 + dt.timedelta(minutes=10), "MORNING", True)
check("B6 mốc KHÔNG tự gia hạn theo mỗi chu kỳ", ex.state["_probe_linger_until"] == until)

# Sau mốc → phiên kết thúc như bình thường.
s2 = ex.step(NOW0 + dt.timedelta(minutes=31), "MORNING", True)
check("B7 quá mốc ⇒ step() trả True (kết thúc phiên)", s2 is True)

# Ngoài phiên khớp liên tục ⇒ KHÔNG linger (mẫu vô nghĩa + cron pkill 11:32 sẽ giết giữa chừng
# làm write_report() không chạy). Executor mới ⇒ chưa đóng dấu mốc nào.
for _ph in ("LUNCH", "ATC", "ATO", "PRE", "CLOSED"):
    exp, _o, _q = make_exec({"probe_linger_min": 30}, tag=TAG + "-ph" + _ph)
    mark_done(exp)
    check(f"B7b phase={_ph} ⇒ KHÔNG linger, phiên kết thúc bình thường",
          exp.step(NOW0, _ph, _ph in ("MORNING", "AFTERNOON")) is True)
    check(f"B7c phase={_ph} ⇒ KHÔNG đóng dấu mốc linger vào state",
          "_probe_linger_until" not in exp.state)
jrn = open(ex.journal_file, encoding="utf-8").read() if os.path.exists(ex.journal_file) else ""
check("B8 journal có PROBE_LINGER_START", "PROBE_LINGER_START" in jrn)
check("B9 journal có PROBE_LINGER_END", "PROBE_LINGER_END" in jrn)

# ---- gap (B): r15 chuyển từ None (phiên 20 giây) sang tính được (phiên linger) ----
print("B'. gap (B) — r15 phải tính được nhờ phiên dài")
ex, o, q = make_exec({"probe_linger_min": 30}, tag=TAG + "-r15")
mark_done(ex)
t = NOW0
ex.step(t, "MORNING", True)
check("B10 sau ~20 giây (phiên ngắn như hôm nay) r15 = None",
      ex._r15("TST", t + dt.timedelta(seconds=20)) is None)
# lấy mẫu mỗi 60s (px_sample_sec) trong 20 phút; giá trượt dần xuống
for i in range(1, 21):
    t = NOW0 + dt.timedelta(minutes=i)
    q.last = REF * (1 - 0.0008 * i)
    ex.step(t, "MORNING", True)
r15 = ex._r15("TST", t)
check("B11 sau 20' linger ⇒ r15 TÍNH ĐƯỢC (hết fail-safe None do cấu trúc)",
      r15 is not None, f"r15={r15}")
check("B12 r15 âm và đúng bậc độ lớn của cú trượt mô phỏng",
      r15 is not None and -0.02 < r15 < -0.001, f"r15={r15}")
check("B13 mẫu px_hist đủ dài (≥15 điểm)", len(ex.state["px_hist"]["TST"]) >= 15,
      f"n={len(ex.state['px_hist']['TST'])}")

# ---- gap (A): tick log đo band-proximity tại-thời-điểm ----
print("B''. gap (A) — tick log band-proximity")
import csv as _csv
rows = list(_csv.DictReader(open(ex.probe_tick_file, encoding="utf-8")))
check("B14 tick log được ghi", len(rows) >= 15, f"rows={len(rows)}")
check("B15 tick log có cột headroom_floor + in_band + r15",
      {"headroom_floor", "in_band", "r15", "trig_ii_threshold"} <= set(rows[0].keys()),
      f"cols={sorted(rows[0].keys())}")
hr = float(rows[0]["headroom_floor"])
check("B16 headroom tính đúng: last=REF, floor=REF×0,93 ⇒ ~+7,53%",
      abs(hr - (REF / FLOOR - 1.0)) < 1e-6, f"headroom={hr:.5f}")
check("B17 giá cách sàn 7,5% ⇒ in_band = 0", all(r["in_band"] == "0" for r in rows))
check("B18 r15 rỗng ở dòng đầu, có số ở dòng cuối (đúng chiều tích luỹ lịch sử)",
      rows[0]["r15"] == "" and rows[-1]["r15"] != "",
      f"first={rows[0]['r15']!r} last={rows[-1]['r15']!r}")

# giá TỤT VÀO band ⇒ in_band phải bật, đo được ĐÚNG GIÂY, không phải suy từ OHLC ngày
ex2, o2, q2 = make_exec({"probe_linger_min": 30}, tag=TAG + "-band", last=FLOOR * 1.02)
mark_done(ex2)
ex2.step(NOW0, "MORNING", True)
rows2 = list(_csv.DictReader(open(ex2.probe_tick_file, encoding="utf-8")))
check("B19 giá trong band ⇒ in_band = 1 (đo trực tiếp, không suy từ OHLC ngày)",
      rows2 and rows2[-1]["in_band"] == "1", f"rows2={rows2[-1] if rows2 else None}")
check("B20 headroom trong band ≤ extreme_band",
      rows2 and float(rows2[-1]["headroom_floor"]) <= float(rows2[-1]["extreme_band"]))

# quote thiếu floor ⇒ không raise, vẫn ghi dòng với headroom rỗng
ex3, o3, q3 = make_exec({"probe_linger_min": 30}, tag=TAG + "-nofloor", floor=None)
mark_done(ex3)
ex3.step(NOW0, "MORNING", True)
rows3 = list(_csv.DictReader(open(ex3.probe_tick_file, encoding="utf-8")))
check("B21 quote thiếu floor ⇒ không raise, headroom rỗng, in_band=0",
      rows3 and rows3[-1]["headroom_floor"] == "" and rows3[-1]["in_band"] == "0")

# probe_tick_log=False ⇒ linger vẫn chạy nhưng KHÔNG ghi file
ex4, o4, q4 = make_exec({"probe_linger_min": 30, "probe_tick_log": False}, tag=TAG + "-nolog")
mark_done(ex4)
check("B22 probe_tick_log=False ⇒ vẫn linger", ex4.step(NOW0, "MORNING", True) is False)
check("B23 probe_tick_log=False ⇒ KHÔNG ghi file", not os.path.exists(ex4.probe_tick_file))

# ============================================================ C. CÁCH LY GATE
print("C. Harness KHÔNG được chạm logic gate EXTREME")

def gate_trace(cfg_over, tag):
    """Chuỗi quyết định của gate trên cùng một kịch bản giá — phải giống hệt nhau."""
    cfg = dict(cfg_over); cfg["extreme_regime_enabled"] = True
    e, oo, qq = make_exec(cfg, tag=tag, last=FLOOR)   # giá NẰM SÁT SÀN ⇒ trigger (i)
    out = []
    for i in range(4):
        t = NOW0 + dt.timedelta(seconds=20 * i)
        out.append((e._extreme_regime(oo, qq, t),
                    e._floor_guard_buy(oo, qq),
                    e._extreme_slice_mult(oo, t)))
    return out

tr_off = gate_trace({"probe_linger_min": 0, "probe_tick_log": False}, TAG + "-gate-off")
tr_on = gate_trace({"probe_linger_min": 30, "probe_tick_log": True}, TAG + "-gate-on")
check("C1 chuỗi quyết định gate GIỐNG HỆT khi bật/tắt probe harness",
      tr_off == tr_on, f"off={tr_off} on={tr_on}")
check("C2 (chứng minh trace không rỗng) gate có thật sự kích ở kịch bản cận sàn",
      any(x[0] for x in tr_off), f"trace={tr_off}")

# ============================================================
print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ tất cả check PASS")
