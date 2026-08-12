# -*- coding: utf-8 -*-
"""Self-check P2 — mẫu số pacing = KL KỲ VỌNG tới giờ này + clamp đuôi trên TAPE THẬT.

Context (job Taylor_20260812_095213; nghiên cứu Taylor_20260812_091343):
`ceil_allow = 30% × KL ĐÃ khớp trong ngày` lấy mẫu số là đại lượng phản ánh thị trường KHÔNG
CÓ TA ⇒ đầu phiên allowance ≈0. Ca thật TV1 2026-08-11: 12.400cp có sẵn ở giá ≤ trần, bot khớp
100cp; lệnh con đi 100→200→300cp (đúng chữ ký "bám 30% KL luỹ kế").

P2: mẫu số = max(KL đã khớp, ADV20_cp × f(t)) + trần đuôi fill_fleet ≤ 50% tape THẬT.

BẤT BIẾN của file này:
  • MẶC ĐỊNH TẮT ⇒ `_child_qty` byte-identical, kể cả khi có truyền `now`.
  • Nới mẫu số và clamp đuôi phải CÙNG bật/CÙNG tắt — không có đường nào nới mà mất clamp.
  • KHÔNG chạm lệnh BÁN, KHÔNG chạm lệnh non-ADV20 (BAL/LAG), kể cả khi cờ BẬT. Đây là điều
    kiện an toàn với EXTREME-regime: lệnh cắt lỗ khẩn là lệnh BÁN, và chiều MUA khi EXTREME đã
    bị `EXTREME_PAUSE` chặn TRƯỚC khi tới `_child_qty`.
  • Mọi ca "P2 mở khoá KL" đều có CA CHỨNG MINH NGƯỢC (tắt cờ ⇒ thật sự bị bóp).

Run: /home/trido/thanhdt/wc_venv/bin/python expected_volume_pacing_selfcheck.py  (exit 0 = pass)
"""
import datetime as dt
import glob
import json
import os
import sys
import tempfile

# §5b: selfcheck chạm Executor PHẢI chặn _publish_bot_event ghi lên bus THẬT.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.plan import PlannedOrder, TradePlan  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.config import load_config, EXEC_DIR  # noqa: E402
from trading_bot.vn_market import LOT  # noqa: E402

TAG = "selfcheck-expvol"          # tag RIÊNG (§7 — không dùng chung với selfcheck khác)
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}*")):
    os.remove(f)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


class FakeQuote:
    def __init__(self, day_volume):
        self.day_volume = day_volume

    def ok(self):
        return True


class _NullBroker:
    name = "null"

    def get_quote(self, *a, **k):
        raise AssertionError("get_quote không nên bị gọi trong self-check này")


def write_state(dirpath, ticker, account, adv_ref_vnd):
    os.makedirs(dirpath, exist_ok=True)
    p = os.path.join(dirpath, f"state_{ticker}_{account}.json")
    json.dump({"ticker": ticker, "account": account, "book": "DISCRETIONARY_SPECIAL",
               "status": "active", "adv_ref_vnd": adv_ref_vnd},
              open(p, "w", encoding="utf-8"))
    return p


def make_ex(tmp, orders, on, shared=None, account=TAG, disc_dir=None, extra_cfg=None):
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=orders,
                     account=account, created_at="2099-01-01T00:00:00")
    cfg = load_config()
    cfg["mode"] = "paper"
    cfg["expected_volume_pacing_enabled"] = on
    if extra_cfg:
        cfg.update(extra_cfg)
    ex = Executor(plan, _NullBroker(), cfg, shared={} if shared is None else shared)
    ex.state_file = os.path.join(tmp, "state.json")
    ex.journal_file = os.path.join(tmp, "journal.csv")
    if disc_dir:
        ex._disc_adv20_vnd = ex._load_discretionary_adv20_basis(base_dir=disc_dir)
    return ex


# TV1 thật: adv_ref_vnd 701tr, giá ~19.900 ⇒ ADV20 ≈ 35.226cp/phiên.
ADV_VND, PX = 701_000_000, 19_900
ADV_CP = ADV_VND / PX
D = dt.date(2099, 1, 4)


def T(hh, mm):
    return dt.datetime.combine(D, dt.time(hh, mm))


def disc_order(oid="D1", qty=3300):
    return PlannedOrder(id=oid, ticker="TV1", side="buy", qty=qty, ref_price=PX,
                        book="DISCRETIONARY_SPECIAL")


