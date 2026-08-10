# -*- coding: utf-8 -*-
"""Self-check cho lịch thực thi HYBRID (`fill_timing_hybrid_enabled`) — job Taylor_20260810_034544.

Cơ chế cần chứng minh (thiết kế: `mike/agents/Taylor/research/twap_vs_window_execution_20260804.md`
§6/§10 — 663 phiên, nến 15'):
  MUA  = trải 5 block trong 11:00-13:45 (KHÔNG gom 1 điểm)
  BÁN  = trải 4 block trong 09:15-10:15 (KHÔNG gom tại mở cửa)
và — điểm then chốt — việc "trải" phải THẬT: chỉ đổi interval là NO-OP vì 151/153 lệnh khớp
trọn trong 1 slice (checkpoint paper Taylor_20260804_091703), nên phải có TRẦN KL mỗi block.

Ca kiểm:
  A. Regression — cờ TẮT (mặc định) ⇒ `_fill_timing_mult` và `_child_qty` y hệt trước.
  B. Lịch block đúng nhãn đo được; cửa sổ CŨ (10:45 BUY) nay ngoài block ⇒ HYBRID THAY, không cộng dồn.
  C. blocks_left đếm đúng ở mọi mốc (trước / trong / sau cửa sổ).
  D. Trải KL thật: 5 lần đặt = 5 phần, KÈM CA CHỨNG MINH NGƯỢC (tắt cờ ⇒ đi trọn 1 lần).
  E. Không bao giờ kẹt hàng: hết cửa sổ ⇒ hết trần, phần dư đi trọn.
  F. Tự sửa sai: lỡ block đầu ⇒ phần dư dồn sang các block còn lại.
  G. Cổng: urgency=high / live+live_gate / fill_timing_enabled=False ⇒ HYBRID không áp.
  H. Fail-safe cấu hình rác (nhãn giờ hỏng / list rỗng) ⇒ không ném lỗi, không kẹt hàng.
  I. Cổ phiếu lẻ (<1 lô) đi trọn; lệnh nhỏ ⇒ trần tối thiểu 1 lô (không sinh lệnh 0).
  J. `_would_be_unchanged` dùng CÙNG trần ⇒ không huỷ+đặt lại vô ích mỗi chu kỳ.
  K. Journal note giữ tương thích bộ đếm adherence sẵn có ("ft:" ∧ "in-window").
  L. Hai chiều không lẫn lịch (BUY 09:15 ngoài block; SELL 13:00 ngoài block).
  M. End-to-end `_place_slices`: lệnh thật đi ra broker đúng KL đã trải.

Chạy: python3 hybrid_fill_timing_selfcheck.py   (exit 0 = pass)
"""
import datetime as dt
import glob
import os
import sys

# §5b coding_guidelines: chặn _publish_bot_event ghi lên bus THẬT — phải đặt TRƯỚC
# khi bất kỳ Executor nào được dựng.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.config import DEFAULTS, EXEC_DIR          # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan       # noqa: E402
from trading_bot.executor import Executor                  # noqa: E402
from trading_bot.vn_market import LOT                      # noqa: E402

# Executor.__init__ nạp state.json theo (account, plan_date) mặc định TRƯỚC khi test kịp
# đổi hướng — file cũ cùng tag làm hỏng state khởi đầu (xem ghost_order_selfcheck.py TAG).
TAG = "selfcheck-hybridft"
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(_f)

SYM = "TST"
PX = 20_000.0


class FakeQuote:
    def __init__(self, day_volume=5_000_000):
        self.symbol = SYM; self.exchange = "HOSE"
        self.last = PX; self.ref = PX; self.bid = PX; self.ask = PX
        self.floor = PX * 0.93; self.ceiling = PX * 1.07
        self.day_volume = day_volume

    def ok(self):
        return True


class FakeBroker:
    name = "fake"

    def __init__(self):
        self.quote = FakeQuote(); self.placed = []; self._oid = 0

    def get_quote(self, sym):
        return self.quote

    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        self._oid += 1
        self.placed.append(dict(symbol=symbol, qty=qty, side=side, price=price))
        return f"OID{self._oid}"

    def cancel_order(self, oid):
        pass

    def poll_orders(self):
        return {}

    def get_cash(self):
        return 10_000_000_000

    def get_max_buy_qty(self, symbol, price, loan_package_id=None):
        return 1_000_000


def mk(orders, hybrid=True, **cfg_over):
    # §23 hệ luận 1: mỗi Executor phải khởi đầu SẠCH — Executor._save_state() của ca trước
    # ghi ra đúng đường dẫn (account=TAG, plan_date) này, ca sau sẽ "resume" trạng thái đó
    # và kết quả phụ thuộc thứ tự chạy. Xoá trước khi dựng.
    for _s in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*state.json")):
        os.remove(_s)
    cfg = dict(DEFAULTS)
    cfg.update({"mode": "paper", "fill_timing_hybrid_enabled": hybrid,
                # tách khỏi các layer khác để ca kiểm chỉ đo HYBRID
                "gap_adaptive_enabled": False, "extreme_regime_enabled": False,
                "chase_cap_vol_scale_enabled": False})
    cfg.update(cfg_over)
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account=TAG,
                     created_at="2099-01-01T00:00:00")
    ex = Executor(plan, FakeBroker(), cfg)
    ex._gap_ref.clear()      # §23: không để test phụ thuộc rvol THẬT (đổi theo ngày)
    return ex


