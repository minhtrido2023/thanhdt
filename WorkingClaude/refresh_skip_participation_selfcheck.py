# -*- coding: utf-8 -*-
"""Regression self-check: REFRESH_SKIP phải kích được cả khi trần participation là BINDING.

BUG (ca thật SpaceX 2026-08-10, job Taylor_20260810_042759 — journal
`data/execution_logs/exec_SpaceX_2026-08-10_journal.csv`, lệnh BUY-DRI-LAG-01):
15/15 chu kỳ sáng đều CANCEL_STALE rồi đặt lại lệnh Y HỆT giá+KL (13.000đ × 200cp lúc
09:15/09:23/09:31, 13.000đ × 300cp lúc 09:47/09:55/10:03) — REFRESH_SKIP không lần nào kích,
mất ưu tiên xếp hàng FIFO vô ích trên đúng mã UPCOM mỏng thanh khoản nhất trong plan.

ROOT CAUSE (không phải race 2 lần get_quote — broker đã có TTL cache 3s, brokers.py:254/377):
`self.shared` = KL fleet đã khớp + đang TREO (reservation, executor.py:253 seed_shared).
`_would_be_unchanged` hỏi "huỷ RỒI đặt lại có ra đúng giá+KL cũ không", nhưng gọi `_child_qty`
mà KHÔNG trừ reservation của CHÍNH lệnh con sắp bị huỷ — trong khi huỷ thật thì
`_release_child()` nhả reservation đó ra TRƯỚC khi `_place_slices` tính KL mới. Hệ quả: đường
KIỂM TRA đếm lệnh của chính mình như quota của người khác.

Khi trần participation là ràng buộc BINDING (qty == round_lot(10% × day_volume)), allowance ở
đường kiểm tra tụt đúng bằng KL đang treo ⇒ luôn < 1 lô ⇒ `_child_qty` trả 0 ⇒
`_would_be_unchanged` trả False ⇒ CANCEL_STALE, MỌI LẦN, một cách tất định.
Số thật DRI 09:23: day_volume≈2.269 ⇒ đúng: 226 → 200cp; sai: 226−200 = 26 < 1 lô ⇒ 0.
Đó cũng là lý do POW/SSI (thanh khoản dày, allowance KHÔNG binding) vẫn REFRESH_SKIP bình
thường cùng phiên — chứng cứ đối chứng nội tại trong cùng 1 journal.

FIX: `_child_qty(..., exclude_reserved=)`; `_would_be_unchanged` truyền KL chưa khớp của lệnh
con sắp huỷ. Mặc định 0 ⇒ `_place_slices` byte-identical.

Mọi ca "sau khi sửa thì giữ được lệnh" ở đây đều đi kèm CA CHỨNG MINH NGƯỢC (chạy lại đúng
nhánh cũ `exclude_reserved=0` và xác nhận nó THẬT SỰ huỷ) — không chỉ khẳng định suông.

Run: python refresh_skip_participation_selfcheck.py   (exit 0 = all pass)
Phụ thuộc môi trường: KHÔNG có (không đọc TZ hệ thống — mọi mốc thời gian là datetime naive tự
dựng trong test; không đọc mạng/BQ/broker thật; không ghi ra ngoài tmpdir).
"""
import datetime as dt
import glob
import os
import sys
import tempfile

# §5b coding_guidelines: chặn _publish_bot_event bắn lên bus THẬT từ selfcheck.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.plan import PlannedOrder, TradePlan  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.brokers import Quote  # noqa: E402
from trading_bot.config import load_config, EXEC_DIR  # noqa: E402
from trading_bot.vn_market import round_lot, LOT  # noqa: E402

TAG = "selfcheck-refresh-skip"
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(f)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def mkquote(day_volume, last=13100, ref=13000, ask=13200, bid=13100,
            ceiling=13900, floor=12100, exchange="HOSE", symbol="DRI"):
    return Quote({"symbol": symbol, "exchange": exchange, "lastprice": last,
                  "refprice": ref, "bestoffer1price": ask, "bestbid1price": bid,
                  "ceiling": ceiling, "floor": floor, "totaltrading": day_volume})