# ================================================================ A. MẶC ĐỊNH = byte-identical
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    o = disc_order()
    ex_off = make_ex(tmp, [o], on=False, disc_dir=dd)
    ex_on = make_ex(tmp, [o], on=True, disc_dir=dd)
    ps_off = ex_off.state["parents"][o.id]
    ps_on = ex_on.state["parents"][o.id]
    same = True
    for vol in (0, 100, 500, 3000, 12400, 42700):
        for now in (None, T(9, 15), T(10, 0), T(11, 30), T(14, 30)):
            a = ex_off._child_qty(o, ps_off, FakeQuote(vol), PX, now)
            b = ex_on._child_qty(o, ps_on, FakeQuote(vol), PX, now) if now is None else None
            if b is not None and a != b:
                same = False
    check("A1 cờ TẮT: mọi (KL ngày × giờ) cho ra đúng hành vi cũ", same)
    # cờ BẬT nhưng now=None (đường gọi không có thời gian) ⇒ vẫn hành vi cũ
    ok = all(ex_off._child_qty(o, ps_off, FakeQuote(v), PX, None)
             == ex_on._child_qty(o, ps_on, FakeQuote(v), PX, None)
             for v in (0, 100, 500, 3000, 12400))
    check("A2 cờ BẬT nhưng now=None ⇒ byte-identical (cùng quy ước với HYBRID)", ok)

# ================================================================ B. Ca thật TV1 08-11
# 09:40, tape mới 500cp, người bán duy nhất của phiên xuất hiện.
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    o = disc_order()
    ex_off = make_ex(tmp, [o], on=False, disc_dir=dd)
    ex_on = make_ex(tmp, [o], on=True, disc_dir=dd)
    q = FakeQuote(day_volume=500)
    off = ex_off._child_qty(o, ex_off.state["parents"][o.id], q, PX, T(9, 40))
    on = ex_on._child_qty(o, ex_on.state["parents"][o.id], q, PX, T(9, 40))
    # f(09:40) ≈ 0,127 ⇒ kỳ vọng ≈ 4.474cp ⇒ ceil = 30%×4.474 = 1.342; clamp = 500−0 = 500
    check("B1 [CHỨNG MINH NGƯỢC] cờ TẮT: 09:40 tape 500cp ⇒ chỉ hiện được 100cp "
          "(đúng chữ ký thất bại thật 08-11)", off == 100, f"off={off}")
    check("B2 cờ BẬT ⇒ hiện được NHIỀU HƠN hẳn", on > off, f"on={on} vs off={off}")
    check("B3 nhưng KHÔNG vượt trần đuôi 50% tape thật (V−2F = 500)", on <= 500, f"on={on}")

    # Tape đã dày (12.400cp lúc 10:30 như TV1 08-11) — P2 vẫn phải tôn trọng floor 10% ADV20.
    q2 = FakeQuote(day_volume=12_400)
    on2 = ex_on._child_qty(o, ex_on.state["parents"][o.id], q2, PX, T(10, 30))
    floor_allow = int(0.10 * ADV_VND / PX)
    check("B4 tape dày: P2 KHÔNG được vượt floor 10% ADV20 (guard cũ còn nguyên)",
          on2 <= floor_allow, f"on2={on2}, floor={floor_allow}")

# ================================================================ C. Đường cong f(t)
with tempfile.TemporaryDirectory() as tmp:
    ex = make_ex(tmp, [disc_order()], on=True)
    f = ex._expected_vol_frac
    check("C1 f tại mốc lưới khớp số đo (09:15=0,045 · 11:00=0,411 · 14:30=0,958)",
          abs(f(T(9, 15)) - 0.045) < 1e-9 and abs(f(T(11, 0)) - 0.411) < 1e-9
          and abs(f(T(14, 30)) - 0.958) < 1e-9,
          f"{f(T(9,15))}/{f(T(11,0))}/{f(T(14,30))}")
    check("C2 trước mốc đầu ⇒ 0,0 (⇒ max(cum_vol,0)=cum_vol = hành vi cũ, KHÔNG phải nhánh lỗi)",
          f(T(8, 0)) == 0.0)
    check("C3 sau mốc cuối (ATC) ⇒ 1,0", f(T(14, 50)) == 1.0 and f(T(23, 59)) == 1.0)
    check("C4 nội suy tuyến tính giữa 2 mốc", abs(f(T(9, 22, )) - (0.045 + (0.082 - 0.045) * 7 / 15)) < 1e-9,
          f"{f(T(9,22))}")
    check("C5 đơn điệu không giảm suốt phiên",
          all(f(T(h, m)) >= f(T(h, m - 5) if m >= 5 else T(h - 1, 55))
              for h in range(9, 15) for m in range(5, 60, 5)))
    check("C6 nghỉ trưa (11:30→13:00) f gần như KHÔNG tăng — đúng thực tế thị trường VN",
          f(T(13, 0)) - f(T(11, 30)) < 0.02, f"{f(T(13,0))} vs {f(T(11,30))}")