def order(side="buy", qty=5000, oid=None, urgency="normal"):
    return PlannedOrder(id=oid or f"{side.upper()}-{SYM}-01", ticker=SYM, side=side,
                        qty=qty, ref_price=PX, book="LAG", play_type="LAG_HI",
                        urgency=urgency)


def T(h, m):
    return dt.datetime(2099, 1, 1, h, m, 0)


fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


OUT = DEFAULTS["fill_timing_outside_mult"]                    # 4.0
BLK = DEFAULTS["hybrid_block_min"] / DEFAULTS["slice_interval_min"]   # 15/8 = 1.875

# ───────────────────────────── A. Regression: cờ TẮT ⇒ hành vi CŨ nguyên vẹn
print("\nA. Regression — fill_timing_hybrid_enabled=False (mặc định)")
# PAPER 2026-08-10 (job Taylor_20260810_034544, quant-skeptic CONFIRMED vòng 5, user duyệt):
# DEFAULTS nay là True (bật trên paper). fill_timing_live_gate vẫn True nên KHÔNG account
# live nào bị ảnh hưởng — mọi test bên dưới dùng hybrid=False TƯỜNG MINH (không dựa DEFAULTS)
# nên hành vi "cờ tắt" vẫn được test đủ dù DEFAULTS đã đổi.
check("mặc định trong DEFAULTS là BẬT (PAPER 2026-08-10)", DEFAULTS["fill_timing_hybrid_enabled"] is True)
ob, os_ = order("buy"), order("sell")
ex_off = mk([ob, os_], hybrid=False)
old = {(s, h, m): mk([ob, os_], hybrid=False)._fill_timing_mult(ob if s == "buy" else os_, T(h, m))
       for s in ("buy", "sell") for h, m in [(9, 20), (10, 50), (11, 20), (13, 10), (14, 0)]}
check("BUY cửa sổ cũ 10:50 = 1.0", old[("buy", 10, 50)] == 1.0)
check("BUY 09:20 ngoài cửa sổ cũ = 4.0", old[("buy", 9, 20)] == OUT)
check("BUY phiên chiều 13:10 = 1.0 (quy tắc cũ)", old[("buy", 13, 10)] == 1.0)
check("SELL 09:20 cửa sổ Open cũ = 1.0", old[("sell", 9, 20)] == 1.0)
check("SELL 10:50 ngoài = 4.0", old[("sell", 10, 50)] == OUT)
ps_off = ex_off.state["parents"][ob.id]
check("_child_qty(now=None) và _child_qty(now) bằng nhau khi cờ TẮT",
      ex_off._child_qty(ob, ps_off, ex_off.broker.quote, PX)
      == ex_off._child_qty(ob, ps_off, ex_off.broker.quote, PX, T(11, 0)) == 5000,
      f"{ex_off._child_qty(ob, ps_off, ex_off.broker.quote, PX, T(11, 0))}")

# ───────────────────────────── B/L. Lịch block đúng nhãn đã đo
print("\nB+L. Lịch block — đúng các nến 15' đã đo, hai chiều không lẫn")
ex = mk([ob, os_])
for h, m, exp, lbl in [(11, 0, BLK, "BUY 11:00 block-1"), (11, 14, BLK, "BUY 11:14 trong block-1"),
                       (11, 15, BLK, "BUY 11:15 block-2"), (11, 30, OUT, "BUY 11:30 nghỉ trưa"),
                       (12, 30, OUT, "BUY 12:30 nghỉ trưa"), (13, 0, BLK, "BUY 13:00 block-3"),
                       (13, 30, BLK, "BUY 13:30 block-5"), (13, 44, BLK, "BUY 13:44 cuối block-5"),
                       (13, 45, OUT, "BUY 13:45 hết cửa sổ"), (14, 0, OUT, "BUY 14:00 sau cửa sổ"),
                       (10, 50, OUT, "BUY 10:50 — CỬA SỔ CŨ nay ngoài block (HYBRID THAY, không cộng dồn)"),
                       (9, 15, OUT, "BUY 09:15 (lịch SELL) ngoài block")]:
    check(lbl, ex._fill_timing_mult(ob, T(h, m)) == exp, f"{ex._fill_timing_mult(ob, T(h, m))}")
for h, m, exp, lbl in [(9, 15, BLK, "SELL 09:15 block-1"), (9, 45, BLK, "SELL 09:45 block-3"),
                       (10, 0, BLK, "SELL 10:00 block-4"), (10, 14, BLK, "SELL 10:14 cuối block-4"),
                       (10, 15, OUT, "SELL 10:15 hết cửa sổ"), (11, 0, OUT, "SELL 11:00 (lịch BUY) ngoài block"),
                       (13, 0, OUT, "SELL 13:00 (lịch BUY) ngoài block")]:
    check(lbl, ex._fill_timing_mult(os_, T(h, m)) == exp, f"{ex._fill_timing_mult(os_, T(h, m))}")
check("nhịp trong block = 1 slice/block (15' > 8' mặc định, không bao giờ nhanh hơn)", BLK > 1.0)

# ───────────────────────────── C. blocks_left
print("\nC. blocks_left — đếm số block chưa kết thúc")
for h, m, exp in [(9, 0, 5), (11, 0, 5), (11, 15, 4), (11, 40, 3), (13, 0, 3), (13, 15, 2),
                  (13, 30, 1), (13, 45, 0), (14, 30, 0)]:
    check(f"BUY {h:02d}:{m:02d} left={exp}", ex._hybrid_sched(ob, T(h, m))[1] == exp,
          f"{ex._hybrid_sched(ob, T(h, m))[1]}")