class FakeBroker:
    """get_quote trả lần lượt các quote trong `queue` (quote cuối lặp lại mãi) — đủ để mô
    phỏng cả trường hợp snapshot LỆCH nhau giữa lần kiểm tra và lần đặt thật."""
    name = "fake"

    def __init__(self, quotes):
        self.queue = list(quotes)
        self.calls = 0
        self.cancelled = []
        self.placed = []
        self._oid = 900000

    def get_quote(self, symbol):
        q = self.queue[min(self.calls, len(self.queue) - 1)]
        self.calls += 1
        return q

    def cancel_order(self, oid):
        self.cancelled.append(oid)

    def place_order(self, symbol, qty, side, price=None, **kw):
        self._oid += 1
        self.placed.append({"symbol": symbol, "qty": qty, "side": side, "price": price})
        return str(self._oid)

    def get_cash(self):
        return 10 ** 12

    def get_max_buy_qty(self, *a, **k):
        return 10 ** 9

    def get_positions(self):
        return {}

    def poll_orders(self):
        return []


def make_executor(tmpdir, broker, orders, shared, hybrid=False):
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=orders,
                     account=TAG, created_at="2099-01-01T00:00:00")
    cfg = load_config()
    cfg["mode"] = "paper"
    cfg["extreme_regime_enabled"] = False
    cfg["gap_adaptive_enabled"] = False
    # Nhóm A-G ghim TẮT cả layer fill-timing để cô lập trần participation. Nhóm H bật
    # HYBRID (đúng cấu hình paper THẬT từ 2026-08-10) — xem lý do ở đầu nhóm H.
    cfg["fill_timing_enabled"] = bool(hybrid)
    cfg["fill_timing_hybrid_enabled"] = bool(hybrid)
    ex = Executor(plan, broker, cfg, shared=shared)
    ex.state_file = os.path.join(tmpdir, "state.json")
    ex.journal_file = os.path.join(tmpdir, "journal.csv")
    ex.report_file = os.path.join(tmpdir, "report.md")
    return ex


def dri_order(qty=2800, ref_price=13000.0, hard=13000.0):
    return PlannedOrder(id="BUY-DRI-LAG-01", ticker="DRI", side="buy", qty=qty,
                        ref_price=ref_price, priority=1,
                        urgency="normal", book="LAG", play_type="LAG_HI",
                        hard_no_chase_ceiling_vnd=hard)


NOW = dt.datetime(2099, 1, 5, 9, 23, 15)


def seed_open_child(ex, o, qty, price, age_min=9, filled=0):
    ps = ex.state["parents"][o.id]
    c = {"oid": "54921", "qty": qty, "price": price, "filled": filled, "status": "open",
         "ts": (NOW - dt.timedelta(minutes=age_min)).isoformat(timespec="seconds")}
    ps["children"].append(c)
    ps["filled"] = filled
    ps["last_slice_ts"] = c["ts"]
    return ps, c


# Event THÔNG TIN của P2 (pacing theo KL kỳ vọng), không phải hành động sổ lệnh. Từ 2026-08-17
# `expected_volume_pacing_enabled=True` trên paper ⇒ mọi executor paper đi qua nhánh ADV20-paced
# ghi thêm 1 dòng EXPVOL_PACING, làm ca E2 dưới đây đỏ dù hành vi churn KHÔNG đổi (E1/E3 vẫn ra
# đúng KL, REFRESH_SKIP vẫn kích, broker không bị gọi cancel). Bất biến mà file này kiểm là
# HUỶ-hay-KHÔNG-HUỶ, không phải độ dài journal ⇒ lọc đúng 2 event thông tin đó.
# ⚠️ CỐ Ý KHÔNG lọc `EXPVOL_SHADOW_ERR`: nó nghĩa là nhánh đo lường đã ném lỗi — muốn nó làm
# đỏ mọi assert so khớp tuyệt đối ở đây, đó là cách rẻ nhất để lỗi đó không đi qua im lặng.
EXPVOL_INFO = {"EXPVOL_PACING", "EXPVOL_SHADOW"}


def journal_events(ex):
    if not os.path.exists(ex.journal_file):
        return []
    with open(ex.journal_file, encoding="utf-8") as f:
        return [e for e in (ln.split(",")[1] for ln in f.read().splitlines()[1:] if "," in ln)
                if e not in EXPVOL_INFO]