# ================================================================ D. Cấu hình hỏng ⇒ fail-safe
BAD = [("D1 curve rỗng", {"expected_volume_curve": []}),
       ("D2 curve 1 điểm", {"expected_volume_curve": [[600, 0.2]]}),
       ("D3 curve KHÔNG đơn điệu", {"expected_volume_curve": [[555, 0.5], [600, 0.2], [885, 1.0]]}),
       ("D4 curve f>1", {"expected_volume_curve": [[555, 0.045], [600, 1.4], [885, 1.0]]}),
       ("D5 curve f âm", {"expected_volume_curve": [[555, -0.1], [600, 0.2], [885, 1.0]]}),
       ("D6 curve phút vô lý", {"expected_volume_curve": [[555, 0.045], [99999, 1.0]]}),
       ("D7 curve phần tử rác", {"expected_volume_curve": [[555, 0.045], "x"]}),
       ("D8 clamp = 0", {"expected_volume_tape_clamp": 0}),
       ("D9 clamp = 1 (ZeroDivisionError nếu không chặn)", {"expected_volume_tape_clamp": 1.0}),
       ("D10 clamp > 1", {"expected_volume_tape_clamp": 1.5}),
       ("D11 clamp âm", {"expected_volume_tape_clamp": -0.5}),
       ("D12 clamp chuỗi KHÔNG parse được", {"expected_volume_tape_clamp": "một nửa"})]
for nm, bad in BAD:
    with tempfile.TemporaryDirectory() as tmp:
        dd = os.path.join(tmp, "disc")
        write_state(dd, "TV1", TAG, ADV_VND)
        o = disc_order()
        ex_off = make_ex(tmp, [o], on=False, disc_dir=dd)
        ex_bad = make_ex(tmp, [o], on=True, disc_dir=dd, extra_cfg=bad)
        try:
            got = ex_bad._child_qty(o, ex_bad.state["parents"][o.id], FakeQuote(500), PX, T(9, 40))
            ref = ex_off._child_qty(o, ex_off.state["parents"][o.id], FakeQuote(500), PX, T(9, 40))
            check(f"{nm} ⇒ fail-safe về hành vi cũ (không raise)", got == ref, f"{got} vs {ref}")
        except Exception as exc:
            check(f"{nm} ⇒ fail-safe về hành vi cũ (không raise)", False, f"RAISE {exc!r}")

# ================================================================ E. Clamp đuôi giữ bất biến 50%
# Mô phỏng phiên MỎNG (KL thật << ADV20 — 12,7% số phiên thuộc nhóm này): lặp "hiện rồi khớp
# hết ngay" (giả định XẤU NHẤT) và kiểm tra fill luỹ kế fleet KHÔNG BAO GIỜ vượt 50% tape thật.
def run_session(on, tape0=3000, at=None):
    with tempfile.TemporaryDirectory() as tmp:
        dd = os.path.join(tmp, "disc")
        write_state(dd, "TV1", TAG, ADV_VND)
        o = disc_order(qty=50_000)     # nhu cầu lớn hơn mọi ràng buộc → guard phải là thứ chặn
        shared = {}
        ex = make_ex(tmp, [o], on=on, shared=shared, disc_dir=dd)
        ps = ex.state["parents"][o.id]
        V, F, worst, steps = tape0, 0, 0.0, 0
        while steps < 40:
            qty = ex._child_qty(o, ps, FakeQuote(V), PX, at or T(10, 0))
            if qty < LOT:
                break
            F += qty
            V += qty                   # fill của ta CŨNG là tape (bản chất của khớp lệnh)
            shared["TV1"] = F
            ps["filled"] = F
            worst = max(worst, F / V)
            steps += 1
        return F, V, worst, steps


F_on, V_on, worst_on, steps_on = run_session(True)
F_off, _, worst_off, _ = run_session(False)
check("E1 fill luỹ kế fleet KHÔNG vượt 50% tape thật ở bất kỳ bước nào",
      worst_on <= 0.5 + 1e-9, f"max F/V = {worst_on:.4f} sau {steps_on} bước")