for h, m, exp in [(9, 0, 4), (9, 15, 4), (9, 30, 3), (10, 0, 1), (10, 15, 0)]:
    check(f"SELL {h:02d}:{m:02d} left={exp}", ex._hybrid_sched(os_, T(h, m))[1] == exp,
          f"{ex._hybrid_sched(os_, T(h, m))[1]}")

# ───────────────────────────── D. Trải KL THẬT + ca chứng minh ngược
print("\nD. Trải KL thật qua 5 block (KÈM ca chứng minh ngược: tắt cờ ⇒ đi trọn 1 lần)")
o5 = order("buy", qty=5000)
exd = mk([o5]); psd = exd.state["parents"][o5.id]
seq = []
for h, m in [(11, 0), (11, 15), (13, 0), (13, 15), (13, 30)]:
    q = exd._child_qty(o5, psd, exd.broker.quote, PX, T(h, m))
    seq.append(q)
    psd["filled"] += q                      # giả lập khớp trọn block đó
check("5 block ⇒ 5 phần 1000cp đều nhau", seq == [1000, 1000, 1000, 1000, 1000], f"{seq}")
check("tổng 5 phần = đúng KL lệnh", sum(seq) == 5000, f"{sum(seq)}")
exn = mk([o5], hybrid=False); psn = exn.state["parents"][o5.id]
check("CHỨNG MINH NGƯỢC: tắt cờ ⇒ 11:00 đi TRỌN 5000 trong 1 slice (nên chỉ đổi interval là NO-OP)",
      exn._child_qty(o5, psn, exn.broker.quote, PX, T(11, 0)) == 5000,
      f"{exn._child_qty(o5, psn, exn.broker.quote, PX, T(11, 0))}")
o4 = order("sell", qty=4000)
exs = mk([o4]); pss = exs.state["parents"][o4.id]
check("SELL 09:15 trải 1/4 (KHÔNG gom tại mở cửa)",
      exs._child_qty(o4, pss, exs.broker.quote, PX, T(9, 15)) == 1000,
      f"{exs._child_qty(o4, pss, exs.broker.quote, PX, T(9, 15))}")
exs2 = mk([o4], hybrid=False)
check("CHỨNG MINH NGƯỢC: tắt cờ ⇒ SELL 09:15 gom trọn 4000",
      exs2._child_qty(o4, exs2.state["parents"][o4.id], exs2.broker.quote, PX, T(9, 15)) == 4000)

# ───────────────────────────── E. Không kẹt hàng sau cửa sổ
print("\nE. Không bao giờ kẹt hàng vì lịch")
exe = mk([o5]); pse = exe.state["parents"][o5.id]
check("sau cửa sổ (14:00) ⇒ hết trần, phần dư đi trọn",
      exe._child_qty(o5, pse, exe.broker.quote, PX, T(14, 0)) == 5000,
      f"{exe._child_qty(o5, pse, exe.broker.quote, PX, T(14, 0))}")
check("block CUỐI (13:30, left=1) ⇒ hết trần, đi nốt",
      exe._child_qty(o5, pse, exe.broker.quote, PX, T(13, 30)) == 5000)
check("trước cửa sổ (09:00, BUY) trần vẫn là 1/5 (lớp 2 — lớp 1 là _hybrid_defer, ca N)",
      exe._child_qty(o5, pse, exe.broker.quote, PX, T(9, 0)) == 1000,
      f"{exe._child_qty(o5, pse, exe.broker.quote, PX, T(9, 0))}")

# ───────────────────────────── F. Tự sửa sai khi lỡ block
print("\nF. Tự sửa sai — lỡ 2 block đầu thì phần dư dồn sang block còn lại")
exf = mk([o5]); psf = exf.state["parents"][o5.id]
qf = exf._child_qty(o5, psf, exf.broker.quote, PX, T(13, 0))    # left=3, chưa khớp gì
check("lỡ 11:00+11:15 ⇒ 13:00 đặt ceil(5000/3)=1667 → làm tròn lô 1600 (> 1000)",
      qf == 1600, f"{qf}")

# ───────────────────────────── G. Cổng
print("\nG. Cổng — HYBRID không áp khi cổng đóng")
oh = order("buy", qty=5000, oid="BUY-URG", urgency="high")
exg = mk([oh]); psg = exg.state["parents"][oh.id]
check("urgency=high ⇒ mult 1.0 + không trần", exg._fill_timing_mult(oh, T(11, 0)) == 1.0
      and exg._child_qty(oh, psg, exg.broker.quote, PX, T(11, 0)) == 5000)
exl = mk([o5], mode="live")     # live + fill_timing_live_gate mặc định True
psl = exl.state["parents"][o5.id]
check("mode=live + live_gate ⇒ mult 1.0 + không trần (LIVE byte-identical)",
      exl._fill_timing_mult(o5, T(11, 0)) == 1.0
      and exl._child_qty(o5, psl, exl.broker.quote, PX, T(11, 0)) == 5000)
exm = mk([o5], fill_timing_enabled=False)
psm = exm.state["parents"][o5.id]
check("fill_timing_enabled=False ⇒ master tắt, cờ hybrid bị bỏ qua hoàn toàn",
      exm._fill_timing_mult(o5, T(11, 0)) == 1.0 and exm._fill_timing_mult(o5, T(9, 20)) == 1.0
      and exm._child_qty(o5, psm, exm.broker.quote, PX, T(11, 0)) == 5000)