# =============================================================== A. Ca DRI thật
print("A. Tái lập ca thật DRI 2026-08-10 09:23 (trần participation BINDING)")
with tempfile.TemporaryDirectory() as td:
    q = mkquote(day_volume=2269)          # back-out từ note journal ratio=123.40%, rem=2800
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0)

    px = ex._limit_price(o, q, cross=True)
    check("A0 giá tái lập đúng 13.000đ (đứng tại trần cứng)", px == 13000.0, f"px={px}")

    qty_fixed = ex._child_qty(o, ps, q, px, exclude_reserved=200)
    qty_old = ex._child_qty(o, ps, q, px, exclude_reserved=0)
    check("A1 SAU sửa: KL tính lại == KL đang treo (200cp)", qty_fixed == 200,
          f"{qty_fixed}cp  (allowance=int(0.10×2269)=226 → round_lot=200)")
    check("A1' CHỨNG MINH NGƯỢC — nhánh CŨ thật sự trả 0 (nên luôn huỷ)", qty_old == 0,
          f"{qty_old}cp  (226−200 reservation = 26 < 1 lô)")

    ex._cancel_stale(NOW)
    ev = journal_events(ex)
    check("A2 _cancel_stale ghi REFRESH_SKIP, KHÔNG CANCEL_STALE", ev == ["REFRESH_SKIP"], str(ev))
    check("A3 KHÔNG gọi broker.cancel_order (giữ ưu tiên FIFO)", br.cancelled == [], str(br.cancelled))
    check("A4 lệnh con vẫn sống, đúng oid cũ",
          c["status"] == "open" and c["oid"] == "54921" and ex._open_child(ps) is c)
    check("A5 đồng hồ tuổi được reset (không cancel ngay chu kỳ sau)", c["ts"] == NOW.isoformat(timespec="seconds"))
    check("A6 shared KHÔNG bị đụng (reservation giữ nguyên 200)", ex.shared["DRI"] == 200,
          str(ex.shared))

# =============================================================== B. Vẫn phải huỷ khi KHÁC thật
print("B. Giá/KL THẬT SỰ khác ⇒ vẫn phải CANCEL_STALE (không nới lỏng)")
with tempfile.TemporaryDirectory() as td:
    # 09:47 thật: day_volume≈3032 ⇒ KL đúng phải là 300cp, lệnh treo là 200cp
    q = mkquote(day_volume=3032)
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0)
    qty_fixed = ex._child_qty(o, ps, q, ex._limit_price(o, q, True), exclude_reserved=200)
    check("B1 KL mới = 300cp (khác 200cp đang treo)", qty_fixed == 300, f"{qty_fixed}cp")
    ex._cancel_stale(NOW)
    check("B2 ⇒ CANCEL_STALE (đúng, KL đã đổi thật)", journal_events(ex) == ["CANCEL_STALE"],
          str(journal_events(ex)))
    check("B3 reservation được nhả đúng 200cp", ex.shared["DRI"] == 0, str(ex.shared))

with tempfile.TemporaryDirectory() as td:
    q = mkquote(day_volume=2269)
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=12900.0)   # giá treo KHÁC giá tính lại
    ex._cancel_stale(NOW)
    check("B4 giá khác (12.900 vs 13.000) ⇒ CANCEL_STALE",
          journal_events(ex) == ["CANCEL_STALE"], str(journal_events(ex)))

with tempfile.TemporaryDirectory() as td:
    q = mkquote(day_volume=2269)
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0, filled=100)
    ex._cancel_stale(NOW)
    check("B5 đã khớp một phần ⇒ vẫn refresh như cũ (fail-safe không đổi)",
          journal_events(ex) == ["CANCEL_STALE"], str(journal_events(ex)))

with tempfile.TemporaryDirectory() as td:
    q = mkquote(day_volume=2269)
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0, age_min=3)   # chưa quá 8'
    ex._cancel_stale(NOW)
    check("B6 chưa quá hạn 8' ⇒ không làm gì cả (không REFRESH_SKIP sớm)",
          journal_events(ex) == [] and br.cancelled == [], str(journal_events(ex)))