check("E2 hội tụ, không lặp vô hạn", steps_on < 40, f"steps={steps_on}")
check("E3 [CHỨNG MINH NGƯỢC] cùng phiên mỏng đó, cờ TẮT gom được ÍT hơn hẳn",
      F_on > F_off, f"ON={F_on}cp vs OFF={F_off}cp")
check("E4 ràng buộc chặn ở đây là trần 30% (KHÔNG phải clamp) — clamp là backstop, "
      "và backstop không được là thứ bind ở phiên bình thường", worst_on < 0.5, f"{worst_on:.4f}")

# clamp phải là RÀNG BUỘC BINDING trên phiên mỏng, không phải trang trí
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    o = disc_order(qty=50_000)
    ex = make_ex(tmp, [o], on=True, disc_dir=dd)
    got = ex._child_qty(o, ex.state["parents"][o.id], FakeQuote(1000), PX, T(14, 30))
    # f(14:30)=0,958 ⇒ kỳ vọng 33.747 ⇒ ceil=10.124; floor=3.522; clamp=1000−0=1000 → clamp thắng
    check("E5 phiên MỎNG cuối phiên: clamp tape (1.000) THẮNG cả floor ADV20 (3.522) "
          "— clamp là ràng buộc BINDING thật, không phải trang trí", got == 1000, f"got={got}")

# clamp nhận cấu hình dạng chuỗi số: CỐ Ý chấp nhận (float("0.5") ra đúng 0,5 — không có cách
# nào sai âm thầm). Khẳng định điều đó bằng test thay vì để nó là hành vi không ai biết.
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    o = disc_order()
    a = make_ex(tmp, [o], on=True, disc_dir=dd)
    b = make_ex(tmp, [o], on=True, disc_dir=dd, extra_cfg={"expected_volume_tape_clamp": "0.5"})
    check("E6 clamp dạng chuỗi số '0.5' ⇒ CÙNG kết quả với 0.5 (coerce có chủ đích)",
          a._child_qty(o, a.state["parents"][o.id], FakeQuote(500), PX, T(9, 40))
          == b._child_qty(o, b.state["parents"][o.id], FakeQuote(500), PX, T(9, 40)))

# ================================================================ F. Không tape ⇒ không đổi
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    o = disc_order()
    ex_off = make_ex(tmp, [o], on=False, disc_dir=dd)
    ex_on = make_ex(tmp, [o], on=True, disc_dir=dd)
    a = ex_off._child_qty(o, ex_off.state["parents"][o.id], FakeQuote(0), PX, T(9, 15))
    b = ex_on._child_qty(o, ex_on.state["parents"][o.id], FakeQuote(0), PX, T(9, 15))
    check("F1 day_volume=0 (halt/chưa có tape): P2 KHÔNG áp clamp ⇒ hành vi cũ nguyên vẹn. "
          "Áp clamp ở đây sẽ là REGRESSION (0 tape ⇒ chặn sạch)", a == b and b > 0, f"{a}/{b}")

# ================================================================ G. Không chạm BÁN / non-ADV20
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    sell = PlannedOrder(id="S1", ticker="TV1", side="sell", qty=3300, ref_price=PX,
                        book="DISCRETIONARY_SPECIAL")
    bal = PlannedOrder(id="B1", ticker="FPT", side="buy", qty=3000, ref_price=100_000, book="BAL")
    capit_sell = PlannedOrder(id="CS", ticker="SAB", side="sell", qty=3000, ref_price=50_000,
                              book="CAPIT")
    ex_off = make_ex(tmp, [sell, bal, capit_sell], on=False, disc_dir=dd)
    ex_on = make_ex(tmp, [sell, bal, capit_sell], on=True, disc_dir=dd)
    ok = True
    for o in (sell, bal, capit_sell):
        for vol in (0, 500, 3000, 42700):
            for now in (T(9, 15), T(9, 40), T(11, 0), T(14, 30)):
                px = o.ref_price
                if (ex_off._child_qty(o, ex_off.state["parents"][o.id], FakeQuote(vol), px, now)
                        != ex_on._child_qty(o, ex_on.state["parents"][o.id], FakeQuote(vol), px, now)):
                    ok = False
    check("G1 lệnh BÁN + lệnh non-ADV20 (BAL) + CAPIT BÁN: cờ BẬT hay TẮT đều RA CÙNG KL", ok)
    check("G2 route: chỉ MUA-ADV20 vào nhánh P2 (`_adv20_basis_for` trả None cho 3 lệnh trên)",
          all(ex_on._adv20_basis_for(o) is None for o in (sell, bal, capit_sell)))