# ───────────────────────────── H. Fail-safe cấu hình rác
print("\nH. Fail-safe — cấu hình block hỏng không được làm sập/kẹt phiên")
exb = mk([o5], hybrid_buy_blocks=["11:00", "khong-phai-gio", "13:00"])
psb = exb.state["parents"][o5.id]
check("nhãn giờ hỏng bị bỏ qua, không ném lỗi (left=2 tại 11:00)",
      exb._hybrid_sched(o5, T(11, 0))[1] == 2, f"{exb._hybrid_sched(o5, T(11, 0))[1]}")
check("… và vẫn đặt được lệnh (2500cp)",
      exb._child_qty(o5, psb, exb.broker.quote, PX, T(11, 0)) == 2500)
exz = mk([o5], hybrid_buy_blocks=[])
check("list block RỖNG ⇒ không trần, không kẹt hàng (đi trọn)",
      exz._child_qty(o5, exz.state["parents"][o5.id], exz.broker.quote, PX, T(11, 0)) == 5000)

# ───────────────────────────── I. Lô lẻ + lệnh nhỏ
print("\nI. Cổ phiếu lẻ và lệnh nhỏ")
oo = order("sell", qty=5000, oid="SELL-ODD")
exo = mk([oo]); pso = exo.state["parents"][oo.id]
pso["filled"] = 4950                                   # còn 50cp lẻ
check("phần lẻ <1 lô đi trọn (không bị trần cắt về 0)",
      exo._child_qty(oo, pso, exo.broker.quote, PX, T(9, 15)) == 50,
      f"{exo._child_qty(oo, pso, exo.broker.quote, PX, T(9, 15))}")
osm = order("buy", qty=300, oid="BUY-SMALL")
exsm = mk([osm]); pssm = exsm.state["parents"][osm.id]
qsm = exsm._child_qty(osm, pssm, exsm.broker.quote, PX, T(11, 0))
check("lệnh 300cp / 5 block ⇒ trần tối thiểu 1 lô = 100cp (không sinh lệnh 0)", qsm == LOT, f"{qsm}")

# ───────────────────────────── J. _would_be_unchanged dùng CÙNG trần
print("\nJ. _would_be_unchanged đồng bộ trần ⇒ không huỷ+đặt lại vô ích")
exj = mk([o5]); psj = exj.state["parents"][o5.id]
exj._place_slices(T(11, 0), "MORNING")
cj = exj._open_child(psj)
check("slice đầu đặt đúng 1000cp qua _place_slices", cj and cj["qty"] == 1000,
      f"{cj and cj['qty']}")
check("_would_be_unchanged=True (cùng giá + cùng KL đã trải) ⇒ REFRESH_SKIP, giữ FIFO",
      exj._would_be_unchanged(o5, psj, cj, T(11, 8)) is True)

# ───────────────────────────── K. Journal note tương thích bộ đếm adherence
print("\nK. Journal note")
note_in = None
with open(exj.journal_file, encoding="utf-8") as f:
    for line in f:
        if "PLACE" in line and "ft:" in line:
            note_in = line
            break
check("note in-block chứa 'ft:' ∧ 'in-window' (execution_quality_review.py vẫn đếm được)",
      note_in is not None and "ft:" in note_in and "in-window" in note_in,
      (note_in or "").strip()[-80:])
check("note in-block có chi tiết HYBRID 'hyb:blk left='",
      note_in is not None and "hyb:blk left=" in note_in)

# ───────────────────────────── M. End-to-end nhiều block
print("\nM. End-to-end _place_slices qua các block")
oe = order("buy", qty=5000, oid="BUY-E2E")
exe2 = mk([oe]); pse2 = exe2.state["parents"][oe.id]
for h, m in [(11, 0), (11, 15), (13, 0), (13, 15), (13, 30)]:
    c = exe2._open_child(pse2)
    if c:                                   # giả lập khớp trọn slice trước rồi mới sang block sau
        c["status"] = "closed"; c["filled"] = c["qty"]
        pse2["filled"] += c["qty"]
        exe2._release_child(oe.ticker, c)
    exe2._place_slices(T(h, m), "MORNING")
qtys = [p["qty"] for p in exe2.broker.placed]
check("5 lệnh con, mỗi lệnh 1000cp, tổng đúng 5000", qtys == [1000] * 5 and sum(qtys) == 5000,
      f"{qtys}")

# ───────────────────────────── N. Cổng HOÃN đặt lệnh ngoài block
print("\nN. _hybrid_defer — hoãn ngoài block, TỰ KẾT THÚC khi hết cửa sổ")
exd2 = mk([ob, os_])
for h, m, exp, lbl in [(9, 30, True, "BUY 09:30 hoãn (khung sáng đắt nhất)"),
                       (10, 50, True, "BUY 10:50 hoãn"),
                       (11, 0, False, "BUY 11:00 vào block ⇒ đặt"),
                       (11, 40, True, "BUY 11:40 nghỉ trưa ⇒ hoãn"),
                       (13, 30, False, "BUY 13:30 block cuối ⇒ đặt"),
                       (13, 45, False, "BUY 13:45 HẾT cửa sổ ⇒ KHÔNG hoãn nữa (chống kẹt hàng)"),
                       (14, 20, False, "BUY 14:20 ⇒ không hoãn")]:
    check(lbl, exd2._hybrid_defer(ob, T(h, m)) is exp, f"{exd2._hybrid_defer(ob, T(h, m))}")