# =============================================================== C. Bất biến fleet đa tài khoản
print("C. Chỉ trừ reservation CỦA MÌNH — quota tài khoản khác vẫn phải tính đủ")
with tempfile.TemporaryDirectory() as td:
    q = mkquote(day_volume=2269)                      # allowance gộp = 226
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200 + 100})   # 200 của mình + 100 account khác
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0)
    px = ex._limit_price(o, q, True)
    qty_ok = ex._child_qty(o, ps, q, px, exclude_reserved=200)
    qty_wrong = ex._child_qty(o, ps, q, px, exclude_reserved=300)   # nếu lỡ trừ CẢ fleet
    check("C1 trừ đúng 200 của mình ⇒ 226−100 = 126 → 100cp (≠200 ⇒ sẽ huỷ, đúng)",
          qty_ok == 100, f"{qty_ok}cp")
    check("C1' CHỨNG MINH NGƯỢC — trừ nhầm cả fleet sẽ ra 200cp và giữ lệnh SAI",
          qty_wrong == 200, f"{qty_wrong}cp")
    ex._cancel_stale(NOW)
    check("C2 ⇒ CANCEL_STALE (quota fleet đã hụt thật, không được giữ)",
          journal_events(ex) == ["CANCEL_STALE"], str(journal_events(ex)))

# =============================================================== D. Không binding ⇒ không đổi
print("D. Trần participation KHÔNG binding (mã dày thanh khoản) ⇒ hành vi cũ giữ nguyên")
with tempfile.TemporaryDirectory() as td:
    # POW thật cùng phiên: 2800cp, day_volume lớn ⇒ allowance ≫ remaining ⇒ REFRESH_SKIP cũ vẫn kích
    q = mkquote(day_volume=60000, last=13400, ref=13400, ask=13400, bid=13300,
                ceiling=14300, floor=12500, symbol="POW")
    br = FakeBroker([q])
    o = PlannedOrder(id="BUY-POW-LAG-02", ticker="POW", side="buy", qty=2800,
                     ref_price=13400.0, priority=2, urgency="normal",
                     book="LAG", play_type="LAG_HI", hard_no_chase_ceiling_vnd=13400.0)
    ex = make_executor(td, br, [o], shared={"POW": 2800})
    ps, c = seed_open_child(ex, o, qty=2800, price=13400.0)
    px = ex._limit_price(o, q, True)
    same = ex._child_qty(o, ps, q, px, exclude_reserved=0)
    fixed = ex._child_qty(o, ps, q, px, exclude_reserved=2800)
    check("D1 cũ và mới ra CÙNG KL khi allowance không binding (regression byte-identical)",
          same == fixed == 2800, f"cũ={same} mới={fixed}")
    ex._cancel_stale(NOW)
    check("D2 REFRESH_SKIP như trước", journal_events(ex) == ["REFRESH_SKIP"],
          str(journal_events(ex)))

# =============================================================== E. Nhánh ADV20 (CAPIT/DISCRETIONARY)
print("E. Nhánh ADV20-paced (CAPIT/DISCRETIONARY_SPECIAL) cũng phải trừ reservation")
with tempfile.TemporaryDirectory() as td:
    q = mkquote(day_volume=2269)
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0)
    ex._adv20_basis_for = lambda _o: 29_500_000.0   # ⇒ floor_allow = int(0.10×29.5tr/13000) = 226
    px = ex._limit_price(o, q, True)
    a_fixed = ex._child_qty(o, ps, q, px, exclude_reserved=200)
    a_old = ex._child_qty(o, ps, q, px, exclude_reserved=0)
    check("E1 ADV20-floor: sau sửa ra 200cp", a_fixed == 200, f"{a_fixed}cp")
    check("E1' CHỨNG MINH NGƯỢC — nhánh cũ trả 0 (cùng bệnh)", a_old == 0, f"{a_old}cp")
    ex._cancel_stale(NOW)
    check("E2 ⇒ REFRESH_SKIP", journal_events(ex) == ["REFRESH_SKIP"], str(journal_events(ex)))