# ================================================================ H. EXTREME-regime KHÔNG bị P2 chặn
# Hai tầng, kiểm cả hai:
#   (i)  chiều MUA khi EXTREME_DOWN bị `EXTREME_PAUSE` chặn TRƯỚC `_child_qty` (executor.py:1404)
#        ⇒ P2 không thể làm chậm gì mà nó vốn không chạy.
#   (ii) lệnh BÁN (chính là lệnh cắt lỗ khẩn của EXTREME) KHÔNG bao giờ vào nhánh ADV20 vì
#        `_is_capit_buy`/`_is_discretionary_special_buy` đều yêu cầu side=="buy".
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    sell = PlannedOrder(id="XS", ticker="TV1", side="sell", qty=3300, ref_price=PX,
                        book="DISCRETIONARY_SPECIAL")
    buy = disc_order("XB")
    ex = make_ex(tmp, [sell, buy], on=True, disc_dir=dd,
                 extra_cfg={"extreme_regime_enabled": True})
    check("H1 EXTREME bật: lệnh BÁN vẫn KHÔNG đi vào nhánh ADV20/P2",
          ex._adv20_basis_for(sell) is None)
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "trading_bot", "executor.py"), encoding="utf-8").read()
    check("H2 chiều MUA khi EXTREME_DOWN bị chặn TRƯỚC khi tính KL (EXTREME_PAUSE + continue)",
          'if extreme_down and o.side == "buy":' in src
          and src.split('if extreme_down and o.side == "buy":')[1].split("continue")[0].count(
              "_child_qty") == 0)
    check("H3 nhánh P2 chỉ tồn tại bên trong `if adv20_vnd and px:` (mua-ADV20)",
          src.index("_expected_vol_basis(o, adv20_vnd") > src.index("adv20_vnd = self._adv20_basis_for(o)"))

# ================================================================ I. HYBRID vẫn thắng khi chặt hơn
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    o = disc_order(qty=3300)
    ex = make_ex(tmp, [o], on=True, disc_dir=dd)
    ps = ex.state["parents"][o.id]
    real = ex._child_qty(o, ps, FakeQuote(12_400), PX, T(10, 0))
    ex._hybrid_block_cap = lambda *a, **k: 200      # giả lập trần HYBRID chặt hơn
    capped = ex._child_qty(o, ps, FakeQuote(12_400), PX, T(10, 0))
    check("I1 trần HYBRID chặt hơn vẫn CẮT sau P2 (P2 không được vượt mặt tầng lịch trải)",
          capped == 200 and real > 200, f"real={real}, capped={capped}")

# ================================================================ J. Journal 1 lần/parent/phiên
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    o = disc_order()
    ex = make_ex(tmp, [o], on=True, disc_dir=dd)
    for _ in range(25):
        ex._child_qty(o, ex.state["parents"][o.id], FakeQuote(3000), PX, T(10, 0))
    rows = [ln for ln in open(ex.journal_file, encoding="utf-8") if "EXPVOL_PACING" in ln]
    check("J1 journal EXPVOL_PACING ghi ĐÚNG 1 lần dù _child_qty chạy 25 lần "
          "(_place_slices + _would_be_unchanged mỗi 20s)", len(rows) == 1, f"{len(rows)} dòng")

# ================================================================ K. 2 đường tính RA CÙNG SỐ
# `_would_be_unchanged` gọi `_child_qty(exclude_reserved=…)`; nếu P2 làm 2 đường lệch nhau thì
# mỗi chu kỳ sẽ huỷ+đặt lại vô ích (mất ưu tiên FIFO) — đúng bug DRI 2026-08-10.
with tempfile.TemporaryDirectory() as tmp:
    dd = os.path.join(tmp, "disc")
    write_state(dd, "TV1", TAG, ADV_VND)
    o = disc_order()
    ex = make_ex(tmp, [o], on=True, shared={"TV1": 400}, disc_dir=dd)
    ps = ex.state["parents"][o.id]
    place = ex._child_qty(o, ps, FakeQuote(12_400), PX, T(10, 0))
    ex.shared["TV1"] = 400 + place                        # lệnh đang treo giữ reservation
    recheck = ex._child_qty(o, ps, FakeQuote(12_400), PX, T(10, 0), exclude_reserved=place)
    check("K1 đường KIỂM TRA (exclude_reserved) ra CÙNG KL với đường ĐẶT ⇒ không huỷ+đặt lại vô ích",
          recheck == place, f"place={place}, recheck={recheck}")

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ tất cả PASS — P2 mặc định byte-identical; clamp giữ bất biến ≤50% tape; "
      "không chạm BÁN/non-ADV20 nên EXTREME không bị làm chậm.")