for h, m, exp, lbl in [(9, 0, True, "SELL 09:00 (trước khớp liên tục) hoãn"),
                       (9, 15, False, "SELL 09:15 vào block ⇒ đặt"),
                       (10, 10, False, "SELL 10:10 vẫn trong block cuối"),
                       (10, 15, False, "SELL 10:15 HẾT cửa sổ ⇒ không hoãn nữa"),
                       (14, 0, False, "SELL 14:00 ⇒ không hoãn")]:
    check(lbl, exd2._hybrid_defer(os_, T(h, m)) is exp, f"{exd2._hybrid_defer(os_, T(h, m))}")
check("cờ TẮT ⇒ không bao giờ hoãn (hành vi cũ)",
      mk([ob], hybrid=False)._hybrid_defer(ob, T(9, 30)) is False)
check("urgency=high ⇒ không hoãn", mk([oh])._hybrid_defer(oh, T(9, 30)) is False)
check("mode=live + live_gate ⇒ không hoãn (LIVE byte-identical)",
      mk([ob], mode="live")._hybrid_defer(ob, T(9, 30)) is False)

print("\nN'. Chống kẹt hàng end-to-end + journal HYBRID_DEFER")
ostr = order("buy", qty=5000, oid="BUY-STRAND")
exst = mk([ostr]); psst = exst.state["parents"][ostr.id]
exst._place_slices(T(9, 30), "MORNING")
check("09:30 (ngoài block) ⇒ KHÔNG có lệnh nào ra broker", exst.broker.placed == [],
      f"{exst.broker.placed}")
exst._place_slices(T(10, 0), "MORNING")
exst._place_slices(T(10, 30), "MORNING")
n_defer = sum(1 for line in open(exst.journal_file, encoding="utf-8")
              if "HYBRID_DEFER" in line)
check("journal HYBRID_DEFER ghi ĐÚNG 1 lần/parent (3 chu kỳ hoãn)", n_defer == 1, f"{n_defer}")
exst._place_slices(T(14, 0), "AFTERNOON")     # hết cửa sổ, chưa khớp gì
check("CHỐNG KẸT HÀNG: 14:00 (hết cửa sổ) ⇒ phần dư đi TRỌN 5000 trong 1 lệnh",
      [p["qty"] for p in exst.broker.placed] == [5000],
      f"{[p['qty'] for p in exst.broker.placed]}")

# ───────────────────────────── O. Bypass tầng RỦI RO (2 lỗi quant-skeptic tái lập 2026-08-10)
print("\nO. _hybrid_bypass — tầng rủi ro luôn thắng HYBRID (2 lỗi thật đã sửa)")
# O1. EXTREME_DOWN: lệnh BÁN khẩn trong cửa sổ BÁN không được HYBRID làm chậm/cắt KL.
oe1 = order("sell", qty=8000, oid="SELL-EXTREME")
exx = mk([oe1], extreme_regime_enabled=True)
psx = exx.state["parents"][oe1.id]
T_EXT = T(9, 30)                                   # 09:30 = GIỮA block BÁN thứ 2
# 09:30 còn 3 block BÁN (09:30/09:45/10:00) ⇒ ceil(8000/3)=2667 → làm tròn lô = 2600
check("O1a chưa EXTREME ⇒ HYBRID áp bình thường (nhịp 1,875× + trần 1/3 = 2600)",
      exx._fill_timing_mult(oe1, T_EXT) == BLK
      and exx._child_qty(oe1, psx, exx.broker.quote, PX, T_EXT) == 2600,
      f"mult={exx._fill_timing_mult(oe1, T_EXT)} qty={exx._child_qty(oe1, psx, exx.broker.quote, PX, T_EXT)}")
exx._extreme_state[SYM] = {"n": 2,                  # armed + còn cooldown
                           "until": (T_EXT + dt.timedelta(minutes=10)).isoformat()}
check("O1b EXTREME armed ⇒ nhịp về 1.0 (không chậm hơn cả thời trước HYBRID)",
      exx._fill_timing_mult(oe1, T_EXT) == 1.0, f"{exx._fill_timing_mult(oe1, T_EXT)}")
check("O1c EXTREME armed ⇒ KHÔNG cắt KL, xả trọn phần dư 8000",
      exx._child_qty(oe1, psx, exx.broker.quote, PX, T_EXT) == 8000,
      f"{exx._child_qty(oe1, psx, exx.broker.quote, PX, T_EXT)}")
check("O1d EXTREME armed ⇒ không bao giờ hoãn (kể cả ngoài block, 11:00)",
      exx._hybrid_defer(oe1, T(11, 0)) is False)
exoff = mk([oe1], extreme_regime_enabled=False)     # CHỨNG MINH NGƯỢC: cờ EXTREME tắt
exoff._extreme_state[SYM] = {"n": 2, "until": (T_EXT + dt.timedelta(minutes=10)).isoformat()}
check("O1e CHỨNG MINH NGƯỢC: extreme_regime_enabled=False ⇒ state armed KHÔNG mở bypass",
      exoff._fill_timing_mult(oe1, T_EXT) == BLK, f"{exoff._fill_timing_mult(oe1, T_EXT)}")

# O2. gap-adaptive: điều kiện phải THUẦN, không lệ thuộc thứ tự gọi trong step().
ogp = order("buy", qty=5000, oid="BUY-GAP")
exgp = mk([ogp], gap_adaptive_enabled=True)
psgp = exgp.state["parents"][ogp.id]
exgp._gap_z_cache[SYM] = -3.0                       # down-gap bất thường
T_GAP = T(9, 30)
check("O2a _last_gap_override CHƯA được nạp (mô phỏng đúng nhánh _cancel_stale chạy trước)",
      SYM not in exgp._last_gap_override)