with tempfile.TemporaryDirectory() as td:
    # trần phụ realized-ceiling (30% × day_volume) mới là ràng buộc binding
    q = mkquote(day_volume=700)
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0)
    ex._adv20_basis_for = lambda _o: 500_000_000.0   # floor_allow rất lớn ⇒ ceil_allow binding
    px = ex._limit_price(o, q, True)
    b_fixed = ex._child_qty(o, ps, q, px, exclude_reserved=200)
    b_old = ex._child_qty(o, ps, q, px, exclude_reserved=0)
    check("E3 realized-ceiling: sau sửa 200cp (int(0.30×700)=210 → 200)", b_fixed == 200,
          f"{b_fixed}cp")
    check("E3' CHỨNG MINH NGƯỢC — nhánh cũ 210−200=10 ⇒ 0", b_old == 0, f"{b_old}cp")

# =============================================================== F. Snapshot quote lệch nhau
print("F. Giả thuyết 'race 2 lần get_quote': snapshot lệch giữa KIỂM TRA và ĐẶT THẬT")
with tempfile.TemporaryDirectory() as td:
    # quote #1 (kiểm tra) dv=2269 → 200cp; quote #2 (đặt) dv=2290 → vẫn 200cp sau round_lot
    br = FakeBroker([mkquote(2269), mkquote(2290)])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0)
    ex._cancel_stale(NOW)
    check("F1 lệch dv trong CÙNG 1 lô ⇒ vẫn REFRESH_SKIP (race không bẻ được fix)",
          journal_events(ex) == ["REFRESH_SKIP"], str(journal_events(ex)))

with tempfile.TemporaryDirectory() as td:
    # lệch VƯỢT ranh giới lô: dv 2269 (→200) vs 3032 (→300)
    br = FakeBroker([mkquote(2269), mkquote(3032)])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0)
    ex._cancel_stale(NOW)
    check("F2 lệch vượt ranh giới lô ⇒ REFRESH_SKIP theo snapshot lúc kiểm tra "
          "(sai lệch tồn dư đã biết, hệ quả lành tính: 1 chu kỳ chậm)",
          journal_events(ex) == ["REFRESH_SKIP"], str(journal_events(ex)))
    check("F2' KL của lần lệch đó chỉ ±1 lô — không bao giờ vượt trần participation",
          abs(300 - 200) == LOT)

# =============================================================== G. End-to-end 1 chu kỳ step
print("G. Nguyên 1 chu kỳ _cancel_stale + _place_slices (đường đi thật)")
with tempfile.TemporaryDirectory() as td:
    br = FakeBroker([mkquote(2269)])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0)
    ex._cancel_stale(NOW)
    ex._place_slices(NOW, "CONT", (), None)
    check("G1 SAU sửa: 0 huỷ, 0 đặt mới — đúng 1 lệnh sống suốt chu kỳ",
          br.cancelled == [] and br.placed == [] and len(ps["children"]) == 1,
          f"cancel={br.cancelled} place={br.placed} children={len(ps['children'])}")
    check("G2 journal đúng 1 dòng REFRESH_SKIP", journal_events(ex) == ["REFRESH_SKIP"],
          str(journal_events(ex)))

with tempfile.TemporaryDirectory() as td:
    # CHỨNG MINH NGƯỢC end-to-end: ép lại đúng nhánh CŨ (bỏ exclude_reserved) ⇒ churn vô ích
    br = FakeBroker([mkquote(2269)])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200})
    ps, c = seed_open_child(ex, o, qty=200, price=13000.0)
    _orig = ex._child_qty
    ex._child_qty = lambda *a, **k: _orig(*a, **{**k, "exclude_reserved": 0})
    ex._cancel_stale(NOW)
    ex._place_slices(NOW, "CONT", (), None)
    same_px_qty = (len(br.placed) == 1 and br.placed[0]["qty"] == 200
                   and br.placed[0]["price"] == 13000.0)
    check("G3 CHỨNG MINH NGƯỢC — nhánh cũ huỷ rồi đặt lại Y HỆT 200cp@13.000 (churn vô ích, "
          "đúng như journal thật)", br.cancelled == ["54921"] and same_px_qty,
          f"cancel={br.cancelled} place={br.placed}")
    check("G4 CHỨNG MINH NGƯỢC — journal nhánh cũ = CANCEL_STALE + PLACE",
          journal_events(ex) == ["CANCEL_STALE", "PLACE"], str(journal_events(ex)))