check("O2b điều kiện gap vẫn đúng qua hàm thuần ⇒ bypass ngay tick đó",
      exgp._gap_override_active(ogp, T_GAP) is True
      and exgp._hybrid_bypass(ogp, T_GAP) is True)
check("O2c ⇒ _child_qty KHÔNG cắt KL dù chưa ai gọi _fill_timing_mult trước (hết churn 1 tick)",
      exgp._child_qty(ogp, psgp, exgp.broker.quote, PX, T_GAP) == 5000,
      f"{exgp._child_qty(ogp, psgp, exgp.broker.quote, PX, T_GAP)}")
check("O2d hai đường (_place_slices và _would_be_unchanged) cho CÙNG KL ở cùng tick",
      exgp._child_qty(ogp, psgp, exgp.broker.quote, PX, T_GAP)
      == (exgp._fill_timing_mult(ogp, T_GAP) and
          exgp._child_qty(ogp, psgp, exgp.broker.quote, PX, T_GAP)))
check("O2e sau 09:45 (hết cửa sổ gap) ⇒ bypass tắt, HYBRID áp lại bình thường",
      exgp._gap_override_active(ogp, T(11, 0)) is False
      and exgp._child_qty(ogp, psgp, exgp.broker.quote, PX, T(11, 0)) == 1000,
      f"{exgp._child_qty(ogp, psgp, exgp.broker.quote, PX, T(11, 0))}")
check("O2f CHỨNG MINH NGƯỢC: gap_adaptive_enabled=False ⇒ không bypass dù cache có gap_z",
      mk([ogp])._gap_override_active(ogp, T_GAP) is False)
check("O2g gap-override chỉ áp chiều MUA (lệnh BÁN không bị ảnh hưởng)",
      exgp._gap_override_active(order("sell", oid="S-GAP"), T_GAP) is False)

print("\nP. Deadlock khởi động EXTREME khi đang HOÃN (lỗi quant-skeptic vòng 2)")
# Vì sao ca này tồn tại: O1 nạp THẲNG `_extreme_state` (already-armed) nên che mất câu hỏi
# "làm sao nó ARM được?". quant-skeptic vòng 2 tái lập: `_hybrid_defer` `continue` TRƯỚC lời
# gọi `_extreme_regime` — đường DUY NHẤT nạp state — mà `_cancel_stale` chỉ poll lại cho lệnh
# ĐÃ có con đang mở (lệnh bị hoãn không bao giờ có) ⇒ bộ đếm 2-poll không bao giờ tăng ⇒ bypass
# không bao giờ mở. Lệnh BÁN cắm sàn từ mở cửa đặt 0 lệnh suốt 09:00-09:15 — TỆ HƠN nền cũ.
# Ca này đi qua ĐÚNG đường thật: `_place_slices` theo tick, KHÔNG nạp tay state.
class FloorQuote(FakeQuote):
    """Quote cắm sàn — kịch bản sập ở mở cửa (trigger (i) cận sàn của `_extreme_regime`)."""
    def __init__(self):
        super().__init__()
        self.last = self.floor          # last == floor ⇒ chắc chắn trong dải cận sàn


def crash_at_open(hybrid):
    osell = order("sell", qty=8000, oid="SELL-CRASH")
    ex = mk([osell], hybrid=hybrid, extreme_regime_enabled=True)
    ex.broker.quote = FloorQuote()
    for mnt in range(0, 15):             # 09:00 → 09:14, TRƯỚC cửa sổ BÁN 09:15
        ex._place_slices(T(9, mnt), phase="MAIN")
    return ex, sum(p["qty"] for p in ex.broker.placed)


ex_hyb, qty_hyb = crash_at_open(hybrid=True)
ex_base, qty_base = crash_at_open(hybrid=False)
check("P1 NỀN (hybrid TẮT): lệnh bán khẩn xả được trong 09:00-09:15",
      qty_base > 0, f"{qty_base}")
check("P2 EXTREME ARM ĐƯỢC dù đang trong khoảng hoãn (không còn deadlock)",
      ex_hyb._extreme_state.get(SYM, {}).get("until") is not None,
      f"state={ex_hyb._extreme_state.get(SYM)}")
check("P3 HYBRID KHÔNG được tệ hơn nền: cũng xả được trong 09:00-09:15",
      qty_hyb > 0, f"hybrid={qty_hyb} vs nền={qty_base}")
check("P4 xả ĐỦ KL như nền (không bị trần block cắt phần dư)",
      qty_hyb == qty_base == 8000, f"hybrid={qty_hyb} nền={qty_base}")
check("P5 KHÔNG đếm-đôi bộ đếm 2-poll (memoize theo (ticker, now) còn hiệu lực)",
      ex_hyb._extreme_state.get(SYM, {}).get("n", 0) <= 15,
      f"n={ex_hyb._extreme_state.get(SYM, {}).get('n')}")
# CHỨNG MINH NGƯỢC: ngày thường (quote KHÔNG cắm sàn) thì HYBRID vẫn phải hoãn như thiết kế —
# bản vá chỉ mở đường cho lệnh KHẨN, không được vô hiệu hoá lịch trải.
onorm = order("sell", qty=8000, oid="SELL-NORMAL")
exn = mk([onorm], extreme_regime_enabled=True)
for mnt in range(0, 15):
    exn._place_slices(T(9, mnt), phase="MAIN")
check("P6 CHỨNG MINH NGƯỢC: ngày thường ⇒ VẪN hoãn trước 09:15 (lịch trải còn nguyên)",
      len(exn.broker.placed) == 0 and exn._extreme_state.get(SYM, {}).get("until") is None,
      f"placed={len(exn.broker.placed)}")

print("\nQ. Throttle poll EXTREME lúc HOÃN — chi phí API (quant-skeptic vòng 3)")
# Bản vá lỗi (3) mở lại đường poll trong lúc hoãn ⇒ mỗi lệnh MUA bị hoãn gọi get_quote MỖI chu kỳ
# 20s suốt 09:15-11:00. Đo được +359 lời gọi/lệnh/phiên (10 lệnh: +3.590) so với 1 ở nền cũ.
# Rơi NGAY khi bật cờ trên paper `main` (account đó đã bật sẵn extreme_regime_enabled trong
# `overrides`). Throttle theo TICKER, mặc định 60s.
def count_quotes(n_orders=10, poll_sec=None, hybrid=True):
    orders = [order("buy", qty=5000, oid=f"BQ{i}") for i in range(n_orders)]
    over = {} if poll_sec is None else {"extreme_defer_poll_sec": poll_sec}
    exq = mk(orders, hybrid=hybrid, extreme_regime_enabled=True, **over)
    cnt = {"n": 0}
    _orig = exq.broker.get_quote

    def _counting(sym):
        cnt["n"] += 1
        return _orig(sym)

    exq.broker.get_quote = _counting
    t = T(9, 0)
    while t < T(11, 0):                      # phiên sáng, chu kỳ 20s như production
        exq._place_slices(t, phase="MAIN")
        t += dt.timedelta(seconds=20)
    return cnt["n"], exq


q_thr, _ = count_quotes(10)                          # mặc định 60s
q_raw, _ = count_quotes(10, poll_sec=0)              # tắt throttle = hành vi trước khi vá
q_base, _ = count_quotes(10, hybrid=False)           # nền trước HYBRID
check("Q1 nền (hybrid TẮT) chỉ tốn 1 quote/lệnh", q_base == 10, f"{q_base}")
check("Q2 KHÔNG throttle ⇒ bùng nổ lời gọi (tái lập đúng vấn đề reviewer nêu)",
      q_raw >= 3000, f"{q_raw}")
check("Q3 throttle 60s cắt ≥5× số lời gọi", q_thr * 5 <= q_raw, f"{q_thr} vs {q_raw}")
check("Q4 throttle gộp theo TICKER (10 lệnh cùng mã KHÔNG nhân 10 lần)",
      q_thr <= 130, f"{q_thr}")
# Quan trọng nhất: throttle KHÔNG được làm hỏng bản vá lỗi (3) — vẫn phải arm + xả được.
osell_t = order("sell", qty=8000, oid="SELL-THR")
ext = mk([osell_t], extreme_regime_enabled=True)
ext.broker.quote = FloorQuote()
for mnt in range(0, 15):
    ext._place_slices(T(9, mnt), phase="MAIN")
check("Q5 throttle BẬT mà lệnh bán khẩn VẪN arm + xả đủ (không tái sinh deadlock)",
      ext._extreme_state.get(SYM, {}).get("until") is not None
      and sum(p["qty"] for p in ext.broker.placed) == 8000,
      f"placed={sum(p['qty'] for p in ext.broker.placed)}")
check("Q6 CHỨNG MINH NGƯỢC: throttle KHÔNG áp cho đường đặt lệnh thường (chỉ nhánh hoãn)",
      count_quotes(1, hybrid=False)[0] == 1)

print("\nR. Throttle GẶP QUOTE LỖI trong cửa sổ hoãn (quant-skeptic REFUTED vòng 4)")
# Lỗ hổng reviewer tái lập trên code thật: bản throttle đầu đóng dấu `_extreme_defer_poll[ticker]`
# TRƯỚC khi biết `get_quote` có trả về quote dùng được không. `PHSBroker.get_quote` (brokers.py)
# `return None` khi có exception — hành vi ĐÃ CÓ SẴN. Nên 1 quote lỗi tiêu trọn 60s throttle mà
# bộ đếm 2-poll-confirm không nhích ⇒ dưới chuỗi lỗi lặp ĐÚNG NHỊP 60s, lệnh BÁN khẩn kẹt sạch
# cửa sổ hoãn = đúng deadlock vòng 2 qua lối khác. FakeBroker của các bộ trên KHÔNG BAO GIỜ lỗi
# nên không ca nào chạm được nhánh này — đây chính là ca còn thiếu.
def run_flaky(fail_pred, hybrid=True, t0=None, t_end=None, step=20, qty=8000):
    """Chạy `_place_slices` theo nhịp 20s thật, `get_quote` trả None theo `fail_pred(elapsed_s)`.
    Trả (executor, số lần THỬ gọi quote, thời điểm EXTREME arm được hoặc None)."""
    t0 = t0 or T(9, 0); t_end = t_end or T(9, 15)
    ex = mk([order("sell", qty=qty, oid="SELL-FLAKY")], hybrid=hybrid,
            extreme_regime_enabled=True)
    ex.broker.quote = FloorQuote()
    tries = {"n": 0}
    _orig = ex.broker.get_quote

    def _flaky(sym):
        tries["n"] += 1
        return None if fail_pred((_t[0] - t0).total_seconds()) else _orig(sym)

    ex.broker.get_quote = _flaky
    _t = [t0]; armed_at = None
    while _t[0] < t_end:
        ex._place_slices(_t[0], phase="MAIN")
        if armed_at is None and ex._extreme_state.get(SYM, {}).get("until"):
            armed_at = _t[0]
        _t[0] += dt.timedelta(seconds=step)
    return ex, tries["n"], armed_at