# =============================================================== H. REFRESH_SKIP × HYBRID
print("H. HYBRID BẬT (đúng cấu hình paper thật) ⇒ hai đường tính KL vẫn phải KHỚP")
# Vì sao nhóm này phải có: cùng một lớp lỗi với bug gốc. `_would_be_unchanged` hỏi "huỷ rồi
# đặt lại có ra ĐÚNG giá+KL cũ không"; nếu đường KIỂM TRA và đường ĐẶT không áp CÙNG các
# trần thì hai bên ra hai số khác nhau ⇒ CANCEL_STALE mỗi chu kỳ ⇒ mất ưu tiên FIFO vô ích,
# đúng triệu chứng DRI 08-10 chỉ khác nguyên nhân. Trần HYBRID (`_hybrid_block_cap`) là trần
# THỨ HAI như vậy, và nó chỉ được áp khi `now` được truyền vào `_child_qty`. Trước nhóm này
# KHÔNG bộ nào phủ: bộ refresh_skip ghim `fill_timing_enabled=False`, còn
# hybrid_fill_timing_selfcheck.py không chạm `_would_be_unchanged`.
NOW_H = dt.datetime(2099, 1, 5, 11, 5, 0)     # trong block MUA đầu tiên (11:00-11:15)

with tempfile.TemporaryDirectory() as td:
    # H1 — trần PARTICIPATION ràng buộc (đúng ca DRI thật) + HYBRID bật: fix vẫn phải sống.
    q = mkquote(day_volume=2269)
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 200}, hybrid=True)
    ps = ex.state["parents"][o.id]
    c = {"oid": "54921", "qty": 200, "price": 13000.0, "filled": 0, "status": "open",
         "ts": (NOW_H - dt.timedelta(minutes=9)).isoformat(timespec="seconds")}
    ps["children"].append(c); ps["filled"] = 0; ps["last_slice_ts"] = c["ts"]
    ex._cancel_stale(NOW_H)
    check("H1 participation binding + HYBRID bật ⇒ vẫn REFRESH_SKIP (fix không bị HYBRID vô hiệu)",
          journal_events(ex) == ["REFRESH_SKIP"] and br.cancelled == [],
          f"journal={journal_events(ex)} cancel={br.cancelled}")

with tempfile.TemporaryDirectory() as td:
    # H2/H3 — đảo vai: thanh khoản DÀY nên participation KHÔNG ràng buộc, giờ chính TRẦN
    # HYBRID quyết định KL (ceil(2800/5 block còn lại)=560 → round_lot 500). Đây là ca duy
    # nhất chứng minh `_would_be_unchanged` có truyền `now`: bỏ `now` đi thì đường kiểm tra
    # trả 2800 còn đường đặt trả 500 ⇒ lệch ⇒ huỷ+đặt lại mỗi chu kỳ.
    q = mkquote(day_volume=5_000_000)
    br = FakeBroker([q])
    o = dri_order()
    ex = make_executor(td, br, [o], shared={"DRI": 500}, hybrid=True)
    ps = ex.state["parents"][o.id]
    c = {"oid": "77001", "qty": 500, "price": 13000.0, "filled": 0, "status": "open",
         "ts": (NOW_H - dt.timedelta(minutes=9)).isoformat(timespec="seconds")}
    ps["children"].append(c); ps["filled"] = 0; ps["last_slice_ts"] = c["ts"]
    px = ex._limit_price(o, q, cross=True)
    qty_with_now = ex._child_qty(o, ps, q, px, NOW_H, exclude_reserved=500)
    qty_no_now = ex._child_qty(o, ps, q, px, exclude_reserved=500)
    check("H2 TRẦN HYBRID thật sự là ràng buộc ở kịch bản này (nếu không, H3 vô nghĩa)",
          qty_with_now == 500 and qty_no_now != qty_with_now,
          f"có `now`={qty_with_now}cp · không `now`={qty_no_now}cp")
    ex._cancel_stale(NOW_H)
    check("H3 trần HYBRID ràng buộc ⇒ REFRESH_SKIP (hai đường áp CÙNG trần, không churn)",
          journal_events(ex) == ["REFRESH_SKIP"] and br.cancelled == [],
          f"journal={journal_events(ex)} cancel={br.cancelled}")

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ ALL PASS")