# R1 — CỘNG HƯỞNG: quote lỗi đúng các mốc throttle mở (mỗi 60s). Đây là ca code CŨ chết hẳn
# (mọi lần được phép poll đều rơi vào lần lỗi ⇒ không bao giờ arm).
ex_r, tries_r, armed_r = run_flaky(lambda s: s % 60 == 0)
check("R1 quote lỗi lặp ĐÚNG NHỊP throttle 60s ⇒ EXTREME VẪN arm được (không deadlock)",
      armed_r is not None, f"armed_at={armed_r}")
check("R1b arm trong thời gian CÓ TRẦN (≤3 phút), không phải 'rồi sẽ arm lúc nào đó'",
      armed_r is not None and armed_r <= T(9, 3), f"armed_at={armed_r}")
check("R1c arm xong thì lệnh bán khẩn xả ĐỦ KL ngay trong cửa sổ hoãn",
      sum(p["qty"] for p in ex_r.broker.placed) == 8000,
      f"placed={sum(p['qty'] for p in ex_r.broker.placed)}")

# R2 — CƠ CHẾ: lần poll LỖI không được đóng dấu throttle (assert thẳng vào nguyên nhân gốc,
# không chỉ vào triệu chứng). Code cũ FAIL ca này.
ex_r2 = mk([order("sell", qty=8000, oid="SELL-FAIL1")], extreme_regime_enabled=True)
ex_r2.broker.quote = FloorQuote()
ex_r2.broker.get_quote = lambda sym: None
ex_r2._place_slices(T(9, 0), phase="MAIN")
check("R2 poll LỖI KHÔNG đóng dấu throttle (không tiêu cửa sổ 60s)",
      SYM not in ex_r2._extreme_defer_poll, f"stamp={ex_r2._extreme_defer_poll}")

# R3 — quote lỗi 100%: phải THỬ LẠI MỖI CHU KỲ (= đúng nhịp nền trước khi có throttle), không
# phải 1 lần/60s. 09:00→09:15 nhịp 20s = 45 chu kỳ. Code cũ ra 15.
CYCLES = 45
ex_r3, tries_r3, armed_r3 = run_flaky(lambda s: True)
check("R3 quote lỗi 100% ⇒ thử lại MỖI chu kỳ (không bị throttle khoá)",
      tries_r3 == CYCLES, f"{tries_r3}/{CYCLES}")
# CHỨNG MINH NGƯỢC: broker chết thì nền (hybrid TẮT) cũng không đặt được lệnh nào — tức 0 lệnh
# ở R3 là do broker, KHÔNG phải HYBRID làm tệ hơn nền (khác hẳn ca P vòng 2).
ex_r3b, _, _ = run_flaky(lambda s: True, hybrid=False)
check("R3b CHỨNG MINH NGƯỢC: broker chết ⇒ nền (hybrid TẮT) cũng 0 lệnh, HYBRID không tệ hơn",
      len(ex_r3.broker.placed) == 0 and len(ex_r3b.broker.placed) == 0,
      f"hybrid={len(ex_r3.broker.placed)} nền={len(ex_r3b.broker.placed)}")

# R4 — CHỨNG MINH NGƯỢC (chi phí): vá này KHÔNG được vô hiệu hoá throttle khi quote chạy bình
# thường — vẫn phải cắt mạnh so với tắt throttle (giữ nguyên kết luận bộ Q).
_, tries_r4, _ = run_flaky(lambda s: False)
check("R4 CHỨNG MINH NGƯỢC: quote chạy bình thường ⇒ throttle VẪN cắt (≤1/3 số chu kỳ)",
      tries_r4 <= CYCLES // 3, f"{tries_r4}/{CYCLES}")

# R5 — LỖI CHẬP CHỜN TỪNG PHẦN (quant-skeptic vòng 4 yêu cầu bổ sung trước khi bật paper):
# R1/R3/R4 mới phủ 3 điểm rời rạc (lỗi đúng nhịp 60s / lỗi 100% / không lỗi). Ca thật hay gặp
# nhất là chuỗi chập chờn — cần chốt TRẦN thời gian arm cho cả họ đó, không chỉ 3 điểm.
for _lbl, _pred in [("xen kẽ 1/2", lambda s: (s // 20) % 2 == 0),
                    ("lỗi 2/3",    lambda s: (s // 20) % 3 != 2),
                    ("lỗi 3/4",    lambda s: (s // 20) % 4 != 3),
                    ("lỗi 4/5",    lambda s: (s // 20) % 5 != 4)]:
    _ex, _tr, _at = run_flaky(_pred)
    check(f"R5 chập chờn ({_lbl}) ⇒ arm được, có TRẦN ≤4 phút, xả đủ KL",
          _at is not None and _at <= T(9, 4)
          and sum(p["qty"] for p in _ex.broker.placed) == 8000,
          f"armed_at={_at} placed={sum(p['qty'] for p in _ex.broker.placed)} tries={_tr}")

print("\n" + ("=" * 60))
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ TẤT CẢ PASS — HYBRID fill-timing đúng thiết kế, cờ TẮT ⇒ hành vi cũ nguyên vẹn")
